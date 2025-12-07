import os

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = os.getenv("postgresql://postgres:PSPChMMvjKmvhimiLzEjIzzezwzDZIGt@postgres.railway.internal:5432/railway")
    SQLALCHEMY_TRACK_MODIFICATIONS = False