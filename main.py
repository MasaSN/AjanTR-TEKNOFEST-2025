from langgraph.graph import START, END, StateGraph
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.store.memory import InMemoryStore
from langchain_core.documents import Document
import pandas as pd
import os
import json
from typing import TypedDict, Optional
import gradio as gr
from typing import TypedDict
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, create_react_agent
from reducer import reducer, clean_think_tags
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from roaming_tools import check_roaming_status, deactivate_roaming
from tools import (
    retrive_customer_information,
    lookup_internet_issue,
    lookup_internet_package,
    initiate_package_change,
    activate_roaming,
    authorize_user,
    update_customer_information,
)
from eligable_tools import check_if_student, lookup_student_package, initiate_student_package
from appointment_tools import book_appointment, retrieve_appointments
from address_tools import lookup_store_address
from billing_tools import lookup_customer_bills
from intent_tools import saving_intent , retrieve_long_term_memory
# -----------------------------------------------------------------
user_id = '55555'
# Define the chat state without 'plan' and 'user_input'
class ChatState(TypedDict):
    messages: list
    intent : Optional[str]

# Updated system message (no planner references)
sys_msg = SystemMessage(content="""
Sen, yardımcı ve adım adım ilerleyen bir telekom müşteri hizmetleri asistanısın. Müşteri bilgilerini sorgulayabilir, internet sorunlarını giderebilir, paket değişikliği yapabilir ve kullanıcı isteklerini hatırlayabilirsin.
**Kesin Kural:** Her yanıt yalnızca telekom hizmetleri ve müşteri işlemleri ile ilgili olmalıdır. Kullanıcı farklı bir konu sorarsa, yalnızca kibarca telekom ile ilgili olduğunu hatırlat ve başka yanıt verme.

## Dil Kuralları:
- Tüm yanıtlar **Türkçe** olacak. Kullanıcı başka bir dilde yazsa bile, yanıtlarını Türkçe ver.
- Kod veya veri çıktılarında açıklamalar Türkçe, ancak değişken ve alan adları orijinal dillerinde kalacak.

## Görevlerin:
- Kullanıcının internet servisi, telefon paketi veya hesabı ile ilgili taleplerine yardımcı ol.
- Gerekli olduğunda veri çekmek veya değişiklik yapmak için araçları kullan.

## Araç Kullanım Kuralları:

1. retrive_customer_information: Müşterinin paketi, e-postası veya genel durumu gibi spesifik bilgilerini almak için kullan.
2. lookup_internet_package: İnternet paketi detaylarını isimle sorgulamak için kullan.
3. lookup_internet_issue: Bildirilen internet sorununu anlamak veya çözmek için kullan.
4. initiate_package_change: Kullanıcının mevcut internet veya telefon paketini değiştirmek için kullan.
5. activate_roaming: Yurtdışından arayan kullanıcılar için dolaşım (roaming) aktivasyonu yapmak için kullan.
6. authorize_user: Bazı işlemler için kullanıcı yetkilendirmesi yapmak için kullan.
7. update_customer_information: Müşterinin paketini, e-posta adresini, hesap durumunu veya diğer bilgilerini güncellemek için kullan.
8. lookup_customer_bills: Müşterinin fatura geçmişini CSV dosyasından almak için kullan.
9. lookup_store_address: Kullanıcının bulunduğu ilçe veya konuma göre en yakın telekom mağazasını bulmak için kullan.
**Not:** Fatura ödemesi sadece uygulama üzerinden veya şubelerden yapılabilir
## Davranış:
- Araç çağırmadan önce adım adım düşün.
- Gereksiz olmadıkça aynı anda sadece bir araç kullan.
- Niyet konusunda emin değilsen, kullanıcıya açıklayıcı bir soru sor.
- Kullanıcı telekom dışı konular hakkında konuşursa, kibarca amacını belirterek sadece telekom konularında yardımcı olabileceğini söyle.
- Yanıtlarını kısa, samimi ve yardımcı şekilde ver.

**Not:** Sorumluluğun, yalnızca telekom ile ilgili taleplere yanıt vermektir ve kullanıcılara kibarca bu sınırı hatırlatabilirsin.
""")


intent_sys_msg = SystemMessage(content="""
    Sen bir niyet (intent) sınıflandırma asistanısın.

Görevin, her kullanıcı mesajını analiz ederek şu adımları uygulamaktır:
- Mesajda açık bir hedef, görev veya talep (yani bir "niyet") olup olmadığını belirlemek.
- Eğer varsa, niyet adını ve ilgili varlıkları (ör. paket adı, telefon numarası vb.) çıkarmak.
- Eğer mesaj günlük sohbet, selamlaşma, teşekkür veya amacı olmayan bir ifade ise (ör. "merhaba", "teşekkürler", "haha", "sadece merak ettim..."), sınıflandırma yapmamalı ve hiçbir araç çağrısı gerçekleştirmemelisin.

Yalnızca mesaj geçerli bir niyet içeriyorsa, `saving_intent` aracını şu parametrelerle çağırmalısın:
- `text`: orijinal kullanıcı mesajı
- `intent`: kullanıcının amacını net şekilde özetleyen kısa bir etiket (ör. "paket_degistirme", "roaming_acma", "hizmet_iptali")
- `entities`: çıkarılan ilgili bilgileri içeren bir sözlük (ör. {"paket": "Gold"}, {"roaming_turu": "uluslararası"})
- 
Sen, daha büyük bir yapay zeka tabanlı çağrı merkezi sisteminin bir parçasısın. Bu nedenle kesin ve hatasız olmalı, gereksiz araç kullanımından kaçınmalısın.

Geçerli ve geçersiz niyet mesajlarına örnekler:

---
Geçerli:
Kullanıcı: "Paketimi Gold’a değiştirmek istiyorum."
→ intent: paket_degistirme, entities: {"paket": "Gold"}

Kullanıcı: "Hattımı uluslararası roaming’e geçirmek istiyorum."
→ intent: roaming_acma, entities: {"roaming_turu": "uluslararası"}

---
Geçersiz:
Kullanıcı: "Merhaba!"
→ Niyet yok — araç çağrısı yapılmaz.

Kullanıcı: "Haha, çok komik."
→ Niyet yok — araç çağrısı yapılmaz.

Kullanıcı: "Teşekkürler, size de."
→ Niyet yok — araç çağrısı yapılmaz.

Net bir niyet yoksa hiçbir araç çağrısı yapma.
""")


