from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import re
import openpyxl
import requests

BOT_TOKEN = "BOT_TOKEN"
CHAT_ID = "CHAT_ID"

DB_FILE = "database.db"
app = FastAPI()

# бд
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            age INTEGER
        )
    """)
    conn.commit()
    conn.close()
init_db()

def validate_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]+", name))

def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\+7\d{10}", phone))

def validate_age(age: str) -> bool:
    if not age.isdigit():
        return False
    a = int(age)
    return 5 <= a <= 99

# регистрация
@app.post("/register")
async def register(name: str = Form(...), phone: str = Form(...), age: str = Form(...)):
    if not validate_name(name):
        return {"success": False, "error": "Имя должно содержать только буквы"}
    if not validate_phone(phone):
        return {"success": False, "error": "Телефон должен быть в формате +79998887766"}
    if not validate_age(age):
        return {"success": False, "error": "Возраст должен быть числом от 5 до 99"}

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO registrations (name, phone, age) VALUES (?, ?, ?)", (name, phone, int(age)))
    conn.commit()
    conn.close()
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": f"Новая заявка:\nИмя: {name}\nТелефон: {phone}\nВозраст: {age}"}
        )
    except:
        pass
    return {"success": True}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# excel
@app.get("/export")
def export_excel():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, age FROM registrations")
    rows = cur.fetchall()
    conn.close()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Имя", "Телефон", "Возраст"])
    for row in rows:
        ws.append(row)
    filepath = "registrations.xlsx"
    wb.save(filepath)
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="registrations.xlsx"
    )

@app.post("/tg_webhook")
async def tg_webhook(update: dict):
    if "message" not in update:
        return {"ok": True}
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    if text.strip() == "/export":
        try:
            export_excel()
            with open("registrations.xlsx", "rb") as f:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                    data={"chat_id": chat_id},
                    files={"document": f}
                )
        except Exception as e:
            requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                params={"chat_id": chat_id, "text": f"Ошибка: {e}"}
            )
    return {"ok": True}
