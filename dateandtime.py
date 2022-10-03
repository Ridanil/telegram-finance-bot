from datetime import date
import quikstart

month_dict = {1: "Январь", 2: "Февраль", 3: "Март",
                  4: "Апрель", 5: "Май", 6: "Июнь",
                  7: "Июль", 8: "Август", 9: "Сентябрь",
                  10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}

def range_prepare():
    """Указывае лист и диапазон ячеек в соответствии с текущим днем и месяцем"""
    current_dt = date.today()
    list_name = month_dict[int(current_dt.month)]
    column_name = str(int(current_dt.day) + 1)
    range_name = "!B" + column_name + ":H" + column_name
    range_gs = list_name + range_name
    return range_gs


def array_prepare(amount, category_text):
    """Возвращает шаблон для записи суммы расхода в соответствующую ячейку"""
    previous_amount = quikstart.previous_amount_from_gs(category_text)
    amnt = amount
    categ_txt = category_text
    categ_dict = {"еда": [amnt + previous_amount, None, None, None, None, None, None],
                  "кафе": [None, amnt + previous_amount, None, None, None, None, None],
                  "алкоголь": [None, None, amnt + previous_amount, None, None, None, None],
                  "сладости": [None, None, None, amnt + previous_amount, None, None, None],
                  "бензин": [None, None, None, None, amnt + previous_amount, None, None],
                  "бх": [None, None, None, None, None, amnt + previous_amount, None],
                  "разное": [None, None, None, None, None, None, amnt + previous_amount]}
    array = categ_dict[categ_txt]
    return array


def previous_day_range():
    current_dt = date.today()
    list_name = month_dict[int(current_dt.month)]
    column_name = str(int(current_dt.day))
    range_name = "!B" + column_name + ":H" + column_name
    prev_range_gs = list_name + range_name
    return prev_range_gs