# Tool list
tools = [
    retrive_customer_information, 
    lookup_internet_package,
    lookup_internet_issue,
    initiate_package_change,
    activate_roaming,
    authorize_user,
    update_customer_information,
    lookup_customer_bills,
    lookup_store_address,
    book_appointment,
    retrieve_appointments,
    check_roaming_status,
    deactivate_roaming,
    check_if_student, 
    lookup_student_package, 
    initiate_student_package
]
intent_tools= [
    saving_intent
]
# LLM setup
action_llm = init_chat_model(
    model='qwen3:30b-a3b',
    model_provider='ollama',
    temperature=0.2,
    max_tokens=512,
    system=sys_msg
)
intent_llm = init_chat_model(
    model='qwen3:1.7b',
    model_provider='ollama',
    temperature=0.2,
    max_tokens=512,
    system=intent_sys_msg
)
action_llm = action_llm.bind_tools(tools)

intent_classifier_llm = intent_llm.bind_tools(intent_tools)
# raw_llm = init_chat_model(CHAT_MODEL, model_provider='ollama')
intent_tools_node = ToolNode(intent_tools)


def intent_classifier_node(state):
    print("CLASSIFIER CALLED")
    """Runs intent classifier and executes its tools (if any)."""
    result = intent_classifier_llm.invoke('kullanıcı mesajı: '+state['messages'][-1]['content'])
    
    tool_calls = getattr(result, 'tool_calls', None)

    if tool_calls:
        tool_result = intent_tools_node.invoke({'messages': [result]})
        print(tool_result)
        print("intent tools called")
        try:
            tool_msg = tool_result['messages'][0]
            content = json.loads(tool_msg.content)
            state['intent'] = content.get('intent')
            
            print(f"Saved to state: {state['intent']}")
        except Exception as e:
            print("Error parsing tool output:", e)

    if 'intent' not in state:
            state['intent'] = None
    
    return {'messages': state['messages'] ,'intent':state['intent']}


def llm_node(state):
    print("MAIN LLM CALLED")
    last_user_msg = None
    memories = []
    for msg in reversed(state['messages']):
        if isinstance(msg, dict) and msg.get('role') == 'user':
            last_user_msg = msg['content']
            break
    # print("last ueser message: -----", last_user_msg)
    if state['intent']:
        print("STATE INTENT", state['intent'])
        memories = retrieve_long_term_memory(last_user_msg,state['intent'],user_id)
    # print("MEMORIES",memories)
    if memories:
        print("MEMORIES",memories)
        memories_text = "\n".join([doc.page_content for doc in memories])
        memory_context = SystemMessage(content=f"Kullanıcının ilgili geçmiş anıları şunlardır:\n{memories_text}")
        combined_messages = [memory_context] + reducer(state['messages'])
    else:
        combined_messages= reducer(state['messages'])

    response = action_llm.invoke(combined_messages)

    # cleaned_content = clean_think_tags(response.content)
    # cleaned_response = AIMessage(content=cleaned_content)

    return {'messages': state['messages'] + [response]}


def router(state):
    last_message = state['messages'][-1]
    return 'tools' if getattr(last_message, 'tool_calls', None) else 'end'



tool_node = ToolNode(tools)


def tools_node(state):
    try:
        result = tool_node.invoke(state)
        return {'messages': state['messages'] + result['messages']}
    except Exception as e:
        return {'messages': state['messages'] + [AIMessage(content=f"Tool error: {str(e)}")]}




builder = StateGraph(ChatState)
builder.add_node('intent_classifier', intent_classifier_node)
builder.add_node('llm', llm_node)
builder.add_node('tools', tools_node)
builder.add_edge(START, 'intent_classifier')
builder.add_edge('intent_classifier', 'llm')
builder.add_edge('tools', 'llm')
builder.add_conditional_edges('llm', router, {'tools': 'tools', 'end': END})

graph = builder.compile()


state = {"messages": []}

def chat_fn(user_message, history):
    # state = {"messages": []}
    # Add user message to state
    state['messages'].append({'role': 'user', 'content': user_message})

    # Run through the LangGraph pipeline
    new_state = graph.invoke(state)
    

    # Update state reference
    state.update(new_state)

    # Get the last assistant message
    
    assistant_reply_raw = state['messages'][-1].content
    if '</think>' in assistant_reply_raw:
        assistant_reply = assistant_reply_raw.split('</think>')[-1].strip()
    else:
        assistant_reply = assistant_reply_raw.strip()
    print(assistant_reply)
    # Append to Gradio's history format
    history.append((user_message, assistant_reply))
    print("STATE",state)
    return history, state

# Create the Gradio interface
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear")

    msg.submit(chat_fn, [msg, chatbot], [chatbot, gr.State(state)])
    clear.click(lambda: ([], {"messages": [], "intent": None}), None, [chatbot, gr.State(state)])

# Run app
if __name__ == "__main__":
    demo.launch()
