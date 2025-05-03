import io
import pdfplumber
from openpyxl import Workbook
from openpyxl.styles import Alignment

def pdf_to_excel_bytes(pdf_bytes: bytes) -> bytes:
    """
    Конвертирует байты PDF в байты Excel-файла.
    """
    # Жёсткие настройки для чётких таблиц
    table_settings = {
        "vertical_strategy":   "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 3,
    }

    all_data = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            tbl = page.extract_table(table_settings=table_settings)
            if tbl:
                all_data.extend(tbl)

    # Первая строка — заголовки
    headers, *rows = all_data if all_data else ([], [])
    wb = Workbook()
    ws = wb.active

    if headers:
        ws.append(headers)
    for row in rows:
        ws.append(row)

    # Настройка: закрепление шапки, фильтры, автоширина, выравнивание
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        max_len = max(len(str(cell.value)) for cell in col if cell.value)
        col_letter = col[0].column_letter
        ws.column_dimensions[col_letter].width = max_len + 2
        for cell in col:
            cell.alignment = Alignment(
                horizontal='center',
                vertical='center',
                wrap_text=True
            )

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()