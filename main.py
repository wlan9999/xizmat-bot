import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from math import radians, cos, sin, asin, sqrt

# BOT TOKEN
BOT_TOKEN = "8474774466:AAHW0lN0yl022NvXeamgEV4TLrAu4fbyYkc"
bot = telebot.TeleBot(BOT_TOKEN)

# GOOGLE SHEETS SETUP
SHEET_URL = "https://docs.google.com/spreadsheets/d/14SlXWI4-aCEAZcDpde5yYzYsFbGJ0Ccaxd8DlEkbcwM/edit#gid=0"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load service account credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# Haversine formula to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Salom! Lokatsiyangizni yuboring, sizga eng yaqin xizmat ko‘rsatuvchilarni topaman.")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_lat = message.location.latitude
    user_lon = message.location.longitude

    rows = sheet.get_all_records()
    nearby = []
    for row in rows:
        try:
            lat = float(row['lat'])
            lon = float(row['lon'])
            distance = haversine(user_lat, user_lon, lat, lon)
            if distance <= 10:
                row['distance'] = round(distance, 2)
                nearby.append(row)
        except:
            continue

    if nearby:
        nearby.sort(key=lambda x: x['distance'])
        for item in nearby[:5]:
            text = (
    f"👤 {item['name']}\n"
    f"🛠 {item['service']}\n"
    f"📍 {item['address']}\n"
    f"📞 {item['phone']}\n"
    f"📏 Masofa: {item['distance']} km"
)
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Afsuski, 10 km radiusda xizmat topilmadi.")

bot.polling()
