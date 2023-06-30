import re
import pandas

from aiogram import types, executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import (
	ReplyKeyboardMarkup, 
	ReplyKeyboardRemove, 
	InlineKeyboardButton, 
	InlineKeyboardMarkup
)

import utils
from config import *
from callbacks import *
from database import db_executor



def restricted_access(user_id):
	def has_permission(func):
		async def wrapper(message: types.Message):
			if message.from_user.id == user_id:
				return await func(message)
		return wrapper
	return has_permission


@dp.message_handler(commands=['start', 'help', 'commands'])
async def start_command_handler(message: types.Message):

	text = """
	
Для использования бота просто введите сообщение в формате 'price comment'. Первым
указываете цену и через пробел комментарий. Например

- <b>850 шаверма с колой</b>

<b>Полный список команд:
/stats - вывод статистики трат по категориям
/category [name] - вывод статистики трат по конкретной категории вместе с самими записями
/clear - очистка записей из выбранной категории
/export - экспорт данных в xlsx файл
/commands - вывод контактной информации
</b>

	""".strip("")
	await message.answer(text)


@dp.message_handler(commands=['stats'], commands_prefix='/')
@restricted_access(user_id=USER_ID)
async def stats_handler(message: types.Message):

	get_statistic = db_executor.get_statistics_from_db()
	await message.reply("Вывод статистики трат по всем категориям:")
	result = utils.format_statistic_records(get_statistic)
	await message.answer(result)


@dp.message_handler(commands=['clear'], commands_prefix='/')
@restricted_access(user_id=USER_ID)
async def delete_transactions_handler(message: types.Message):

    categories = db_executor.get_categories_from_db()

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[category[1] for category in categories])
    keyboard.add(HIDE_KEYBOARD_BTN)
    await message.reply("<b>⚠️ Выберите категорию, записи из которой вы хотите удалить:</b>", reply_markup=keyboard)

    await Form.waiting_for_clear_category.set()


@dp.message_handler(commands=['export'], commands_prefix='/')
@restricted_access(user_id=USER_ID)
async def export_handler(message: types.Message):

	data = db_executor.get_export_db_data()

	if not data:
		await message.answer("<b>⚠️ База пустая. Данных для экспорта нет</b>")
	else:
		await message.answer("<b>🪄 Начинаю экспортировать данные..</b>")
		
		df = pandas.DataFrame(
			data, columns=['Id', 'Amount', 'Category', 'Comment', 'Date']
		)

		with pandas.ExcelWriter('finance_data.xlsx') as writer:
			df.to_excel(writer, index=False)

		with open('finance_data.xlsx', 'rb') as file:
			await message.answer_document(file)


@dp.message_handler(lambda message: message.from_user.id == int(USER_ID), state=Form.waiting_for_clear_category)
async def process_clear_category(message: types.Message, state: FSMContext):
	category_name = message.text

	if category_name == HIDE_KEYBOARD_BTN.text:
		await bot.send_message(message.chat.id, "Клавиатура скрыта.", reply_markup=ReplyKeyboardRemove())
		await state.finish()
		return None
	else:
		keyboard = InlineKeyboardMarkup()
		yes_button = InlineKeyboardButton(text="✅ Да", callback_data=f"clear_category:{category_name}")
		no_button = InlineKeyboardButton(text="❌ Нет", callback_data="clear_category_cancel")
		keyboard.add(yes_button, no_button)
		await message.answer(f"<b>⚠️ Вы уверены, что хотите удалить все записи из категории: {category_name} ?</b>", reply_markup=keyboard)
		await state.update_data(category=category_name)


@dp.message_handler(commands=['category'], commands_prefix='/', state=None)
@restricted_access(user_id=USER_ID)
async def stats_category_handler(message: types.Message):
	
	category_name = ""
	try:	
		category_name = message.text.split()[1]
	except:
		await message.answer("⚠️ <b>Для команды /category необходимо передать имя категории после пробела</b>")
		return None
	
	records = db_executor.get_records_by_category_from_db(category_name)

	if not records:
		await message.answer(f"⚠️ <b>Записи в категории '{category_name}' отсутствуют или категории не существует</b>")
		return None

	if len(records) > RECORDS_PER_PAGE:
		current_page = 0
		total_pages = len(records) // RECORDS_PER_PAGE
		if len(records) % RECORDS_PER_PAGE:
			total_pages += 1

		keyboard = InlineKeyboardMarkup(row_width=2)
		previous_btn = InlineKeyboardButton(
			'⏪ Предыдущая', 
			callback_data=f'prev::{category_name}::{current_page}::{total_pages}'
		)
		next_btn = InlineKeyboardButton(
			'⏩ Следующая',
			callback_data=f'next::{category_name}::{current_page}::{total_pages}'
		)
		hide_btn = InlineKeyboardButton('Скрыть', callback_data="hide_keyboard")
		keyboard.add(previous_btn, next_btn, hide_btn)

		records_text = utils.format_records(records[:RECORDS_PER_PAGE])
		await message.reply(records_text, reply_markup=keyboard)

	else:
		records_text = utils.format_records(records)
		await message.reply(records_text)
        

@dp.message_handler(lambda message: message.from_user.id == int(USER_ID), ~Text(HIDE_KEYBOARD_BTN.text), state=None)
async def add_expense_handler(message: types.Message, state: FSMContext):
    
    text = message.text.strip()
    match = re.match(r'^(\d+(?:\.\d+)?)\s+(.+)$', text)
    if not match:
        await message.reply(
			"<b>⛔️ Неверный формат!</b> Используйте формат: <b>\"цена комментарий\"</b>. Используй команду /help для справки"
		)
        return None

    price = float(match.group(1))
    comment = match.group(2)

    async with state.proxy() as data:
        data['price'] = price
        data['comment'] = comment

    categories = db_executor.get_categories_from_db()

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[category[1] for category in categories])
    keyboard.add(HIDE_KEYBOARD_BTN)
    await message.reply("Выберите категорию:", reply_markup=keyboard)

    await Form.waiting_for_category.set()


@dp.message_handler(lambda message: message.from_user.id == int(USER_ID), state=Form.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):

	category_name = message.text
	async with state.proxy() as data:
		price = data['price']
		comment = data['comment']
		status = db_executor.save_finance_record(
			price=price, comment=comment, category_name=category_name
		)

	async with state.proxy() as data:
		data['category'] = category_name

	hide_keyboard = ReplyKeyboardRemove()
	inline_kb = InlineKeyboardMarkup()
	inline_kb.add(InlineKeyboardButton("❌ Отменить транзакцию", callback_data="cancel"))
	inline_kb.add(InlineKeyboardButton("Скрыть клавиатуру", callback_data="hide_keyboard"))

	if status is not None:
		await message.answer(
			"<b>⛔️ Транзакция добавления товара отменена</b>", reply_markup=hide_keyboard
		)
	else:
		formatted_date = utils.transform_datetime(message["date"])
		await message.reply(
			f"✅ Внесено <b>{float(price):,.2f} ₽</b>\n💬 {comment}\n🗓 {formatted_date[0]} {formatted_date[1]} \n\n🗃 Сохранено в категории <b>{category_name}</b>",
			reply_markup=inline_kb,
		)
		
	await state.finish()


@dp.message_handler(lambda message: message.from_user.id == int(USER_ID) and message.text == HIDE_KEYBOARD_BTN.text)
async def hide_keyboard_handler(message: types.Message, state: FSMContext):

	hide_keyboard = ReplyKeyboardRemove()
	await message.answer("Категории скрыты", reply_markup=hide_keyboard, )
	await state.finish()


if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)