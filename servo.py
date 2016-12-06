import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import getch
import math
import random
import time
import sys
import atexit

laser_on = False

auto_mode_on = False

jitter_count_max = 3 #How many loops before the jitter direction is reset
jitter_sensitivity = 1 #How intense the jitter is (how far it can wander in a single movement)
jitter_pause_max = 6 #Loops between new jitter direction (how long of a pause between). Random number between 0 and this is taken when jitter direction assigned
jitter_count = 0 #timer used for jitter direction
jitter_pause = 0 #assigned random number from 0 to jitter_pause_max
curr_jitter_angle = 0 #angle used for jitter direction (randomly assigned radian. cos and sin are added to top and bottom servo angles)


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

GPIO.setup(laser_pin, GPIO.OUT)
GPIO.output(laser_pin, GPIO.HIGH if laser_on else GPIO.LOW)

PWM.start(servo_pin_top, 100-(duty_min + duty_span * servo_start_angle_top/180), duty_freq, 1)
PWM.start(servo_pin_bottom, 100-(duty_min + duty_span * servo_start_angle_bottom/180), duty_freq, 1)

for arg in sys.argv:
	print arg
	if arg == "--auto":
		auto_mode_on = True

if auto_mode_on:
	laser_on = True
	GPIO.output(laser_pin, GPIO.HIGH)

def clean_up():
	PWM.stop(servo_pin_top)
	PWM.stop(servo_pin_bottom)
	PWM.cleanup()
	GPIO.cleanup()

atexit.register(clean_up)

while True:

	input = ''
	do_jitter = False

	if auto_mode_on:
		time.sleep(.01)
		do_jitter = True
	else:
		input = getch.getch()

	if input == 'x' or input == 'X':
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
