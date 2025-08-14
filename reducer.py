from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
def reducer(messages: list) -> list:
    # Keep last 10 messages (5 interactions)
    recent_msgs = messages[-10:]

    cleaned_msgs = []
    for msg in recent_msgs:
        # Get content depending on type
        if isinstance(msg, dict):
            content = msg.get('content', '')
            role = msg.get('role', 'user')
        else:
            # Assume LangChain message object
            content = getattr(msg, 'content', '')
            role = getattr(msg, 'role', 'user')

        # Optionally keep <think> blocks intact, or process content here
        # Example: content = content  (no change)

        cleaned_msgs.append({'role': role, 'content': content})
    return cleaned_msgs



def clean_think_tags(text: str) -> str:
    if '<think>' in text:
        return text.split('</think>')[-1].strip()
    return text
