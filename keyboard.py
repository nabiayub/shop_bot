from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from database import *


def send_contact_button():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Поделиться контактом', request_contact=True)]
    ], resize_keyboard=True, input_field_placeholder='Отправьте контакт...')


def generate_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='✔ Сделать заказ')],
        [KeyboardButton(text='📖 История'), KeyboardButton(text='🛒 Корзина'), KeyboardButton(text='⚙ Настройки')]
    ], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберете действие...')


def generate_category_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(text='Все меню', url='https://telegra.ph/Vkusnyaha-fastfud-07-13')
    )
    categories = get_all_categories()
    buttons = []
    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def generate_products_by_category(category_id):
    markup = InlineKeyboardMarkup(row_width=2)
    products = get_products_by_category_id(category_id)
    buttons = []
    for product in products:
        btn = InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}')
        buttons.append(btn)
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(text='◀ Назад', callback_data='main_menu')
    )
    return markup


def generate_product_detail_menu(product_id, category_id, card_id, product_name='', c=0):
    markup = InlineKeyboardMarkup(row_width=3)
    try:
        quantity = get_quantity(card_id, product_name)
    except:
        quantity = c

    buttons = []
    btn_minus = InlineKeyboardButton(text=str('➖'), callback_data=f'minus_{quantity}_{product_id}')
    btn_quantity = InlineKeyboardButton(text=str(c), callback_data=f'coll')
    btn_plus = InlineKeyboardButton(text=str('➕'), callback_data=f'plus_{quantity}_{product_id}')
    buttons.append(btn_minus)
    buttons.append(btn_quantity)
    buttons.append(btn_plus)
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(text='Добавить в корзину', callback_data=f'card_{product_id}_{quantity}')
    )
    markup.row(
        InlineKeyboardButton(text='◀ Назад', callback_data=f'back_{category_id}')
    )
    return markup


def generate_card_menu_buttons(card_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='✅  Оформить заказ', callback_data=f'order_{card_id}')
    )
    markup.row(
        InlineKeyboardButton(text='🔛  Продолжить заказ', callback_data=f'main_menu')
    )
    markup.row(
        InlineKeyboardButton(text='🛒 Очистить корзину', callback_data='remove')
    )
    card_products = get_card_product_for_delete(card_id)
    for card_product_id, product_name in card_products:
        markup.row(
            InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{card_product_id}')
        )

    return markup

def generate_continue_shopping_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='🔛  Продолжить заказ', callback_data=f'main_menu')
    )

    return markup

def choose_number_orders():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='📕 Все заказы')]
    ], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Напишите число заказов...')

def generate_settings_button():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='👨🏻 Изменить имя'), KeyboardButton(text='☎ Изменить номер')]
    ], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберете пункт...')


def generate_button_cancel():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='❌ Отменить')]
    ], resize_keyboard=True, one_time_keyboard=True)






