"""Работает с категориями"""
import json
from keyboards import kb_client


# data = {"еда": ["еда", "хлеб", "вода", "фрукты", "овощи"],
#         "кафе": ["кафе", "шаурма", "мейхане", "бургер", "роллы", "пицца", "суши"],
#         "алкоголь": ["алкоголь", "пиво", "к пиву"],
#         "сладкое": ["сладкое", "торт", "печенье", "сладости", "мороженное"],
#         "бензин": ["бензин"],
#         "бытовая химия": ["бытовая химия", "б/х", "мыло", "шампунь"],
#         "разное": []
#         }


def get_category(text_for_prepare):
    """Определяет категорию в которую необходимо записать расход"""
    with open("categories.json", "r", encoding="utf-8") as categ_data:
        data_from_json = json.load(categ_data)
    try:    
        result = next(key for key in data_from_json
                    if text_for_prepare in data_from_json[key])
    except StopIteration:
        result = update_categories_json(text_for_prepare, data_from_json)
    return result


def update_categories_json(text_for_prepare, data_from_json):
    """Если на основании нового расхода не удалось определить категорию,
    она вводится вруную а расход добавляется в алиасы"""
    ask_category = kb_client #TODO input заменить на сообщение пользователю с запросом нужной категории
    try:
        data_from_json[ask_category].append(text_for_prepare)
        with open("categories.json", "w", encoding="utf-8") as categ:
             json.dump(data_from_json, categ, indent=2)
    except KeyError:
        print(f"The {ask_category} is not a category") 
    return ask_category
