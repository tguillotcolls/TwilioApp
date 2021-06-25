# This was tested running in replit

from flask import Flask, request

clientMessage="-"
recordingReady="-"
app = Flask('bootcamp')


@app.route('/getClientAnswer', methods=['GET', 'POST'])
def getClientAnswer():
  global clientMessage
  buffer = clientMessage
  clientMessage="-"
  return buffer

@app.route('/getRecordingDone', methods=['GET', 'POST'])
def getRecordingDone():
  global recordingReady
  buffer = recordingReady
  recordingReady="-"
  return buffer

@app.route('/clientAnswer', methods=['GET', 'POST'])
def clientAnswer():
  global clientMessage
  clientMessage = request.values['Body']
  return """<?xml version="1.0" encoding="UTF-8"?>
  <Response>
    <Message>Okay!</Message>
  </Response>"""

@app.route('/recordingDone', methods=['GET', 'POST'])
def recordingDone():
  print("recordingDone!!")
  global recordingReady
  recordingReady=request.values["RecordingUrl"]
  return """<?xml version="1.0" encoding="UTF-8"?>
  <Response>
  </Response>"""

@app.route('/incomingCallMessage', methods=['GET', 'POST'])
def incomingCallMessage():
  return """<?xml version="1.0" encoding="UTF-8"?>
  <Response>
    <Say>
        Please leave a message at the beep. 
        Press the star key when finished. 
    </Say>
    <Record 
        action="https://App-Bootcamp-tguillotcolls.twiliobootcamp.repl.co/recordingDone"
        method="GET" 
        maxLength="20"
        finishOnKey="*"
        />
    <Say>I did not receive a recording</Say>
</Response>"""
