import logging
import sqlite3
import requests
import pymorphy3
import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
import keyboard as kb
from geocode import get_ll_span

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

# создание бота и его состояний
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)


class AllStates(StatesGroup):
    waiting_for_support = State()

    gl_q1 = State()
    gl_q2 = State()
    gl_q3 = State()
    gl_q4 = State()
    gl_q5 = State()
    gl_answ = State()

    zh_q1 = State()
    zh_q2 = State()
    zh_q3 = State()
    zh_q4 = State()
    zh_q5 = State()
    zh_answ = State()

    zub_q1 = State()
    zub_q2 = State()
    zub_q3 = State()
    zub_q4 = State()
    zub_q5 = State()
    zub_answ = State()

    ru_q1 = State()
    ru_q2 = State()
    ru_q3 = State()
    ru_q4 = State()
    ru_q5 = State()
    ru_answ = State()

    uh_q1 = State()
    uh_q2 = State()
    uh_q3 = State()
    uh_q4 = State()
    uh_q5 = State()
    uh_answ = State()

    c1_st = State()
    admin_st = State()
    photo_st = State()
    vopr_st = State()


# функция, которая создает инлайн-клавиатуры с входным массивом кнопок
def create_inline_keyboard(array_of_buttons, size):
    in_keyboard = types.InlineKeyboardMarkup(row_width=size)
    mas = []
    for i in array_of_buttons:
        mas.append(types.InlineKeyboardButton(text=i[0], callback_data=i[1]))
    in_keyboard.add(*mas)
    return in_keyboard


# Явно указываем в декораторе, на какую команду реагируем.
# Так как код работает асинхронно, то обязательно пишем await.
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Привет {message.from_user.full_name}!\n{config.HI}", reply_markup=kb.menu)

    await bot.send_message(chat_id=message.from_user.id,
                           text=config.VOT,
                           reply_markup=kb.main_inline_menu)


# специальная команда только для администратора
@dp.message_handler(commands=['admin'])
async def send_welcome(message: types.Message):
    await AllStates.admin_st.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.ADMHI, reply_markup=kb.menu)
    await message.answer(config.ADMNUM)
    conn = sqlite3.connect(config.sql)
    curs = conn.cursor()
    res_support = curs.execute(f'''SELECT id, id_user, quest FROM support''').fetchall()

    for el in res_support:
        await message.answer(f'{el[0]} - {el[1]} - {el[2]}')

    conn.commit()


# функции админа
@dp.message_handler(state=AllStates.admin_st)
async def admin_support(message: types.Message, state: FSMContext):
    num_quest = int(message.text)

    conn = sqlite3.connect(config.sql)
    curs = conn.cursor()

    curs.execute('''DELETE FROM support WHERE id == ?''', (num_quest,))
    conn.commit()

    await message.answer(text=config.QUEDEL,
                         reply_markup=kb.main_inline_menu)
    await state.finish()


# пункт 5 задания
@dp.message_handler(content_types=['text'], text="☎ Обратиться в поддержку")
async def waiting_for_support(message: types.Message):
    await AllStates.waiting_for_support.set()
    await message.answer(config.ANSAS)


# функция обращения в тех поддержку
@dp.message_handler(state=AllStates.waiting_for_support)
async def process_support(message: types.Message, state: FSMContext):
    id_us = message.from_user.username
    mes = message.text
    conn = sqlite3.connect(config.sql)
    curs = conn.cursor()

    curs.execute(f'''INSERT INTO support (id_user, quest)
                    VALUES (?, ?)''', (id_us, mes)).fetchall()

    conn.commit()

    await message.answer(text="Спасибо, что напиcали нам. Мы ответим Вам в ближайшее время",
                         reply_markup=kb.main_inline_menu)
    await state.finish()


# задание 2
@dp.message_handler(text=['❤Симптомы'])
async def docs(message: types.Message, state: FSMContext):
    await message.answer(text="Что у Вас болит?",
                         reply_markup=kb.menu_simp)
    await state.finish()


@dp.message_handler(text=['Назад 🔙'])
async def back(message: types.Message):
    await message.answer(text=config.BACK, reply_markup=kb.menu)


