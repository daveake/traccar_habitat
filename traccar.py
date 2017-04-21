import time
import sys
import http.client
import urllib.parse
import urllib.request

# usage: python traccar.py <filename> <IMEI> <chase_id>

filename = sys.argv[1]
IMEI = sys.argv[2]
ChaseCarID = sys.argv[3]

print("Reading file '" + filename + "'")
print("Searching for IMEI '" + IMEI + "'")
print("Uploading as ID '" + ChaseCarID + "'")

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
					temp = fields[9]
					timestamp = temp[0:2] + temp[3:5] + temp[6:8]
					latitude = fields[11][:-1]
					longitude = fields[13][:-1]
					print (temp + " - Vehicle " + ChaseCarID + " located at " + latitude + ',' + longitude)
					
					url = 'http://spacenear.us/tracker/track.php'
					values = {'vehicle' : ChaseCarID,
							 'time'  : timestamp,
							 'lat'  : latitude,
							 'lon'  : longitude,
							 'pass'  : 'aurora'}
					data = urllib.parse.urlencode(values)
					data = data.encode('utf-8') # data should be bytes
					req = urllib.request.Request(url, data)
					with urllib.request.urlopen(req) as response:
						the_page = response.read()
					
					time.sleep(1)
	else:
		print("Waiting ...")
		time.sleep(1)

