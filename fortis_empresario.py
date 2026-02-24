import sqlite3
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

import os
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 123456789  # TU ID

# Estados
NOMBRE, TALLA, PAGO = range(3)

# --- BASE DE DATOS ---
conn = sqlite3.connect("fortis.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    talla TEXT,
    pago TEXT,
    fecha TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    talla TEXT PRIMARY KEY,
    cantidad INTEGER
)
""")

# Stock inicial (solo si no existe)
for talla in ["S", "M", "L", "XL"]:
    cursor.execute("INSERT OR IGNORE INTO stock (talla, cantidad) VALUES (?, ?)", (talla, 10))

conn.commit()

# --- FUNCIONES ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Comprar"], ["Ver stock"]]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔥 FORTIS NOBILIS 🔥\nMarca de disciplina.\n\nSelecciona una opción:",
        reply_markup=reply,
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Comprar":
        await update.message.reply_text("Ingresa tu nombre completo:")
        return NOMBRE

    if text == "Ver stock":
        cursor.execute("SELECT * FROM stock")
        datos = cursor.fetchall()
        mensaje = "📦 STOCK DISPONIBLE:\n\n"
        for talla, cantidad in datos:
            mensaje += f"{talla}: {cantidad}\n"
        await update.message.reply_text(mensaje)

async def nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nombre"] = update.message.text
    keyboard = [["S", "M"], ["L", "XL"]]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Selecciona talla:", reply_markup=reply)
    return TALLA

async def talla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    talla = update.message.text.upper()

    cursor.execute("SELECT cantidad FROM stock WHERE talla=?", (talla,))
    resultado = cursor.fetchone()

    if not resultado or resultado[0] <= 0:
        await update.message.reply_text("❌ No hay stock disponible en esa talla.")
        return ConversationHandler.END

    context.user_data["talla"] = talla
    keyboard = [["Yappy"], ["Transferencia"]]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Selecciona método de pago:", reply_markup=reply)
    return PAGO

async def pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pago = update.message.text
    nombre = context.user_data["nombre"]
    talla = context.user_data["talla"]

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO ventas (nombre, talla, pago, fecha) VALUES (?, ?, ?, ?)",
                   (nombre, talla, pago, fecha))

    cursor.execute("UPDATE stock SET cantidad = cantidad - 1 WHERE talla=?", (talla,))
    conn.commit()

    await update.message.reply_text(
        "✅ Pedido confirmado.\nEnvía comprobante al WhatsApp.\nFORTIS NOBILIS 💪"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔥 NUEVA VENTA 🔥\n\n{nombre}\nTalla: {talla}\nPago: {pago}"
    )

    return ConversationHandler.END

async def ganancias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM ventas")
        total = cursor.fetchone()[0]
        ganancias = total * 25
        await update.message.reply_text(
            f"📊 Ventas totales: {total}\n💰 Ganancias: ${ganancias}"
        )

# --- BOT ---
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Comprar$"), menu)],
    states={
        NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre)],
        TALLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, talla)],
        PAGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, pago)],
    },
    fallbacks=[],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ganancias", ganancias))
app.add_handler(conv)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))

print("🔥 SISTEMA EMPRESARIO FORTIS ACTIVO 🔥")
app.run_polling()


