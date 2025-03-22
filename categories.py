"""Работает с категориями"""
import json
import exceptions


def get_category(text_for_prepare):
    """Определяет категорию в которую необходимо записать расход"""
    global data_from_json
    with open("categories/categories.json", "r", encoding="utf-8") as categ_data:
        data_from_json = json.load(categ_data)
    try:    
        result = next(key for key in data_from_json
                    if text_for_prepare in data_from_json[key])
    except StopIteration:
        raise exceptions.NoSuchCategory("Укажите категорию")
    return result


def update_categories_json(text_for_prepare, ask_category): # TODO what it must return? Maybe "PASS"?
    """Если на основании нового расхода не удалось определить категорию,
    она вводится c помощью кнопки, а расход добавляется в алиасы"""
    try:
        data_from_json[ask_category].append(text_for_prepare)
        with open("categories/categories.json", "w", encoding="utf-8") as categ:
             json.dump(data_from_json, categ, indent=2)
    except KeyError:
        print(f"The {ask_category} is not a category") 
    return ask_category

def get_list_of_category() -> list:
    """Возвращает список категорий"""
    with open("categories/categories.json", "r", encoding="utf-8") as categ_data:
        data_from_json = json.load(categ_data)
    list_of_category = [key for key in data_from_json]
    return list_of_category
