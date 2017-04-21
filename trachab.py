import time
import sys
import http.client
import urllib.parse
import urllib.request
import crcmod
import json
from base64 import b64encode
from hashlib import sha256
from datetime import datetime

def crc16_ccitt(data):
    crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
    return hex(crc16(data))[2:].upper().zfill(4)


def UploadTelemetry(Callsign, Sentence):
        sentence_b64 = b64encode(Sentence.encode())

        date = datetime.utcnow().isoformat("T") + "Z"

        data = {"type": "payload_telemetry", "data": {"_raw": sentence_b64.decode()}, "receivers": {Callsign: {"time_created": date, "time_uploaded": date,},},}
        data = json.dumps(data)

        url = "http://habitat.habhub.org/habitat/_design/payload_telemetry/_update/add_listener/%s" % sha256(sentence_b64).hexdigest()
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        try:
                response = urllib.request.urlopen(req, data.encode())
        except Exception as e:
                pass

# usage: python trachab.py <filename> <IMEI> <callsign> <balloon_id>

print("TracCar --> Habitat Balloon Uploader")

filename = sys.argv[1]
IMEI = sys.argv[2]
Callsign = sys.argv[3]
BalloonID = sys.argv[4]

SentenceID = 0

print("Reading file '" + filename + "'")
print("Searching for IMEI '" + IMEI + "'")
print("Uploading with callsign '" + Callsign + "'")
print("Uploading as Payload ID '" + BalloonID + "'")

time.sleep(1)

fp = open(filename, 'r')
print("Skipping to end of file ...")
while fp.readline():
	pass
print("Waiting for new positions in file")
while True:
	line = fp.readline()
	if line:
		# 2017-02-10 09:52:50  INFO: [0A1BEF70] id: 357454072667296, time: 2017-02-10 09:52:25, lat: 53.83371, lon: -1.82213, speed: 3.2, course: 183.0
		fields = line.split(' ')
		# ['2017-02-10', '09:52:50', '', 'INFO:', '[0A1BEF70]', 'id:', '357454072667296,', 'time:', '2017-02-10', '09:52:25,', 'lat:', '53.83371,', 'lon:', '-1.82213,', ' speed:', '3.2,', 'course:', '183.0']
		
		if len(fields) >= 14:
			if fields[3] == 'INFO:':
				ID = fields[6][:-1]
				if ID == IMEI:
					timestamp = fields[9][:-1]
					latitude = fields[11][:-1]
					longitude = fields[13][:-1]
					altitude = '0'
					speed = str(int(float(fields[15][:-1]) * 0.44704))
					course = str(int(float(fields[17][:-1])))
					print (timestamp + " - Vehicle " + BalloonID + " located at " + latitude + ',' + longitude + ', speed ' + speed + ', course ' + course)
					SentenceID += 1 
					Packet = BalloonID + ',' + str(SentenceID) + ',' + timestamp + ',' + latitude + ',' + longitude + ',' + altitude + ',' + speed + ',' + course
					print("Packet = '" + Packet + "'")
					Sentence = '$$' + Packet + '*' + crc16_ccitt(Packet.encode()) + '\n'
					print("Sentence = " + Sentence)
					UploadTelemetry(Callsign, Sentence)
					time.sleep(10)
	else:
		print("Waiting ...")
		time.sleep(5)

