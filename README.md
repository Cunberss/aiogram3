Telegram Bot on Aiogram3
- PostgreSQL db
- Sqlalchemy ORM
- Asyncpg engine


P.S:
- Edit 12 in docker-compose.yml to: 
  command: ["/bin/bash", "-c", "sleep 10 && alembic upgrade head && cd src && python3 main.py"]
if except: ConnectionRefusedError
