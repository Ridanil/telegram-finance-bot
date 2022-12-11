class NotCorrectMessage(Exception):
	"""Некорректное сообщение в бот, которое не удалось распаршить"""
	pass

class NoSuchCategory(Exception):
	"""Категория не найдена или введена не верно"""
	pass
