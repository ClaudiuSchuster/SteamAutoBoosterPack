print("Program started...")

import os, sys
import configparser
import json
import re
import steam
import steamfront
import datetime
import time
import urllib

from PyQt5.QtWidgets import (
        QMainWindow, QApplication, QInputDialog, QLineEdit, QMessageBox, QCheckBox, QGroupBox, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from UI import Ui_MainWindow
from util import resource_path, print_log



class mainProgram(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)
        self.print_text = print_log(self.status_print)
        print("Loading all Steam games...")
        try:
            data = urllib.request.urlopen(r"http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json").read()
            output = json.loads(data)
            self.steam_apps = {}
            for i in output['applist']['apps']:
                self.steam_apps[i['appid']] = i['name']
        except:
            self.print_text.append("Connection error, can not connect to internect",True,color = "#ff0000")
        # Set default tab to Main
        self.tabWidget.setCurrentIndex(0)
        # Set button connect
        self.save_btn.clicked.connect(self.save_config)
        self.start_btn.clicked.connect(self.start)
        self.remove_btn.clicked.connect(self.remove_apps)
        self.add_btn.clicked.connect(self.add_apps)
        # Load config
        if os.path.exists('config.ini'):
            self.config_found = True
            config = configparser.ConfigParser()
            config.read('config.ini')
            self.username = config['ACCOUNT INFO']['username']
            self.username_text.setText(self.username)
            self.password = config['ACCOUNT INFO']['password']
            self.password_text.setText(self.password)
            self.inventory_id = config['ACCOUNT INFO']['inventory_id']
            self.inventory_id_text.setText(self.inventory_id)
            self.game_id = json.loads(config['APP LIST']['game_id'])
            self.set_texteditor_font()
            self.print_text.append("Load config success!")
            self.set_checkbox_layout(self.game_id,True)
        else:
            self.config_found = False
            self.game_id = []
            self.print_text.append("Config file not detected, please create a new config file.",color = "#ff0000")
        self.print_text.text_out()
    
    def set_checkbox_layout(self,game_id,init=False):
        self.checkbox_groupbox = QGroupBox()
        self.checkbox_vboxlayout = QVBoxLayout()
        self.checkbox_groupbox.setLayout(self.checkbox_vboxlayout)
        self.checkbox_scroll.setWidget(self.checkbox_groupbox)
        self.checkbox_list = []
        for gi in game_id:
            try:
                newQbox = QCheckBox(str(gi)+" : "+self.steam_apps[gi],self)
            except:
                newQbox = QCheckBox(str(gi)+" : UnknownGame",self)
            self.checkbox_list.append(newQbox)
            self.checkbox_vboxlayout.addWidget(newQbox)
        if not init:
            bar = self.checkbox_scroll.verticalScrollBar()
            bar.rangeChanged.connect( lambda x,y: bar.setValue(y) )
        
    def set_texteditor_font(self):
        self.username_text.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.password_text.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.inventory_id_text.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        text_input_font = QFont()
        text_input_font.setPointSize(12)
        text_input_font.setBold(False)
        self.username_text.setFont(text_input_font)
        self.password_text.setFont(text_input_font)
        self.inventory_id_text.setFont(text_input_font)
        
    # Save current config setting to config.ini
    def save_config(self) :
        config = configparser.ConfigParser()
        config['ACCOUNT INFO'] = {'username': self.username_text.toPlainText(),
                                  'password': self.password_text.toPlainText(),
                                  'inventory_id': self.inventory_id_text.toPlainText()}
        config['APP LIST'] = {'game_id':self.game_id}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        QMessageBox.information(self, "Success!", f"Save config file success!")
#        self.config_found = True
        return None
    
    def remove_apps(self):
        pop_index = []
        for j,i in enumerate(self.checkbox_list):
            if i.isChecked():
                pop_index.append(j)
        self.game_id = [i for j, i in enumerate(self.game_id) if j not in pop_index]
        self.set_checkbox_layout(self.game_id)
    
    def add_apps(self):
        new_app_id, okPressed = QInputDialog.getText(self, "Add app","For several apps, seperate with ',':", QLineEdit.Normal, "")
        if okPressed:
            new_app_id = new_app_id.replace(" ","").split(",")
            self.game_id += [int(i) for i in new_app_id if int(i) not in self.game_id]
            self.set_checkbox_layout(self.game_id)
        
    # Start make booster pack
    def start(self):
        def run_thread():
            self.print_text.append("Getting login information...",True)
            self.account = steam.webauth.WebAuth(self.username, self.password)    
            twofactor_code_inp, okPressed = QInputDialog.getText(self, "Mobile Authenticator","Enter steam mobile authenticator:", QLineEdit.Normal, "")
            if okPressed:
                try:
                    self.account_session = self.account.login(twofactor_code=str(twofactor_code_inp))
                    self.print_text.append("Login success!",True)
                except:
                    self.print_text.append("Login failed, please check account info or authenticator code.",True,"#ff0000")
                    return None
                # Set main work
                self.worker = main_worker(self.account, self.print_text, self.account_session, self.inventory_id, self.game_id)
                self.worker.signal.connect(self.print_text.text_out)
                self.worker.start()
                
        if self.config_found:
            run_thread()
        else:
            if os.path.exists('config.ini'):
                config = configparser.ConfigParser()
                config.read('config.ini')
                self.username = config['ACCOUNT INFO']['username']
                self.username_text.setText(self.username)
                self.password = config['ACCOUNT INFO']['password']
                self.password_text.setText(self.password)
                self.inventory_id = config['ACCOUNT INFO']['inventory_id']
                self.inventory_id_text.setText(self.inventory_id)
                self.game_id = json.loads(config['APP LIST']['game_id'])
                self.set_texteditor_font()
                self.print_text.append("Load config success!",True)
                self.set_checkbox_layout(self.game_id,True)
                run_thread()                
            else:
                self.print_text.append("Config file not detected, please create a new config file.",True,color = "#ff0000")
class main_worker(QThread):
    signal = pyqtSignal()
    signal_stop = pyqtSignal()
    def __init__(self, account, print_text, accountSession, inventory_id, game_id):
        QThread.__init__(self)
        self.account = account
        self.print_text = print_text
        self.inventory_id = inventory_id
        self.game_id = game_id
        self.account_session = accountSession
        self.client = steamfront.Client()
        self.make_url = 'https://steamcommunity.com//tradingcards/ajaxcreatebooster'
        self.unpack_url = f'https://steamcommunity.com/id/{self.inventory_id}/ajaxunpackbooster/'
        self.headers = {
            "Referer": "https://steamcommunity.com/tradingcards/boostercreator/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }      
    def run(self):
        while True:
            params = {
                "sessionid" : self.account.session_id,
                "appid": -1,
                "series": 1,
                "tradability_preference" : 1
            }
            response = self.account_session.post(self.make_url, headers=self.headers, data=params)
            goo_amount = int(re.search(r'"goo_amount":"([^"]+)"', response.text).group(1))
            if goo_amount <= 1000:
                self.print_text.append(f"Steam gems stock low({goo_amount}), please re-fill and run again.",False,'#ff0000')
                self.signal.emit()
                return None
            for gi in self.game_id:
                time.sleep(0.1)
                params = {
                    "sessionid" : self.account.session_id,
                    "appid": gi,
                    "series": 1,
                    "tradability_preference" : 1
                }
                response = self.account_session.post(self.make_url, headers=self.headers, data=params)
                if response.text[2:18]!='purchase_eresult':
                    self.print_text.append(f"Puchase booster pack SUCCESS on game : {gi}-{self.client.getApp(appid=gi).name}")
                    item_id = re.search(r'"communityitemid":"([^"]+)"', response.text).group(1)
                    params = {
                        "appid": gi,
                        "communityitemid": item_id,
                        "sessionid" : self.account.session_id
                    }
                    self.account_session.post(self.unpack_url, headers=self.headers, data=params)
                else:
                    try:
                        game_name = self.client.getApp(appid=gi).name
                    except:
                        game_name = "Unknown game"
                    self.print_text.append(f"Purchase booster pack FAILED on game : {gi}-{game_name}")
                self.signal.emit()
            self.print_text.append("Current time : "+str(datetime.datetime.now())[:19])
            self.signal.emit()
            QThread.sleep(60*60*6+60) #Retry after 4 hours and 1 minutes         
     

    
if __name__ == '__main__':  
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('main.ico')))
    main = mainProgram()
    main.show()
    sys.exit(app.exec_())