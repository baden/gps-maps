# -*- coding: utf-8 -*-

import os
import logging
import datamodel
import utils

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch

from datetime import date, timedelta, datetime

SERVER_NAME = os.environ['SERVER_NAME']

jit_lat = 0
jit_long = 0

def SaveGPSPointFromBin(pdata, result):
	def LogError():
		sstr = "==  pdata: "
		for p in pdata:
			sstr += " %02X" % ord(p)
		#sstr += "\nEncode partial data:\n\tdate:%s\n\tLatitude:%f\n\tLongitude:%f\n\tSatelites:%d\n\tSpeed:%f\n\tCource:%f\n\tAltitude:%f" % (datestamp, latitude, longitude, sats, speed, course, altitude)
		logging.error( sstr )
		

	global jit_lat
	global jit_long

	if ord(pdata[0]) != 0xF2:	# ID
		logging.error("\n==\t GPS_PARSE_ERROR: ID != 0xF2")
		return None
	if ord(pdata[1]) != 0x20:
		logging.error("\n==\t GPS_PARSE_ERROR: LENGTH != 0x20")
		return None	# LENGTH

	day = ord(pdata[2])
	month = ord(pdata[3]) & 0x0F
	year = (ord(pdata[3]) & 0xF0)/16 + 2010
	hours = ord(pdata[4])
	minutes = ord(pdata[5])
	seconds = ord(pdata[6])

	"""
	if day<1 or day>31:
		logging.error("\n==\t GPS_PARSE_ERROR: DAY=%d" % day)
		return None	# LENGTH
	if month<1 or month>12:
		logging.error("\n==\t GPS_PARSE_ERROR: MONTH=%d" % month)
		return None	# LENGTH
	if year<2010 or year>2014:
		logging.error("\n==\t GPS_PARSE_ERROR: YEAR=%d" % year)
		return None	# LENGTH
	"""

	try:
		datestamp = datetime(year, month, day, hours, minutes, seconds)
	except ValueError, strerror:
		logging.error("\n==\t GPS_PARSE_ERROR: error datetime (%s)" % strerror)
		LogError()
		return None	# LENGTH

	latitude = float(ord(pdata[7])) + (float(ord(pdata[8])) + float(ord(pdata[9])*100 + ord(pdata[10]))/10000.0)/60.0
	longitude = float(ord(pdata[11])) + (float(ord(pdata[12])) + float(ord(pdata[13])*100 + ord(pdata[14]))/10000.0)/60.0
	if ord(pdata[15]) & 1:
		latitude = - latitude
	if ord(pdata[15]) & 2:
		longitude = - longitude

	sats = ord(pdata[16])

	fix = 1
	speed = (float(ord(pdata[17])) + float(ord(pdata[18])) / 100.0) * 1.852 # Переведем в км/ч

	if ord(pdata[15]) & 4:
		course = float(ord(pdata[19])*2 + 1) + float(ord(pdata[20])) / 100.0
	else:
		course = float(ord(pdata[19])*2) + float(ord(pdata[20])) / 100.0;

	altitude = 0.0	#100.0 * float(ord(pdata[21]) + ord(pdata[22])) / 10.0;

	error = False

	if latitude > 90.0: error = True
	if latitude < -90.0: error = True
	if longitude > 180.0: error = True
	if longitude < -180.0: error = True

	if SERVER_NAME=='localhost':
		#jit_lat = jit_lat + (random.random()-0.5)*0.001
		#jit_long = jit_long + (random.random()-0.5)*0.001
		#latitude = latitude + jit_lat
		#longitude = longitude + jit_long
		pass

	if error:
		logging.error("Corrupt latitude or longitude %f, %f" % (latitude, longitude))
		LogError()
		"""
		sstr = "  pdata: "
		for p in pdata:
			sstr += " %02X" % ord(p)
		sstr += "\nEncode partial data:\n\tdate:%s\n\tLatitude:%f\n\tLongitude:%f\n\tSatelites:%d\n\tSpeed:%f\n\tCource:%f\n\tAltitude:%f" % (datestamp, latitude, longitude, sats, speed, course, altitude)
		logging.error( sstr )
		"""
		return None

	if sats < 3:
		logging.error("No sats.")
		LogError()
		return None

	#in1 = float(self.request.get('in1'))*100.0/65535 
	#in2 = float(self.request.get('in2'))*100.0/65535 
	in1 = 0.0
	in2 = 0.0
	vout = float(ord(pdata[21])) / 10.0;
	vin = float(ord(pdata[22])) / 50.0;

	fsource = ord(pdata[26]);	# Причина фиксации координаты


	#_log += '\n Date: %s' % datestamp.strftime("%d/%m/%Y %H:%M:%S")
	#_log += '\n Latitude: %.5f' % latitude
	#_log += '\n Longitude: %.5f' % longitude
	#_log += '\n Satelits: %d' % sats
	#_log += '\n Speed: %.5f' % speed
	#_log += '\n Course: %.5f' % course
	#_log += '\n Altitude: %.5f' % altitude
	#logging.info('[%s]' % datestamp.strftime("%d/%m/%Y %H:%M:%S"))

	#gpspoint = datamodel.DBGPSPoint()
	#gpspoint = datamodel.DBGPSPoint(key_name = "gps_%s_%s" % (result.user.imei, datestamp.strftime("%Y%m%d%H%M%S")))
	gpspoint = datamodel.DBGPSPoint()
	gpspoint.user = result.user
	gpspoint.date = datestamp
	gpspoint.latitude = latitude
	gpspoint.longitude = longitude
	gpspoint.sats = sats
	gpspoint.fix = fix
	gpspoint.speed = speed
	gpspoint.course = course
	gpspoint.altitude = altitude
	gpspoint.vout = vout
	gpspoint.vin = vin
	gpspoint.in1 = in1
	gpspoint.in2 = in2
	gpspoint.fsource = fsource

	return gpspoint
	#gpspoint.put()

