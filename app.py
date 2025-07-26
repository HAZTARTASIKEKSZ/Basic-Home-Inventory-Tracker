import os
import sys
import tkinter as tk
from tkinter import messagebox, Listbox, END
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Google Sheets connection constants
SHEET1 = "Sheet1" # Put the name of your sheet here
SHEET2 = "Sheet2" # You can extend this with more sheets if needed
SPREADSHEET_ID = "your_spreadsheet_id_here"  # Put your Google Sheets spreadsheet ID here
aktualis_sheet = SHEET1


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


if getattr(sys, 'frozen', False):
    # PyInstaller - executable, key file has to be in the EXE folder
    app_path = os.path.dirname(sys.executable)
else:
    # Run from Python during development
    app_path = os.path.dirname(os.path.abspath(__file__))


# Put your Google Service Account JSON key filename here, placed alongside the executable or script
keyfile_path = os.path.join(app_path, "your_service_account_key.json")  

creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
gc = gspread.authorize(creds)


# Local data structure (header is the first element)
local_data = {
    SHEET1: [],
    SHEET2: []
}


# --- Helper functions for data processing ---


def parse_input_text_v2(text):
    seged = text.strip().split()
    if len(seged) < 3:
        return None, None, None
    egyseg = seged[-1].lower()  # The last element is the unit
    mennyseg_str = seged[-2].replace(",", ".")  # Second to last is the quantity
    nev = " ".join(seged[:-2]).lower()  # The rest is the name
    if nev == "":
        return None, None, None  # error for empty name
    return nev, mennyseg_str, egyseg


def convert_to_float(mennyseg_str):
    try:
        mennyseg = float(mennyseg_str)
        return mennyseg if mennyseg > 0 else None
    except ValueError:
        return None


def format_quantity(mennyseg):
    return str(int(mennyseg)) if mennyseg.is_integer() else str(mennyseg)


# --- Status / message labels ---


def set_status_message(msg, color="green"):
    status_label.config(text=msg, fg=color)


def set_message(msg, color="blue", timeout=3000):
    message_label.config(text=msg, fg=color)
    if timeout:
        message_label.after(timeout, lambda: message_label.config(text=""))


# --- GUI main functions ---


def update_listbox(sheet_name):
    max_nev = 25
    max_menny = 12
    max_egyseg = 8


    listbox.delete(0, END)
    for row in local_data[sheet_name]:
        nev = row[0] if len(row) > 0 else ""
        menny = row[1] if len(row) > 1 else ""
        egyseg = row[2] if len(row) > 2 else ""
        # Fixed width columns padded with spaces (left aligned)
        sor_string = f"{nev.ljust(max_nev)}{menny.ljust(max_menny)}{egyseg.ljust(max_egyseg)}"
        listbox.insert(END, sor_string)


def update_listbox_from_data(data):
    """Refresh listbox directly from data list"""
    max_nev = 25
    max_menny = 12
    max_egyseg = 8


    listbox.delete(0, END)
    for row in data:
        nev = row[0] if len(row) > 0 else ""
        menny = row[1] if len(row) > 1 else ""
        egyseg = row[2] if len(row) > 2 else ""
        sor_string = f"{nev.ljust(max_nev)}{menny.ljust(max_menny)}{egyseg.ljust(max_egyseg)}"
        listbox.insert(END, sor_string)


def show_data(sheet_name):
    global aktualis_sheet
    aktualis_sheet = sheet_name
    try:
        worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        data = worksheet.get_all_values()
        local_data[sheet_name] = data
        update_listbox(sheet_name)
        set_status_message("Minden mentve.", "green")
        message_label.config(text="")  # clear feedback message
    except Exception as e:
        messagebox.showerror("Hiba", str(e))


def hozzaad_elem():
    beirt_szoveg = entry_hozzaad.get().strip()
    nev, mennyseg_str, egyseg = parse_input_text_v2(beirt_szoveg)
    if not nev:
        set_message("Kérlek, add meg a termék nevét, mennyiségét és egységét (pl. 'répa 3 kg').", color="red")
        return
    mennyseg = convert_to_float(mennyseg_str)
    if mennyseg is None:
        set_message(f"A mennyiség nem érvényes (pl. '3', '1.5'): {mennyseg_str}", color="red")
        return
    formatted_qty = format_quantity(mennyseg)


    sheet_data = local_data.get(aktualis_sheet, [])
    # if same name+unit exists --> increase, else new row
    for idx, sor in enumerate(sheet_data[1:], start=1):
        if len(sor) >= 3 and sor[0].lower() == nev and sor[2].lower() == egyseg:
            try:
                aktual_menny = float(sor[1].replace(",", "."))
            except ValueError:
                aktual_menny = 0
            uj_menny = aktual_menny + mennyseg
            uj_menny_str = format_quantity(uj_menny)
            sheet_data[idx][1] = uj_menny_str
            set_message(f"Sikeres hozzáadás: {nev} {egyseg} mennyisége megnőtt: {uj_menny_str}")
            break
    else:
        sheet_data.append([nev, formatted_qty, egyseg])
        set_message(f"Sikeres hozzáadás: {nev} ({egyseg}) {formatted_qty} hozzáadva.")
    local_data[aktualis_sheet] = sheet_data
    update_listbox(aktualis_sheet)
    set_status_message("Módosítások mentésre várnak!", "red")
    entry_hozzaad.delete(0, tk.END)


