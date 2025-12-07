from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from threading import Thread
from flask_migrate import Migrate

TOKEN = ""

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


# @app.route('/add_code', methods=['POST'])
# def add_code():
#     data = request.json
#     code = data.get("code")
#     if code:
#         active_codes[code] = True
#         print(f"[INFO] Добавлен код: {code}")
#         return "OK"
#     return "ERROR", 400

# @app.route('/check_code', methods=['GET'])
# def check_code():
#     code = request.args.get("code")
#     if code in used_codes:
#         telegram_id = used_codes.pop(code)
#         active_codes.pop(code, None)
#         return str(telegram_id)
#     return "NONE"

# @app.route('/remove_code', methods=['POST'])
# def remove_code():
#     data = request.json
#     code = data.get("code")
#     if code:
#         active_codes.pop(code, None)
#         used_codes.pop(code, None)
#         print(f"[INFO] Код {code} удалён")
#         return "OK"
#     return "ERROR", 400

if __name__ == "__main__":
    app.run(debug=True)
