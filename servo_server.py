from websocket_server import WebsocketServer
import RPi.GPIO as GPIO
import time
import json 
from io import StringIO
import atexit
import pigpio
import random
import configparser

config = configparser.ConfigParser()
config.read('./connection.ini', 'UTF-8')

# サーバ設定
SERVER_IP = config.get('server','ip')
SERVER_PORT = 3001

servoPIN = 12
MIN_WIDTH=1000
MAX_WIDTH=2000

pi = pigpio.pi()

if not pi.connected:
    exit()

step = random.randrange(5,25)
width = random.randrange(MIN_WIDTH,MAX_WIDTH+1)

def start():
    # クライアントが接続してきた時のイベント
    def new_client(client, server):
        print('New client {}:{} has joined.'.format(client['address'][0], client['address'][1]))
 
    # クライアントが切断した時のイベント
    def client_left(client, server):
        print('Client {}:{} has left.'.format(client['address'][0], client['address'][1]))
 
    # クライアントからのメッセージを受信した時のイベント
    def message_received(client, server, message):
        gain = 1
        sleepTime = 0.1
        global width
        print(message)
        io = StringIO(message)
        message = json.load(io)
        try:
            #1入力あたりの首の回転単位
            gain = message["gain"]
            #クールタイム
            sleepTime = message["sleep_time"]

            message["dir"]
            if(message["dir"] == "positive" and width <  MAX_WIDTH):
                width += step * gain
                pi.set_servo_pulsewidth(servoPIN,width)
            elif(message["dir"] == "negative" and width > MIN_WIDTH):
                width -= step * gain
                pi.set_servo_pulsewidth(servoPIN,width)
            time.sleep(sleepTime)
        except NameError as error:
            print(error)
 
    # サーバーを立ち上げる
    server = WebsocketServer(port=3001, host=SERVER_IP)
    # イベントで使うメソッドの設定
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    # 実行
    server.run_forever()
 
def terminate_server():
    print("\nTidying up")
    pi.set_servo_pulsewidth(12, 0)
    pi.stop()

if __name__ == "__main__":
    atexit.register(terminate_server)
    start()
