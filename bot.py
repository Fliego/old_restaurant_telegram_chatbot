# -*- coding: utf-8 -*-

import telebot
from telebot import types
import time
from markup import markup, fuck_markup, count_markup, hide_markup, big_small_markup
import config
from config import COMMENT_LENGTH, MESSAGE_LENGTH, LOYALTY_LOW_LIMIT
from SQLighter import SQLighter
from datetime import datetime
import utils
import sqlite3
from sqlite3 import OperationalError
import os
import string
import random
import cherrypy
import shutil
import time
from tqdm import tqdm
from threading import Thread

step = {}
request = {}
message_counter = {}

bot = telebot.TeleBot(config.token)


@bot.message_handler(func=lambda m: str(m.from_user.id) not in step or (m.text is not None and m.text == '/start'))
def start_handler(message):
    uid = str(message.from_user.id)
    # cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    # print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)

    step[uid] = {'cur': '', 'path': []}
    step[uid]['path'].append('start')
    step[uid]['cur'] = 'start'

    full_name = message.from_user.first_name
    if message.from_user.last_name is not None: full_name += " " + message.from_user.last_name

    if not db.has_user(uid):
        username = '' if message.from_user.username is None else message.from_user.username
        db.save_user_info(uid, full_name, username, '')

    lst = db.get_messages(step[uid]['cur'])
    if lst:
        text = lst[0].format(full_name) + "\n" + lst[1]
        m = markup(db, step[uid]['cur'])
        db.close()
        bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
    else:
        db.close()
        print(str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " " + uid + ': database error')


#################### BROADCAST
def broadcast_video_handler(message):
    if message.content_type == 'text' and message.text == 'Назад':
        request_broadcast_type(message)
        return
    if message.content_type == 'video':
        video = message.video.file_id
        bot.send_message(message.chat.id, 'Отправьте текст', parse_mode='HTML')
        bot.register_next_step_handler(message, lambda msg: broadcast_text_handler(msg, video=video))
    else:
        text = "Отправленное Вами сообщение является "
        if message.content_type == 'text':
            text += "<b>текстом</b>"
        if message.content_type == 'photo':
            text += "<b>фото</b>"
        if message.content_type == 'document':
            text += "<b>файлом</b>"
        if message.content_type == 'video':
            text += "<b>видео</b>"
        text += "\nОтправьте <b>видео</b>"
        bot.send_message(message.chat.id, text, parse_mode='HTML')
        bot.register_next_step_handler(message, broadcast_video_handler)


def broadcast_document_handler(message):
    if message.content_type == 'text' and message.text == 'Назад':
        request_broadcast_type(message)
        return
    if message.content_type == 'document':
        document = message.document.file_id
        bot.send_message(message.chat.id, 'Отправьте текст', parse_mode='HTML')
        bot.register_next_step_handler(message, lambda msg: broadcast_text_handler(msg, document=document))
    else:
        text = "Отправленное Вами сообщение является "
        if message.content_type == 'text':
            text += "<b>текстом</b>"
        if message.content_type == 'photo':
            text += "<b>фото</b>"
        if message.content_type == 'document':
            text += "<b>файлом</b>"
        if message.content_type == 'video':
            text += "<b>видео</b>"
        text += "\nОтправьте <b>файл</b>"
        bot.send_message(message.chat.id, text, parse_mode='HTML')
        bot.register_next_step_handler(message, broadcast_document_handler)


def broadcast_image_handler(message):
    if message.content_type == 'text' and message.text == 'Назад':
        request_broadcast_type(message)
        return
    if message.content_type == 'photo':
        image = message.photo[-2].file_id
        bot.send_message(message.chat.id, 'Отправьте текст', parse_mode='HTML')
        bot.register_next_step_handler(message, lambda msg: broadcast_text_handler(msg, image))
    else:
        text = "Отправленное Вами сообщение является "
        if message.content_type == 'text':
            text += "<b>текстом</b>"
        if message.content_type == 'photo':
            text += "<b>фото</b>"
        if message.content_type == 'document':
            text += "<b>файлом</b>"
        if message.content_type == 'video':
            text += "<b>видео</b>"
        text += "\nОтправьте <b>фото</b>"
        bot.send_message(message.chat.id, text, parse_mode='HTML')
        bot.register_next_step_handler(message, broadcast_image_handler)


