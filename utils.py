# -*- coding: utf-8 -*-
import re


def is_correct_phone(phone):
    if phone is None:
        return False
    if re.match(r'^\+?[0-9 -()]+$', phone) is not None:
        phone = phone.replace(' ', '').replace('-', '').replace('+', '').replace('(', '').replace(')', '')
        if 5 <= len(phone) <= 15:
            return True
    else:
        return False


def is_correct_item(req):
    if req is None:
        return False
    if re.match(r'^[a-zA-Zа-яА-я ,.-]+,  [0-9]+ x [0-9]+$', req) is not None:
        return True
    else:
        return False
