from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import (
	KeyboardButton, 
	InlineKeyboardButton, 
)
from aiogram.dispatcher.filters.state import State, StatesGroup


USER_ID = os.environ.get("TELEGRAM_USER_ID")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


HIDE_KEYBOARD_BTN = KeyboardButton('Скрыть клавиатуру')
RECORDS_PER_PAGE = 5

CANCEL_BTN = InlineKeyboardButton('Отменить транзакцию', callback_data='cancel')
HIDE_INLINE_BTN = InlineKeyboardButton('Скрыть клавиатуру', callback_data='hide')


class Form(StatesGroup):
    waiting_for_input = State()
    waiting_for_category = State()
    waiting_for_clear_category = State()