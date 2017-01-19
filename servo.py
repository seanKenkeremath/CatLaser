import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import os
import getch
import math
import random
import time
import sys
import atexit

temp_file = sys.path[0] + "/isrunning.tmp"
laser_on = False

auto_mode_on = False

jitter_count_max = 6 #How many loops before the jitter direction is reset
jitter_sensitivity = .75 #How intense the jitter is (how far it can wander in a single movement)
jitter_pause_max = 6 #Loops between new jitter direction (how long of a pause between). Random number between 0 and this is taken when jitter direction assigned


jitter_count = 0 #timer used for jitter direction
jitter_pause = 0 #assigned random number from 0 to jitter_pause_max
curr_jitter_angle = 0 #angle used for jitter direction (randomly assigned radian. cos and sin are added to top and bottom servo angles)

auto_run_length_seconds = 180 #default amount of time --auto runs for unless time is specified with -t param  
start_time = time.time()
stop_time = 0 #set after parameters are read. start time of execution + run length in seconds

laser_pin = "P8_10"
servo_pin_top = "P8_13"
servo_pin_bottom = "P9_14"

servo_start_angle_top = 90
servo_start_angle_bottom = 45

angle_top = servo_start_angle_top
angle_bottom = servo_start_angle_bottom

duty_freq = 50
duty_min = 5
duty_max = 10
duty_span = duty_max - duty_min


#Create a temporary file before we set up
#tmp file indicates script is running
#Only 1 copy of script should run at a time
if (os.path.exists(temp_file)):
	print "Cat Laser is already running"
	sys.exit()
else:
	print "creating tmp file"
	open(temp_file, 'a')

GPIO.setup(laser_pin, GPIO.OUT)
GPIO.output(laser_pin, GPIO.HIGH if laser_on else GPIO.LOW)

PWM.start(servo_pin_top, 100-(duty_min + duty_span * servo_start_angle_top/180), duty_freq, 1)
PWM.start(servo_pin_bottom, 100-(duty_min + duty_span * servo_start_angle_bottom/180), duty_freq, 1)

i = 0
while i < len(sys.argv):
	arg = sys.argv[i]
	if arg == "--auto":
		auto_mode_on = True
	if arg == "-t":
		auto_run_length_seconds = int(sys.argv[i+1])
		i+=1
	i += 1

if auto_mode_on:
	stop_time = start_time + auto_run_length_seconds
	print "running auto mode for " + str(auto_run_length_seconds) + " seconds until " + str(stop_time)
	laser_on = True
	GPIO.output(laser_pin, GPIO.HIGH)

def clean_up():
	print "Cleaning up"
	PWM.stop(servo_pin_top)
	PWM.stop(servo_pin_bottom)
	PWM.cleanup()
	GPIO.cleanup()
	if os.path.isfile(temp_file):
		os.remove(temp_file)

atexit.register(clean_up)

while True:

	input = ''
	do_jitter = False
	stop = False

	if auto_mode_on:
		if time.time() > start_time + auto_run_length_seconds:
			stop = True
		time.sleep(.01)
		do_jitter = True
	else:
		input = getch.getch()

	if stop or input == 'x' or input == 'X':
		clean_up()
		break;
	else:
		if input == ' ':
			laser_on = not laser_on
			GPIO.output(laser_pin, GPIO.HIGH if laser_on else GPIO.LOW)

		elif input == 'j' or input == 'J':
			do_jitter = True

		elif input == 'd':
			angle_top = angle_top - 3
		elif input == 'a':
			angle_top = angle_top + 3
		elif input == 'D':
			angle_top = angle_top - 1
		elif input == 'A':
			angle_top = angle_top + 1

		elif input == 'w':
			angle_bottom = angle_bottom - 3
		elif input == 's':
			angle_bottom = angle_bottom + 3
		elif input == 'W':
			angle_bottom = angle_bottom - 1
		elif input == 'S':
			angle_bottom = angle_bottom + 1
		elif not do_jitter:
			continue
		
		if do_jitter:
			if jitter_count == 0:
				jitter_pause = random.randint(0, jitter_pause_max) 
				jitter_count = jitter_count_max + jitter_pause
				curr_jitter_angle = random.uniform(0, 2*math.pi)			

			#Pause will happen while counting down from jitter_count_max + jitter_pause
			if jitter_count <= jitter_count_max:
				angle_top += jitter_sensitivity * math.cos(curr_jitter_angle)
				angle_bottom += jitter_sensitivity * math.sin(curr_jitter_angle) 
			jitter_count -= 1

		if angle_top > 180:
			angle_top = 180
		if angle_top < 0:
			angle_top = 0

		if angle_bottom > 90:
			angle_bottom = 90
		if angle_bottom < 0:
			angle_bottom = 0
		

		angle_top_f = float(angle_top)
		duty_top = 100 - ((angle_top_f/180) * duty_span + duty_min)

		angle_bottom_f = float(angle_bottom)
		duty_bottom = 100 - ((angle_bottom_f/180) * duty_span + duty_min)
		
		PWM.set_duty_cycle(servo_pin_top, duty_top)
		PWM.set_duty_cycle(servo_pin_bottom, duty_bottom)