def broadcast_text_handler(message, image=None, document=None, video=None):
    if message.content_type == 'text':
        if message.text == 'Назад':
            request_broadcast_type(message)
            return
        bot.send_chat_action(message.chat.id, 'typing')
        db = sqlite3.connect(config.database_name)
        c = db.cursor()
        c.execute("SELECT user_id FROM users GROUP BY user_id")
        users = c.fetchall()
        chat_ids = [int(row[0]) for row in users]
        db.close()
        bot.send_message(message.chat.id, "<b>Рассылка</b> начата", parse_mode='HTML')
        msg = bot.send_message(message.chat.id, "Отправлено: <b>0/{}</b>".format(len(chat_ids)), parse_mode='HTML')
        if chat_ids:
            print(len(chat_ids))
            Thread(target=send_broadcast, args=[chat_ids, image, message.text, document, video, msg]).start()
        return
        start_handler(message)
        # request_broadcast_type(message)
    else:
        text = "Отправленное Вами сообщение является "
        if message.content_type == 'text':
            text += "<b>текстом</b>"
        if message.content_type == 'photo':
            text += "<b>фото</b>"
        if message.content_type == 'document':
            text += "<b>файлом</b>"
        if message.content_type == 'video':
            text += "<b>видео</b>"
        text += "\nОтправьте <b>текст</b>"
        bot.send_message(message.chat.id, text, parse_mode='HTML')
        bot.register_next_step_handler(message, lambda m: broadcast_text_handler(m, image))


def request_broadcast_video(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('Назад'))
    msg = bot.send_message(message.chat.id, "Отправьте видео", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: broadcast_video_handler(m))


def request_broadcast_document(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('Назад'))
    msg = bot.send_message(message.chat.id, "Отправьте файл", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: broadcast_document_handler(m))


def request_broadcast_image(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('Назад'))
    msg = bot.send_message(message.chat.id, "Отправьте фото", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: broadcast_image_handler(m))


def request_broadcast_text(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton('Назад'))
    msg = bot.send_message(message.chat.id, "Отправьте текст", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: broadcast_text_handler(m, None))


def handle_broadcast_type(message):
    if message.content_type != 'text':
        bot.register_next_step_handler(message, lambda m: handle_broadcast_type(m))
        return
    text = message.text
    if text == 'Отправить текст с фото':
        request_broadcast_image(message)
        return
    if text == 'Отправить текст':
        request_broadcast_text(message)
        return
    if text == 'Отправить текст с файлом':
        request_broadcast_document(message)
        return
    if text == 'Отправить текст с видео':
        request_broadcast_video(message)
        return
    if text == 'Назад':
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Рассылка отменена", reply_markup=markup)
        start_handler(message)
        return
    bot.register_next_step_handler(message, lambda m: handle_broadcast_type(m))
    return


def request_broadcast_type(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton('Отправить текст'), types.KeyboardButton('Отправить текст с фото'),
               types.KeyboardButton('Отправить текст с файлом'), types.KeyboardButton('Отправить текст с видео'))
    markup.add(types.KeyboardButton('Назад'))
    msg = bot.send_message(message.chat.id, "Выберите тип рассылки", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: handle_broadcast_type(m))


@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    chat_id = message.chat.id
    if str(chat_id) not in ['put admin id here']:
        return
    request_broadcast_type(message)


