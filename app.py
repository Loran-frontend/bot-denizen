# app.py
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    uuid = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    id_telegram = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Для хранения кодов можно использовать базу данных
# или оставить в памяти если это временно
from datetime import datetime

class AuthCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    telegram_id = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)

@app.route('/')
def home():
    return """
    <h1>Minecraft-Telegram Auth Service</h1>
    <p>API работает ✅</p>
    """

@app.route('/add_code', methods=['POST'])
def add_code():
    data = request.json
    code = data.get("code")
    
    if not code:
        return {"error": "Code is required"}, 400
    
    # Проверяем, существует ли уже код
    existing = AuthCode.query.filter_by(code=code).first()
    if existing:
        existing.is_active = True
        existing.telegram_id = None
        existing.used_at = None
    else:
        new_code = AuthCode(code=code, is_active=True)
        db.session.add(new_code)
    
    db.session.commit()
    
    print(f"[INFO] Добавлен код: {code}")
    return {"status": "OK", "code": code}

@app.route('/check_code', methods=['GET'])
def check_code():
    code = request.args.get("code")
    uuid = request.args.get("uuid")
    name = request.args.get("name")
    
    if not all([code, uuid, name]):
        return {"error": "Missing parameters"}, 400
    
    auth_code = AuthCode.query.filter_by(code=code, is_active=True).first()
    
    if auth_code and auth_code.telegram_id:
        # Код использован
        telegram_id = auth_code.telegram_id
        auth_code.is_active = False
        auth_code.used_at = datetime.utcnow()
        
        # Создаем пользователя
        new_user = User(username=name, uuid=uuid, id_telegram=telegram_id)
        db.session.add(new_user)
        db.session.commit()
        
        return {"status": "used", "telegram_id": telegram_id}
    
    return {"status": "not_found"}

@app.route('/remove_code', methods=['POST'])
def remove_code():
    data = request.json
    code = data.get("code")
    
    if not code:
        return {"error": "Code is required"}, 400
    
    auth_code = AuthCode.query.filter_by(code=code).first()
    if auth_code:
        db.session.delete(auth_code)
        db.session.commit()
    
    print(f"[INFO] Код {code} удалён")
    return {"status": "OK"}