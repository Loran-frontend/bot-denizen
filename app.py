from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask_migrate import Migrate

TOKEN = "8394612560:AAEA_-8I-TMpW7LxCEmGHBu8uWa6FMoHcJk"

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    uuid = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    id_telegram = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f''

active_codes = {}
used_codes = {}

@app.route('/')
def index():
    return {
        "status": "running",
        "service": "Minecraft-Telegram Auth",
        "endpoints": {
            "check_code": "/check_code?code=XXX&uuid=XXX&name=XXX",
            "add_code": "/add_code (POST)",
            "remove_code": "/remove_code (POST)"
        }
    }

@app.route('/health')
def health_check():
    try:
        # Проверяем подключение к БД
        db.session.execute('SELECT 1')
        return {"database": "connected", "status": "healthy"}
    except Exception as e:
        return {"database": "error", "status": "unhealthy", "error": str(e)}, 500

@app.route('/add_code', methods=['POST'])
def add_code():
    data = request.json
    code = data.get("code")
    if code:
        active_codes[code] = True
        print(f"[INFO] Добавлен код: {code}")
        return "OK"
    return "ERROR", 400

@app.route('/check_code', methods=['GET'])
def check_code():
    code = request.args.get("code")
    uuid = request.args.get("uuid")
    name = request.args.get("name")
    if code in used_codes:
        telegram_id = used_codes.pop(code)
        active_codes.pop(code, None)
        new_user = User(username=name, uuid=uuid, id_telegram=telegram_id)
        db.session.add(new_user)
        db.session.commit()
        return str(telegram_id)
    return "NONE"

@app.route('/remove_code', methods=['POST'])
def remove_code():
    data = request.json
    code = data.get("code")
    if code:
        active_codes.pop(code, None)
        used_codes.pop(code, None)
        print(f"[INFO] Код {code} удалён")
        return "OK"
    return "ERROR", 400

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    telegram_id = update.message.from_user.id

    if text in active_codes:
        used_codes[text] = telegram_id
        await update.message.reply_text("Ваш профиль майнкрафт успешно привязан")
        print(f"[INFO] Код {text} использован пользователем {telegram_id}")
    else:
        await update.message.reply_text("Код не найден или уже использован")

if __name__ == "__main__":
    appTG = ApplicationBuilder().token(TOKEN).build()
    appTG.add_handler(MessageHandler(filters.TEXT, handle_update))
    
    import threading
    bot_thread = threading.Thread(target=appTG.run_polling)
    bot_thread.start()
    
    print("Telegram бот запущен в отдельном потоке")
    app.run(debug=False, host='0.0.0.0', port=5000)


# gunicorn -w 4 -b :5000 app:app