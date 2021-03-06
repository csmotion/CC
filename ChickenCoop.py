import RPi.GPIO as GPIO
from time import sleep, time
import datetime
import Temp
import sys
import Email

RELAY_OFF = 1
RELAY_ON = 0

MOTOR_OFF = 0
MOTOR_ON = 1

DIR_OPEN = 0
DIR_CLOSED = 1

DOOR_TIMEOUT = 12

relay_pins = {'socket1':6, 'socket2':13, 'socket3':19, 'socket4':26}
motor_pins = {'dir':22, 'enable':17, 'brake':27}
limit_pins = {'open':24, 'closed':23}

T1_SN = '000006c39295'
T2_SN = '000006c40ed9'

TIME_OPEN = datetime.time(7, 15, 0)
TIME_CLOSE = datetime.time(8, 45, 0)

# INITIALIZE GPIO
#-----------------------------------------------------------------#
GPIO.setwarnings(False)

# choose BCM port numbering
GPIO.setmode(GPIO.BCM)

# setup relay pins
for pin in relay_pins.values():
	GPIO.setup(pin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
	GPIO.output(pin, RELAY_OFF)

# setup motor pins
for pin in motor_pins.values():
	GPIO.setup(pin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
	GPIO.output(pin, MOTOR_OFF)

# setup limit switch pins
for pin in limit_pins.values():
	GPIO.setup(pin, GPIO.IN)

#FUNCTIONS
#-----------------------------------------------------------------#
def testRelays():
	for pin in relay_pins.values():
		print str(pin) + "\n"
		GPIO.output(pin, RELAY_ON)
		sleep(1)
		GPIO.output(pin, RELAY_OFF)
		sleep(1)

def testMotor():
	GPIO.output(motor_pins['dir'], DIR_OPEN)
	GPIO.output(motor_pins['enable'], MOTOR_ON)
	sleep(1)
	GPIO.output(motor_pins['dir'], DIR_CLOSED)
	sleep(1)
	GPIO.output(motor_pins['enable'], MOTOR_OFF)

def testLimits():
	for pin in limit_pins.values():
		state = GPIO.input(pin)
		print "Limit state = " + str(state)

def doorStatus():
	open = not GPIO.input(limit_pins['open'])
	closed = not GPIO.input(limit_pins['closed'])

	if (open==True) and (closed==True):
		return 'fault'
	elif (open==True):
		return 'open'
	elif (closed==True):
		return 'closed'
	else: 
		return 'unknown'

def openDoor():
	if (doorStatus() != 'open'):
		GPIO.output(motor_pins['dir'], DIR_OPEN)
		GPIO.output(motor_pins['enable'], MOTOR_ON)
		
		elapsed = 0
		start = time()
		while((doorStatus() != 'open') and elapsed < DOOR_TIMEOUT):
			elapsed = time() - start
			pass
		GPIO.output(motor_pins['enable'], MOTOR_OFF)
		return doorStatus()

def closeDoor():
	if (doorStatus() != 'closed'):
		GPIO.output(motor_pins['dir'], DIR_CLOSED)
		GPIO.output(motor_pins['enable'], MOTOR_ON)

		elapsed = 0
		start = time()
		while((doorStatus() != 'closed') and elapsed < DOOR_TIMEOUT):
			elapsed = time() - start
			pass
		GPIO.output(motor_pins['enable'], MOTOR_OFF)
		return doorStatus()

def checkTime():
	time_curr = datetime.datetime.time(datetime.datetime.now())
	#print time_curr

	if TIME_OPEN <= TIME_CLOSE:
		return TIME_OPEN <= time_curr <= TIME_CLOSE
	else:
		return TIME_OPEN <= time_curr or time_curr <= TIME_CLOSE

def updateCoop():
	if(checkTime()):
		if(openDoor() != 'open'):
			Email.sendMessage('ChickenCoop','FAULT - DOOR OPEN')
	else:
		if(closeDoor() != 'closed'):
			Email.sendMessage('ChickenCoop','FAULT - DOOR CLOSED')


#-----------------------------------------------------------------#
if __name__ == "__main__":
	if(len(sys.argv)>1):
		if(sys.argv[1] == 'updateCoop'):
			print 'updating Coop...'
			updateCoop()
		
		if(sys.argv[1] == 'test'):
			testRelays()
			
			#testMotor()
			
			print doorStatus()
			
			print openDoor()
			sleep(1)
			print closeDoor()

