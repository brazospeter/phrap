import gspread
from google.oauth2.service_account import Credentials
from loguru import logger

try:
    from ..config import HEADER, BODY
except:
    HEADER = "A1"
    BODY = "A2"

import time
import traceback

scope = ["https://www.googleapis.com/auth/spreadsheets", 
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file("creds.json", scopes=scope)
client = gspread.authorize(creds)

class Sheet:
    def __init__(self, file_name, tab_name):
        spreadsheet = client.open_by_url(file_name)
        self.sheet = spreadsheet.worksheet(tab_name)

    def get_data(self):
        data = self.sheet.get_all_records()
        return data
    
    def write_data(self, coordinate = "A1", data = None):
        self.sheet.update(coordinate, data)

    def write_dict(self, dict: dict, t_key: str, n_digits: int = None):
        header = []
        body = []

        t_list = None
        for k, v in dict.items():
            if k == t_key:
                t_list = v
                header.insert(0, k)
            else:
                header.append(k)

        if t_list is not None:
            for i in range(len(t_list)):
                row = [t_list[i]]
                for k, v in dict.items():
                    if k != t_key:
                        try:
                            if n_digits:
                                row.append(round(v[i], n_digits))
                            else:
                                row.append(float(v[i]))
                        except:
                            row.append(str(v[i]))
                body.append(row)
            self.sheet.update(range_name = HEADER, values = [header])
            self.sheet.update(range_name = BODY, values = body)
        else:
            logger.error("t_key was not found!")

    def poll(self, fun = None, status_sheet: Sheet = None, button_coord: str = None, end_coord: str = None):
        record_status(status_sheet, True, False, False, bool(button_coord))
        current_data = self.get_data()

        running = True
        button_value = False
        while running:
            try:
                if button_coord:
                    if self.sheet.acell(button_coord).value == "TRUE":
                        button_value = True
                else:
                    button_value = current_data != self.get_data()
                if button_value:
                    button_value = False
                    logger.info("Poll triggered. Running the connected function.")
                    record_status(status_sheet, True, True, False)
                    if fun is not None:
                        fun(self.get_data())
                    record_status(status_sheet, True, False, False, bool(button_coord))
                else:
                    time.sleep(2)
                if self.sheet.acell(end_coord).value == "TRUE":
                    running = False
                current_data = self.get_data()
            except:
                logger.critical("Polling failed.")
                logger.critical(traceback.format_exc())
                try:
                    record_status(status_sheet, True, False, True)
                except:
                    logger.critical("Recording status failed.")
                    logger.critical(traceback.format_exc())
                time.sleep(5)

        try:
            record_status(status_sheet, False, False, False)
        except:
            logger.critical("Recording status failed.")
            logger.critical(traceback.format_exc())

def record_status(sheet: Sheet = None, is_polling: bool = False, is_fun: bool = False, is_error: bool = False, has_button: bool = None):
    if sheet:
        if has_button:
            sheet.write_data(coordinate = HEADER, data = [["Polling", "Busy", "Error", "Start Button"]])
            sheet.write_data(coordinate = BODY, data = [[is_polling, is_fun, is_error, False]])
        else:
            sheet.write_data(coordinate = HEADER, data = [["Polling", "Busy", "Error"]])
            sheet.write_data(coordinate = BODY, data = [[is_polling, is_fun, is_error]])