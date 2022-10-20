import json


data = {"еда": ["еда", "хлеб", "вода", "фрукты", "овощи"],
        "кафе": ["кафе", "шаурма", "мейхане", "бургер", "роллы", "пицца", "суши"],
        "алкоголь": ["алкоголь", "пиво", "к пиву"],
        "сладкое": ["сладкое", "торт", "печенье", "сладости", "мороженное"],
        "бензин": ["бензин"],
        "бытовая химия": ["бытовая химия", "б/х", "мыло", "шампунь"],
        "разное": []
        }
# with open("categories.json", "w", encoding="utf-8") as categ:
#     json.dump(data, categ, indent=2)


cake = "мусор"

def search_in_json(input_text):
    with open("categories.json", "r", encoding="utf-8") as categ_data:
        data_from_json = json.load(categ_data)
    for i in data_from_json:
            if cake in (data_from_json[i]):
                print(f"расход {cake} добавлен в {i}")
                break


