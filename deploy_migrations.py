import os
import shutil
import subprocess
import sys

def run_command(cmd, check=True):
    """Запускает команду и возвращает результат"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        if check:
            print(f"❌ Команда завершилась с ошибкой")
            sys.exit(1)
        return False
    print(result.stdout)
    return True

def main():
    print("=== Настройка миграций для Railway ===")
    
    # 1. Удаляем старые миграции
    if os.path.exists("migrations"):
        print("Удаляем старые миграции...")
        shutil.rmtree("migrations")
    
    # 2. Инициализируем миграции
    print("\nИнициализируем Alembic...")
    run_command("flask db init")
    
    # 3. Проверяем, что созданы все нужные директории
    required_dirs = ["migrations", "migrations/versions"]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"Создаём директорию: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # 4. Создаём миграции
    print("\nСоздаём миграции...")
    run_command('flask db migrate -m "Initial migration"')
    
    # 5. Применяем миграции
    print("\nПрименяем миграции к базе данных...")
    run_command("flask db upgrade")
    
    print("\n✅ Все миграции успешно выполнены!")

if __name__ == "__main__":
    main()