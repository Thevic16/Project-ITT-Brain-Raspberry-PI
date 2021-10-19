# Import threading module.
import threading
#Module for API-REST-Request----------------------------------------------------------------
# Import picamara from PiCamara module.
from picamera import PiCamera
# Importing time.
import time
# Importing base64 (encoding and decoding functionality).
import base64
# Import requests to make HTTP requests.
import requests
import json
# Import date class from datetime module.
from datetime import date
# Import the entire datetime module.
from datetime import datetime
#Import geocoder module.
import geocoder
#Import serial module.
import serial
#Import modulo to ensure internet conection
import urllib.request
# Module that helps to send SMS message.
from curses import ascii


#Modules for Speech Recognition ------------------------------------------------------------

# Import Speech Recognition Module.
import speech_recognition as sr



# Set up serialPorts.
serialPortSTM32 = serial.Serial(port="/dev/ttyACM0", baudrate=9600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

serialPortGPRS = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

#Defining fuction to know if there is internet conexion.
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        print("Internet connection")
        return True
    except Exception as E:
        print("No Internet connection")
        return False


# Transmitting AT Commands to the Modem
def test_GPRS_connection():
    serialPortGPRS.write(b'AT\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'ATI\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+GMM\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+COPS?\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+COPS=0\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CFUN?\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CSQ\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CSCS="IRA"\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CSCS?\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CREG?\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CSCA?\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)


def send_GPRS_FallEvent(username,password,photo,latitude,longitude,dataTime,hour):
    serialPortGPRS.write(b'AT+SAPBR=3,1,"Contype","GPRS"\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+SAPBR=3,1,"APN","internet.ideasclaro.com.do"\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+CGREG?\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+SAPBR=1,1\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+SAPBR=2,1\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+HTTPINIT\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+HTTPPARA="CID",1\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+HTTPSSL=0\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+HTTPPARA="URL","http://148.255.64.20:7000/api/FallEvent"\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+HTTPPARA="CONTENT","application/json"\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    serialPortGPRS.write(b'AT+HTTPDATA=10000,10000\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
#     "data:image/jpeg;base64," + photo
    data = {
        "username": username,
        "password": password,
        "photo": "",
        "latitude": latitude,
        "longitude": longitude,
        "dateTime": dataTime,
        "hour": hour
    }
    json_send = json.dumps(data).encode()
    serialPortGPRS.write(json_send+b'')
    time.sleep(11)
    rcv = serialPortGPRS.readall()
    print(rcv)
    time.sleep(5)
    serialPortGPRS.write(b'AT+HTTPACTION=1\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    time.sleep(20)
    serialPortGPRS.write(b'AT+HTTPREAD\r\n')
    rcv = serialPortGPRS.readall()
    print(rcv)
    # time.sleep(5)
    rcv = rcv.decode()
    rcv = rcv[rcv.find('{'):]
    rcv = rcv.replace('\\',"")
    clean_json = rcv[:rcv.index('"\r\n')]
    print(clean_json)
    return clean_json
    
def send_GPRS_SMS(num,username,name,lastname,latitute,longitude):
    time.sleep(5)
    serialPortGPRS.write(b'AT+CMGS="' + num.encode() + b'"\r')
    output = "Se ha detectado una posible caida! \n"+"Informacion del usuario de la silla de ruedas:\n"+"Usuario: "+username+"\n"+"Nombre: "+name+"\n"+"Apellido: "+lastname+"\n"+"Para ver la ubicacion acceda al siguiente enlace:\n"+"https://www.google.com/maps/search/?api=1&query="+str(latitute)+","+str(longitude)+" \n"+"Para mas informacion visitar el sitio web https://telecos.me/ o revisar su correo electronico asociado a la aplicacion."
    #output = "Se ha detectado una posible caida!"
    rcv = serialPortGPRS.readall()
    print(rcv)
    time.sleep(1)
    serialPortGPRS.write(output.encode() + b"\r")
    time.sleep(1)
    serialPortGPRS.write(ascii.ctrl('z').encode())
    time.sleep(1)
    print(serialPortGPRS.readall())
    time.sleep(1)
    print("message to "+num+" have been sent")

# Defining Thread for API REST REQUEST.
def api_rest_request_thread():
    while(True):
        try:
            #If a fall event is receive.
            messageSTM32 = serialPortSTM32.readline()
            #print(messageSTM32)
            if(messageSTM32 == b'Fall Event \n'):
                #PiCamara -----------------------------------------------------------------------------------
                print("Fall Event have been detected. \n")
                
                camera = PiCamera() #Start PiCamara.
                camera.resolution = (460, 340) #setup resolution
                time.sleep(2) # Delay to give time to the module to start.
                camera.capture("/home/pi/Pictures/fallEvent.jpg") #Capture a image and then save it.

                #Base64 encode and decode -------------------------------------------------------------------

                image = open('/home/pi/Pictures/fallEvent.jpg', 'rb') #Open the image from the path saved before.
                image_read = image.read()
                image_64_encode = base64.b64encode(image_read) #Encode the image in bytes in format Base64.
                photo = image_64_encode.decode('ascii') #Decode the image from bytes Base64 to text Base64.
                #print(photo) #check that everything is ok.


                #Preparing to obtain hour.
                dt = datetime.now()

                #Preparing to obtain localization
                myloc = geocoder.ip('me') #Get coordinate base on ip address.

                #Defining parameter Json
                username = "usuariosilla1"
                password = "12345678"
                latitude = myloc.lat
                longitude = myloc.lng
                dataTime = str(date.today())
                hour = dt.strftime("%H:%M")

                #True: There is internet connection, false: There is not
                if connect():
                    # Make HTTP request to the API-REST aplication of the project.
                    response = requests.post('http://148.255.64.20:7000/api/FallEvent', json ={
                            "username": username,
                            "password": password,
                            "photo": "data:image/jpeg;base64,"+photo,
                            "latitude": latitude,
                            "longitude": longitude,
                            "dateTime": dataTime,
                            "hour": hour
                        })

                    dataFromServer = json.loads(response.json()+"")

                    print(dataFromServer)

                    for phoneNumber in dataFromServer["numbers"]:
                       send_GPRS_SMS(phoneNumber, dataFromServer["username"], dataFromServer["name"], dataFromServer["lastname"], 18.47186, -69.89232)
                    
                else:
                    dataFromServer = json.loads(send_GPRS_FallEvent(username, password, photo, 18.47186, -69.89232, dataTime, hour))
                    for phoneNumber in dataFromServer["numbers"]:
                       send_GPRS_SMS(phoneNumber, dataFromServer["username"], dataFromServer["name"], dataFromServer["lastname"], 18.47186, -69.89232)

                
                #Close camara.
                camera.close()
                time.sleep(600) # Delay to avoid over messages to the page.
                
        #Handle errors.
        except Exception as ex:
            print("Error occured trying to do API-REST-Request: \n")
            print(ex)
        

def speech_recognition_thread():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while(1):
            
            # Adjusting parameters.
            print('Speak Anything : ')
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, phrase_time_limit=4)
            
            try:
                # Gettting speech recognition in text format. 
                text = r.recognize_google(audio, language='es-DO')
                text_str = format(text)
                print('You said: '+text_str)

                # Conditions.
                if "Sofía" in text_str and "delante" in text_str:
                    serialPortSTM32.write(b"w \r\n")
                elif "Sofía" in text_str and "derecha" in text_str:
                    serialPortSTM32.write(b"d \r\n")
                elif "Sofía" in text_str and "atrás" in text_str:
                    serialPortSTM32.write(b"s \r\n")
                elif "Sofía" in text_str and "izquierda" in text_str:
                    serialPortSTM32.write(b"a \r\n")

            #Handle errors. 
            except Exception as ex:
                print('Sorry could not hear \n')
                print("Error occured \n")
                print(ex)
            

def main():
    test_GPRS_connection()
        
    thread1 = threading.Thread(target=api_rest_request_thread)
    
    thread2 = threading.Thread(target=speech_recognition_thread)
    
    thread1.start()
    thread2.start()
    


if __name__ == "__main__":
    main()
    
        