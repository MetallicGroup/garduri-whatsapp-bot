from flask import Flask, request
import requests
import json

app = Flask(__name__)

# ===== CONFIG =====
GUPSHUP_API_KEY = "sk_61acaaa5c9bb46988dd1d8a6de151156"
WHATSAPP_APP_ID = "745575598094192"
PHONE_NUMBER = "15557799070"

# Google Sheets endpoints
LEADS_URL = "https://script.google.com/macros/s/AKfycbzkX0oACXfyCayKuzm1tZhBTOg0-KYEUrk23jX69UIqPpm26cNpfR3N7AziL4xkWGomlA/exec"
PRICES_URL = "https://script.google.com/macros/s/AKfycbwFOnEhGNhx-J3YxjF4e5AxLkiuaexiPcF-baqAT-WMOJGdRklnB-mB8xoSSKXhmJpu/exec"
SECRET = "MX25secure_2025_AI"

# Poze modele gard
IMAGE_URLS = {
    "MX25 0.5mm": "https://ibb.co/wqf2Wnd",
    "MX25 0.6mm": "https://ibb.co/3yfz066S",
    "MX25 DUO 0.5mm": "https://ibb.co/TqN0wLPj",
    "MX25 DUO 0.6mm": "https://ibb.co/3yfz066S"
}

AR_LINK = "https://skfb.ly/pzUtW"


# ===== FUNCȚIE TRIMITERE WHATSAPP =====
def send_whatsapp_text(phone, text):
    url = f"https://api.gupshup.io/sm/api/v1/msg"
    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "channel": "whatsapp",
        "source": PHONE_NUMBER,
        "destination": phone,
        "message": json.dumps({"type": "text", "text": text}),
        "src.name": WHATSAPP_APP_ID
    }
    requests.post(url, headers=headers, data=data)


def send_whatsapp_image(phone, img_url, caption):
    url = f"https://api.gupshup.io/sm/api/v1/msg"
    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "channel": "whatsapp",
        "source": PHONE_NUMBER,
        "destination": phone,
        "message": json.dumps({"type": "image", "originalUrl": img_url, "previewUrl": img_url, "caption": caption}),
        "src.name": WHATSAPP_APP_ID
    }
    requests.post(url, headers=headers, data=data)


# ===== LOGICA PRINCIPALĂ =====
def process_leads():
    leads = requests.get(LEADS_URL).json()

    for lead in leads:
        name = lead.get("nume", "").strip()
        phone = lead.get("telefon", "").strip()
        if not phone.startswith("4"):  # Adaugă prefix internațional RO dacă lipsește
            phone = "4" + phone

        # Mesaj inițial
        send_whatsapp_text(phone, f"Salut {name}! 📏 Spune-mi lungimea gardului în metri.")

        # Pentru test, punem valori fixe la dimensiuni
        payload = {
            "secret": SECRET,
            "lungime": 10,
            "inaltime": 1.5,
            "panouri": 1
        }
        resp = requests.post(PRICES_URL, json=payload).json()

        if resp.get("ok"):
            prices = resp["prices"]
            modele = [
                ("MX25 0.5mm", prices["OUT_MX25_05"]),
                ("MX25 0.6mm", prices["OUT_MX25_06"]),
                ("MX25 DUO 0.5mm", prices["OUT_MX25_DUO_05"]),
                ("MX25 DUO 0.6mm", prices["OUT_MX25_DUO_06"])
            ]

            for nume, pret in modele:
                img = IMAGE_URLS.get(nume)
                send_whatsapp_image(phone, img, f"{nume}: {pret} lei")

            send_whatsapp_text(
                phone,
                f"📱 Uite și cum ar arăta gardul în curtea ta!\n\n"
                f"✅ Ține telefonul orientat spre locul unde vrei gardul.\n"
                f"✅ Mergi încet pe linia gardului ca să vezi efectul complet.\n\n"
                f"🔗 {AR_LINK}"
            )


@app.route("/run", methods=["GET"])
def run_script():
    process_leads()
    return "Done", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    print(request.json)
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
