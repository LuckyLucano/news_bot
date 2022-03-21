from telebot.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def generate_category_markup(category_list):
    category_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for category in category_list:
        category_button = KeyboardButton(text=category[0])
        category_markup.add(category_button)
    return category_markup


def generate_link_markup(link):
    link_markup = InlineKeyboardMarkup()
    link_button = InlineKeyboardButton(url=link, text='Читать на сайте')
    link_markup.add(link_button)
    return link_markup
