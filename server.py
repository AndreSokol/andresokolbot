#!/usr/bin/python3
import requests
import random
from time import sleep

from os.path import join, dirname
from dotenv import load_dotenv
from os import environ as ENV

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

url = "https://api.telegram.org/" + ENV['BOT_TOKEN'] + "/"
FILE_URL = "https://api.telegram.org/file/" + ENV['BOT_TOKEN'] + "/"
STUPID_DB_PATH = "updateid.temp"

class Message:
    msgtype = 'text'
    data = ''
    chatid = 0
    firstname = ''
    lastname = ''
    username = ''

    def __init__(self, json_data):
        print(json_data['message'])
        keys = json_data['message'].keys()
        print(keys)
        if 'text' in keys:
            self.msgtype = 'text'
        elif 'photo' in keys:
            self.msgtype = 'photo'
        else:
            self.msgtype = 'unsupported'

        if self.msgtype == 'text':
            self.data = json_data['message']['text']

        if self.msgtype == 'photo':
            self.data = json_data['message']['photo'][0]['file_id']

        self.chatid = json_data['message']['chat']['id']
        self.firstname = json_data['message']['from']['first_name']
        self.lastname = json_data['message']['from']['last_name']
        self.username = json_data['message']['from']['username']
        return

    def __str__(self):
        return self.firstname + " " + self.lastname + "(@" + self.username + "): " + self.data


class Handler:
    last_update_id = 0
    updates = ''
    STUPID_DB = None

    def __init__(self):
        try:
            self.STUPID_DB = open(STUPID_DB_PATH)    
            self.last_update_id = int(self.STUPID_DB.read())
            self.STUPID_DB.close()
        except FileNotFoundError as e:
            print("No file " + STUPID_DB_PATH + " found, creating new one")
        self.STUPID_DB = open(STUPID_DB_PATH, "w")
        print('Bot started')
        return None

    def __del__(self):
        print(self.last_update_id)
        print(self.last_update_id, file=self.STUPID_DB)
        self.STUPID_DB.close()
        print("STUPID DB updated")

    def run(self):
        while True:
            self.check_updates()
            sleep(1)

    def check_updates(self):
        response = requests.get(url + 'getUpdates')
        updates = response.json()

        if len(updates['result']) == 0:
            return

        if updates['result'][-1]['update_id'] != self.last_update_id:
            for up in updates['result']:
                if up['update_id'] <= self.last_update_id:
                    continue
                msg = Message(up)
                print(msg)
                self.last_update_id = updates['result'][-1]['update_id']
                self.handle_msg(msg)
        return

    def send_msg(self, chat, text):
        params = {'chat_id': chat, 'text': text}
        print(text)
        response = requests.post(url + 'sendMessage', data=params)
        return response

    def handle_msg(self, msg):
        if msg.msgtype == 'text':
            if msg.data == '/start':
                self.send_msg(msg.chatid, "Hello " + msg.firstname + "!")
            elif msg.data == '/shutdown' and msg.username == 'AndreSokol':
                self.send_msg(msg.chatid, "Shutting down")
                exit()
            else:
                self.send_msg(msg.chatid, random.choice(["нет", "да"]))
        elif msg.msgtype == 'photo':
            print(url + "getFile?file_id=" + msg.data)
            res = requests.get(url + "getFile?file_id=" + msg.data)
            print(res.json())
            file_path = res.json()['result']['file_path']

            print('\ngetting file...')
            print(FILE_URL + file_path)
            res2 = requests.get(FILE_URL + file_path)
            print(res.content)
        else:
            self.send_msg(msg.chatid, "Come on, its not even a text message!")


def main():
    h = Handler()
    h.run()


if __name__ == '__main__':
    main()