def send_broadcast(chat_ids, image, text, document=None, video=None, msg_to_edit=None):
    count = 0
    if not chat_ids:
        return
    for chat_id in tqdm(chat_ids):
        try:
            if image:
                msg = bot.send_photo(chat_id, image, disable_notification=True)
            if document:
                msg = bot.send_document(chat_id, document, disable_notification=True)
            if video:
                msg = bot.send_video(chat_id, video, disable_notification=True)
            if text:
                msg = bot.send_message(chat_id, text, disable_notification=True)
            count += 1
            bot.edit_message_text("Прогресс: <b>{}/{}</b>".format(count, len(chat_ids)), chat_id=msg_to_edit.chat.id,
                                  message_id=msg_to_edit.message_id, parse_mode='HTML')
        except Exception:
            pass
    bot.send_message(msg_to_edit.chat.id, "<b>Рассылка</b> завершена", parse_mode='HTML')
    # print('send_broadcast %d/%d', count, len(chat_ids))


@bot.message_handler(content_types=['photo'])
def assign_image(message):
    uid = str(message.from_user.id)
    mx = 0
    mxid = 0
    for i, msg in enumerate(message.photo):
        if mx < msg.file_size:
            mx = msg.file_size
            mxid = msg.file_id
    name = '' if not message.caption else message.caption
    bot.send_photo(uid, mxid, mxid + '\n' + \
                   name, disable_notification=True)


#################### MAIN MENU
@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)][
    'cur'] == 'start' and m.text is not None and m.text[2:] == 'Оставить отзыв', content_types=['text'])
def comment_handle(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    if db.has_user(uid):
        t = ''
        if len(message.text.split(' ')) > 2:
            for i in message.text.split(' ')[1:]:
                t += i + ' '
            t = t[:-1]
        else:
            t = message.text.split(' ')[-1]
        step[uid]['cur'] = t
        step[uid]['path'].append(step[uid]['cur'])
        text = db.get_messages(step[uid]['cur'])
        if len(text) > 0:
            text = text[0]
            m = markup(db, step[uid]['cur'])
            db.close()
            bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
        else:
            db.close()
            print(
                str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " " + uid + ': database error')
    else:
        text = db.get_messages('Невозможно оставить отзыв')[0]
        bot.send_message(message.chat.id, text, parse_mode='HTML')


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'start',
                     content_types=['text'])
def step_start(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    # print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    start_btns = db.get_buttons(step[uid]['cur'])

    # отрезаем смайл
    t = ''
    if len(message.text.split(' ')) > 2:
        for i in message.text.split(' ')[1:]:
            t += i + ' '
        t = t[:-1]
    else:
        t = message.text.split(' ')[-1]
    fucking_flag = 0
    for button in start_btns:
        if t is not None and t == button:
            fucking_flag = 1
            step[uid]['cur'] = button
            step[uid]['path'].append(step[uid]['cur'])
            break

    msgs = db.get_messages(step[uid]['cur'])
    if len(msgs) > 0:
        text = msgs[0]

        m = markup(db, step[uid]['cur'], uid)
        if m is None and (t == 'Корзина' or t == 'Оформить'):
            step[uid]['path'].pop()
            step[uid]['cur'] = step[uid]['path'][-1]
            text = db.get_messages('recycle_empty')[0]
            m = markup(db, step[uid]['cur'])

        elif t == "Корзина":
            total = 0
            reqs = db.get_requests(uid)

            if len(reqs) == 0:
                text = db.get_messages('recycle_empty')[0]
                step[uid]['path'].pop()
                step[uid]['cur'] = step[uid]['path'][-1]
                m = markup(db, step[uid]['cur'])
            else:
                for i in reqs:
                    if len(i) >= 3:
                        text += str(i[0]) + ",  " + str(i[1]) + " x " + str(i[2]) + "\n"
                        total += int(i[1]) * int(i[2])
                text += "\nВсего: {} сум".format(total) + "\n\n" + msgs[1]

        db.close()
        if fucking_flag:
            bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
        else:
            pass

    else:
        db.close()
        print(str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "| " + uid + ': database error')


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)][
    'cur'] == 'Корзина' and m.text is not None and m.text.split(' ')[-1] == 'Очистить', content_types=['text'])
