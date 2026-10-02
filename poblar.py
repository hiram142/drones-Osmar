import gsheets

print("Inyectando el historial del cliente Marco...")
# La deuda original (DEBE de 17,150)
gsheets.add_operation("Vuelo", "Marco", "Aplicación de herbicida", "2026-07-07", hectareas=49, costo_ha=350)

# Los pagos parciales (HABER)
gsheets.add_operation("Abono", "Marco", "Abono parcial por aplicación", "2026-07-15", importe=7000)
gsheets.add_operation("Abono", "Marco", "Abono parcial por aplicación", "2026-07-16", importe=4900)
gsheets.add_operation("Abono", "Marco", "Abono parcial por aplicación", "2026-07-17", importe=3500)

print("Inyectando otros clientes y gastos del mes...")
# Otros clientes del resumen
gsheets.add_operation("Vuelo", "Tirso", "Trabajos Tirso", "2026-07-02", importe=5000)
gsheets.add_operation("Vuelo", "El Guayal", "Trabajos El Guayal", "2026-07-03", importe=8500)

# Gastos extraídos de la foto
gsheets.add_expense("GASOLINA CAMIONETA RANGER", 1500, "2026-07-01")
gsheets.add_expense("Cable", 300, "2026-07-02")
gsheets.add_expense("Comida", 450, "2026-07-03")
gsheets.add_expense("Mantenimiento camioneta", 2500, "2026-07-04")

print("¡Listo! Datos de prueba inyectados.")