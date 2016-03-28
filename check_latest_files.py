#!/usr/bin/python

import os
import sys
import datetime
import time
import argparse

parser = argparse.ArgumentParser(prog='check_latest_files', description='Verifica cuando fue la ultima creacion de un archivo', 
    epilog='Uso: check_latest_files --path "c:\windows" --seconds 300')

parser.add_argument('--path', dest='path', help='Ruta al directorio. Ej: [/var/log (linux)| c:\my app\ (windows)]', required=True, type=str)
parser.add_argument('--seconds', dest='seconds', help='Cantidad de segundos permitidos para la creacion del ultimo archivo', required=False, type=int, default=300)
parser.add_argument('-d', dest='debug', help='Habilita el modo debug', action='store_true', required=False)
parser.add_argument('--snmp', dest='snmp', help='Retorna un valor para ser leido por snmp. No envia alertas por mail', action='store_true', required=False)

args = parser.parse_args()

try:
	if os.path.isdir(args.path):
		for filename in os.listdir(args.path):
			full_path = args.path + '/' + filename if os.name=="posix" else args.path + '\\' + filename
			ctime = os.stat(full_path).st_ctime # file creation time format timestamp 1457381538.0
			file_creation_time = datetime.datetime.fromtimestamp(int(ctime)).strftime('%Y-%m-%d %H:%M:%S') # format %Y-%m-%d %H:%M:%S
			today_in_timestamp = time.time() 
			timedelta = datetime.datetime.fromtimestamp(time.time()) - datetime.datetime.fromtimestamp(int(ctime))

			# debug mode ON
			if args.debug and not args.snmp:
				print "ctime: %s" %ctime
				print "full_path: %s" %full_path
				print "filename: %s" %filename
				print "file creation time: %s" %file_creation_time
				print "now(): %s" %datetime.datetime.now()
				print "time.time(): %s" %time.time()
				print "from timestamp obj: %s" %datetime.datetime.fromtimestamp(int(ctime))
				print "timedelta: %s" %timedelta
				print "timedelta seconds: %s" %timedelta.seconds
				print "timedelta minutes: %s" %(timedelta.seconds/60)
				print "*"*200

			# alert if the time was exceeded
			if timedelta.seconds>args.seconds:
				if args.debug and not args.snmp:
					print "%s exceeded time of [%s] seconds with total of [%s] seconds" %(filename,args.seconds,timedelta.seconds)

				# if snmp return 1 condition match
				if args.snmp:
					print 1
					sys.exit(0)

				# send an alert by email
				if not args.snmp:
					print "aca deberia mandar un mail"


		# return 0 condition unmatch
		if args.snmp:
			print 0
			sys.exit(0)

except Exception as e:
	print e
	pass