def clear_all(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    db.clear_requests(uid)

    step[uid]['cur'] = 'start'
    step[uid]['path'] = ['start']
    text = db.get_messages('Очистить')
    if len(text) > 0:
        text = text[0]
        m = markup(db, step[uid]['cur'], uid)
        db.close()
        bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')
    else:
        db.close()
        cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)][
    'cur'] == 'Корзина' and utils.is_correct_item(m.text), content_types=['text'])
def clear_item(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": delete " + message.text)

    db = SQLighter(config.database_name)
    db.delete_request(uid, message.text)
    text = db.get_messages('Оплата')[0].format(message.text) + "\n"

    total = 0
    reqs = db.get_requests(uid)

    if len(reqs) == 0:
        text = db.get_messages('recycle_empty')[0]
        step[uid]['path'].pop()
        step[uid]['cur'] = step[uid]['path'][-1]
        m = markup(db, step[uid]['cur'])
    else:
        for i in reqs:
            if len(i) >= 3:
                text += str(i[0]) + ",  " + str(i[1]) + " x " + str(i[2]) + "\n"
                total += int(i[1]) * int(i[2])
        text += "\nВсего: {} сум".format(total)
        m = markup(db, step[uid]['cur'], uid)
    db.close()
    bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(
    func=lambda m: str(m.from_user.id) in step and m.text is not None and m.text.split(' ')[-1] == 'Назад',
    content_types=['text'])
def handle_back(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    # print(str(cur_time) + " | " + uid + ": " + message.text)

    if step[uid]['path'][-1] != 'start':
        if step[uid]['cur'] == 'Размер':
            step[uid]['path'].pop()
            step[uid]['cur'] = step[uid]['path'][-1]
        step[uid]['path'].pop()
        step[uid]['cur'] = step[uid]['path'][-1]

        # if step[uid]['cur'] in config.products_list:
        #    step[uid]['path'].pop()
        #    step[uid]['cur'] = step[uid]['path'][-1]

        if step[uid]['cur'] == 'start':
            if uid in request:
                del request[uid]

        if step[uid]['cur'] == 'Оформить':
            del request[uid]['deliver']
            del request[uid]['longitude']
            del request[uid]['latitude']
            del request[uid]['destination']

        if step[uid]['cur'] == 'Адрес':
            del request[uid]['info']

        if step[uid]['cur'] == 'Контакт':
            del request[uid]['additional']

        if step[uid]['cur'] == 'Дополнительно':
            del request[uid]['payment']

        db = SQLighter(config.database_name)
        m = markup(db, step[uid]['cur'], uid)
        msgs = db.get_messages(step[uid]['cur'])

        if step[uid]['cur'] == 'start':
            text = msgs[1]

        elif step[uid]['cur'] in config.products_list or step[uid]['cur'] in config.type_list:
            m = fuck_markup(db, step[uid]['cur'], uid)
            text = db.get_messages('choose')[0]

        else:
            text = msgs[0]
        db.close()

        bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Food',
                     content_types=['text'])
@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Напитки',
                     content_types=['text'])
def step_food_drink(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    # print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    step_btns = db.get_buttons(step[uid]['cur'])

    # отрезаем смайл
    t = ''
    if message.text not in config.type_list:
        if len(message.text.split(' ')) > 2:
            for i in message.text.split(' ')[1:]:
                t += i + ' '
            t = t[:-1]
        else:
            t = message.text.split(' ')[-1]
    else:
        t = message.text

    fucking_flag = 0
    for button in step_btns:
        if t is not None and t == button:
            fucking_flag = 1
            step[uid]['cur'] = button
            step[uid]['path'].append(step[uid]['cur'])
            break

    msgs = db.get_messages(step[uid]['cur'])
    if len(msgs) > 0:
        text = msgs[0]
        m = markup(db, step[uid]['cur'], uid)
        db.close()

        if fucking_flag:
            bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
        else:
            pass

    else:
        db.close()
        print(str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " | " + uid + ': database error')


@bot.message_handler(
    func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] in config.step_list,
    content_types=['text'])
