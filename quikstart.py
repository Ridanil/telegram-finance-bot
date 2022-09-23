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
RANGE_NAME = 'Лист1'

service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()


def previous_amount_from_gs(category_text):
        range_sample = dateandtime.range_prepare()
        result = service.get(spreadsheetId=SPREADSHEET_ID,
                            range=range_sample,
                            majorDimension='ROWS').execute()
        try:
                f=result["values"][0]
        else:
                f=result.__setitem__("values", ['','','',''])
        dict_amount_from_gs = {"еда":f[0],"бензин":f[1],"б/х":f[2],"разное":f[3]}
        if dict_amount_from_gs[category_text]=='':
                frd = 0
        else:
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