# ГОЛОВА
@dp.message_handler(text=['🧠 Голова'])
async def g1_st(message: types.Message):
    await message.answer(text="Ответьте на несоклько вопросов")
    await AllStates.gl_q1.set()
    await message.answer(text="Как давно болит голова?<b>\nДавно/Недавно/Не знаю</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.gl_q1)
async def g1_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_1'] = message.text
    await AllStates.next()
    await message.answer(text="Может быть вы упали? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.gl_q2)
async def g2_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_2'] = message.text
    await AllStates.next()
    await message.answer(text="Мерили давление? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.gl_q3)
async def g3_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_3'] = message.text
    await AllStates.next()
    await message.answer(text="Вы уже приняли лекарство? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.gl_q4)
async def g4_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_4'] = message.text
    await AllStates.next()
    await message.answer(text="У вас сильно болит голова? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.gl_q5)
async def g5_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_5'] = message.text
    await AllStates.next()

    async with state.proxy() as data:
        # ответ на результаты исследования при выборе головы
        if data['1_1'] == "Давно" and data['1_2'] == "Да" and data['1_3'] == "Нет" \
                and data['1_4'] == "Да" and data['1_5'] == "Да":
            await message.answer(text="Видимо у вас мигрень, обратитесь к врачу, ссылка для записи ниже",
                                 reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Недавно" and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Видимо у вас просто болит голова, выпейте лекарство или запишитесь к врачу на обследдование",
                reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Давно" and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Видимо у вас просто болит голова, выпейте лекарство или запишитесь к врачу на обследдование",
                reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Не знаю" and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Видимо вы сильно упали, советуем записаться к врачу на диагностику головы",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Нет" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(text="Может у вас ничего не болит?", reply_markup=kb.inline_kb1)

        else:
            await message.answer(text="Советуем выпить лекарства и подождать,"
                                      " если не помогло - вернитесь назад и нажмите на кнопку 📋 Записаться к врачу")

    await state.finish()


# ЖИВОТ
@dp.message_handler(text=['❤ Живот'])
async def zh1_st(message: types.Message):
    await message.answer(text="Ответьте на несоклько вопросов")
    await AllStates.zh_q1.set()
    await message.answer(text="Как давно болит живот? <b>\nДавно/Недавно/Не знаю</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zh_q1)
async def zh1_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_1'] = message.text
    await AllStates.next()
    await message.answer(text="Может быть вы ушиблись? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zh_q2)
async def zh2_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_2'] = message.text
    await AllStates.next()
    await message.answer(text="У вас есть темпреатура? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zh_q3)
async def zh3_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_3'] = message.text
    await AllStates.next()
    await message.answer(text="Вы уже приняли лекарство? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zh_q4)
async def zh4_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_4'] = message.text
    await AllStates.next()
    await message.answer(text="У вас сильно болит живот? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zh_q5)
async def zh5_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_5'] = message.text
    await AllStates.next()

    async with state.proxy() as data:
        # ответ на результаты исследования при выборе головы
        if data['1_1'] == "Давно" and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Да" and data['1_5'] == "Да":
            await message.answer(
                text="Видимо у вас несварение, если это продолжиться то обратитесь к врачу, ссылка для записи ниже",
                reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Недавно" and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Скорее выпейте лекарство или запишитесь к врачу на обследование",
                reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Давно" and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Видимо у вас просто болит живот, выпейте лекарство или запишитесь к врачу на обследдование",
                reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Не знаю" and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Видимо вы просто ударились, советуем записаться к врачу на диагностику живота",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Нет" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(text="Может у вас ничего не болит?", reply_markup=kb.inline_kb1)

        else:
            await message.answer(text="Советуем выпить лекарства и подождать,"
                                      " если не помогло - вернитесь назад и нажмите на кнопку 📋 Записаться к врачу")

    await state.finish()


# ЗУБ
@dp.message_handler(text=['🦷 Зубы'])
async def z_st(message: types.Message):
    await message.answer(text="Ответьте на несоклько вопросов")
    await AllStates.zub_q1.set()
    await message.answer(text="Как давно у вас болят зубы? <b>\nДавно/Недавно/Не знаю</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zub_q1)
async def z1_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_1'] = message.text
    await AllStates.next()
    await message.answer(text="Могли ли произойти скол кусочка зуба? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zub_q2)
async def z2_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_2'] = message.text
    await AllStates.next()
    await message.answer(text="Чистите ли вы зубы 2 раза в день? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zub_q3)
async def z3_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_3'] = message.text
    await AllStates.next()
    await message.answer(text="Вы уже выпили лекарство? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zub_q4)
async def z4_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_4'] = message.text
    await AllStates.next()
    await message.answer(text="Ели ли вы кислое/фрукты недавно? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.zub_q5)
async def z5_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_5'] = message.text
    await AllStates.next()

    async with state.proxy() as data:
        # ответ на результаты исследования при выборе головы
        if data['1_1'] == "Недавно" and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Да" and data['1_5'] == "Да":
            await message.answer(text="Возможно зуб болит из-за принятой пищи, прополощите рот, если боль не утихнет"
                                      " то запишитесь к стоматологу по кнопке внизу", reply_markup=kb.inline_kb1)

        elif data['1_1'] == "Недавно" and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Возможно зуб болит из-за принятой пищи, прополощите рот и можете выпить слабое обезболивающие,"
                     " если боль не утихнет то запишитесь к стоматологу по кнопке внизу", reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Давно" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Да" and data['1_5'] == "Нет":
            await message.answer(
                text="У вас может быть повреждена эмаль зубов, обратитесь к стоматологу по кнопке снизу",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Не знаю" or data['1_1'] == 'Недавно') and data['1_2'] == "Да" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(
                text="Видимо вы скололи небольшой кусочек зуба, советуем записаться к стоматологу",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Нет" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(text="Может у вас ничего не болит?", reply_markup=kb.inline_kb1)

        else:
            await message.answer(text="Советуем выпить лекарства и подождать,"
                                      " если не помогло - вернитесь назад и нажмите на кнопку 📋 Записаться к врачу")

    await state.finish()


# РУКА ИЛИ НОГА
@dp.message_handler(text=['💪 Рука или нога'])
async def r1_st(message: types.Message):
    await message.answer(text="Ответьте на несоклько вопросов")
    await AllStates.ru_q1.set()
    await message.answer(text="Как давно у вас болит конечность? <b>\nДавно/Недавно/Не знаю</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.ru_q1)
async def r1_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_1'] = message.text
    await AllStates.next()
    await message.answer(text="Может вы ушиблись? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.ru_q2)
async def r2_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_2'] = message.text
    await AllStates.next()
    await message.answer(text="У вас есть синяк на конечности? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.ru_q3)
async def r3_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_3'] = message.text
    await AllStates.next()
    await message.answer(text="Вас мог кто-то укусить? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.ru_q4)
async def r4_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_4'] = message.text
    await AllStates.next()
    await message.answer(text="Сильно ли болит конечность? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.ru_q5)
async def r5_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_5'] = message.text
    await AllStates.next()

    async with state.proxy() as data:
        # ответ на результаты исследования при выборе головы
        if (data['1_1'] == "Недавно" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Да" and data['1_5'] == "Да":
            await message.answer(
                text="Возможно вас укусило какое-либо насекомое или животное, советуем обратиться к врачу",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Недавно" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(
                text="Возмона нехватка воды в организме, если это будет причинять дискомфорт, то обратитесь к врачу",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Давно" or data['1_1'] == "Не знаю") and data['1_2'] == "Да" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Да":
            await message.answer(
                text="Скорее всего вы сильно ударились, рекомендуем обратится к травматологу",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Не знаю" or data['1_1'] == 'Недавно') and data['1_2'] == "Да" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(
                text="Возможно вы не сильно ударились, через некоторое время пройдет")

        elif (data['1_1'] == "Нет" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(text="Может у вас ничего не болит?", reply_markup=kb.inline_kb1)

        else:
            await message.answer(text="Советуем выпить обезболивающее и подождать, если не помогло - вернитесь"
                                      " назад и нажмите на кнопку 📋 Записаться к врачу")

    await state.finish()


# УХО
@dp.message_handler(text=['👂 Ухо'])
async def u1_st(message: types.Message):
    await message.answer(text="Ответьте на несоклько вопросов")
    await AllStates.uh_q1.set()
    await message.answer(text="Как давно у вас болит ухо? <b>\nДавно/Недавно/Не знаю</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.uh_q1)
async def u1_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_1'] = message.text
    await AllStates.next()
    await message.answer(text="Оно звенит? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.uh_q2)
async def u2_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_2'] = message.text
    await AllStates.next()
    await message.answer(text="Вы стали хуже слышать? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.uh_q3)
async def u3_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_3'] = message.text
    await AllStates.next()
    await message.answer(text="Вы болеете? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.uh_q4)
async def u4_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_4'] = message.text
    await AllStates.next()
    await message.answer(text="Сильно ли болит ухо? <b>\nДа/Нет</b>", parse_mode='HTML')


@dp.message_handler(state=AllStates.uh_q5)
async def u5_q(message: types.Message, state: AllStates):
    async with state.proxy() as data:
        data['1_5'] = message.text
    await AllStates.next()

    async with state.proxy() as data:
        # ответ на результаты исследования при выборе головы
        if (data['1_1'] == "Недавно" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Да" and data['1_5'] == "Да":
            await message.answer(
                text="Возможно ухо болит из-за болезни, используйте капли для ушей и обратитесь к лору",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Недавно" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(
                text="Возможно оно скоро пройдет, если нет, то обратитесь к врачу",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Давно" or data['1_1'] == "Не знаю") and data['1_2'] == "Да" and data['1_3'] == "Да" \
                and data['1_4'] == "Да" and data['1_5'] == "Да":
            await message.answer(
                text="Обратись к лору, возможно что-то серьезное",
                reply_markup=kb.inline_kb1)

        elif (data['1_1'] == "Не знаю" or data['1_1'] == 'Недавно') and data['1_2'] == "Да" and data['1_3'] == "Да" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(
                text="Попробуйте прочистить уши, возможно они забились")

        elif (data['1_1'] == "Нет" or data['1_1'] == "Не знаю") and data['1_2'] == "Нет" and data['1_3'] == "Нет" \
                and data['1_4'] == "Нет" and data['1_5'] == "Нет":
            await message.answer(text="Может у вас ничего не болит?", reply_markup=kb.inline_kb1)

        else:
            await message.answer(
                text="Советуем выпить лекарства и подождать,если не помогло - вернитесь назад и"
                     " нажмите на кнопку 📋 Записаться к врачу")

    await state.finish()


# задание 4
@dp.callback_query_handler(lambda c: c.data, state='*')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery, state: FSMContext):
    # выбрали города из нашей БД
    conn = sqlite3.connect(config.sql)
    curs = conn.cursor()

    res = curs.execute(f'''SELECT name_city, discr_city FROM cities''').fetchall()
    conn.commit()

    array_btn_cities = []
    for el in res:
        array_btn_cities.append(list(el))

    answer = query.data
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    if answer == 'inf_about_all':
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Выбирайте город для поиска необходимой информации')
        # создаем новую клаиватуру и добавляем в нее кнопку выхода в главное меню
        inf_keyboard = create_inline_keyboard(array_btn_cities, 2)
        main_button = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        inf_keyboard.row(main_button)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                            reply_markup=inf_keyboard)
    elif answer == 'main_menu':
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Вы попали в главное меню выбирайте раздел')

        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                            reply_markup=kb.main_inline_menu)
    elif answer == 'backmenu':
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Выбирайте город для поиска необходимой информации')

        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                            reply_markup=create_inline_keyboard(array_btn_cities, 2))

    elif answer == 'city_1' or answer == 'back_city1':
        # выводим список того, что мы хоти узнать в г. Орск, у него номер 1 в таблице сотрудников (stuff)
        await bot.delete_message(chat_id, message_id)
        inkb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="Отделения", callback_data='otd1'),
                                                     InlineKeyboardButton(text="СОТРУДНИКИ", callback_data='stuff1'),
                                                     InlineKeyboardButton(text="📞 КОНТАКТНАЯ ИНФОРМАЦИЯ 📞",
                                                                          callback_data='contacts'),
                                                     InlineKeyboardButton(text="НАЗАД", callback_data='backmenu'))

        await bot.send_message(chat_id, "Выберите раздел", reply_markup=inkb)
    elif answer == 'otd1':
        # все отдения в первом городе otd1
        conn = sqlite3.connect(config.sql)
        curs = conn.cursor()
        c1 = curs.execute(f'''SELECT name_city FROM cities
                            WHERE discr_city= "city_1" ''').fetchone()
        res = curs.execute(f'''SELECT name_fil, filials.discr_fil FROM filials
                    WHERE city_fil = 1''').fetchall()
        conn.commit()

        array_btn_city1 = []
        for el in res:
            array_btn_city1.append(list(el))

        back_keyboard_city1 = create_inline_keyboard(array_btn_city1, 1)
        back_btn_otd = types.InlineKeyboardButton(text='НАЗАД', callback_data='back_city1')
        back_keyboard_city1.add(back_btn_otd)

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f"Список отделений города {c1[0]}", reply_markup=back_keyboard_city1)
    elif answer == 'stuff1':
        # список всех сотрудников города city1 - Орск
        await AllStates.photo_st.set()

        conn = sqlite3.connect(config.sql)
        curs = conn.cursor()
        c1 = curs.execute(f'''SELECT name_city FROM cities
                                    WHERE discr_city= "city_1" ''').fetchone()

        res = curs.execute(f'''SELECT fio, discr_doc FROM stuff
                            WHERE stuff.city = 1''').fetchall()
        conn.commit()

        array_btn_all_stuff = []
        for el in res:
            array_btn_all_stuff.append(list(el))

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f"Список ВСЕХ СОТРУДНИКОВ города {c1[0]}",
                                    reply_markup=create_inline_keyboard(array_btn_all_stuff, 1))
    elif answer == 'fil_1_1':
        # информация об уреждении Поликлиника
        conn = sqlite3.connect(config.sql)
        curs = conn.cursor()

        fil1 = curs.execute(f'''SELECT name_fil FROM filials
                            WHERE discr_fil= "fil_1_1" ''').fetchone()

        inf_res = curs.execute(f'''SELECT name_fil, adress_fil, grafik_fil, cities.name_city FROM filials
                                        JOIN cities ON cities.id=filials.city_fil
                                        WHERE filials.discr_fil = "fil_1_1" ''').fetchall()
        conn.commit()

        # создаем новую клаиватуру и добавляем в нее кнопку выхода в главное меню
        inf_keyboard = types.InlineKeyboardMarkup()
        main_button = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        inf_keyboard.add(main_button)

        inf_mess = f'''
        ℹ ИНФОРМАЦИЯ ОБ УЧРЕЖДЕНИИ ℹ
        НАИМЕНОВАНИЕ УЧРЕЖДЕНИЯ: {inf_res[0][0]}
        АДРЕС: {inf_res[0][1]}
        ГРАФИК РАБОТЫ: {inf_res[0][2]}
        Город: {inf_res[0][3]}
        '''
        # получаем карту
        try:
            ll, spn = get_ll_span(inf_res[0][1])

            if ll and spn:
                lon, lat = map(float, ll.split(','))
                params = {'appid': config.WEATHER_TOKEN, 'lat': lat,
                          'lon': lon, 'units': 'metric', 'lang': 'ru'}
                weather = requests.get(f'http://api.openweathermap.org/data/2.5/weather?lat='
                                       f'{lat}&lon={lon}&appid={config.WEATHER_TOKEN}', params).json()
                point = "{ll},pm2vvl".format(ll=ll)
                static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map&pt={point}". \
                    format(**locals())
                await bot.send_photo(chat_id=chat_id, photo=static_api_request, caption=inf_mess)
                await bot.send_message(chat_id=chat_id,
                                       text=f"Температура в {inf_res[0][1]} сейчас {weather['main']['temp']} градусов,"
                                            f" а по ощущениям {weather['main']['feels_like']} градусов",
                                       reply_markup=inf_keyboard)
        except RuntimeError as ex:
            await bot.reply_text(str(ex))
        await state.finish()
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                            reply_markup=inf_keyboard)
    elif answer == 'contacts':
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='📞 КОНТАКТНАЯ ИНФОРМАЦИЯ 📞')
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=config.CONTACTS_MES)
        # создаем новую клаиватуру и добавляем в нее кнопку выхода в главное меню
        inf_keyboard = types.InlineKeyboardMarkup()
        main_button = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        inf_keyboard.add(main_button)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                            reply_markup=inf_keyboard)
    elif answer == 'help_bot' or answer == '/help':
        # задание 6
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='📍 Помощь')
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=config.HELP_MES)
        # создаем новую клаиватуру и добавляем в нее кнопку выхода в главное меню
        inf_keyboard = types.InlineKeyboardMarkup()
        main_button = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        inf_keyboard.add(main_button)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                            reply_markup=inf_keyboard)
    elif answer == 'doc_appoit':
        # задание 1
        # создаем новую клаиватуру и добавляем в нее кнопку выхода в главное меню

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text="Для записи к врачу нажмите на кнопку", reply_markup=kb.inline_kb1)


@dp.callback_query_handler(text="city_2")
async def city1(callback: types.CallbackQuery):
    await callback.message.answer("Список врачей города2")
    await callback.answer()


@dp.callback_query_handler(text="city_3")
async def city1(callback: types.CallbackQuery):
    await callback.message.answer("Список врачей города3")
    await callback.answer()


@dp.message_handler(text=['❔ Задать вопрос'])
async def z_st(message: types.Message):
    await message.answer(text="Задайте вопрос и я постараюсь на него ответить")
    await AllStates.vopr_st.set()


@dp.message_handler(state=AllStates.vopr_st)
async def vopr(message: types.Message, state: AllStates):
    time = ["время", "час", "который", "скажи", "сколько"]
    doc = ["как", "запись", "записаться", "врач", "к", "где", "доктор", "терапевт", "стоматолог",
           "окулист", "лор", "нарколог"]
    bolit = ["болит", "что", "делать", "если", "у", "меня", "болеть"]
    admin = ["как", "админ", "администратор", "связь", "связать", "написать", "тех", "поддержка", "обратиться"]
    morph = pymorphy3.MorphAnalyzer()
    p = morph.parse(str(message.text).lower())[0]
    sovpadenie_time = 0
    sovpadenie_doc = 0
    sovpadenie_bolit = 0
    sovpadenie_admin = 0
    for word in p[0].split():
        if word in time:
            sovpadenie_time += 1
            continue
        elif word in doc:
            sovpadenie_doc += 1
            continue
        elif word in bolit:
            sovpadenie_bolit += 1
            continue
        elif word in admin:
            sovpadenie_admin += 1
            continue

    if sovpadenie_time > 1:
        now = datetime.datetime.now()
        await message.reply(f'Сейчас - {now.strftime("%d-%m-%Y %H:%M:%S")}')
    if sovpadenie_doc > 2:
        await message.reply(f"Для записи к врачу нажмите на <b>кнопку</b> ниже",
                            reply_markup=kb.inline_kb1, parse_mode='HTML')
    if sovpadenie_bolit > 2:
        await message.reply(f"Советую пройти в раздел <b>Симптомы</b> и пройти тест, или же запишитесь к врачу"
                            f" на прием по ссылке ниже", reply_markup=kb.inline_kb1, parse_mode='HTML')
    if sovpadenie_doc > 2:
        await message.reply(f"Для связи с тех поддержкой перейдите в раздел <b>Обратиться в поддержку</b>",
                            parse_mode='HTML')
    else:
        await message.reply(f"Задайте другой вопрос")
    await state.finish()


# функция ответа на неизвестный текст/команду
@dp.message_handler(content_types=['text'])
async def send_sorry(message: types.Message):
    await message.answer(text=config.SORRY)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
