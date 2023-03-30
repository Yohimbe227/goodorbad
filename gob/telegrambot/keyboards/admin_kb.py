"""Кнопки клавиатуры администратора."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button_load = KeyboardButton('/Загрузить')
button_delete = KeyboardButton('/Удалить')

kb_admin = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .add(button_load)
    .add(button_delete)
)
