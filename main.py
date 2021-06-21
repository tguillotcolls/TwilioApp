import os
import time
from datetime import datetime

from twilio.rest import Client
import cv2


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
    print(message.sid)

def drawRectangle(faceList, img):
    # Draw rectangle around the faces
    for (x, y, w, h) in faceList:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # Display the output
    cv2.imshow('img', img)
    cv2.imwrite('faces/' + str(datetime.now())+'.jpg', img)

def detectFace():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Read the input image
    img = cv2.imread('capture.jpg')
    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    numF=len(faces)
    if (numF > 0):
        #print("Faces detected: ", numF)
        drawRectangle(faces, img)
        logFile.write(str(datetime.now())+", " +str(numF) +"\n")
        return 1
    return 0


cap = cv2.VideoCapture(0)
now = datetime.now()
logFile=open("logs/"+str(now)+".txt","w")

while (True):
    time.sleep(1)
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    cv2.imshow('frame', rgb)
    out = cv2.imwrite('capture.jpg', frame)
    intruder=detectFace()
    k = cv2.waitKey(1) & 0xFF
    if intruder==1:
        sendMessage("Intruder detected at: " + str (datetime.now()))
        break


logFile.close()
cap.release()
cv2.destroyAllWindows()

#TODO: allow response of text and read out loud as message to intruder by bot!
#TODO: if they answer yes, send image through sms of detected person!
#TODO: maybe call them and allow their voice to be played, or recorded for th eintruder?