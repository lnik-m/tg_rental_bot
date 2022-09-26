import logging

from datetime import datetime
import re

from aiogram import types
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from dispatcher import dp
from bot import BotDB
from config import admin_id

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

current_entry = {'room': '', 'date': '', 'time':''}

commands_user = """\nСписок команд:\n
/delete № удалить запись\n
/deleteAll удалить все записи
"""

commands = """\nСписок команд:\n
/room_list список комнат\n
/add_room имя_комнаты для добавления помещения\n
/delete_room № для удаления помещения\n
/room_entry № записи в комнату\n
/delete № удалить запись\n
/commands вывести этот список команд\n
** /deleteAll только для удаления собственных записей
"""

intro = "Этот бот предназначен для аренды рабочих мест в салоне ART_SALON_013 🥰🌿"

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Back to main menu button --- #
btnBack = InlineKeyboardButton('⬅ В главное меню', callback_data='btnBack')

# --- Main menu --- #
btnRent = InlineKeyboardButton("Арендовать рабочее место", callback_data='btnRent')
btnEntries = InlineKeyboardButton('Мои записи', callback_data='btnEntries')
main_menu_kb = InlineKeyboardMarkup(resize_keyboard=True).add(btnRent, btnEntries)

back_menu_kb = InlineKeyboardMarkup(resize_keyboard=True).add(btnBack)

# --- Rent menu --- #
btnList = BotDB.get_rooms_names()
btnListNew = []
for i in range(len(btnList)):
    btnListNew.append(InlineKeyboardButton(btnList[i], callback_data=f"btnListNew{i+1}"))
rent_menu_kb = InlineKeyboardMarkup(resize_keyboard=True).add(*btnListNew, btnBack)

# --- Confirm menu --- #
btnConfirm = InlineKeyboardButton("✅ Всё верно", callback_data='btnConfirm')
confirm_menu_kb = InlineKeyboardMarkup(resize_keyboard=True).add(btnConfirm, btnBack)

# --- Time menu --- #
btnTime1 = InlineKeyboardButton("10-11", callback_data='btnTime10-11')
btnTime2 = InlineKeyboardButton("11-12", callback_data='btnTime11-12')
btnTime3 = InlineKeyboardButton("12-13", callback_data='btnTime12-13')
btnTime4 = InlineKeyboardButton("13-14", callback_data='btnTime13-14')
btnTime5 = InlineKeyboardButton("14-15", callback_data='btnTime14-15')
btnTime6 = InlineKeyboardButton("15-16", callback_data='btnTime15-16')
btnTime7 = InlineKeyboardButton("16-17", callback_data='btnTime16-17')
btnTime8 = InlineKeyboardButton("17-18", callback_data='btnTime17-18')
btnTime9 = InlineKeyboardButton("18-19", callback_data='btnTime18-19')
btnTime10 = InlineKeyboardButton("19-20", callback_data='btnTime19-20')
btnTime11 = InlineKeyboardButton("20-21", callback_data='btnTime20-21')

time_menu_kb = InlineKeyboardMarkup(resize_keyboard=True).add(btnTime1, btnTime2, btnTime3, btnTime4, btnTime5,
                                                              btnTime6, btnTime7, btnTime8, btnTime9, btnTime10,
                                                              btnTime11)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        if int(message.from_user.id) in admin_id:
            BotDB.add_user(user_id=message.from_user.id, user_name=message.from_user.username, is_admin=True)
        else:
            BotDB.add_user(message.from_user.id, message.from_user.username)
    if int(message.from_user.id) in admin_id:
        await message.bot.send_message(message.from_user.id, f"Добро пожаловать, {message.from_user.first_name}!\n{intro}\n{commands}", reply_markup=main_menu_kb)
    else:
        await message.bot.send_message(message.from_user.id, f"Добро пожаловать, {message.from_user.first_name}!\n{intro}", reply_markup=main_menu_kb)


@dp.message_handler(user_id=admin_id, commands='commands')
async def commands_list(message: types.Message):
    await message.bot.send_message(message.from_user.id, f"{commands}", reply_markup=main_menu_kb)


