from aiogram import executor, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from database import *
from keyboard import *
from datetime import datetime
from configs import number_to_emoji, TOKEN, PAYMENT, all_commands

bot = Bot(TOKEN, parse_mode='HTML')

dp = Dispatcher(bot, storage=MemoryStorage())

class MyDiaLog(StatesGroup):
    phone = State()
    name = State()
    feedback = State()


@dp.message_handler(commands=['start', 'info'])
async def command_start(message: Message):
    chat_id = message.chat.id
    try:
        name = get_user_name(chat_id)
    except:
        name = message.from_user.full_name
    if message.text == '/start':
        await message.answer(f'Здравствуйте {name}. Вас приветствует бот вкусняха')
        await register_user(message)

    elif message.text == '/info':
        await message.answer(f'''Это тестовый telegram - бот для заказа еды.
Смело вводите номер своей карты для оплаты, деньги не снимутся (тестовый режим).
В качесетве кода подтверждения пишите любые цифры''')
        await message.answer('Выберите следующее действие:', reply_markup=generate_main_menu())




async def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = first_select_user(chat_id)
    print(user)
    if not user:
        first_register_user(chat_id, full_name)
        await message.answer('Для регистрации поделитесь контактом', reply_markup=send_contact_button())

    elif user[3] == None:
        await message.answer('Для полной регистрации поделитесь контактом', reply_markup=send_contact_button())

    else:
        await message.answer('Авторизация прошла успешно')
        await show_main_menu(message)


@dp.message_handler(content_types=['contact'])
async def finish_register_user(message: Message):
    print(message)
    chat_id = message.chat.id
    phone = message.contact.phone_number
    update_user_to_finish_register(chat_id, phone)
    await create_card_for_user(message)
    await message.answer('Регистрация прошла успешно')
    await show_main_menu(message)


async def create_card_for_user(message):
    print('he')
    chat_id = message.chat.id
    try:
        insert_into_card(chat_id)
    except:
        pass


async def show_main_menu(message: Message):
    await message.answer('Выберите навправления', reply_markup=generate_main_menu())


# --------------------------------------------------
@dp.message_handler(regexp=r'Сделать заказ')
async def make_order(message: Message):
    chat_id = message.chat.id
    card_id = get_user_card_id(chat_id)
    drop_card_products_default(card_id)
    await message.answer('Выберите категорию', reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'category' in call.data)
async def show_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    await bot.edit_message_text('Выберите продукт: ', chat_id, message_id,
                                reply_markup=generate_products_by_category(category_id))


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text('Выберите категорию', chat_id, message_id, reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'product' in call.data)
async def show_detail_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product_id = int(product_id)
    product = get_product_detail(product_id)
    card_id = get_user_card_id(chat_id)
    try:
        quantity = get_quantity(card_id, product[1])

        if quantity is None:
            quantity = 0
    except:
        quantity = 0

    await bot.delete_message(chat_id, message_id)
    with open(product[4], mode='rb') as img:
        await bot.send_photo(chat_id=chat_id, photo=img, caption=f'''{product[1]}
        
Ингредиенты: {product[3]}

Цена: {product[2]} сум''', reply_markup=generate_product_detail_menu(product_id=product_id, category_id=product[-1],
                                                                     card_id=card_id, product_name=product[1],
                                                                     c=quantity))


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def return_to_categories(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, 'Выберите продукт', reply_markup=generate_products_by_category(category_id))


@dp.callback_query_handler(lambda call: 'plus' in call.data)
async def add_product_card(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    quantity += 1
    message_id = call.message.message_id
    product = get_product_detail(product_id)
    card_id = get_user_card_id(chat_id)
    await bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                   caption=f'''{product[1]}

Ингредиенты: {product[3]}

Цена: {product[2]} сум''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                     category_id=product[-1],
                                                                     card_id=card_id, c=quantity))


@dp.callback_query_handler(lambda call: 'minus' in call.data)
async def remove_product_card(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    product = get_product_detail(product_id)
    card_id = get_user_card_id(chat_id)
    if quantity <= 1:
        await bot.answer_callback_query(call.id, 'Ниже нульля нельзя')
        pass
    else:
        quantity -= 1
        await bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                       caption=f'''{product[1]}

Ингредиенты: {product[3]}

Цена: {product[2]} сум''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                     category_id=product[-1],
                                                                     card_id=card_id, c=quantity))


