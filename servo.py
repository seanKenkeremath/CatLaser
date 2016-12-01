import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import getch

laser_on = False

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

while True:
	input = getch.getch()
	if input == 'x' or input == 'X':
		PWM.stop(servo_pin_top)
		PWM.stop(servo_pin_bottom)
		PWM.cleanup()
		GPIO.cleanup()
		break
	else:
		if input == ' ':
			laser_on = not laser_on
			GPIO.output(laser_pin, GPIO.HIGH if laser_on else GPIO.LOW)
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
		else:
			continue

		if angle_top > 180:
			angle_top = 180
		if angle_top < 0:
			angle_top = 0

		if angle_bottom > 90:
			angle_bottom = 90
		if angle_bottom < 0:
			angle_bottom = 0

		print "angle top: " + str(angle_top)
		print "angle bottom: " + str(angle_bottom)		

		angle_top_f = float(angle_top)
		duty_top = 100 - ((angle_top_f/180) * duty_span + duty_min)

		angle_bottom_f = float(angle_bottom)
		duty_bottom = 100 - ((angle_bottom_f/180) * duty_span + duty_min)
		
		PWM.set_duty_cycle(servo_pin_top, duty_top)
		PWM.set_duty_cycle(servo_pin_bottom, duty_bottom)
