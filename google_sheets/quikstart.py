import os.path
from datetime import date
from google_sheets import dateandtime
from dotenv import load_dotenv, find_dotenv

from googleapiclient.discovery import build
from google.oauth2 import service_account

load_dotenv(find_dotenv())

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "credentials.json")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
service = build('sheets', 'v4', credentials=credentials)


def previous_amount_from_gs(category_text, specified_date):
    """Возвращает предидущее значение (сумма расода) из ячейки"""
    range_sample = dateandtime.range_prepare(specified_date)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=range_sample,
                                                 majorDimension='ROWS')
    if "values" not in result.execute():
        data_for_new_day(specified_date)
        current_dt = date.today()
        if int(current_dt.day) == 28 and int(current_dt.month) != 12:
            title = dateandtime.month_dict[int(current_dt.month) + 1]
            sheetid = int(current_dt.month) + 1
            create_new_glist(sheetid, title)
    f = result.execute()["values"][0]
    dict_amount_from_gs = {"еда": f[0], "кафе": f[1], "алкоголь": f[2],
                           "сладкое": f[3], "бензин": f[4], "бытовая химия": f[5],
                           "разное": f[6]}
    frd = (int(dict_amount_from_gs[category_text]))
    return frd


def add_into_gs(amount: int, category_text: str, specified_date=None):
    """Записывает новые данные в таблицу"""
    array = {"values": [dateandtime.array_prepare(amount, category_text, specified_date)]}
    range_gs = dateandtime.range_prepare(specified_date)
    response = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                                      range=range_gs,
                                                      valueInputOption="USER_ENTERED",
                                                      body=array)
    return response.execute()


def data_for_new_day(specified_date):
    """заполняет ячейки gs для корректного считывания при первой за день записи расхода"""
    array = {"values": [[0, 0, 0, 0, 0, 0, 0]]}
    range_sample = dateandtime.range_prepare(specified_date)
    service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                           range=range_sample,
                                           valueInputOption="USER_ENTERED",
                                           body=array).execute()
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=range_sample,
                                                 majorDimension='ROWS').execute()
    return result


def create_new_glist(sheetid, title):
    """Шаблон с форматом для создания нового листа"""
    requests = [
        {
            'addSheet': {
                'properties':
                    {
                        "sheetId": sheetid, 'title': title
                    }
            },
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheetid,
                    "startRowIndex": 0,
                    "startColumnIndex": 0,
                    "endColumnIndex": 8,
                    "endRowIndex": 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.1,
                            "green": 0.5,
                            "blue": 0.9,
                            "alpha": 0.2
                        },
                    },
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheetid,
                    "startRowIndex": 0,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1,
                    "endRowIndex": 33,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.1,
                            "green": 0.5,
                            "blue": 0.9,
                            "alpha": 0.2
                        }
                    },
                },
                "fields": "userEnteredFormat.backgroundColor",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheetid,
                    "startRowIndex": 1,
                    "startColumnIndex": 1,
                    "endColumnIndex": 8,
                    "endRowIndex": 33,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.9,
                            "green": 0.9,
                            "blue": 0.1,
                            "alpha": 0.2
                        },
                    },
                },
                "fields": "userEnteredFormat"
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheetid,
                    "startRowIndex": 32,
                    "startColumnIndex": 0,
                    "endColumnIndex": 8,
                    "endRowIndex": 33,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.1,
                            "green": 0.5,
                            "blue": 0.9,
                            "alpha": 0.2
                        },
                    },
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        }]
    body1 = {'requests': requests}
    body2 = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"{title}!B1:H1",
             "majorDimension": "ROWS",
             "values": [['еда', 'кафе', 'алкоголь', 'сладкое', 'бензин', 'бытовая химия', 'разное']]},
            {"range": f"{title}!A2:A33",
             "majorDimension": "COLUMNS",
             "values": [[i for i in range(1, 31)]]},
            {"range": f"{title}!B33:H33",
             "majorDimension": "ROWS",
             "values": [['=sum(B2:B32)',
                         '=sum(C2:C32)', '=sum(D2:D32)',
                         '=sum(E2:E32)', '=sum(F2:F32)',
                         '=sum(G2:G32)', '=sum(H2:H32)']]},
            {"range": f"{title}!B34:C34",
             "majorDimension": "ROWS",
             "values": [['=AVERAGE(B2:B32)', '=AVERAGE(C2:C32)']]},
            {"range": f"{title}!B35:C35",
             "majorDimension": "ROWS",
             "values": [['=sum(B2:C32)']]}
        ]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body1).execute()
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=body2).execute()
    pass

