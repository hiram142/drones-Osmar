    return [values_by_name[column] for column in SCHEMAS["Gastos"]], expense_id


def add_rows(sheet_name: str, records: Sequence[Mapping[str, Any]]) -> list[str]:
    """Validate and append one or more rows; return their generated or given IDs.

    For ``Operaciones``, each mapping uses the sheet column names. A ``Vuelo``
    needs ``Cliente``, ``Concepto``, ``Hectareas`` and ``Costo_HA``; ``Debe`` is
    calculated and ``Haber`` is zero. An ``Abono`` needs ``Cliente``,
    ``Concepto`` and ``Haber``; ``Debe`` is zero. For ``Gastos``, pass
    ``Concepto`` and positive ``Importe``. ``Fecha`` defaults to today's date in
    Mexico City and IDs are generated when omitted.
    """
    if sheet_name not in SCHEMAS:
        raise ValueError(
            f"Hoja no válida: {sheet_name!r}. Usa una de: {', '.join(SCHEMAS)}."
        )
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise TypeError("records debe ser una lista o secuencia de diccionarios.")
    if not records:
        return []
    if any(not isinstance(record, Mapping) for record in records):
        raise TypeError("Cada fila debe ser un diccionario de columnas y valores.")

    normalize = _operation_row if sheet_name == "Operaciones" else _expense_row
    normalized = [normalize(record) for record in records]
    worksheet = _worksheet(sheet_name)
    sheet_values = _check_headers(worksheet, sheet_name, allow_empty=False)
    existing_ids = {row[0].strip() for row in sheet_values[1:] if row and row[0].strip()}
    new_ids = [record_id for _, record_id in normalized]
    duplicate_ids = existing_ids.intersection(new_ids)
    if len(new_ids) != len(set(new_ids)):
        raise ValueError("La solicitud contiene IDs duplicados.")
    if duplicate_ids:
        raise ValueError(
            "Ya existe una fila con este ID: " + ", ".join(sorted(duplicate_ids))
        )
    try:
        worksheet.append_rows(
            [row for row, _ in normalized],
            value_input_option="USER_ENTERED",
            insert_data_option="INSERT_ROWS",
        )
    except Exception as exc:
        raise GoogleSheetsError(
            f"No se pudieron agregar filas a {sheet_name!r}. Comprueba que la cuenta "
            "de servicio tenga permiso de edición."
        ) from exc
    return [record_id for _, record_id in normalized]


def add_row(sheet_name: str, record: Mapping[str, Any]) -> str:
    """Append a single validated row and return its ID."""
    return add_rows(sheet_name, [record])[0]


def add_operation(
    tipo: str,
    cliente: str,
    concepto: str,
    *,
    fecha: date | datetime | str | None = None,
    hectareas: Any | None = None,
    costo_ha: Any | None = None,
    importe: Any | None = None,
    operation_id: str | None = None,
) -> str:
    """Add a flight charge or customer payment using app-friendly arguments.

    A flight's amount is derived from hectares times cost per hectare. For an
    abono, ``importe`` is the amount received.
    """
    kind = _text(tipo, "Tipo").casefold()
    record: dict[str, Any] = {
        "Fecha": fecha,
        "Tipo": kind,
        "Cliente": cliente,
        "Concepto": concepto,
    }
    if operation_id is not None:
        record["ID_Operacion"] = operation_id
    if kind == "vuelo":
        record.update({"Hectareas": hectareas, "Costo_HA": costo_ha})
    elif kind == "abono":
        record["Haber"] = importe
    else:
        raise ValueError("Tipo debe ser 'Vuelo' o 'Abono'.")
    return add_row("Operaciones", record)


def add_expense(
    concepto: str,
    importe: Any,
    *,
    fecha: date | datetime | str | None = None,
    expense_id: str | None = None,
) -> str:
    """Add an operating expense and return its generated ID."""
    record = {"Fecha": fecha, "Concepto": concepto, "Importe": importe}
    if expense_id is not None:
        record["ID_Gasto"] = expense_id
    return add_row("Gastos", record)