class BinGps(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('OK\r\n')

	def post(self):
		_log = "\n== BINGPS ["
		self.response.headers['Content-Type'] = 'application/octet-stream'
		uimei = self.request.get('imei')
		userdb = utils.GetOrCreateUserByIMEI(uimei)

		sdataid = self.request.get('dataid')
		if sdataid:
			dataid = int(sdataid, 16)
		else:
			dataid = 0

		pdata = self.request.body

		_log += '\n==\tData ID: %d' % dataid

		_log += '\nSaving to backup'
		newbinb = datamodel.DBGPSBinBackup()
		newbinb.user = userdb
		newbinb.dataid = dataid
		newbinb.data = pdata

		crc = ord(pdata[-1])*256 + ord(pdata[-2])
		pdata = pdata[:-2]
		_log += '\n==\tData size: %d' % len(pdata)

		crc2 = 0
		for byte in pdata:
			crc2 = utils.crc(crc2, ord(byte))


		if crc!=crc2:
			_log += '\n==\tWarning! Calculated CRC: 0x%04X but system say CRC: 0x%04X. (Now error ignored.)' % (crc2, crc)
			_log += '\n==\t\tData (HEX):'
			for data in pdata:
				_log += ' %02X' % ord(data)

			newbinb.crcok = False
			newbinb.put()
			logging.info(_log)
			self.response.out.write('BINGPS: CRCERROR\r\n')
			return
		else:
			_log += '\n==\tCRC OK %04X' % crc

		newbinb.crcok = True
		newbinb.put()

		newbin = datamodel.DBGPSBin()
		newbin.user = userdb
		newbin.dataid = dataid
		newbin.data = pdata #db.Text(pdata)
		newbin.put()

		#logging.info("==> Bin data: %s" % repr(pdata))
		#parts = pdata.split('\xFF')
		#logging.info("==> Parts data: %s" % repr(parts))

		_log += '\nSaved to DBGPSBin creating tasque'

		url = "/bingps/parse?dataid=%s&key=%s" % (dataid, newbin.key())
		#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
		countdown=0
		taskqueue.add(url = url, method="GET", countdown=countdown)

		newconfigs = utils.CheckUpdates(userdb)
		if newconfigs:
			self.response.out.write('CONFIGUP\r\n')

		self.response.out.write('BINGPS: OK\r\n')

		logging.info(_log)
		return

		#_log = "\nUrl-fetch redirect: "
		logging.info("\nUrl-fetch redirect: ")
		#url = "http://212.110.139.65/"
		#url = "http://gps-maps.appspot.com/gpstestbin?imei=%s" % uimei
		host = "gps-maps.appspot.com"	#http://gps-maps.appspot.com
		host = "74.125.39.141"	#http://gps-maps.appspot.com
		url = "http://%s/gpstestbin?imei=%s" % (host, uimei)
		#url = "http://localhost/gpstestbin?imei=%s" % uimei
		result = urlfetch.fetch(
			url,
			payload = pdata,
			method = urlfetch.POST,
			headers={'Content-Type': 'application/octet-stream'}
		)
		if result.status_code == 200:
			pass
			logging.info('Url fetch: Ok.')
		else:
			logging.info('Url fetch: Fail.')


class BinGpsParse(webapp.RequestHandler):
	def get(self):
		_log = "\n== BINGPS/PARSE ["

		key = db.Key(self.request.get('key'))
		result = datamodel.DBGPSBin().get(key)
		#result = db.get(key)

		if result:
			dataid = result.dataid
			pdata = result.data
			_log += '\n==\tDATA ID: %d' % dataid
			_log += '\n==\tDATA LENGHT: %d' % len(pdata)

			if len(pdata) > (32*450):	# было 24*60 (1 минута на самой высокой скорости)
				_log += '\nSPLIT BINDATA BY 10800 bytes (450 points):'
				while len(pdata) > 0:
					newbin = datamodel.DBGPSBin()
					newbin.user = result.user
					newbin.dataid = result.dataid
					newbin.data = pdata[:(32*450)]
					newbin.put()

					_log += '\nSaved to DBGPSBin creating tasque'

					url = "/bingps/parse?dataid=%d&key=%s" % (dataid, newbin.key())
					#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
					countdown=0
					taskqueue.add(url = url, method="GET", countdown=countdown)

					pdata = pdata[(32*450):]

				self.response.out.write('SPLIT TASK\r\n')
				result.delete()
				_log += '\nOriginal data deleted.'
				logging.info(_log)
				return

			_log += '\nParsing...'

			_log += 'spliting...'
			parts = pdata.split('\xFF')
			_log += '%d patrs...' % len(parts)
                        			
			#odata_s = None
			#odata_f = None
			if len(parts[0]) == 0:
				_log += 'pat[0] is == 0 - its ok...'
				del parts[0]

			if len(parts) > 0:
				if len(parts[-1]) != 31:
					_log += 'pat[-1] is cutted - its NOT OK!!!...'
					del parts[-1]

			_log += '%d patrs now...' % len(parts)
			
			position = 0
			points = []
			for part in parts:
				if len(part) == 31:
					_log += '*'
					point = SaveGPSPointFromBin(part, result)
					if point:
						points.append(point)
				else:
					_log += '\npat%d is corrupted' % position
				position = position+1

			_log += '\n==\tSave points: %d\r\n' % len(points)
			"""
			_log += '\nPurge future (break) cut-part...'
			futparts = datamodel.DBGPSBinParts().all().filter('user =', result.user).filter('dataid >=', result.dataid).fetch(10)
			for futpart in futparts:
				_log += '*'
				futpart.delete()

			if odata_s:
				_log += '\nFinding prevoiuse cut-part...'
				prevpart = datamodel.DBGPSBinParts().all().filter('user =', result.user).filter('dataid =', result.dataid-1).get()
				if prevpart:
					_log += 'ok. mergin...'
					part = prevpart.data + odata_s
					if len(part) == 23:
						_log += 'ok.'
						point = SaveGPSPointFromBin(part, result)
						if point:
							points.append(point)
					else:
						_log += 'fail [%d]:' % len(part)
						for data in part:
							_log += ' %02X' % ord(data)
					prevpart.delete()
				else:
					_log += 'fail.'
			if odata_f:
				part2 = datamodel.DBGPSBinParts()
				part2.user = result.user
				part2.dataid = result.dataid
				part2.data = odata_f
				_log += '\nSaving cutting part.'
				part2.put()
			"""


			if len(points) > 0:
				#logging.error("==> IMEI: %s" % result.user.imei)
				if result.user.imei=='353358019726996':
					_log += "Disabled save points. Imitate only.\r\n"
				else:
					db.put(points)		# Сохраним GPS-точки
			else:
				logging.error("points has no data")

			result.delete()
			self.response.out.write('BINGPS/PARSE: OK\r\n')
			_log += '\nData deleted.'
			
			#for name in os.environ.keys():
			#	self.response.out.write("%s = %s\n" % (name, os.environ[name]))
			
		else:
			self.response.out.write('BINGPS/PARSE: NODATA\r\n')


		logging.info(_log)
		pass


application = webapp.WSGIApplication(
	[
	('/bingps/parse.*', BinGpsParse),
	('/bingps.*', BinGps),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
