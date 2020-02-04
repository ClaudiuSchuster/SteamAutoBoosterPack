import steam
import re
import requests
import datetime
import time
import os, sys

username = 'your_steam_account'
password = 'your_steam_password'
inventory_id = "Chihang0711"
game_id = ["292030","20920", "105600"]

make_url = 'https://steamcommunity.com//tradingcards/ajaxcreatebooster'
unpack_url = f'https://steamcommunity.com/id/{inventory_id}/ajaxunpackbooster/'
headers = {
    "Referer": "https://steamcommunity.com/tradingcards/boostercreator/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}
account = steam.webauth.WebAuth(username, password)

twofactor_code = input("Please enter steam guard code : ")
account_session = account.login(twofactor_code=twofactor_code)
while True:
    for gi in game_id:
        params = {
            "sessionid" : account.session_id,
            "appid": gi,
            "series": 1,
            "tradability_preference" : 2
        }
        response = account_session.post(make_url, headers=headers, data=params)
        if response.text[2:18]!='purchase_eresult':
            print(f"Puchase booster pack SUCCESS on game : {gi}")
            item_id = re.search(r'"communityitemid":"([^"]+)"', response.text).group(1)
            params = {
                "appid": gi,
                "communityitemid": item_id,
                "sessionid" : account.session_id
            }
            account_session.post(unpack_url, headers=headers, data=params)
        else:
            print(f"Puchase booster pack FAILED on game : {gi}")
            
    print("Current time :",str(datetime.datetime.now())[:19])
    time.sleep(60*60*24+60*5) #Retry after 24hours and 5minutes




