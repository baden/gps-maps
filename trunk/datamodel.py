# -*- coding: utf-8 -*-


from google.appengine.ext import db

class DBUser(db.Model):
	userid = db.IntegerProperty()			# Unique
	imei = db.StringProperty(multiline=False)	# IMEI
	phone = db.StringProperty(multiline=False)	# Phone number, for example: +380679332332
	password = db.StringProperty(multiline=False)	# User password
	date = db.DateTimeProperty(auto_now_add=True)	# Registration date
	desc = db.StringProperty(multiline=False)	# Описание

class GPSLogs(db.Model):
	user = db.ReferenceProperty(DBUser)
	text = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

class Greeting(db.Model):
	author = db.UserProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

class DBGPSPoint(db.Model):
	user = db.ReferenceProperty(DBUser)
	cdate = db.DateTimeProperty(auto_now_add=True)
	date = db.DateTimeProperty()
	latitude = db.FloatProperty()
	longitude = db.FloatProperty()
	sats = db.IntegerProperty()
	fix = db.IntegerProperty()
	speed = db.FloatProperty()
	course = db.FloatProperty()
	altitude = db.FloatProperty()
	in1 = db.FloatProperty()		# Значение на аналоговом входе 1
	in2 = db.FloatProperty()		# Значение на агалоговом входе 2
	#power = db.FloatProperty()		# Уровень заряда батареи (на

class DBGPSPoint2(db.Model):
	user = db.ReferenceProperty(DBUser, name='a')
	cdate = db.DateTimeProperty(auto_now_add=True, name='b')
	date = db.DateTimeProperty(name='c')
	latitude = db.FloatProperty(name='d')
	longitude = db.FloatProperty(name='e')
	sats = db.IntegerProperty(name='f')
	fix = db.IntegerProperty(name='g')
	speed = db.FloatProperty(name='h')
	course = db.FloatProperty(name='i')
	altitude = db.FloatProperty(name='j')
	in1 = db.FloatProperty(name='k')		# Значение на аналоговом входе 1
	in2 = db.FloatProperty(name='l')		# Значение на агалоговом входе 2
	#power = db.FloatProperty()		# Уровень заряда батареи (на


class DBGPSBin(db.Model):
	user = db.ReferenceProperty(DBUser)
	cdate = db.DateTimeProperty(auto_now_add=True)
	dataid = db.IntegerProperty()
	data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)

class DBGPSBinParts(db.Model):
	user = db.ReferenceProperty(DBUser)
	cdate = db.DateTimeProperty(auto_now_add=True)
	dataid = db.IntegerProperty()
	data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)

class DBFirmware(db.Model):
	cdate = db.DateTimeProperty(auto_now_add=True)	# Дата размещения прошивки
	boot = db.BooleanProperty(default=False)	# Устанавливается в True если это образ загрузчика
	hwid = db.IntegerProperty()			# Версия аппаратуры
	swid = db.IntegerProperty()			# Версия прошивки
	data = db.BlobProperty()			# Образ прошивки
	size = db.IntegerProperty()			# Размер прошивки (опция)
	desc = db.StringProperty(multiline=True)	# Описание прошивки (опция)

# Конфигурация систем
# Содержит динамически наполняемым контентом
class DBConfig(db.Model):
	cdate = db.DateTimeProperty(auto_now_add=True)	# Дата размещения конфигурации
	user = db.ReferenceProperty(DBUser)
	config = db.BlobProperty()
	#strconfig = db.StringProperty()

class DBNewConfig(db.Model):
	cdate = db.DateTimeProperty(auto_now_add=True)	# Дата размещения конфигурации
	user = db.ReferenceProperty(DBUser)
	config = db.BlobProperty()
	#strconfig = db.StringProperty()


class DBDescription(db.Model):
	name = db.StringProperty(multiline=False)	# имя параметра
	value = db.StringProperty(multiline=False)	# Текстовое описание
	unit = db.StringProperty(multiline=False)	# Единица измерения
	coef = db.FloatProperty(default=1.0)		# Коэффициент преобразования для человеческого представления
	mini = db.IntegerProperty(default=0)		# Минимальное значение для типа INT
	maxi = db.IntegerProperty(default=32767)	# Максимальное значение для типа INT
