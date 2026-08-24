import aiohttp
from typing import List, Dict

async def fetch_check_from_fns(qr_raw: str, api_token: str) -> dict:
    """
    Отправляет запрос к API proverkacheka.com для получения данных чека
    """
    url = "https://proverkacheka.com/api/v1/check/get"

    # Формируем данные для запроса (формат запроса 2 из документации)
    data = {
        "qrraw": qr_raw,
        "token": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            result = await response.json()
            return result


#def format_check_response(api_response: dict) -> str:
    """
    Форматирует ответ API в читаемый текст для пользователя
    """
    if api_response.get("code") != 1:
        error_messages = {
            0: "❌ Чек некорректен",
            2: "⏳ Данные чека пока не получены, попробуйте позже",
            3: "⚠️ Превышено количество запросов",
            4: "⏱️ Необходимо подождать перед повторным запросом",
            5: "❓ Данные не получены (прочая ошибка)"
        }
        return error_messages.get(api_response.get("code"), f"❌ Ошибка: код {api_response.get('code')}")

    data = api_response.get("data", {})
    json_data = data.get("json", {})

    if not json_data:
        return "❌ Не удалось получить данные чека"

    # Формируем красивый вывод
    lines = [
        "🧾 *ДАННЫЕ ЧЕКА*",
    ]

    # Позиции товаров (все позиции)
    items = json_data.get('items', [])
    if items:
        lines.append("\n📦 *ПОКУПКИ:*")
        for i, item in enumerate(items, 1):  # все позиции без ограничения
            name = item.get('name', '—')
            sum_kop = item.get('sum', 0)
            sum_rub = int(sum_kop) / 100 if sum_kop else 0
            lines.append(f"{i}. {name} — {sum_rub:.2f}₽")

    # Итоговая сумма
    total_sum = int(json_data.get('totalSum', 0)) / 100
    lines.append(f"\n💰 *ИТОГО:* {total_sum:.2f} ₽")

    return "\n".join(lines)


def format_processed_response(items: List[Dict]) -> str:
    """
    Форматирует обработанные товары для вывода пользователю
    """
    if not items:
        return "❌ Нет данных для отображения"

    lines = [
        "🧾 *ОБРАБОТАННЫЙ ЧЕК*",
        "📊 *Категоризация товаров:*\n"
    ]

    # Группируем по категориям
    categories = {}
    for item in items:
        category = item.get('category', 'Другое')
        if category not in categories:
            categories[category] = []
        categories[category].append(item)

    # Выводим по категориям
    for category, category_items in categories.items():
        # Эмодзи для категорий
        emoji_map = {
            'Продукты питания': '🍎',
            'Напитки': '🥤',
            'Хозяйственные товары': '🧹',
            'Канцелярские товары': '✏️',
            'Личная гигиена': '🧴',
            'Бытовая химия': '🧪',
            'Другое': '📦'
        }
        emoji = emoji_map.get(category, '📦')

        lines.append(f"\n{emoji} *{category}:*")
        for item in category_items:
            name = item.get('clean_name', item.get('name', '—'))
            # Добавляем метки
            tags = []
            if item.get('is_food'):
                tags.append('🍽️')
            if item.get('is_alcohol'):
                tags.append('🍷')
            if item.get('is_essential'):
                tags.append('⭐')

            tags_str = ' '.join(tags) if tags else ''
            lines.append(f"  • {name} {tags_str}")

    # Статистика
    total_items = len(items)
    food_items = sum(1 for i in items if i.get('is_food'))
    alcohol_items = sum(1 for i in items if i.get('is_alcohol'))
    essential_items = sum(1 for i in items if i.get('is_essential'))

    lines.extend([
        f"\n📈 *Статистика:*",
        f"• Всего товаров: {total_items}",
        f"• Продукты: {food_items}",
        f"• Алкоголь: {alcohol_items}",
        f"• Товары первой необходимости: {essential_items}"
    ])

    return "\n".join(lines)

