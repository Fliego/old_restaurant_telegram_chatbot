# -*- coding: utf-8 -*-
from SQLighter import SQLighter

TEST_CONFIG = 1

if TEST_CONFIG:
    # test config
    # token = '214820989:AAEHsLvgydAYspHBhz1kf4Ay7fUCaUUbPwY'
    token = 'BOT_TOKEN'
    database_name = './db.db'
    # testBotName: @EdemLPBot
else:
    # main config
    token = 'BOT_TOKEN'
    # database_name = '../db.db'
    database_name = '/usr/share/nginx/html/project/db.db'
    # mainBotName: @dbbot

emojis = {
    'Локация': '\U0001F4CD',
    'Контакт': '\U0001F4F1',
    'Подтвердить': '\U00002705',
    'Отменить': '\U0001F6AB',
    'Пропустить': '\U000027A1',
    'Назад': '\U0001F519',  # '\U00002B05',
    'Суши': '\U0001F363',
    'Пицца': '\U0001F355',
    'Корейская': '\U0001F35C',
    'Национальная': '\U0001F35B',
    'Очистить': '\U0001F504',
    'Карта': '\U0001F4B3',
    'Наличные': '\U0001F4B8',
    'Вынос': '\U0001F3EB',
    'Отзыв': '\U0001F4DD',
    'Оформить': '\U0001F695',
    'Корзина': '📥',
    'Напитки': '\U0001F379',
    'Food': '🍳',
    'Алкогольные': '\U0001F377',
    'Безалкогольные': '\U00002615',
    'Дополнительно': '\U0001F58A',
    'Отлично': '\U0001F44D\U0001F3FB',
    'Гарниры': '🍚',
    'Шашлык': '🍢',
    'Десерты': '🍰',
    'Закуски': '🍱',
    'Список': '⏩',
    'bread': '\U0001F35E'
}

conn = SQLighter(database_name)

step_list = conn.get_button_steps()
reserved = ['Контакт', 'Оставить отзыв', 'Дополнительно', 'Адрес', 'start', 'Оформить', 'Оплата', 'Корзина', 'back']
for i in reserved:
    if i in step_list:
        step_list.remove(i)
# print(step_list)

type_list = conn.get_type_list()
# print(type_list)

products_list = conn.get_product_names()
# print(products_list)

conn.close()

COMMENT_LENGTH = 1024
MESSAGE_LENGTH = 512
LOYALTY_LOW_LIMIT = -15
