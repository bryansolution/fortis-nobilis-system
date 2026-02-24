import sqlite3
from openpyxl import Workbook

conn = sqlite3.connect("fortis.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM ventas")
ventas = cursor.fetchall()

wb = Workbook()
ws = wb.active
ws.append(["ID", "Nombre", "Talla", "Pago", "Fecha"])

for venta in ventas:
    ws.append(venta)

wb.save("ventas_fortis.xlsx")

print("✅ Exportado a ventas_fortis.xlsx")

