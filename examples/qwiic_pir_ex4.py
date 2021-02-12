#!/usr/bin/env python
#-----------------------------------------------------------------------------
# qwiic_pir_ex4.py
#
# Simple Example for the Qwiic PIR Device
#------------------------------------------------------------------------
#
# Written by Andy England @ SparkFun Electronics, January 2021
# 
# This python library supports the SparkFun Electroncis qwiic 
# qwiic sensor/board ecosystem on a Raspberry Pi (and compatable) single
# board computers. 
#
# More information on qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#
#==================================================================================
# Copyright (c) 2021 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#==================================================================================
# Example 4
#

from __future__ import print_function
import qwiic_pir
import time
import sys
import RPi.GPIO as GPIO

INTERRUPT_GPIO = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(INTERRUPT_GPIO, GPIO.IN)

myPIR = qwiic_pir.QwiicPIR()

def interruptCallback(channel):
	if myPIR.objectDetected():
		print("Object Detected")
	if myPIR.objectRemoved():
		print("Object Removed")
	myPIR.clearEventBits()


def runExample():

	print("\nSparkFun Qwiic PIR  Example 2\n")
	myPIR = qwiic_pir.QwiicPIR()

	if myPIR.begin() == False:
		print("The Qwiic PIR isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

	print ("Waiting 30 seconds for PIR to stabilize")
	for i in range(0, 30):
		print(i)
		time.sleep(1)

	GPIO.add_event_detect(INTERRUPT_GPIO, GPIO.FALLING, callback=interruptCallback, bouncetime=5)
	print("Device Stable")

	while True:
		time.sleep(.1)


if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Example 1")
		sys.exit(0)