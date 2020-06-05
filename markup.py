# -*- coding: utf-8 -*-

from telebot import types
from config import emojis as emj
import config


def markup(db, step, uid=''):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if step != 'start' and step != 'Корзина' and step != 'Адрес' and step != 'Оплата' and step != 'Дополнительно' and step != 'Контакт' and step != 'Оформить':
        type_list = db.get_menu_type_list()
        if step in type_list:
            m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0], emj['Список'] + ' ' + db.get_buttons('list')[0])
        else:
            m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])

    if step == 'start':
        btns = db.get_buttons(step)
        m.add(emj['Food'] + ' ' + btns[0], emj['Напитки'] + ' ' + btns[1])
        m.add(emj['Корзина'] + ' ' + btns[2], emj['Оформить'] + ' ' + btns[3])
        m.add(emj['Отзыв'] + ' ' + btns[4])

    elif step == 'Food':
        btns = db.get_buttons(step)
        m.add(emj['Национальная'] + ' ' + btns[0], emj['Корейская'] + ' ' + btns[1])
        m.add(emj['Пицца'] + ' ' + btns[2], emj['Суши'] + ' ' + btns[3])
        m.add(emj['Гарниры'] + ' ' + btns[4], emj['Десерты'] + ' ' + btns[5])
        m.add(emj['Закуски'] + ' ' + btns[6], emj['Шашлык'] + ' ' + btns[7])
        m.add(emj['bread'] + ' ' + btns[8])

    elif step == 'Напитки':
        btns = db.get_buttons(step)
        for b in btns:
            m.add(b)

    elif step == 'Оставить отзыв':
        btns = db.get_buttons(step)
        m.add(emj['Отлично'] + ' ' + btns[0])

    else:
        steps = db.get_message_steps()
        for i in steps:
            if step == 'Корзина':
                m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0],
                      emj['Корзина'] + ' ' + db.get_buttons('Корзина')[0])
                reqs = db.get_requests(uid)
                for j in reqs:
                    if len(j) >= 3:
                        temp = str(j[0]) + ",  " + str(j[1]) + " x " + str(j[2])
                        m.add(temp)
                    else:
                        print('В таблице requests у пользователя {} неправильный запрос'.format(uid))
                        break
                break

            elif step == 'Оформить':
                if uid != '':
                    reqs = db.get_requests(uid)
                    if len(reqs) == 0:
                        return None
                    else:
                        btns = db.get_buttons(step)
                        if len(btns) != 0:
                            m.add(emj['Вынос'] + ' ' + btns[0])
                            # loc_btn = types.KeyboardButton(emj['Локация'] + ' ' + btns[1], request_location=True)
                            # m.add(loc_btn)
                            m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
                            break
                        else:
                            print('Не могу получить кнопки из базы| step = ' + step)
                            break

            elif step == 'Адрес':
                btns = db.get_buttons(step)
                if len(btns) != 0:
                    contact = types.KeyboardButton(emj['Контакт'] + ' ' + btns[0], request_contact=True)
                    m.add(contact)
                    m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
                    break
                else:
                    print('Не могу получить кнопки из базы| step = ' + step)
                    break

            elif step == 'Контакт':
                btns = db.get_buttons(step)
                if len(btns) != 0:

                    m.add(emj['Пропустить'] + ' ' + btns[0])
                    m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
                    break
                else:
                    print('Не могу получить кнопки из базы| step = ' + step)
                    break

            elif step == 'Дополнительно':
                btns = db.get_buttons(step)
                if len(btns) != 0:

                    m.add(emj['Наличные'] + ' ' + btns[0], emj['Карта'] + ' ' + btns[1])
                    m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
                    break
                else:
                    print('Не могу получить кнопки из базы| step = ' + step)
                    break

            elif step == 'Оплата':
                btns = db.get_buttons('Оплата')
                if len(btns) != 0:
                    m.add(emj['Подтвердить'] + ' ' + btns[0], emj['Отменить'] + ' ' + btns[1])
                    m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
                    break
                else:
                    print('Не могу получить кнопки из базы| step = ' + step)
                    break

            elif step == i:
                btns = db.get_buttons(step)
                if len(btns) > 0:
                    if len(btns) % 2 == 0:
                        for j in range(0, len(btns) - 1, 2):
                            m.add(btns[j], btns[j + 1])
                    else:
                        for j in range(0, len(btns) - 2, 2):
                            m.add(btns[j], btns[j + 1])
                        m.add(btns[-1])
                else:
                    btns = config.type_list
                    if step in btns:
                        btns = db.get_products(step)
                        for j in range(0, len(btns)):
                            m.add(btns[j])
    return m


def fuck_markup(db, step, uid=''):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    type_list = db.get_menu_type_list()
    if step in type_list:
        m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0], emj['Список'] + " " + db.get_buttons('list')[0])
    else:
        m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
    steps = db.get_button_steps()

    if step == 'Food':
        btns = db.get_buttons(step)
        m.add(emj['Национальная'] + ' ' + btns[0], emj['Корейская'] + ' ' + btns[1])
        m.add(emj['Пицца'] + ' ' + btns[2], emj['Суши'] + ' ' + btns[3])
        m.add(btns[4], btns[5])
        m.add(btns[6], btns[7])

    elif step == 'Напитки':
        btns = db.get_buttons(step)
        m.add(emj['Алкогольные'] + ' ' + btns[0], emj['Безалкогольные'] + ' ' + btns[1])

    elif step in steps:
        btns = db.get_buttons(step)
        if len(btns) % 2 == 0:
            for j in range(0, len(btns)):
                m.add(btns[j], btns[j + 1])
        else:
            for j in range(0, len(btns) - 2, 2):
                m.add(btns[j], btns[j + 1])
            m.add(btns[-1])
        return m

    elif step in config.type_list:
        btns = db.get_products(step)
        if "Куксу" in btns and "Куксу мясо жареное" in btns:
            btns.remove("Куксу")
            btns.remove("Куксу мясо жареное")
            btns = ["Куксу", "Куксу мясо жареное"] + btns
        for j in range(0, len(btns)):
            m.add(btns[j])
        return m

    else:
        return None


def count_markup(db):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
    for i in range(1, 10, 3):
        m.add(str(i), str(i + 1), str(i + 2))
    return m


def hide_markup():
    return types.ReplyKeyboardRemove()


def big_small_markup(db):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(emj['Назад'] + ' ' + db.get_buttons('back')[0])
    m.add('Большая', 'Маленькая')
    return m
