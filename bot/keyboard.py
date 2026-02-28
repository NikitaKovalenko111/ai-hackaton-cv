from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

first = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отправить фото", callback_data="load_photo")],
                                               [InlineKeyboardButton(text="О проекте", callback_data="help")],
                                           ])
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отправить фото"),KeyboardButton(text="О проекте")],],
                           resize_keyboard=True,
                           one_time_keyboard=True)
