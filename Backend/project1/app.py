# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify,request
from flask_socketio import SocketIO
from flask_cors import CORS
from helpers.MCP3008 import MCP
from helpers.HX711 import HX711
from subprocess import check_output
from RPi import GPIO
from helpers.Ultrasoon import ultrasoon
from helpers.Servo import servo
import time
import threading
from datetime import datetime
import lcddriver

SPICLK=11
SPIMISO=9
SPIMOSI=10
SPICS=8
watersens_ch=0
servopin=21
trigger=20
echo=16
pomp=18

waterbak=HX711(17,27) 
voederbak=HX711(13,19)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pomp,GPIO.OUT)
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(servopin, GPIO.OUT)
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
serv=servo()
endpoint="/dog-o-matic/api/v1/"

def return_ip():
    # get ip
    ips = check_output(['hostname', '--all-ip-addresses'])
    ips = str(ips)
    ip = ips.strip("b'").split(" ")
    return ip[1]

def waterpomp(pomp):
    GPIO.output(pomp,GPIO.HIGH)
    time.sleep(10)
    GPIO.output(pomp,GPIO.LOW)
# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."
# API ENDPOINTS
@app.route(endpoint+"sensoren",methods=['GET'])
def read_sensoren():
    if(request.method=='GET'):
        output=DataRepository.read_sens()
        return jsonify(sensoren=output),200

@app.route(endpoint+"sensoren/<sensorid>",methods=['GET'])
def watersensor_data(sensorid):
    if(request.method=='GET'):
        output=DataRepository.read_data_sens(sensorid)
        return jsonify(data=output),200

@app.route(endpoint+"data",methods=['GET'])
def all_data():
    if(request.method=='GET'):
        output=DataRepository.read_all_data()
        return jsonify(data=output),200
# SOCKET IO
@socketio.on('connect')
def connection():
    print('A new client connect')
    # # Send to the client!
@socketio.on('F2B_schakelen')
def schakelmethode():
    print("boe")
    serv.servobewegen(servopin)
    time.sleep(60)
    print("pomp start")
    waterpomp(pomp)
def loop(): 
    try:
        print("code started:")
        mcp=MCP() 
        ultra=ultrasoon()
        display = lcddriver.lcd()
        #8491376.25
        #-223.1304347826087
        #voeder
        #8530706.625
        #-213.04347826086956
        waterbak.set_offset(8491376.25)
        waterbak.set_scale(-223.1304347826087)
        voederbak.set_offset(8530706.625)
        voederbak.set_scale(-213.04347826086956)
        waterbak.tare()
        voederbak.tare()
        while True:
           waarde=mcp.readadc(watersens_ch,SPICLK,SPIMOSI,SPIMISO,SPICS)
           waarde2 = ultra.distance(trigger,echo)
           waardevoedsel=voederbak.get_grams()
           waardewater=waterbak.get_grams()
           if waarde == 0:
                print("no water\n")
           elif waarde>0 and waarde<30 :
                print("it is raindrop\n")
           elif waarde>=30 and waarde<200 :
                print("it is water flow")
           print("waarde= " +str(waarde)+"\n")
           print("water level:"+str("%.1f"%(waarde/200.*100))+"%\n")
           print(waardevoedsel)
           print(waardewater)
           print(waarde)
           display.lcd_display_string(return_ip(),1)
           display.lcd_display_string("F:"+"%.2f" %waardevoedsel+" W:"+"%.2f" % waardewater,2)
           print ("de afstand is: %.2f cm" % waarde2)
           DataRepository.update_sens_read(3,waarde)
           DataRepository.update_sens_read(4,waarde2)
           if waardevoedsel <=10:
                DataRepository.update_sens_read(1,"Plaats voederbak terug")
           else:
                DataRepository.update_sens_read(1,waardevoedsel)
           if waardewater <= 10:
                DataRepository.update_sens_read(2,"Plaats waterbak terug")
           else:
                DataRepository.update_sens_read(2,waardewater)
           if datetime.now().strftime("%H:%M") == "17:30":
                serv.servobewegen(servopin)
           elif datetime.now().strftime("%H:%M") == "17:31":
                waterpomp(pomp)
           time.sleep(10)
    except KeyboardInterrupt as e:
        print(e)
    finally:
        GPIO.cleanup()

threading.Timer(10,loop).start()
if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
