# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time
import sys
import RPi.GPIO as GPIO
import pika
from rmq_params import rmq_params
import pickle
import argparse

# Import the PCA9685 module.
import Adafruit_PCA9685

blind = 'Open'
proj = 'Up'

parser = argparse.ArgumentParser(description='Server')
parser.add_argument('-s', required=True, help='RMQ-IP OR HOSTNAME')
args = parser.parse_args()
HOST = args.s

redPin = 17
greenPin = 22
bluePin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)
GPIO.setup(bluePin, GPIO.OUT)

def blink(pin):
    GPIO.output(pin, GPIO.HIGH)

def turnOff():
    GPIO.output(redPin, GPIO.LOW)
    GPIO.output(greenPin, GPIO.LOW)
    GPIO.output(bluePin, GPIO.LOW)

turnOff()

def redOn():
    blink(redPin)

def greenOn():
    blink(greenPin)

def blueOn():
    blink(bluePin)
#
VHOST = rmq_params['vhost']
USERNAME = rmq_params['username']
PASSWORD = rmq_params['password']
EXCHANGE = rmq_params['exchange']
BT_QUEUE = rmq_params['bt_queue']
IO_QUEUE = rmq_params['io_queue']

IO_ROUTE = 'IO'
BT_ROUTE = 'BT'
PORT = '5672'

credentials = pika.PlainCredentials(USERNAME, PASSWORD)
params = pika.ConnectionParameters(HOST, PORT, VHOST, credentials)

connection = pika.BlockingConnection(params)
channel = connection.channel()
#

# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
min = 337
max = 447
dif = 392

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

def callback(ch, method, properties, body):
    newbody = pickle.loads(body)
    global proj, blind
    if (proj == 'Up'):
        if (newbody['Projector'] == 'Down'):
            run = 5
            proj = 'Down'
            print('Lowering Projector')
            pwm.set_pwm(0, 0, max)
            time.sleep(run)
            pwm.set_pwm(0, 4096, 0)
        elif (newbody['Projector'] == 'Up'):
            print('Projector already Up')
    elif (proj == 'Down'):
        if (newbody['Projector'] == 'Down'):
            print('Projector already Down')
        elif (newbody['Projector'] == 'Up'):
            run = 5
            proj = 'Up'
            print('Raising Projector')
            pwm.set_pwm(0, 0, min)
            time.sleep(run)
            pwm.set_pwm(0, 4096, 0)
    
    led = int(newbody['Lights'])
    
    if (led == 0):
        turnOff()
        print('Lights Off')
    elif (led == 1):
        redOn()
        print('Red Light')
    elif (led == 2):
        greenOn()
        print('Green Light')
    else:
        blueOn()
        print('Blue Light')
    
    
    
    if (blind == 'Open'):
        if (newbody['Blinds'] == 'Open'):
            print('Blinds already Open')
        elif (newbody['Blinds'] == 'Closed'):
            run = 5
            blind = 'Closed'
            print('Closing Blinds')
            pwm.set_pwm(0, 0, max)
            time.sleep(run)
            pwm.set_pwm(0, 4096, 0)
    elif (blind == 'Closed'):
        if (newbody['Blinds'] == 'Open'):
            run = 5
            blind = 'Open'
            print('Opening Blinds')
            pwm.set_pwm(0, 0, min)
            time.sleep(run)
            pwm.set_pwm(0, 4096, 0)
        elif (newbody['Blinds'] == 'Closed'):
            print('Blinds already Closed')
    
    print('')
    
channel.basic_consume(callback, queue=IO_QUEUE, no_ack=True)
print("Consuming from RMQ queue: %s"%(IO_QUEUE))
print('')
channel.start_consuming()