import openpyxl
from datetime import datetime
import os

def catat_permainan(durasi, langkah, status):
    nama_file = "data_solitaire.xlsx"

    if not os.path.exists(nama_file):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(["Tanggal", "Durasi (detik)", "Langkah", "Status"])
    else:
        wb = openpyxl.load_workbook(nama_file)
        sheet = wb.active

    sheet.append([datetime.now().strftime("%Y-%m-%d %H:%M"), durasi, langkah, status])
    wb.save(nama_file)