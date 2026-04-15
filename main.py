import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
YETKILI_IDS_ENV = os.getenv("YETKILI_IDS")

if not TOKEN:
    raise ValueError("BOT_TOKEN bulunamadı!")

if not YETKILI_IDS_ENV:
    raise ValueError("YETKILI_IDS bulunamadı!")

YETKILI_IDLER = [int(x.strip()) for x in YETKILI_IDS_ENV.split(",")]

GRUPLAR_DOSYASI = "gruplar.txt"


async def her_seyi_yonet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = update.message.text if update.message.text else ""

    # 📌 /help komutu
    if text.lower() == "/help":
        await update.message.reply_text(
            "🤖 BOT YARDIM MENÜSÜ\n\n"
            "📌 /help - Komutları gösterir\n"
            "📌 /ayril - Botu gruptan çıkarır (yetkili)\n\n"
            "📢 Yetkililer özelden mesaj atarak tüm gruplara duyuru gönderebilir\n"
            "⚙️ Bot otomatik olarak grupları kaydeder"
        )
        return

    # 📥 GRUP KAYDETME
    if update.effective_chat.type in ["group", "supergroup"]:
        if not os.path.exists(GRUPLAR_DOSYASI):
            open(GRUPLAR_DOSYASI, "w").close()

        with open(GRUPLAR_DOSYASI, "r") as f:
            gruplar = f.read().splitlines()

        if str(chat_id) not in gruplar:
            with open(GRUPLAR_DOSYASI, "a") as f:
                f.write(str(chat_id) + "\n")

    # 📢 DUYURU SİSTEMİ
    if update.effective_chat.type == "private" and user_id in YETKILI_IDLER:
        if not os.path.exists(GRUPLAR_DOSYASI):
            await update.message.reply_text("Kayıtlı grup yok.")
            return

        with open(GRUPLAR_DOSYASI, "r") as f:
            gruplar = set(f.read().splitlines())

        basarili, hatali = 0, 0

        for gid in gruplar:
            try:
                await context.bot.send_message(
                    chat_id=int(gid),
                    text=f"📢 DUYURU\n\n{text}"
                )
                basarili += 1
            except:
                hatali += 1

        await update.message.reply_text(
            f"✅ Duyuru tamamlandı\nGönderilen: {basarili}\nHata: {hatali}"
        )
        return

    # 🚪 GRUPTAN AYRILMA
    if user_id in YETKILI_IDLER and text.lower() == "/ayril":
        if os.path.exists(GRUPLAR_DOSYASI):
            with open(GRUPLAR_DOSYASI, "r") as f:
                lines = f.readlines()

            with open(GRUPLAR_DOSYASI, "w") as f:
                for line in lines:
                    if line.strip() != str(chat_id):
                        f.write(line)

        await update.message.reply_text("Gruptan ayrılıyorum 👋")
        await context.bot.leave_chat(chat_id)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, her_seyi_yonet))

if __name__ == "__main__":
    print("Bot aktif...")
    app.run_polling()