def some_handle(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    # print(str(cur_time) + " | " + uid + ": " + message.text)

    if message.text in config.type_list:
        db = SQLighter(config.database_name)
        step[uid]['cur'] = message.text
        step[uid]['path'].append(step[uid]['cur'])

        if message.text in config.products_list:

            m = count_markup(db)
            text = db.get_messages('count')[0]
            product_info = db.get_product_info(message.text)
            if product_info is not None:
                if len(product_info[uid]['price']) == 1:
                    caption = message.text + "\n\n" + "Цена: " + product_info['price'][0] + " сум"
                else:
                    caption = message.text + "\n\n" + "Большая: " + product_info['price'][
                        0] + " сум" + "\n" + "Маленькая: " + product_info['price'][1] + " сум"
                request[uid] = {}
                request[uid]['name'] = message.text
                request[uid]['size'] = 0  # по-умолчанию выбирается большая

                if len(product_info['price']) == 1:
                    step[uid]['cur'] = message.text
                else:
                    step[uid]['cur'] = 'Размер'
                    text = db.get_messages('Размер')[0]
                    m = big_small_markup(db)
                    step[uid]['path'].append(message.text)

                step[uid]['path'].append(step[uid]['cur'])

                db.close()
                try:
                    if product_info['fid'] is not None:
                        bot.send_photo(message.chat.id, product_info['fid'], caption=caption)
                except ValueError:
                    pass
                bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
            else:
                step[uid]['cur'] = 'start'
                step[uid]['path'] = ['start']
                m = markup(db, step[uid]['cur'], uid)
                text = db.get_messages('db_error')[0]
                db.close()
                cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")
                bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
        else:
            m = fuck_markup(db, step[uid]['cur'], uid)
            text = db.get_messages('choose')[0]
            db.close()
            bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(
    func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] in config.type_list and
                   m.text.split(' ')[-1] == 'Список', content_types=['text'])
def handle_list_menu(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    # print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    try:
        ids = db.get_menu_ids(step[uid]['cur'])
        for i in ids:
            bot.send_photo(message.chat.id, i)
        db.close()
    except OperationalError:
        text = db.get_messages('no_menu')[0]
        db.close()
        bot.send_message(message.chat.id, text)


@bot.message_handler(
    func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] in config.type_list,
    content_types=['text'])
def count_handle(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    config.products_list = db.get_product_names()
    if message.text in config.products_list:
        m = count_markup(db)
        text = db.get_messages('count')[0]
        product_info = db.get_product_info(message.text)
        if product_info is not None:
            if len(product_info['price']) == 1:
                caption = message.text + "\n\n" + "Цена: " + product_info['price'][0] + " сум"
            else:
                caption = message.text + "\n\n" + "Большая: " + product_info['price'][
                    0] + " сум" + "\n" + "Маленькая: " + product_info['price'][1] + " сум"

            request[uid] = {}
            request[uid]['name'] = message.text
            request[uid]['size'] = 0  # по-умолчанию выбирается большая

            if len(product_info['price']) == 1:
                step[uid]['cur'] = message.text
            else:
                step[uid]['cur'] = 'Размер'
                text = db.get_messages('Размер')[0]
                m = big_small_markup(db)
                step[uid]['path'].append(message.text)

            step[uid]['path'].append(step[uid]['cur'])
            db.close()
            try:
                if product_info['fid'] is not None:
                    bot.send_photo(message.chat.id, product_info['fid'], caption=caption)
            except:
                pass
            bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
        else:
            step[uid]['cur'] = 'start'
            step[uid]['path'] = ['start']
            m = markup(db, step[uid]['cur'], uid)
            text = db.get_messages('db_error')[0]
            db.close()
            cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            print(str(cur_time) + " | " + uid + ": Нет продукта {} в базе данных".format(message.text))
            bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Размер',
                     content_types=['text'])
