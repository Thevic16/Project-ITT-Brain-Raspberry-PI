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
# Import date class from datetime module.
from datetime import date
# Import the entire datetime module.
from datetime import datetime
#Import geocoder module.
import geocoder
#Import serial module.
import serial


#Modules for Speech Recognition ------------------------------------------------------------

# Import Speech Recognition Module.
import speech_recognition as sr
# Import serial module.


# Set up serialPort.
serialPort = serial.Serial(port="/dev/ttyACM0", baudrate=9600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

# Defining Thread for API REST REQUEST.
def api_rest_request_thread():
    while(True):
        try:
            #If a fall event is receive.
            messageSTM32 = serialPort.readline()
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


                # Make HTTP request to the API-REST aplication of the project. 
                response = requests.post('http://10.0.0.251:7000/api/FallEvent', json ={
                        "username": "usuariosilla1",
                        "photo": "data:image/jpeg;base64,"+photo,
                        "latitude": myloc.lat,
                        "longitude": myloc.lng,
                        "dateTime": str(date.today()),
                        "hour": dt.strftime("%H:%M")
                    })


                print(response.json())
                
                #Close camara.
                camera.close()
                #time.sleep(600) # Delay to avoid over messages to the page.
                
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
                if "Sofía" in text_str and "adelante" in text_str:
                    serialPort.write(b"w \r\n")
                elif "Sofía" in text_str and "derecha" in text_str:
                    serialPort.write(b"d \r\n")
                elif "Sofía" in text_str and "atrás" in text_str:
                    serialPort.write(b"s \r\n")
                elif "Sofía" in text_str and "izquierda" in text_str:
                    serialPort.write(b"a \r\n")

            #Handle errors. 
            except Exception as ex:
                print('Sorry could not hear \n')
                print("Error occured \n")
                print(ex)
            

def main():
    thread1 = threading.Thread(target=api_rest_request_thread)
    
    thread2 = threading.Thread(target=speech_recognition_thread)
    
    thread1.start()
    thread2.start()
    


if __name__ == "__main__":
    main()
    
        