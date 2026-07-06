"""Работает с категориями"""
import json
import exceptions

def load_categories():                                                                      
       """Загружает категории из JSON-файла."""                                                
       with open("categories/categories.json", "r", encoding="utf-8") as categ_data:           
           return json.load(categ_data)

def save_categories(data):                                                                  
       """Сохраняет категории обратно в JSON-файл."""                                          
       with open("categories/categories.json", "w", encoding="utf-8") as categ:                
           json.dump(data, categ, indent=2)

def get_category(text_for_prepare):
    """Определяет категорию в которую необходимо записать расход"""
    categories = load_categories()
    for category, aliases in categories.items():                                            
           if text_for_prepare in aliases:                                                     
               return category
    raise exceptions.NoSuchCategory("Укажите категорию")
    
def update_categories_json(text_for_prepare, ask_category): # TODO what it must return? Maybe "PASS"?
    """Если на основании нового расхода не удалось определить категорию,
    она вводится c помощью кнопки а расход добавляется в алиасы"""
    categories = load_categories()
    try:
        categories[ask_category].append(text_for_prepare)
    except KeyError:
        print(f"The {ask_category} is not a category") 
    return ask_category

def get_list_of_category():
    """Возвращает список категорий."""
    return list(load_categories().keys())
