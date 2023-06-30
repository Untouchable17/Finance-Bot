from decimal import Decimal

from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import (
	InlineKeyboardButton, 
	InlineKeyboardMarkup
)

import utils
from config import *
from database import db_executor


@dp.callback_query_handler(lambda callback_query: True, state=Form.waiting_for_clear_category)
async def process_clear_category_callback(callback_query: types.CallbackQuery, state: FSMContext):
	
	data = await state.get_data()
	category_name = data.get("category")
	
	if callback_query.data == "clear_category_cancel":
		await callback_query.message.answer("<b>⛔️ Транзакция отменена</b>")
		await bot.answer_callback_query(callback_query.id)
		await bot.edit_message_reply_markup(
			chat_id=callback_query.message.chat.id, 
			message_id=callback_query.message.message_id, 
			reply_markup=None
		)
		await state.finish()
	
	elif callback_query.data.startswith("clear_category:"):
		category_name = callback_query.data.split(":")[1]
		db_executor.delete_records_for_category(category_name)
		await callback_query.message.answer(
			f"✅ Записи из категории <b>{category_name}</b> успешно удалены"
		)
		await bot.answer_callback_query(callback_query.id)
		await bot.edit_message_reply_markup(
			chat_id=callback_query.from_user.id, 
			message_id=callback_query.message.message_id, 
			reply_markup=None
		)


def handle_inline_button(update: types.Update, context: types.CallbackQuery):
	
	query = update.callback_query
	data = query.data.split('::')
	button_type = data[0]
	category_name = data[1]
	
	current_page = int(data[2])
	total_pages = int(data[3])

	if button_type == 'prev':
		if current_page > 1:
			current_page -= 1
			send_products(update, context, category_name, current_page, total_pages)

	elif button_type == 'next':
		if current_page < total_pages:
			current_page += 1
			send_products(update, context, category_name, current_page, total_pages)


@dp.callback_query_handler(lambda c: c.data.startswith('next'))
async def process_callback_show_next_records(callback_query: types.CallbackQuery):
	_, category_name, current_page, total_pages = callback_query.data.split('::')
	current_page = int(current_page)
	total_pages = int(total_pages)

	records = db_executor.get_records_by_category_from_db(category_name)[(current_page + 1) * RECORDS_PER_PAGE:(current_page + 2) * RECORDS_PER_PAGE]
	records_text = utils.format_records(records[:RECORDS_PER_PAGE])
	keyboard = InlineKeyboardMarkup(row_width=2)
	previous_btn = InlineKeyboardButton(
		'⏪ Предыдущая', 
		callback_data=f'prev::{category_name}::{current_page + 1}::{total_pages}'
	)
	next_btn = InlineKeyboardButton(
		'⏩ Следующая', 
		callback_data=f'next::{category_name}::{current_page + 1}::{total_pages}'
	)
	hide_btn = InlineKeyboardButton('Скрыть', callback_data=f"hide_keyboard")
	keyboard.add(previous_btn, next_btn, hide_btn)

	await bot.edit_message_text(
		chat_id=callback_query.message.chat.id, 
		message_id=callback_query.message.message_id, 
		text=records_text, 
		reply_markup=keyboard
	)


@dp.callback_query_handler(lambda c: c.data.startswith('prev'))
async def process_callback_show_previous_records(callback_query: types.CallbackQuery):
    _, category_name, current_page, total_pages = callback_query.data.split('::')
    current_page = int(current_page)
    total_pages = int(total_pages)

    records = db_executor.get_records_by_category_from_db(category_name)[
		current_page * RECORDS_PER_PAGE:(current_page + 1) * RECORDS_PER_PAGE
	]
    records_text = utils.format_records(records[:RECORDS_PER_PAGE])

    keyboard = InlineKeyboardMarkup(row_width=2)
    previous_btn = InlineKeyboardButton(
		'⏪ Предыдущая', 
		callback_data=f'prev::{category_name}::{current_page - 1}::{total_pages}'
	)
    next_btn = InlineKeyboardButton(
		'⏩ Следующая', 
		callback_data=f'next::{category_name}::{current_page - 1}::{total_pages}'
	)
    hide_btn = InlineKeyboardButton('Скрыть', callback_data='hide_keyboard')
    keyboard.add(previous_btn, next_btn, hide_btn)

    await bot.edit_message_text(
		chat_id=callback_query.message.chat.id, 
		message_id=callback_query.message.message_id, 
		text=records_text, 
		reply_markup=keyboard
	)


@dp.callback_query_handler(lambda c: True)
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):

	if callback_query.data == "cancel":

		last_record = db_executor.get_last_record_from_db()
		formatted_dt = last_record[4].strftime("%Y-%m-%d %H:%M:%S").split(" ")

		if last_record:
			db_executor.delete_last_record_from_db()
			text = f"✅ Внесено <b>{'{0:,.0f}'.format(last_record[1]).replace(',', '.')} ₽</b>\n💬 {last_record[2]}\n🗓 {formatted_dt[0]} {formatted_dt[1]} \n\n<b>❌ Транзакция отменена</b>"
			await bot.edit_message_text(
				text=text, 
				chat_id=callback_query.message.chat.id, 
				message_id=callback_query.message.message_id
			)
			await callback_query.answer("⛔️ Транзакция была отменена", show_alert=True)
		else:	
			await callback_query.answer("📛 Произошла ошибка при отмене транзакции", show_alert=True)

	elif callback_query.data == "hide_keyboard":
		await callback_query.message.edit_reply_markup(reply_markup=None)
