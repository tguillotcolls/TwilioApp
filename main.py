import os
from datetime import datetime
import requests
from twilio.rest import Client
import cv2
import gtts
from playsound import playsound
import vlc
import time

# Send sms message to client
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

# Sends image to client (at the moment its an owl)
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

# From an image, draws a rectangle around the detected face
def drawRectangle(faceList, img):
    # Draw rectangle around the faces
    for (x, y, w, h) in faceList:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # TODO uncomment when using
    # Saves all the framed detected faces
    # cv2.imwrite('faces/' + getTime() + '.jpg', img)

# From image determines if there is a face present
def detectFace():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Read the input image
    img = cv2.imread('capture.jpg')
    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    numF = len(faces)
    # Actions when face is detected, log, and draw rectangle around face
    if (numF > 0):
        print("Faces detected: ", numF)
        drawRectangle(faces, img)
        logFile.write(getTime() + ", Faces Detected: " + str(numF) + "\n")
        return True
    return False

# Collects text written by client
def readClient():
    webhook_url = 'https://App-Bootcamp-tguillotcolls.twiliobootcamp.repl.co/getClientAnswer'
    response = requests.get(webhook_url)
    text = response.text
    if text != '-':
        print("Client response: " + text)
        return text
    else:
        return None

# GET recording petition to server and play it
def playRecording():
    webhook_url = 'https://App-Bootcamp-tguillotcolls.twiliobootcamp.repl.co/getRecordingDone'
    response = requests.get(webhook_url)
    text = response.text
    # Checks if response is empty or is audio url
    if text != '-':
        print("Playing real audio")
        # Obtains the audio file from the url provided
        audioResponse = requests.get(text)
        # Writes file into playable format
        with open('audio/clientAudioREAL.mp3', 'wb') as f:
            f.write(audioResponse.content)
        f.close()
        # Plays audio through speakers
        p = vlc.MediaPlayer("audio/clientAudioREAL.mp3")
        p.play()
        logFile.write(getTime() + ", Voice Recording Played \n")
        return True
    else:
        return False

# Uses MAC front camera to take picture and save it to capture.jpg file
def scanCamera():
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    cv2.imshow('frame', rgb)
    cv2.imwrite('capture.jpg', frame)
    print("Scanning...")

# Returns current time without miliseconds
def getTime():
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Checks if client has answered text and if so text-to-speech plays it
def speakMessage():
    print("Waiting for client message to read: ")
    msg = readClient()
    while (msg == None):
        time.sleep(1)
        msg = readClient()
        # Cancels text-to-speech
        if (msg != None and msg.lower() == "x"):
            print("Speak message canceled")
            return
    # Converts text to an audio file
    tts = gtts.gTTS(msg)
    audioName = "audio/clientAudio.mp3"
    tts.save(audioName)
    # Plays audio file through speaker
    playsound(audioName)
    logFile.write(getTime() + ", Message Spoken: " + msg + "\n")

# Calls client and prompts for voicemail message
def call():
    print("Calling!")
    twilioPhone = '+13236151943'
    personalPhone = '+34608126348'
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    phoneAnswer = 'https://App-Bootcamp-tguillotcolls.twiliobootcamp.repl.co/incomingCallMessage'
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        # url='http://demo.twilio.com/docs/voice.xml',
        url=phoneAnswer,
        from_=twilioPhone,
        to=personalPhone,
    )
    # Checks if call recording is available, if available plays recording and exits loop
    while not playRecording():
        print("Waiting for recording...")
        time.sleep(1)


# https://replit.com/@twiliobootcamp/App-Bootcamp-tguillotcolls#main.py EXECUTE THIS (twilio phone server)

cap = cv2.VideoCapture(0)
logFile = open("logs/" + getTime() + ".txt", "w")
scanOn = True
time.sleep(1)
programOn = True
# Main App thread
while programOn:
    time.sleep(1)
    if scanOn:
        # Takes picture through MAC camera
        scanCamera()
        # Analyzes recent picture taken from MAC camera
        if detectFace():
            # If a face was detected, client is contacted
            sendMessage("Intruder detected at: " + getTime())
            time.sleep(1)
            sendMessage(
                "Options: \n 1: See image \n 2: Text to Voice \n 3: Send voice \n 4: Keep Scanning  \n 5: Stop Camera")
            # Stop scanning until clients response
            scanOn = False
    else:
        # Since a face has been detected, the scan is off, listening for clients response
        option = readClient()
        if option is not None and option.isnumeric():
            option = int(option)
            if option == 1:
                # Sends image taken where face was detected
                sendImage()
            elif option == 2:
                # Asks for text through sms
                sendMessage("Enter message (x to cancel): ")
                # Plays through speakers the text with text-to-speech
                speakMessage()
            elif option == 3:
                # Calls client and record voice that then played through speakers
                call()
            elif option == 4:
                # Resumes scanning
                scanOn = True
            elif option == 5:
                # Stops running program
                programOn = False

sendMessage("Bye!")
logFile.close()
cap.release()
cv2.destroyAllWindows()
