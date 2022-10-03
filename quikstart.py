import os.path
import dateandtime

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "credentials.json")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SPREADSHEET_ID = '1tevcPXVxUGB9FRbEvltZI6ogmK_7CnELWcClrpKlIZk'
service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()




def previous_amount_from_gs(category_text):
    range_sample = dateandtime.range_prepare()
    result = service.get(spreadsheetId=SPREADSHEET_ID,
                         range=range_sample,
                         majorDimension='ROWS')
    if "values" not in result.execute():
        data_for_new_day()
    f = result.execute()["values"][0]
    dict_amount_from_gs = {"еда": f[0], "кафе": f[1], "алкоголь": f[2],
                           "сладости": f[3], "бензин": f[4], "бх": f[5],
                           "разное": f[6]}
    frd = (int(dict_amount_from_gs[category_text]))
    return frd


def add_into_gs(amount, category_text):
    array = {"values": [dateandtime.array_prepare(amount, category_text)]}
    range_gs = dateandtime.range_prepare()
    response = service.update(spreadsheetId=SPREADSHEET_ID,
                              range=range_gs,
                              valueInputOption="USER_ENTERED",
                              body=array)
    return response.execute()


def data_for_new_day():
    """заполняет ячейки gs для корректного считывания при первой за день записи расхода"""
    array = {"values": [[0, 0, 0, 0, 0, 0, 0]]}
    range_sample = dateandtime.range_prepare()
    service.update(spreadsheetId=SPREADSHEET_ID,
                   range=range_sample,
                   valueInputOption="USER_ENTERED",
                   body=array).execute()
    result = service.get(spreadsheetId=SPREADSHEET_ID,
                         range=range_sample,
                         majorDimension='ROWS').execute()
    return result



