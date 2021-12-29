import re

def select_first(list):
    return list[0] if list else ''

def select_area(string):
    result = re.match(r'Общая площадь: (\d+\.?\d*) м2', string)
    return result.group(1) if result else ''

def select_uid(string):
    result = re.match(r'No (\d+)', string)
    return result.group(1) if result else ''

def select_room_count(string):
    result = re.match(r'Количество комнат: (\d+)', string)
    return result.group(1) if result else ''

def select_floor(string):
    result = re.match(r'Этаж: (\d+)', string)
    return result.group(1) if result else ''

def select_num_stor(string):
    result = re.match(r'Этаж: (\d+) из (\d+)', string)
    return result.group(2) if result else ''

def select_year(string):
    result = re.match(r'Год постройки: (\d+)', string)
    return result.group(1) if result else ''

def select_finish(string):
    result = re.match(r'Ремонт: (.+)', string)
    return result.group(1) if result else ''

def select_material(string):
    result = re.match(r'Тип дома: (.+)', string)
    return result.group(1) if result else ''

def select_parking(string):
    result = re.match(r'Парковка: (.+)', string)
    return result.group(1) if result else ''