@dp.callback_query_handler(lambda call: 'card' in call.data)
async def add_choose_product_to_card(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)

    card_id = get_user_card_id(chat_id)
    product = get_product_detail(product_id)
    final_price = product[2] * quantity

    if insert_or_update_card_product(card_id, product[1], quantity, final_price):
        await bot.answer_callback_query(call.id, '✅ Продукт успешно добавлен')
    else:
        await bot.answer_callback_query(call.id, '✅ Количество успешно изменено')


@dp.message_handler(regexp='🛒 Корзина')
async def show_card(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    card_id = get_user_card_id(chat_id)

    try:
        update_total_product_price(card_id)
    except Exception as e:
        await message.answer('Корзина не доступна. Обратитесь в тех. поддержку')

    card_products = get_card_products(card_id)
    total_products, total_price = get_total_products_price(card_id)

    if total_products == None:
        await bot.send_message(chat_id, 'Ваша корзина пуста', reply_markup=generate_continue_shopping_buttons())
    else:
        text = 'Ваша корзина: \n\n'

        for product_name, quantity, final_price in card_products:
            text1 = f'''{quantity} ✖ {product_name}\n'''
            text += number_to_emoji(text1) + f'Стоимость: {final_price} сум\n\n'

        text += f'''Общее количество продуктов: {0 if total_products is None else total_products}
    Общая сумма: {0 if total_price is None else total_price}'''

        if edit_message:
            await bot.edit_message_text(text, chat_id, message.message_id,
                                        reply_markup=generate_card_menu_buttons(card_id))
        else:
            await bot.send_message(chat_id, text, reply_markup=generate_card_menu_buttons(card_id))

@dp.callback_query_handler(lambda call: 'remove' in call.data)
async def delete_card(call: CallbackQuery):
    chat_id = call.message.chat.id
    message = call.message
    card_id = get_user_card_id(chat_id)
    drop_card_products_default(card_id)

    await bot.answer_callback_query(call.id, text='Корзина успешно очищена')
    await show_card(message, edit_message=True)

@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_card_product(call: CallbackQuery):
    _, card_product_id = call.data.split('_')
    card_product_id = int(card_product_id)
    message = call.message

    delete_card_prodcut_from(card_product_id)

    await bot.answer_callback_query(call.id, text='Продукт успешно удален')
    await show_card(message, edit_message=True)


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id

    _, card_id = call.data.split('_')
    card_id = int(card_id)

    time_now = datetime.now().strftime('%H:%M')
    new_date = datetime.now().strftime('%d.%m.%Y')

    card_products = get_card_products(card_id)
    total_products, total_price = get_total_products_price(card_id)

    save_order_table(card_id, total_products, total_price, time_now, new_date)
    orders_total_id = orders_total_price(card_id)

    text = 'Ваша корзина \n\n'

    for product_name, quantity, final_price in card_products:
        text1 = f'''{quantity} ✖ {product_name}\n'''
        text += number_to_emoji(text1) + f'Стоимость: {final_price} сум\n\n'
        save_order(orders_total_id, product_name, quantity, final_price)

    text += f'''\nОбщее количество продуктов: {0 if total_products is None else total_products}
Итого: {0 if total_price is None else total_price}'''

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Заказ №{card_id}',
        description=text,
        payload='bot-defined invoice payload',
        provider_token=PAYMENT,
        currency='UZS',
        prices=[
            LabeledPrice(label='общая стоимость', amount=int(total_price * 100)),
            LabeledPrice(label='Доставка', amount=1000000)
        ],
        start_parameter='start_parameter'
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Ошибка. Оплата не прошла')


@dp.message_handler(content_types=['successful_payment'])
async def get_payment(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Ура, оплата прошла успешно. Ожидайте заказ')
    card_id = get_user_card_id(chat_id)

    drop_card_products_default(card_id)


@dp.message_handler(lambda message: '📖 История' in message.text)
@dp.message_handler(commands=['history'])
async def ask_number_orders(message: Message):
    chat_id = message.chat.id
    card_id = get_user_card_id(chat_id)
    order_total_price = get_orders_total_price(card_id)

    await message.answer(f'''Всего заказов: {len(order_total_price)}
Напишите сколько последних заказов вы хотите посмотреть или выберете все''', reply_markup=choose_number_orders())


@dp.message_handler(lambda message: '📕 Все заказы' in message.text or message.text.isdigit())
async def show_history(message: Message):
    chat_id = message.chat.id
    card_id = get_user_card_id(chat_id)
    order_total_price = get_orders_total_price(card_id)
    if message.text == '📕 Все заказы':
        for i in order_total_price:
            if i[2] == None:
                pass
            else:
                text = f'''Дата заказа: {i[-1]}
Время заказа: {i[-2]} \n\n'''

                detail_product = get_detail_product(i[0])
                for j in detail_product:
                    text1 = number_to_emoji(f'''{j[1]} ✖ {j[0]} \n''')
                    text += text1

                text += f'''\nСумма товаров: {i[2]} сум
Доставка: 10000 сум
Итого: {10000 if i[2] == None else i[2] + 10000}'''
                await bot.send_message(chat_id, text)
        await bot.send_message(chat_id, 'Выберите следующее действие:', reply_markup=generate_main_menu())


    elif message.text.isdigit():
        order_nums = int(message.text)
        num = 0
        for i in order_total_price:
            if num >= order_nums:
                break
            else:
                if i[2] == None:
                    pass
                else:
                    num += 1
                    text = f'''Дата заказа: {i[-1]}
Время заказа: {i[-2]} \n\n'''

                    detail_product = get_detail_product(i[0])
                    for j in detail_product:
                        text1 = number_to_emoji(f'''{j[1]} ✖ {j[0]} \n''')
                        text += text1

                    text += f'''\nСумма товаров: {i[2]} сум
Доставка: 10000 сум
Итого: {10000 if i[2] == None else i[2] + 10000}'''
                    await bot.send_message(chat_id, text)
        await bot.send_message(chat_id, 'Выберите следующее действие:', reply_markup=generate_main_menu())




@dp.message_handler(lambda message: '/settings' in message.text)
@dp.message_handler(lambda message: '⚙ Настройки' in message.text)
async def show_settings(message: Message):
    await message.answer('⚙ Выберете пункт:', reply_markup=generate_settings_button())

@dp.message_handler(lambda message: '❌ Отменить' in message.text)
def return_main_menu(message: Message):
    message.answer('Выберите следующее действие: ', reply_markup=generate_main_menu())



@dp.message_handler(lambda message: 'Изменить' in message.text)
async def change_name_or_phone(message: Message):
    if message.text == '👨🏻 Изменить имя':
        await message.answer('Напишите свое новое имя:', reply_markup=generate_button_cancel())
        await MyDiaLog.name.set()
    elif message.text == '☎ Изменить номер':
        await message.answer('Напишите свой новый номер:', reply_markup=generate_button_cancel())
        await MyDiaLog.phone.set()

@dp.message_handler(content_types=['text'], state=MyDiaLog.name)
async def change_name(message: Message, state: FSMContext):
    new_name = message.text
    if new_name == '❌ Отменить':
        await return_main_menu(message)
    elif new_name in all_commands:
        await message.answer('Вы ввели команду вместо имени')
    print(new_name)
    chat_id = message.chat.id
    update_users_name(chat_id, new_name)
    await message.answer('Имя успешно изменено')
    await state.finish()


@dp.message_handler(content_types=['text'], state=MyDiaLog.phone)
async def change_phone(message: Message, state: FSMContext):
    new_phone = message.text
    chat_id = message.chat.id
    update_users_phone(chat_id, new_phone)
    await message.answer('Номер успешно изменен')
    await state.finish()

@dp.message_handler(lambda message: '/feedback' in message.text)
async def give_feedback(message: Message):
    await message.answer('Оставьте свой отзыв:')
    await MyDiaLog.feedback.set()

@dp.message_handler(content_types=['text'], state=MyDiaLog.feedback)
async def receive_feedback(message: Message, state: FSMContext):
    feedback = message.text
    if feedback in all_commands:
        await state.finish()
        await message.answer('Вы ввели команду вместо отзыва 🗨')
        await give_feedback(message)
    else:

        chat_id = message.chat.id
        try:
            name = get_user_name(chat_id)
        except:
            name = message.from_user.full_name
        insert_into_feedbacks(feedback, chat_id, name)
        await message.reply('🙃 Спасибо за отзыв :)')
        await state.finish()


executor.start_polling(dp)