def levon_elem():
    beirt_szoveg = entry_levon_egy_mezo.get().strip()
    nev, mennyseg_str, egyseg = parse_input_text_v2(beirt_szoveg)
    if not nev:
        set_message("Írd be a termék nevét, mennyiségét és egységét (pl. 'borsó 1 kg')!", color="red")
        return
    menny_levon = convert_to_float(mennyseg_str)
    if menny_levon is None:
        set_message(f"A mennyiség értéke nem szám (pl. '2'): {mennyseg_str}", color="red")
        return
    sheet_data = local_data.get(aktualis_sheet, [])
    for idx, sor in enumerate(sheet_data[1:], start=1):
        if len(sor) >= 3 and sor[0].lower() == nev and sor[2].lower() == egyseg:
            try:
                aktual_menny = float(sor[1].replace(",", "."))
            except ValueError:
                set_message(f"Hibás mennyiség a táblában: {sor[1]}", color="red")
                return
            uj_menny = aktual_menny - menny_levon
            if uj_menny <= 0:
                del sheet_data[idx]
                set_message(f"Törölve: {nev} ({egyseg}) elfogyott.")
            else:
                uj_menny_str = format_quantity(uj_menny)
                sheet_data[idx][1] = uj_menny_str
                set_message(f"Levontam: {nev} ({egyseg}) új mennyisége: {uj_menny_str}")
            local_data[aktualis_sheet] = sheet_data
            update_listbox(aktualis_sheet)
            set_status_message("Módosítások mentésre várnak!", "red")
            entry_levon_egy_mezo.delete(0, tk.END)
            return
    set_message(f"Nincs találat: {nev} nevű, {egyseg} egységű terméket nem találtam.", color="red")


def szinkronizal():
    worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(aktualis_sheet)
    sheet_adatok = local_data[aktualis_sheet]
    if not sheet_adatok or len(sheet_adatok) < 2:
        worksheet.clear()
        if sheet_adatok:
            worksheet.append_row(sheet_adatok[0])
        set_status_message("Minden mentve.", "green")
        set_message("Változtatások mentve a Google Sheets-be!", color="green")
        return
    header = sheet_adatok[0]
    adatok = sheet_adatok[1:]
    adatok.sort(key=lambda x: x[0].lower())
    worksheet.clear()
    worksheet.append_row(header)
    if adatok:
        worksheet.append_rows(adatok)
    local_data[aktualis_sheet] = [header] + adatok
    update_listbox(aktualis_sheet)
    set_status_message("Minden mentve.", "green")
    set_message("Változtatások mentve és ABC-rendbe rakva!", color="green")


def keres_local_data(keyword):
    keyword = str(keyword).strip().lower()
    if not keyword:
        set_message("Nem adott meg keresési kulcsszót.", color="red")
        return


    data = local_data.get(aktualis_sheet, [])
    keresett_talalatok = []
    if data:
        keresett_talalatok.append(data[0])  # header


    for sor in data[1:]:
        if len(sor) > 0 and keyword in str(sor[0]).lower():
            keresett_talalatok.append(sor)


    if len(keresett_talalatok) > 1:
        update_listbox_from_data(keresett_talalatok)
        set_message(f"{len(keresett_talalatok)-1} találat a '{keyword}' kulcsszóra.", color="blue")
    else:
        set_message(f"Nincs találat a '{keyword}' kulcsszóra.", color="red")


# --- Build GUI ---


font_label = ("Arial", 16)
font_button = ("Arial", 16, "bold")
font_entry = ("Arial", 16)
font_listbox = ("Consolas", 16)


root = tk.Tk()
root.title("Kamra – Google Sheets kezelő")


# Search entry and button at top of GUI (above the listbox)
search_frame = tk.Frame(root)
search_frame.pack(padx=10, pady=(5, 0), fill="x")


entry_kereses = tk.Entry(search_frame, width=40, font=font_entry)
entry_kereses.pack(side=tk.LEFT, padx=(0, 5))


btn_keres = tk.Button(search_frame, text="Keresés", font=font_button,
                      command=lambda: keres_local_data(entry_kereses.get()))
btn_keres.pack(side=tk.LEFT)


# Main frame: listbox left, control panel right
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=(0,10))


# Listbox on left
listbox = Listbox(main_frame, width=60, height=15, font=font_listbox)
listbox.pack(side=tk.LEFT, padx=(0, 10))


# Control panel on right
control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.LEFT, fill=tk.Y)


# Add item entry and button
entry_hozzaad = tk.Entry(control_frame, width=40, font=font_entry)
entry_hozzaad.pack(pady=(0, 10))
btn_hozzaad = tk.Button(control_frame, text="Elem hozzáadása", font=font_button, command=hozzaad_elem)
btn_hozzaad.pack(fill=tk.X, pady=(0, 10))


# Quick feedback message label
message_label = tk.Label(control_frame, text="", fg="blue", font=font_label)
message_label.pack()


# Subtract item entry and button
entry_levon_egy_mezo = tk.Entry(control_frame, width=40, font=font_entry)
entry_levon_egy_mezo.pack(pady=(10, 5))
btn_levon = tk.Button(control_frame, text="Elem levonása", font=font_button, command=levon_elem)
btn_levon.pack(fill=tk.X)


# Status label for sync/update
status_label = tk.Label(control_frame, text="Minden mentve.", fg="green", font=font_label)
status_label.pack(pady=(20, 5))


# Sync button
btn_szinkron = tk.Button(control_frame, text="Szinkronizálás", font=font_button, command=szinkronizal)
btn_szinkron.pack(fill=tk.X, pady=(5, 0))


# Sheet switch buttons at window bottom
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
btn_sheet1 = tk.Button(button_frame, text="Élelmiszerek", font=font_button, command=lambda: show_data(SHEET1))
btn_sheet1.pack(side=tk.LEFT, padx=10)
btn_sheet2 = tk.Button(button_frame, text="Háztartás", font=font_button, command=lambda: show_data(SHEET2))
btn_sheet2.pack(side=tk.LEFT, padx=10)


# Load first sheet on startup
show_data(aktualis_sheet)


root.mainloop()