@dp.message_handler(user_id=admin_id, commands='room_list')
async def get_room_list(message: types.Message):
    room_list = BotDB.get_rooms()
    result = []
    for el in room_list:
        room_id = el['room_id']
        room_name = el['name']
        result.append(str('\n' + '№' + str(room_id) + ' ' + room_name))
    result = ('').join(result)
    await message.bot.send_message(message.from_user.id, f"Список комнат: {result}", reply_markup=main_menu_kb)


@dp.message_handler(user_id=admin_id, commands='add_room')
async def add_room(message: types.Message):
    if message.text[10:] != '':
        BotDB.add_room(message.text[10:])
        await message.bot.send_message(message.from_user.id, f"Добавлена комната {message.text[10:]}", reply_markup=main_menu_kb)
    else:
        await message.bot.send_message(message.from_user.id, "В строке с командой введите имя комнаты", reply_markup=main_menu_kb)


@dp.message_handler(user_id=admin_id, commands='delete_room')
async def delete_room(message: types.Message):
    if message.text[12:] != '':
        room_name = BotDB.get_room_name(int(message.text[12:]))
        BotDB.delete_room(int(message.text[12:]))
        await message.bot.send_message(message.from_user.id, f"🗑 Удалена комната {room_name}", reply_markup=main_menu_kb)
    else:
        await message.bot.send_message(message.from_user.id, "В строке с командой введите номер комнаты", reply_markup=main_menu_kb)


@dp.message_handler(user_id=admin_id, commands='room_entry')
async def room_entry(message: types.Message):
    if message.text[12:] != '':
        room_id = int(message.text[12:])
        room_name = BotDB.get_room_name(room_id)

        room_entries = BotDB.get_room_entries(room_id)
        result = []
        for el in room_entries:
            user_id = el['user_id']
            entry_id = el['entry_id']
            date = el['date']
            result.append(f"\n №{entry_id} @{BotDB.get_user_name(user_id)} {date}")
        result = ('').join(result)

        await message.bot.send_message(message.from_user.id, f"Записи в комнате {room_name}:{result}", reply_markup=main_menu_kb)
    else:
        await message.bot.send_message(message.from_user.id, "В строке с командой введите номер комнаты", reply_markup=main_menu_kb)


@dp.message_handler(commands='delete')
async def delete_entry(message: types.Message):
    if int(message.from_user.id) in admin_id:
        if message.text[8:] != '':
            entry_id = int(message.text[8:])
            BotDB.delete_entry(entry_id)
            await message.bot.send_message(message.from_user.id, f"🗑 Запись №{entry_id} удалена",
                                           reply_markup=main_menu_kb)
        else:
            await message.bot.send_message(message.from_user.id, "В строке с командой введите номер записи",
                                           reply_markup=main_menu_kb)
    else:
        user_entries = BotDB.get_user_entries(message.from_user.id)
        entries_list = []
        for el in user_entries:
            entries_list.append(int(el['entry_id']))
        if message.text[8:] != '':
            entry_id = int(message.text[8:])
            if entries_list.count(entry_id)>0:
                BotDB.delete_entry(entry_id)
                await message.bot.send_message(message.from_user.id, f"🗑 Запись №{entry_id} удалена",
                                               reply_markup=main_menu_kb)
            else:
                await message.bot.send_message(message.from_user.id, f"Вы не администратор и не владелец записи №{entry_id}, она не может быть удалена",
                                               reply_markup=main_menu_kb)
        else:
            await message.bot.send_message(message.from_user.id, "В строке с командой введите номер записи",
                                           reply_markup=main_menu_kb)


@dp.message_handler(commands='deleteAll')
async def delete_all_entries(message: types.Message):
    entries = BotDB.get_user_entries(message.from_user.id)
    for el in entries:
        BotDB.delete_entry(int(el['entry_id']))
    await message.bot.send_message(message.from_user.id, f"🗑 Записи удалены", reply_markup=main_menu_kb)


