from aiogram import types

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_btn2 = types.KeyboardButton("❤Симптомы")
main_btn3 = types.KeyboardButton("❔ Задать вопрос")
main_btn5 = types.KeyboardButton("☎ Обратиться в поддержку")
menu.add(main_btn2, main_btn3, main_btn5)


main_inl_btn1 = types.InlineKeyboardButton("📋 Записаться к врачу", callback_data="doc_appoit")
main_inl_btn4 = types.InlineKeyboardButton("ℹ Информация", callback_data="inf_about_all")
main_inl_btn6 = types.InlineKeyboardButton("📍 Помощь", callback_data="help_bot")
main_inline_menu = types.InlineKeyboardMarkup()
main_inline_menu.add(main_inl_btn1, main_inl_btn4, main_inl_btn6)

inline_btn_1 = types.InlineKeyboardButton('📋 Записаться к врачу', url="https://www.gosuslugi.ru/category/health", callback_data='button1')
main_button = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
inline_kb1 = types.InlineKeyboardMarkup().add(inline_btn_1, main_button)

# клавиатура для получения информации

menu_simp = types.ReplyKeyboardMarkup(resize_keyboard=True)
simp_btn1 = types.KeyboardButton("🧠 Голова")
simp_btn2 = types.KeyboardButton("❤ Живот")
simp_btn3 = types.KeyboardButton("🦷 Зубы")
simp_btn4 = types.KeyboardButton("💪 Рука или нога")
simp_btn5 = types.KeyboardButton("👂 Ухо")
back_btn = types.KeyboardButton("Назад 🔙")
menu_simp.add(simp_btn1, simp_btn2, simp_btn3, simp_btn4, simp_btn5, back_btn)