def size_handler(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    if message.text in ["Большая", "Маленькая"]:
        db = SQLighter(config.database_name)
        if message.text == "Большая":
            request[uid]['size'] = 0
        elif message.text == "Маленькая":
            request[uid]['size'] = 1
        step[uid]['path'].pop()
        step[uid]['cur'] = step[uid]['path'][-1]
        m = count_markup(db)
        text = db.get_messages('count')[0]
        bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(
    func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] in config.products_list,
    content_types=['text'])
def count_handler(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)

    if message.text.isdigit() and int(message.text) >= 1:
        request[uid]['count'] = int(message.text)
        request[uid]['price'] = db.get_product_info(request[uid]['name'])['price'][request[uid]['size']]
        if len(db.get_product_info(request[uid]['name'])['price']) != 1:
            if request[uid]['size'] == 0:
                request[uid]['name'] += " , Большая "
            elif request[uid]['size'] == 1:
                request[uid]['name'] += " , Маленькая "

        db.save_to_recycle(uid, request[uid]['name'], request[uid]['price'], request[uid]['count'],
                           int(request[uid]['price']) * int(request[uid]['count']))
        text = db.get_messages('added_to_recycle')[0] + "\n\n" + db.get_messages('start_more')[0]
        step[uid]['cur'] = 'start'
        step[uid]['path'] = ['start']
        del request[uid]
        m = markup(db, step[uid]['cur'], uid)
        db.close()
        bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')


#################### ORDER CREATION
@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Оформить',
                     content_types=['text'])
def step_checkout_outside(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    btns = db.get_buttons(step[uid]['cur'])

    if len(message.text.split(' ')) > 2 and message.text.split(' ')[-2] + ' ' + message.text.split(' ')[-1] == \
            db.get_buttons('Оформить')[1]:
        text = db.get_messages('location_error')
        db.close()
        bot.send_message(message.from_user.id, text, parse_mode='HTML')
    else:
        step[uid]['cur'] = 'Адрес'
        step[uid]['path'].append(step[uid]['cur'])
        text = db.get_messages(step[uid]['cur'])
        if len(text) > 0:
            request[uid] = {}
            if message.text in btns:
                request[uid]['deliver'] = message.text
                request[uid]['longitude'] = ''
                request[uid]['latitude'] = ''
                request[uid]['destination'] = ''
            else:
                request[uid]['deliver'] = ''
                request[uid]['longitude'] = ''
                request[uid]['latitude'] = ''
                request[uid]['destination'] = message.text

            text = text[0]
            m = markup(db, step[uid]['cur'], uid)
            db.close()
            bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')
        else:
            db.close()
            cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Адрес',
                     content_types=['contact'])
def step_contact(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": sent contact")

    db = SQLighter(config.database_name)
    if message.contact.user_id == message.from_user.id:
        step[uid]['cur'] = 'Контакт'
        step[uid]['path'].append(step[uid]['cur'])
        text = db.get_messages(step[uid]['cur'])
        # проверить контакт на принадлежность юзеру
        if len(text) > 0:
            if message.contact.last_name is not None:
                full_name = message.contact.first_name + " " + message.contact.last_name
            else:
                full_name = message.contact.first_name

            if message.from_user.username is not None:
                username = message.from_user.username
            else:
                username = ''

            phone = str(message.contact.phone_number)

            request[uid]['info'] = {
                'full_name': full_name,
                'username': username,
                'phone': phone
            }
            text = text[0]
            m = markup(db, step[uid]['cur'], uid)
            db.close()
            bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')
        else:
            db.close()
            cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")
    else:
        text = db.get_messages('wrong_contact')[0]
        db.close()
        bot.send_message(message.chat.id, text, parse_mode='HTML')


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)][
    'cur'] == 'Адрес' and utils.is_correct_phone(m.text), content_types=['text'])
