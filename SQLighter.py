# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:

    # users: id(autoinc), user_id, username, photo, phone
    # requests: id(autoinc), user_id, type_id, date, additional, status

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    def get_buttons(self, step):
        with self.connection:
            q = "SELECT type FROM buttons WHERE step = '{}'".format(step)
            lst = self.cursor.execute(q).fetchall()
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def get_messages(self, step):
        with self.connection:
            q = "SELECT message FROM messages WHERE step = '{}'".format(step)
            lst = self.cursor.execute(q).fetchall()
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def get_requests(self, uid):
        with self.connection:
            q = "SELECT name, price, count FROM requests WHERE user_id = '{}' AND deleted = 0".format(uid)
            return self.cursor.execute(q).fetchall()

    def get_message_steps(self):
        with self.connection:
            q = "SELECT step FROM messages WHERE 1"
            lst = list(set(self.cursor.execute(q).fetchall()))
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def get_button_steps(self):
        with self.connection:
            q = "SELECT step FROM buttons WHERE 1"
            lst = list(set(self.cursor.execute(q).fetchall()))
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def get_product_names(self):
        with self.connection:
            q = "SELECT name FROM products WHERE in_stock = 1"
            lst = list(set(self.cursor.execute(q).fetchall()))
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def clear_requests(self, uid):
        with self.connection:
            self.cursor.execute("UPDATE requests SET deleted = 1 WHERE user_id = ?", (uid,))

    def delete_request(self, uid, req):
        req = req.split('  ')
        # print(req)
        name = req[0][:-1]
        # print(name)
        price = req[1].split(' ')[0]
        # print(price)
        count = req[1][1:].split(' ')[2]
        # print(count)

        with self.connection:
            self.cursor.execute(
                "UPDATE requests SET deleted = 1 WHERE user_id = ? AND name = ? AND price = ? AND count = ?",
                (uid, name, price, count))

    def has_user(self, uid):
        with self.connection:
            q = "SELECT user_id FROM users WHERE user_id = '{}'".format(uid)
            res = self.cursor.execute(q).fetchall()
            if len(res) > 0:
                return True
            else:
                return False

    def save_comment(self, uid, comment, date):
        comment = comment.replace("'", '').replace('"', '')
        with self.connection:
            q = "INSERT INTO comments VALUES (null, ?, ?, ?)"
            self.cursor.execute(q, (uid, comment, date))

    def save_user_info(self, uid, full_name, username, phone):
        full_name = full_name.replace("'", '').replace('"', '')
        username = username.replace("'", '').replace('"', '')
        phone = phone.replace("'", '').replace('"', '')
        with self.connection:
            q = "INSERT INTO users VALUES (null, ?, ?, ?, ?, 0, 0, 0)"
            self.cursor.execute(q, (uid, full_name, username, phone))

    def get_req_ids(self, uid):
        with self.connection:
            q = "SELECT id FROM requests WHERE user_id = ? AND deleted = 0"
            req_lst = self.cursor.execute(q, (uid,))
            req_ids = ''
            for i in req_lst:
                req_ids += str(i[0]) + ","
            return req_ids[:-1]

    def save_requests(self, uid, deliver, longitude, latitude, destination, additional, payment, date, time):
        deliver = deliver.replace("'", '').replace('"', '')
        destination = destination.replace("'", '').replace('"', '')
        additional = additional.replace("'", '').replace('"', '')
        with self.connection:
            req_list = self.get_req_ids(uid)
            q = "INSERT INTO orders VALUES (null, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)"
            self.cursor.execute(q, (
                uid, req_list, deliver, payment, longitude, latitude, destination, additional, date, time))

    def save_photo_id(self, name, fid):
        with self.connection:
            q = "INSERT INTO menu VALUES (null, ?, ?, ?)"
            self.cursor.execute(q, (name, name, fid))

    def get_product_info(self, product):
        with self.connection:
            q = "SELECT price, image_id FROM products WHERE in_stock = 1 AND name = ?"
            res = self.cursor.execute(q, (product,)).fetchall()
            d = {}
            if len(res) > 0:
                d['price'] = []
                for i in res:
                    d['price'].append(i[0])
                d['fid'] = res[0][1]
                return d
            else:
                return None

    def get_type_list(self):
        with self.connection:
            q = "SELECT type FROM products WHERE 1"
            lst = list(set(self.cursor.execute(q).fetchall()))
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def get_menu_type_list(self):
        with self.connection:
            q = "SELECT type FROM menu WHERE 1"
            lst = list(set(self.cursor.execute(q).fetchall()))
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def get_products(self, step):
        with self.connection:
            q = "SELECT name FROM products WHERE type = ? AND in_stock = 1"
            lst = list(set(self.cursor.execute(q, (step,)).fetchall()))
            j = 0
            for i in lst:
                lst[j] = i[0]
                j += 1
            return lst

    def save_to_recycle(self, uid, name, price, count, cost):
        with self.connection:
            q = "INSERT INTO requests VALUES (null, ?, ?, ?, ?, ?, 0)"
            self.cursor.execute(q, (uid, name, price, count, cost))

    def update_photo_id(self, name, image_id, id):
        with self.connection:
            q = "UPDATE products SET name = ?, image_id = ? WHERE id = ?"
            self.cursor.execute(q, (name, image_id, id))

    def ban_user(self, uid):
        with self.connection:
            q = "UPDATE users SET banned = 1 WHERE user_id = ?"
            self.cursor.execute(q, (uid,))

    def get_banned_users(self):
        with self.connection:
            q = "SELECT user_id FROM users WHERE banned = 1"
            res = self.cursor.execute(q).fetchall()
            lst = []
            for i in res:
                lst.append(i[0])
            return lst

    def get_menu_ids(self, type):
        with self.connection:
            q = "SELECT image_id FROM menu WHERE type = ?"
            res = self.cursor.execute(q, (type,)).fetchall()
            lst = []
            for i in res:
                lst.append(i[0])
            return lst

    def get_admin_list(self):
        with self.connection:
            q = "SELECT admin FROM users WHERE admin != 0"
            res = self.cursor.execute(q).fetchall()
            lst = []
            for i in res:
                lst.append(i[0])
            return lst

    def update_user_info(self, uid, full_name, username, phone):
        full_name = full_name.replace("'", '').replace('"', '')
        username = username.replace("'", '').replace('"', '')
        phone = phone.replace("'", '').replace('"', '')
        with self.connection:
            q = "UPDATE users SET full_name = ?, username = ?, phone = ? WHERE user_id = ?"
            self.cursor.execute(q, (full_name, username, phone, uid))

    def set_admin(self, uid, admin_id):
        with self.connection:
            q = "UPDATE users SET admin = ? WHERE user_id = ?"
            self.cursor.execute(q, (admin_id, uid))

    def unset_admin(self, uid):
        with self.connection:
            q = "UPDATE users SET admin = 0 WHERE user_id = ?"
            self.cursor.execute(q, (uid,))

    def get_loyalty(self, uid):
        with self.connection:
            q = "SELECT loyalty FROM users WHERE user_id = ?"
            res = self.cursor.execute(q, (uid,)).fetchall()
            if len(res) == 0:
                return None
            else:
                return res[0][0]

    def loyalty_decrement(self, uid):
        with self.connection:
            q = "UPDATE users SET loyalty = ? WHERE user_id = ?"
            loyalty = self.get_loyalty(uid)
            if loyalty is not None:
                loyalty -= 1
            else:
                return
            self.cursor.execute(q, (loyalty, uid))
