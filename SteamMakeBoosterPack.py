import steam
import re
import requests
import datetime
import time
import os, sys
import steamfront

username = 'your_steam_account'
password = 'your_steam_password'
inventory_id = "Chihang0711"
game_id = ["292030","20920", "105600"]


client = steamfront.Client()
make_url = 'https://steamcommunity.com//tradingcards/ajaxcreatebooster'
unpack_url = f'https://steamcommunity.com/id/{inventory_id}/ajaxunpackbooster/'
headers = {
    "Referer": "https://steamcommunity.com/tradingcards/boostercreator/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}
account = steam.webauth.WebAuth(username, password)
twofactor_code_inp = input("Please enter steam guard code : ")
account_session = account.login(twofactor_code=twofactor_code_inp)

while True:
    for gi in game_id:
        params = {
            "sessionid" : account.session_id,
            "appid": gi,
            "series": 1,
            "tradability_preference" : 1
        }
        response = account_session.post(make_url, headers=headers, data=params)
        if goo_amount <= 1000:
            print("Steam gems stock low, please re-fill.")
            break
        if response.text[2:18]!='purchase_eresult':
            print(f"Puchase booster pack SUCCESS on game : {client.getApp(appid=gi).name}-{gi}")
            item_id = re.search(r'"communityitemid":"([^"]+)"', response.text).group(1)
            params = {
                "appid": gi,
                "communityitemid": item_id,
                "sessionid" : account.session_id
            }
            account_session.post(unpack_url, headers=headers, data=params)
        else:
            print(f"Puchase booster pack FAILED on game : {client.getApp(appid=gi).name}-{gi}")
            
    print("Current time :",str(datetime.datetime.now())[:19])
    time.sleep(60*60*6+60) #Retry after 4 hours and 1 minutes