@dp.callback_query_handler(lambda c: c.data == 'btnRent')
async def rent(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await callback_query.bot.send_message(callback_query.from_user.id, "Выберите нужное помещение", reply_markup=rent_menu_kb)


@dp.callback_query_handler(lambda c: c.data == 'btnEntries')
async def my_entries(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user_entries = BotDB.get_user_entries(callback_query.from_user.id)
    await callback_query.bot.send_message(callback_query.from_user.id, f"Ваши записи: {str_user_entries(user_entries)}\n\n{commands_user}", reply_markup=back_menu_kb)


@dp.callback_query_handler(lambda c: c.data.startswith('btnListNew'))
async def choose_room(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    current_entry['room'] = BotDB.get_room_name(int(callback_query.data[10:]))

    room_id = BotDB.get_room_id(current_entry['room'])
    room_entries = BotDB.get_room_entries(room_id)
    result = []
    for el in room_entries:
        user_id = el['user_id']
        entry_id = el['entry_id']
        date = el['date']
        time = el['time']
        result.append(f"\n №{entry_id} @{BotDB.get_user_name(user_id)} {date} {time}")
    result = ('').join(result)
    reply = f"Записи в комнате {current_entry['room']}:{result}\n\n📆 Выберите нужную дату"
    await callback_query.bot.send_message(callback_query.from_user.id, reply, reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(lambda c: c.data == 'btnBack')
async def back(callback_query: types.CallbackQuery):
    await callback_query.bot.send_message(callback_query.from_user.id, "Вы в главном меню", reply_markup=main_menu_kb)


@dp.callback_query_handler(lambda c: c.data == 'btnConfirm')
async def confirm(callback_query: types.CallbackQuery):
    BotDB.add_entry(callback_query.from_user.id, current_entry['room'], current_entry['date'], current_entry['time'])
    await callback_query.bot.send_message(callback_query.from_user.id, "Вы в главном меню", reply_markup=main_menu_kb)


@dp.message_handler()
async def main_dialog(message: types.Message):
   await message.bot.send_message(message.from_user.id, "Такой команды нет, вы в главном меню", reply_markup=main_menu_kb)


@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    datesList = BotDB.get_room_entries_dates(current_entry['room'])

    if selected:
        current_entry['date'] = date.strftime('%d/%m/%Y')
        if datesList.count(current_entry['date']) > 0:
            await callback_query.message.answer(
                f"Вы выбрали {current_entry['date']}, эта дата занята, выберите другую",
                reply_markup=await SimpleCalendar().start_calendar()
            )
        elif date > datetime.today():
            room_id = BotDB.get_room_id(current_entry['room'])
            room_entries = BotDB.get_room_entries(room_id)
            result = []
            for el in room_entries:
                user_id = el['user_id']
                entry_id = el['entry_id']
                date = el['date']
                time = el['time']
                result.append(f"\n №{entry_id} @{BotDB.get_user_name(user_id)} {date} {time}")
            result = ('').join(result)
            reply = f"Записи в комнате {current_entry['room']}:{result}\n\n🕑 Выберите нужное время"
            await callback_query.bot.send_message(callback_query.from_user.id, reply, reply_markup=time_menu_kb)
        else:
            await callback_query.message.answer(
                f"Вы выбрали {current_entry['date']}, эта дата прошла, выберите другую",
                reply_markup=await SimpleCalendar().start_calendar()
            )


@dp.callback_query_handler(lambda c: c.data.startswith('btnTime'))
async def choose_time(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    current_entry['time'] = callback_query.data[7:]
    reply = f"Вы выбрали {current_entry['room']} {current_entry['date']} {current_entry['time']}, всё верно?"
    await callback_query.bot.send_message(callback_query.from_user.id, reply, reply_markup=confirm_menu_kb)


def str_user_entries(user_entries):
    result = []
    for el in user_entries:
        name = el['room_name']
        date = el['date']
        time = el['time']
        result.append(str('\n' + '№' + str(el['entry_id']) + ' ' + name + ' ' + date + ' ' + time))
    return ('').join(result)