def step_phone_number(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    step[uid]['cur'] = 'Контакт'
    step[uid]['path'].append(step[uid]['cur'])
    text = db.get_messages(step[uid]['cur'])

    if len(text) > 0:
        if message.from_user.last_name is not None:
            full_name = message.from_user.first_name + " " + message.from_user.last_name
        else:
            full_name = message.from_user.first_name

        if message.from_user.username is not None:
            username = message.from_user.username
        else:
            username = ''

        phone = message.text

        request[uid]['info'] = {
            'full_name': full_name,
            'username': username,
            'phone': phone
        }
        text = text[0]
        m = markup(db, step[uid]['cur'], uid)
        db.close()
        bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')
    else:
        db.close()
        cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Контакт',
                     content_types=['text'])
def step_additional(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    step[uid]['cur'] = 'Дополнительно'
    step[uid]['path'].append(step[uid]['cur'])
    text = db.get_messages(step[uid]['cur'])
    if len(text) > 0:
        if message.text.split(' ')[-1] == 'Пропустить':
            request[uid]['additional'] = ''
        else:
            request[uid]['additional'] = message.text
        text = text[0]
        m = markup(db, step[uid]['cur'])
        db.close()
        bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')
    else:
        db.close()
        cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Дополнительно',
                     content_types=['text'])
