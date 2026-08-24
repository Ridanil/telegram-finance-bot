from gigachat import GigaChat
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any
from gigachat.models import Chat, Messages, MessagesRole
import logging
import json
import os

load_dotenv(find_dotenv())

GIGACHAT_MODEL = os.getenv('GIGACHAT_MODEL')
GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')


class GigaChatProcessor:
    """Обработчик чеков с использованием GigaChat"""

    def __init__(self):
        self.client = GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            scope="GIGACHAT_API_PERS",
            model=GIGACHAT_MODEL,
            verify_ssl_certs=False  # Для тестирования
        )

    async def categorize_items(self, items: List[Dict]) -> List[Dict]:
        """Категоризация товаров через GigaChat"""
        if not items:
            return items

        # Формируем промпт
        prompt = self._build_prompt(items)

        try:
            # Запрос к GigaChat
            response = self.client.chat(
                Chat(
                    messages=[
                        Messages(
                            role=MessagesRole.SYSTEM,
                            content="Ты - AI ассистент для категоризации товаров. Отвечай только в формате JSON."
                        ),
                        Messages(
                            role=MessagesRole.USER,
                            content=prompt
                        )
                    ],
                    temperature=0.1,
                    max_tokens=1000,
                )
            )

            # Парсим ответ
            result = json.loads(response.choices[0].message.content)

            # Применяем категории
            for idx, item in enumerate(items):
                if idx < len(result.get('items', [])):
                    item['category'] = result['items'][idx].get('category')
                    item['clean_name'] = result['items'][idx].get('clean_name', item['name'])  # Сохраняем очищенное название
                    item['is_food'] = result['items'][idx].get('is_food', False)
                    item['is_alcohol'] = result['items'][idx].get('is_alcohol', False)
                    item['is_essential'] = result['items'][idx].get('is_essential', False)
            return items

        except Exception as e:
            logging.error(f"GigaChat error: {e}")
            return items

    def _build_prompt(self, items: List[Dict]) -> str:
        """Строит промпт для GigaChat"""
        items_list = []
        for idx, item in enumerate(items):
            items_list.append(f"{idx + 1}. {item['name']}")

        return f"""
Ты - эксперт по категоризации товаров. Категоризируй следующие товары из чека:

{chr(10).join(items_list)}

ПРАВИЛА КАТЕГОРИЗАЦИИ:
1. Еда (is_food=true): продукты питания, овощи, фрукты, мясо, рыба, крупы, макароны, хлеб, снеки, чипсы
2. Сладости (is_food=false): соки, газировка, печенье, кондитерские изделия,
3. Хозяйственные товары: перчатки, губки, средства для уборки, туалетная бумага, салфетки
4. Канцелярские товары: тетради, ручки, карандаши, ластики, бумага
5. Бытовая химия: стиральные порошки, моющие средства, мыло, шампуни, зубные пасты
6. Другое: пакеты,

ОСОБЫЕ ПРАВИЛА:
- Чипсы, снеки, орехи, семечки → Еда (is_food=true)
- Туалетная бумага, салфетки → Хозяйственные товары (is_food=false)
- Перчатки хозяйственные → Хозяйственные товары (is_food=false)
- Алкогольное пиво → Напитки (is_food=true, is_alcohol=true)
- Безалкогольное пиво → Напитки (is_food=true, is_alcohol=false)
- Вода → Напитки (is_food=true, is_alcohol=false)
- Тетради, блокноты → Канцелярские товары (is_food=false)

Для is_essential (товары первой необходимости) указывай true для: еды, воды, товаров гигиены, бытовой химии.

ОЧИСТКА НАЗВАНИЙ:
Убирай лишнюю информацию: бренды, артикулы, размеры упаковок. Оставляй только название товара.
Примеры:
- "BAR.Изд.мак.SPAGHETTI в/с 1000г" → "Спагетти"
- "ЩЕД.ГОД Рис кр/зерн.шлиф.900г" → "Рис"
- "TAFO Бумага DEL.т.т/п.3сл 8рул" → "Туалетная бумага"

Ответ строго в формате JSON:
{{
    "items": [
        {{
            "category": "Категория", 
            "clean_name": "Очищенное название",
            "is_food": true/false, 
            "is_alcohol": true/false, 
            "is_essential": true/false
        }}
    ]
}}
"""

