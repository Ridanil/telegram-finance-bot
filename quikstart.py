import os.path

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


# result = sheet.get(spreadsheetId=SPREADSHEET_ID,
#                     range=RANGE_NAME,
#                     majorDimension='COLUMNS').execute()
#
# data_from_sheet = result.get('values', [])
# print(data_from_sheet)

range_ = "Лист1!A3:B4"
array = {"values": [[5, 5], [5, 5]]}
response = service.update(spreadsheetId=SPREADSHEET_ID,
                            range=range_,
                            valueInputOption="USER_ENTERED",
                            body=array).execute()



