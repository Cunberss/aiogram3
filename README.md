Edit 12 in docker-compose.yml to: 
  command: ["/bin/bash", "-c", "sleep 10 && alembic upgrade head && cd src && python3 main.py"]
if except: ConnectionRefusedError
