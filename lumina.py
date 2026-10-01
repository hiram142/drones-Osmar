import gsheets

def obtener_operaciones():
    return gsheets.read_df("Operaciones")

def obtener_gastos():
    return gsheets.read_df("Gastos")

def registrar_vuelo(fecha, cliente, concepto, hectareas, precio_ha, total):
    return gsheets.add_operation(
        tipo="Vuelo",
        cliente=cliente,
        concepto=concepto,
        fecha=fecha,
        hectareas=hectareas,
        costo_ha=precio_ha
    )

def registrar_abono(fecha, cliente, concepto, monto):
    return gsheets.add_operation(
        tipo="Abono",
        cliente=cliente,
        concepto=concepto,
        fecha=fecha,
        importe=monto
    )

def registrar_gasto(fecha, concepto, monto):
    return gsheets.add_expense(
        concepto=concepto,
        importe=monto,
        fecha=fecha
    )