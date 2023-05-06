from datetime import date
from google_sheets import quikstart


month_dict = {1: "Январь", 2: "Февраль", 3: "Март",
              4: "Апрель", 5: "Май", 6: "Июнь",
              7: "Июль", 8: "Август", 9: "Сентябрь",
              10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}


def range_prepare(specified_date=None):
    """Указывае лист и диапазон ячеек в соответствии с текущим днем и месяцем"""
    current_dt = date.today()
    if specified_date is None:
        column_name = str(int(current_dt.day) + 1)
        list_name = month_dict[int(current_dt.month)]
    elif type(specified_date) == int:
        column_name = str(specified_date + 1)
    else:
        column_name = str(int(specified_date[3:]) + 1)
        list_name = month_dict[int(specified_date[0:2])]
    range_name = "!B" + column_name + ":H" + column_name
    range_gs = list_name + range_name
    return range_gs


def array_prepare(amount, category_text, specified_date):
    """Возвращает шаблон для записи суммы расхода в соответствующую ячейку"""
    previous_amount = quikstart.previous_amount_from_gs(category_text, specified_date)
    current_amount = amount
    categ_txt = category_text
    categ_dict = {"еда": [current_amount + previous_amount, None, None, None, None, None, None],
                  "кафе": [None, current_amount + previous_amount, None, None, None, None, None],
                  "алкоголь": [None, None, current_amount + previous_amount, None, None, None, None],
                  "сладкое": [None, None, None, current_amount + previous_amount, None, None, None],
                  "бензин": [None, None, None, None, current_amount + previous_amount, None, None],
                  "бытовая химия": [None, None, None, None, None, current_amount + previous_amount, None],
                  "разное": [None, None, None, None, None, None, current_amount + previous_amount]}
    array = categ_dict[categ_txt]
    return array


def previous_day_range():
    current_dt = date.today()
    list_name = month_dict[int(current_dt.month)]
    column_name = str(int(current_dt.day))
    range_name = "!B" + column_name + ":H" + column_name
    prev_range_gs = list_name + range_name
    return prev_range_gs

