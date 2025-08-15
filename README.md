# 📞 TEKNOFEST NLP Senaryo Kategorisi - Yapay Zeka Çağrı Merkezi Asistanı

Bu proje, **TEKNOFEST 2025 NLP Senaryo Yarışması** için geliştirilmiş bir yapay zeka çağrı merkezi asistanıdır.  
Sistem, **ReAct tarzı** akıl yürütme, çok adımlı karar alma, dinamik araç kullanımı, bellek yönetimi ve bağlam değiştirme özelliklerine sahiptir.  
Tüm geliştirme sürecinde **yalnızca açık kaynak teknolojiler** kullanılmıştır.

---

## 📦 Bağımlılıklar

Aşağıdaki kütüphaneler ve araçlar projeyi çalıştırmak için gereklidir.

> Tüm bağımlılıkları yüklemek için:

pip install -r requirements.txt

**➤ Python Kütüphaneleri**

⬩ langgraph — Grafik tabanlı AI orkestrasyonu

⬩ langchain-core — LangChain çekirdek bileşenleri

⬩ langchain-ollama — Ollama entegrasyonu

⬩ chromadb — Vektör veritabanı (bellek ve arama)

⬩ gradio — Web tabanlı test arayüzü

⬩ pandas — Veri işleme

⬩ numpy — Sayısal hesaplamalar

⬩ typing-extensions — Genişletilmiş tip desteği

**➤ Sistem Gereksinimleri**

⬩ Python: 3.10+

⬩ Ollama: Ollama’yı indir

⬩ Git (depo klonlamak için)

⬩ Git (depo klonlamak için)


## ⚙️ Kurulum ve Çalıştırma Adımları

**1️⃣ Depoyu Klonla**

┃ git clone https://github.com/KULLANICI_ADI/DEPO_ADI.git     
┃ cd DEPO_ADI                                                

**2️⃣ Sanal Ortam Oluştur ve Aktifleştir**

┃ python -m venv venv
┃ source venv/bin/activate   # Mac/Linux
┃ venv\Scripts\activate      # Windows

**3️⃣ Bağımlılıkları Yükle**

┃ pip install -r requirements.txt

**4️⃣ Modeli İndir**

┃ ollama pull qwen3:8b

**5️⃣ Uygulamayı Başlat**

┃ python main.py

**6️⃣ Arayüze Eriş**

✦Terminalde görünen bağlantıyı (örn. http://127.0.0.1:7860) tarayıcıda aç.



## 📝 Notlar

⬩ .env dosyasına gerekli ortam değişkenlerini eklemeyi unutmayın.

⬩ Kullanılacak veri setlerini data/ klasörüne yerleştirin.

⬩ Proje mimarisi ve araç açıklamaları docs/ klasöründe bulunur.
