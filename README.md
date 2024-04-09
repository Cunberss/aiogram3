Telegram Bot on Aiogram3
- PostgreSQL db
- Sqlalchemy ORM
- Asyncpg engine

Main functions:
- Watch catalog products (PER_PAGE - number of category and subcategory objects in the keyboard)
- Add product to cart
- Quantity selection
- Watch cart
- Delete product in cart
- Create Order
- Payment for the order (get token_kassa in BotFather)
- Watch paid orders
- Faq in demo-inline mode
- Сheck for joining a group or channel

For the manager:
- Notification of a new paid order
- special command: /orders - get a table of orders for the day

Folders:
- Folder alembic - alembic migration
- Folder src - main folder project
- Folder orders - for storing order tables Excel
- Folder logs - for storing logs (loguru)
- Folder images - images products (Products.photo_url in model)

P.S:
- Edit 12 in docker-compose.yml to: 
  command: ["/bin/bash", "-c", "sleep 10 && alembic upgrade head && cd src && python3 main.py"]
if except: ConnectionRefusedError
