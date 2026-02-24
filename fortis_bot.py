import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8538158905:AAFElYJkjVPvYnAk2OWrQn57S7H1ydWNxcU"


ADMIN_ID = 123456789  # PON AQUI TU ID PERSONAL DE TELEGRAM

ventas_totales = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 FORTIS NOBILIS 🔥\n\n"
        "T-shirt Oversize Premium\n"
        "Precio: $25\n\n"
        "Tallas disponibles: S M L XL\n\n"
        "Escribe /comprar para ordenar ahora 💪"
    )

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["estado"] = "esperando_datos"
    await update.message.reply_text(
        "Envía los siguientes datos en un solo mensaje:\n\n"
        "Nombre completo\n"
        "Talla\n"
        "Método de pago (Yappy o Transferencia)"
    )

async def recibir_datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ventas_totales

    if context.user_data.get("estado") == "esperando_datos":
        datos = update.message.text
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("ventas.txt", "a") as f:
            f.write(f"{fecha} | {datos}\n")

        ventas_totales += 1

        await update.message.reply_text(
            "🔥 Pedido recibido 🔥\n\n"
            "Realiza el pago y envía comprobante.\n"
            "Yappy: 6XXXXXXX\n"
            "Transferencia: Banco General\n\n"
            "Gracias por confiar en FORTIS NOBILIS 💪"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 NUEVA VENTA 🚨\n\n{datos}\n\nTotal ventas: {ventas_totales}"
        )

        context.user_data["estado"] = None

async def ventas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"Ventas totales hoy: {ventas_totales}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("comprar", comprar))
app.add_handler(CommandHandler("ventas", ventas))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_datos))

print("🔥 BOT FORTIS NOBILIS ACTIVO 🔥")
app.run_polling()
