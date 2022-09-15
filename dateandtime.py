from datetime import date
import processing

def range_prepare():
	"Указывае лист и диапазон ячеек в соответствии с текущим днем и месяцем"
	current_dt = date.today()
	month_dict = {1:"Январь",2:"Февраль",3:"Март",4:"Апрель",5:"Май",9:"Сентябрь"}
	list_name = month_dict[int(current_dt.month)]
	collum_name = str(int(current_dt.day)+1)
	range_name = "!B"+collum_name+":F"+collum_name
	range_gs = list_name+range_name
	return range_gs

def array_prepare(amount, category_text):
	#parsed_msg = processing.add_expens(raw_message)
	amnt = amount
	categ_txt = category_text
	categ_dict = {"еда":[amnt, None, None, None],
				"бензин":[None, None, amnt, None],
				"разное":[None, None, None, amnt]}
	array = categ_dict[categ_txt]
	return array
