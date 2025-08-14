from vector import retriver, lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
from langchain.tools import tool
import pandas as pd
import os

CSV_FILE = "appointments.csv"

# CSV dosyasının varlığını kontrol et, yoksa oluştur
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["appointment_id","user_id","service_type","date","time","location","phone","email"])
    df.to_csv(CSV_FILE, index=False)

def save_appointment_to_csv(appointment):
    """Tek bir randevu kaydını CSV dosyasına kaydeder."""
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([appointment])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def get_appointments_from_csv():
    """CSV dosyasındaki tüm randevuları döndürür."""
    return pd.read_csv(CSV_FILE)

@tool
def book_appointment(user_id, service_type, date, time, location, phone, email):
    """
    Belirli bir hizmet türü için randevu oluşturur ve CSV dosyasına kaydeder.

    Argümanlar:
        user_id (str): Kullanıcının benzersiz kimliği.
        service_type (str): Hizmet türü (örn. 'router_installation', 'cleaning').
        date (str): Randevu tarihi (YYYY-MM-DD formatında).
        time (str): Randevu saati (HH:MM formatında).
        location (str): Randevu yapılacak yer.
        phone (str): İletişim telefon numarası.
        email (str): İletişim e-posta adresi.

    Döndürür:
        dict: {
            "success": bool,        # True ise randevu başarıyla oluşturuldu, False ise tarih dolu
            "message": str,         # Kullanıcıya gösterilecek mesaj
            "appointment_id": str   # Başarılı ise randevunun benzersiz ID'si
        }
    """
    df = pd.read_csv(CSV_FILE)

    # Uygunluk kontrolü
    existing = df[
        (df['date'] == date) &
        (df['time'] == time) &
        (df['service_type'] == service_type)
    ]
    if not existing.empty:
        return {"success": False, "message": "Seçilen tarih ve saat dolu."}

    appointment_id = f"APT-{len(df)+1:05d}"
    appointment = {
        "appointment_id": appointment_id,
        "user_id": user_id,
        "service_type": service_type,
        "date": date,
        "time": time,
        "location": location,
        "phone": phone,
        "email": email
    }

    save_appointment_to_csv(appointment)

    return {
        "success": True,
        "message": f"Randevunuz {date} saat {time} için başarıyla oluşturuldu.",
        "appointment_id": appointment_id
    }

@tool
def retrieve_appointments(user_id=None):
    """
    Tüm randevuları veya belirli bir kullanıcıya ait randevuları döndürür.

    Argümanlar:
        user_id (str, opsiyonel): Eğer belirtilirse, yalnızca bu kullanıcıya ait randevular döndürülür.

    Döndürür:
        list[dict]: Her randevu için bir sözlük listesi. Sözlükler şunları içerir:
            - appointment_id
            - user_id
            - service_type
            - date
            - time
            - location
            - phone
            - email
    """
    df = pd.read_csv(CSV_FILE)
    if user_id:
        df = df[df['user_id'] == user_id]
    return df.to_dict(orient='records')

result = book_appointment.invoke(
    {'user_id':"11111",
    'service_type':"router_installation",
    'date':"2025-08-20",
    'time':"14:00",
    'location':"Istanbul",
    'phone':"555-1234",
    'email':"john@example.com"}
)

print("Booking Result:")
print(result)