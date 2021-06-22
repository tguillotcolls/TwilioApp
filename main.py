import os
import time
from datetime import datetime
import requests
import json
from twilio.rest import Client
import cv2
import gtts
from playsound import playsound


def sendMessage(text):
    twilioPhone = '+13236151943'
    personalPhone = '+34608126348'

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=text,
        from_=twilioPhone,
        to=personalPhone,
    )

def sendImage():
    twilioPhone = '+13236151943'
    personalPhone = '+34608126348'

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body="Incoming image: ",
        from_=twilioPhone,
        media_url=['https://demo.twilio.com/owl.png'],
        to=personalPhone,
    )

def drawRectangle(faceList, img):
    # Draw rectangle around the faces
    for (x, y, w, h) in faceList:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # Display the output
    cv2.imshow('img', img)
    #todo uncomment when using
    cv2.imwrite('faces/' + getTime() + '.jpg', img)


def detectFace():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Read the input image
    img = cv2.imread('capture.jpg')
    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    numF = len(faces)
    if (numF > 0):
        print("Faces detected: ", numF)
        drawRectangle(faces, img)
        logFile.write(getTime() + ", Faces Detected: " + str(numF) + "\n")
        return True
    return False


def readClient():
    webhook_url = 'https://App-Bootcamp-tguillotcolls.twiliobootcamp.repl.co/getClientAnswer'
    response = requests.get(webhook_url)
    text = response.text
    if text != '-':
        print("Client response: " + text)
        return text
    else:
        return None


def scanCamera():
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    cv2.imshow('frame', rgb)
    cv2.imwrite('capture.jpg', frame)
    print("Scanning...")


def getTime():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def speakMessage():
    print("Waiting for client message to read: ")
    msg = readClient()
    while (msg == None):
        time.sleep(1)
        msg = readClient()
        if(msg!=None and msg.lower()=="x"):
            print("Speak message canceled")
            return

    tts = gtts.gTTS(msg)
    audioName = "audio/clientAudio.mp3"
    tts.save(audioName)
    playsound(audioName)
    logFile.write(getTime() + ", Message Spoken: " + msg + "\n")


cap = cv2.VideoCapture(0)
logFile = open("logs/" + getTime() + ".txt", "w")
scanOn = True
time.sleep(5)
programOn=True
while (programOn):
    time.sleep(1)
    if (scanOn):
        scanCamera()
        if (detectFace()):
            sendMessage("Intruder detected at: " + getTime())
            time.sleep(1)
            sendMessage("Options: \n 1: See image \n 2: Broadcast message \n 3: Keep Scanning \n 4: Stop Camera")
            scanOn = False
    else:
        option = readClient()
        if option!=None and option.isnumeric():
            option = int(option)
            if option == 1:
                sendImage()
            elif option == 2:
                sendMessage("Enter message (x to cancel): ")
                speakMessage()
            elif option == 3:
                scanOn = True
            elif option == 4:
                programOn = False
sendMessage("Bye!")
logFile.close()
cap.release()
cv2.destroyAllWindows()

# TODO: allow response of text and read out loud as message to intruder by bot!
# TODO: if they answer yes, send image through sms of detected person!
# TODO: maybe call them and allow their voice to be played, or recorded for th eintruder?