def step_payment(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    pay_type_list = db.get_buttons(step[uid]['cur'])

    t = ''
    if len(message.text.split(' ')) > 2:
        for i in message.text.split(' ')[1:]:
            t += i + ' '
        t = t[:-1]
    else:
        t = message.text.split(' ')[-1]
    if t in pay_type_list:
        step[uid]['cur'] = 'Оплата'
        step[uid]['path'].append(step[uid]['cur'])
        text = db.get_messages(step[uid]['cur'])

        if len(text) > 0:
            request[uid]['payment'] = t
            text = text[0] + "\n"
            total = 0
            for i in db.get_requests(uid):
                if len(i) >= 3:
                    text += str(i[0]) + ",  " + str(i[1]) + " x " + str(i[2]) + "\n"
                    total += int(i[1]) * int(i[2])
            text += "\nВсего: {} сум".format(total) + "\n"
            if total >= 120000:
                text += "<b>При заказе от 120 000 сум доставка бесплатна.\nУ Вас бесплатная доставка!</b>" + '\n\n' + \
                        db.get_messages('confirm')[0]
            else:
                text += "<b>При заказе от 120 000 сум доставка бесплатна.\nДо бесплатной доставки - {} сум</b>\n\n".format(
                    120000 - total) + db.get_messages('confirm')[0]

            m = markup(db, step[uid]['cur'], uid)
            db.close()
            bot.send_message(message.from_user.id, text, reply_markup=m, parse_mode='HTML')
        else:
            db.close()
            cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            print(str(cur_time) + " | " + uid + ": Произошла ошибка чтения из базы данных")


@bot.message_handler(
    func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Оставить отзыв',
    content_types=['text'])
def step_comment(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d    %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    if message.from_user.last_name is not None:
        comment = message.from_user.first_name + " " + message.from_user.last_name + "    \n"
    else:
        comment = message.from_user.first_name + "\n"

    if message.from_user.username is not None:
        comment += "@" + message.from_user.username + "\n\n"
    comment += message.text + "\n\n" + str(cur_time)
    db.save_comment(uid, comment, str(cur_time))

    text = db.get_messages('Спасибо за отзыв')
    db.loyalty_decrement(uid)
    if len(text) > 0:
        text = text[0]
    else:
        text = db.get_messages('Спасибо за отзыв')
        print(str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + " " + uid + ': database error')

    admin_message = "<b>Отзыв:</b>" + "\n" + comment
    admins = db.get_admin_list()
    for i in admins:
        bot.send_message(i, admin_message, parse_mode='HTML')

    step[uid]['path'].pop()
    step[uid]['cur'] = step[uid]['path'][-1]
    m = markup(db, step[uid]['cur'])
    db.close()
    bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(func=lambda m: str(m.from_user.id) in step and step[str(m.from_user.id)]['cur'] == 'Оплата',
                     content_types=['text'])
def final(message):
    uid = str(message.from_user.id)
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(str(cur_time) + " | " + uid + ": " + message.text)

    db = SQLighter(config.database_name)
    if message.text.split(' ')[-1] == "Подтвердить":
        if not db.has_user(uid):
            db.save_user_info(uid, request[uid]['info']['full_name'], request[uid]['info']['username'],
                              request[uid]['info']['phone'])
        else:
            db.update_user_info(uid, request[uid]['info']['full_name'], request[uid]['info']['username'],
                                request[uid]['info']['phone'])

        request[uid]['date'] = str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d'))
        request[uid]['time'] = str(datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'))
        db.save_requests(uid, request[uid]['deliver'],
                         request[uid]['longitude'],
                         request[uid]['latitude'],
                         request[uid]['destination'],
                         request[uid]['additional'],
                         request[uid]['payment'],
                         request[uid]['date'],
                         request[uid]['time'])
        print("Запись прошла успешно")

        # теперь сгенерируем сообщение и отошлем его всем администраторам

        admin_message = '<b>' + request[uid]['info']['full_name'] + "</b>\n"
        if request[uid]['info']['username'] != '':
            admin_message += "@" + request[uid]['info']['username'] + "\n"
        admin_message += "<b>Телефон:</b> " + request[uid]['info']['phone'] + "\n\n"
        k = 1
        reqs = db.get_requests(uid)
        total = 0
        for i in reqs:
            if len(i) >= 3:
                admin_message += str(k) + ") " + str(i[0]) + ",  " + str(i[1]) + " x " + str(i[2]) + "\n"
                total += int(i[1]) * int(i[2])
                k += 1
        admin_message += "\nВсего: {} сум".format(total) + "\n\n"
        if request[uid]['additional'] != '':
            admin_message += "<b>Дополнение:</b> " + request[uid]['additional'] + "\n\n"
        admin_message += "<b>Адрес:</b> " + request[uid]['destination'] + '\n'
        admin_message += "<b>Тип оплаты:</b> " + request[uid]['payment'] + "\n"
        admin_message += "<b>Время заказа:</b> " + " " + request[uid]['time'] + "    " + request[uid]['date']
        admins = db.get_admin_list()

        for i in admins:
            try:
                bot.send_message(i, admin_message, parse_mode='HTML')
            except:
                pass

        # очищаем данные

        del request[uid]
        db.clear_requests(uid)
        step[uid]['path'] = []
        step[uid]['path'].append('start')
        step[uid]['cur'] = 'start'
        text = db.get_messages('Новый заказ')[0]
        m = markup(db, step[uid]['cur'])
        bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')

    elif message.text.split(' ')[-1] == "Отменить":
        del request[uid]
        step[uid]['path'] = []
        step[uid]['path'].append('start')
        step[uid]['cur'] = 'start'
        text = db.get_messages('start')[1]
        m = markup(db, step[uid]['cur'])
        bot.send_message(message.chat.id, text, reply_markup=m, parse_mode='HTML')

    else:
        pass


if config.TEST_CONFIG:
    if __name__ == "__main__":
        bot.remove_webhook()
        bot.polling(none_stop=True)
else:
    class WebhookServer(object):
        @cherrypy.expose
        def index(self):
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length)
            json_string = json_string.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            if update.message:
                bot.process_new_messages([update.message])
            if update.inline_query:
                bot.process_new_inline_query([update.inline_query])
            return ''


    if __name__ == '__main__':
        bot.remove_webhook()
        bot.set_webhook("https://webhook.com/BOT_TOKEN")

        cherrypy.config.update({
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 7771,
            'engine.autoreload.on': False
        })

        cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
