import datetime
from typing import List, Tuple


def transform_datetime(note_time):

    timestamp = note_time.timestamp()
    formatted_date = datetime.datetime.fromtimestamp(
        timestamp
    ).strftime(
        '%Y-%m-%d %H:%M:%S'
    ).split(" ")

    return formatted_date


def format_records(records: List[Tuple]) -> str:

    if not records:
        return "Нет записей в данной категории"
    
    response = "\n".join([
        f"Запись: <b>{record[2].title()}</b>\nСумма: <b>{'{0:,.0f}'.format(record[1]).replace(',', '.')}</b> ₽\nДата: <b>{record[3].strftime('%Y.%m.%d')}</b>\n"
        for record in records
    ])
    
    return response


def format_statistic_records(data):

    if not data:
        return "Записи еще не были созданы"
    response = '\n'.join([
        f"Категория: <b>{category}</b>\nЗаписей: <b>{count}</b>\nСумма: <b>{'{0:,.0f}'.format(price).replace(',', '.')}</b> ₽\n"
        for category, count, price in data
    ])

    return response



"""
/give SecDet minecraft:netherite_axe{
    display:{Name:'[{"text":"Перфоратор"}]'},
    Enchantments:[
        {id:"minecraft:unbreaking",lvl:1337},
        {id:"minecraft:sharpness",lvl:666},
        {id:"minecraft:mending",lvl:228}, 
        {id:"minecraft:fire_aspect",lvl:1488}
    ]
}

"""