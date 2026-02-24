from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8538158905:AAGLPYGcmqIEANB4QCpudHb0BWrs4Pxtqpo

"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🔥 FORTIS NOBILIS 🔥
T-shirt Oversize $25

Tallas: S M L XL
Pago: Yappy / Transferencia

Escribe:
Comprar
""")

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envía tu talla y nombre completo.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("comprar", comprar))

app.run_polling()

