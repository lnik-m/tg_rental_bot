from dispatcher import dp
from faunaDB import BotDB
from aiogram import executor
import handlers

BotDB = BotDB()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)