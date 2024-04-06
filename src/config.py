from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
GROUP_NAME = os.getenv('GROUP_NAME')
PER_PAGE = 3
