#-----------------------------------------------------------------------------
# qwiic_pir.py
#
# Python library for the SparkFun qwiic pir.
#   https://www.sparkfun.com/products/16407
#
#------------------------------------------------------------------------
#
# Written by Andy England @ SparkFun Electronics, January 2021
# 
# This python library supports the SparkFun Electroncis qwiic 
# qwiic sensor/board ecosystem 
#
# More information on qwiic is at https:// www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
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

"""
qwiic_pir
============
Python module for the Qwiic PIR.
This python package is a port of the exisiting [SparkFun Qwiic PIR Arduino Library](https://github.com/sparkfun/SparkFun_Qwiic_PIR_Arduino_Library)
This package can be used in conjunction with the overall [SparkFun Qwiic Python Package](https://github.com/sparkfun/Qwiic_Py)
New to qwiic? Take a look at the entire [SparkFun Qwiic Ecosystem](https://www.sparkfun.com/qwiic).
"""
#-----------------------------------------------------------------------------------

import math
import qwiic_i2c

# Define the device name and I2C addresses. These are set in the class definition
# as class variables, making them available without having to create a class instance.
# This allows higher level logic to rapidly create an index of qwiic devices at runtime.

# This is the name of the device
_DEFAULT_NAME = "Qwiic PIR"

# Some devices have  multiple available addresses - this is a list of these addresses.
# NOTE: The first address in this list is considered the default I2C address for the 
# device.
_AVAILABLE_I2C_ADDRESS = [0x12]

# Define the class that encapsulates the device being created. All information associated 
# with this device is encapsulated by this class. The device class should be the only value
# exported from this module.

class QwiicPIR(object):
    """"
    QwiicPIR
        
        :param address: The I2C address to use for the device.
                        If not provided, the default address is used.
        :param i2c_driver: An existing i2c driver object. If not provided
                        a driver object is created.
        :return: The GPIO device object.
        :rtype: Object
    """
    # Constructor
    device_name = _DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS

    # Device ID for all Qwiic PIRs
    DEV_ID = 0x72

    # Registers
    ID = 0x00
    FIRMWARE_MINOR = 0x01
    FIRMWARE_MAJOR = 0x02
    EVENT_STATUS = 0x03
    INTERRUPT_CONFIG = 0x04
    EVENT_DEBOUNCE_TIME = 0x05
    DETECTED_QUEUE_STATUS = 0x07
    DETECTED_QUEUE_FRONT = 0x08
    DETECTED_QUEUE_BACK = 0x0C
    REMOVED_QUEUE_STATUS = 0x10
    REMOVED_QUEUE_FRONT = 0x11
    REMOVED_QUEUE_BACK = 0x15
    I2C_ADDRESS = 0x19

    # Status Flags
    eventAvailable = 0
    objectRemove = 0
    objectDetect = 0
    rawObjectDetected = 0

    # Interrupt Configuration Flags
    interruptEnable = 0

    # Queue Status Flags
    popRequest = 0
    isEmpty = 0
    isFull = 0

    # Constructor
    def __init__(self, address=None, i2c_driver=None):

        # Did the user specify an I2C address?
        self.address = address if address != None else self.available_addresses[0]

        # Load the I2C driver if one isn't provided
        if i2c_driver == None:
            self._i2c = qwiic_i2c.getI2CDriver()
            if self._i2c == None:
                print("Unable to load I2C driver for this platform.")
                return
            else: 
                self._i2c = i2c_driver

    # -----------------------------------------------
    # isConnected()
    #
    # Is an actual board connected to our system?
    def isConnected(self):
        """
            Determine if a Qwiic PIR device is connected to the system.
            :return: True if the device is connected, otherwise False.
            :rtype: bool
        """
        return qwiic._i2c.isDeviceConnected(self.address)
    
    # ------------------------------------------------
    # begin()
    #
    # Initialize the system/validate the board.
    def begin(self):
        """
            Initialize the operation of the Qwiic PIR
            Run isConnected() and check the ID in the ID register
            :return: Returns true if the intialization was successful, otherwise False.
            :rtype: bool
        """
        if self.isConnected() == True:
            id = self._i2c.readByte(self.address, self.ID)
            
            if id == self.DEV_ID:
                return True
        
        return False
    
    # ------------------------------------------------
    # getFirmwareVersion()
    #
    # Returns the firmware version of the attached devie as a 16-bit integer.
    # The leftmost (high) byte is the major revision number, 
    # and the rightmost (low) byte is the minor revision number.
    def getFirmwareVersion(self):
        """
            Read the register and get the major and minor firmware version number.
            :return: 16 bytes version number
            :rtype: int
        """
        version = self._i2c.readByte(self.address, self.FIRMWARE_MAJOR) << 8
        version |= self._i2c.readByte(self.address, self.FIRMWARE_MINOR)
        return version

    # -------------------------------------------------
    # setI2Caddress(address)
    #
    # Configures the attached device to attach to the I2C bus using the specified address
    def setI2Caddress(self, newAddress):
        """
            Change the I2C address of the Qwiic PIR
            :return: True if the change was successful, false otherwise.
            :rtype: bool
        """
        # First, check if the specified address is valid
        if newAddress < 0x08 or newAddress > 0x77:
            return False
        
        # Write new address to the I2C address register of the Qwiic PIR
        success = self._i2c.writeByte(self.address, self.I2C_ADDRESS, newAddress)

        # Check if the write was successful
        if success == True:
            self.address = newAddress
            return True
        
        else:
            return False
    
    # ---------------------------------------------------
    # getI2Caddress()
    #
    # Returns the I2C address of the device
    def getI2Caddress(self):
        """
            Returns the current I2C address of the Qwiic PIR
            :return: current I2C address
            :rtype: int
        """
        return self.address

    # ---------------------------------------------------
    # rawReading()
    #
    # Returns 1 if the PIR is detecting an object, 0 otherwise
    def rawReading(self):
        """
            Returns the value of the rawReading status bit of the EVENT_STATUS register
            :return: rawObjectDetected bit
            :rtype: bool
        """
        # Read the pir status register
        pirStatus = self._i2c.readByte(self.address, self.EVENT_STATUS)
        # Convert to binary and clear all bits but rawObjectDetected
        self.rawObjectDetected = bin(pirStatus) & 0x01
        # Return rawObjectDetected as a bool
        return bool(self.rawObjectDetected)
    
    # ---------------------------------------------------
    # objectDetected()
    #
    # Returns 1 if the PIR has a debounced detect object event
    def objectDetected(self):
        """
            Returns the value of the objectDetect status bit of the EVENT_STATUS register
            :return: objectDetect bit
            :rtype: bool
        """
        # Read the pir status register
        pirStatus = self._i2c.readByte(self.address, self.EVENT_STATUS)
        # Convert to binary and clear all bits but objectDetect
        self.objectDetect = bin(pirStatus) & 0x08
        # Return objectDetect as a bool
        self.objectDetect = self.objectDetect >> 4
        return bool(self.objectDetect)
    
    # ----------------------------------------------------
    # objectRemoved()
    #
    # Returns 1 if the object in front of the PIR is removed, and 0 otherwise
    def objectRemoved(self):
        """
            Returns the value of the objectRemove status bit of the EVENT_STATUS register
            :return: objectRemove bit
            :rtype: bool
        """
        # Read the pir status register
        pirStatus = self._i2c.readByte(self.address, self.EVENT_STATUS)
        # Convert to binary and clear all bits but objectRemove
        self.objectRemove = bin(pirStatus) & 0x04
        # Shift objectRemoved to the zero bit
        self.objectRemove = self.objectRemove >> 2
        # Return objectRemoved as a bool
        return bool(self.objectRemove)
    
    # ------------------------------------------------------
    # getDebounceTime()
    #
    # Returns the time that the PIR is using to debounce events
    def getDebounceTime(self):
        """
            Returns the value in the EVENT_DEBOUNCE_TIME register
            :return: debounce time in milliseconds
            :rtype: int
        """
        # TODO: just so you know, this will return a list. You need to find out how to concatenate the two items into one time silly
        return self._i2c.readBlock(self.address, self.EVENT_DEBOUNCE_TIME, 2)
    
    # -------------------------------------------------------
    # setDebounceTime(time)
    #
    # Sets the time that the PIR is using to debounce events
    def setDebouncetime(self, time):
        """
            Write two bytes into the EVENT_DEBOUNCE_TIME register
            :return: Nothing
            :rtype: void
        """
        # First check that time is not too big
        if time > 0xFFFF:
            time = 0xFFFF
        # Then write two bytes
        self._i2c.writeWord(self.address, self.EVENT_DEBOUNCE_TIME, time)

    # -------------------------------------------------------
    # enableInterrupt()
    #
    # The interrupt will be configured to trigger when the pir
    # detects an object.
    def enableInterrupt(self):
        """
            Set interruptEnable bit of the INTERRUPT_CONFIG register to a 1
            :return: Nothing
            :rtype: Void
        """
        # First, read the INTERRUPT_CONFIG register
        interruptConfig = self._i2c.readByte(self.address, self.INTERRUPT_CONFIG)
        self.interruptEnable = 1
        # Set the interruptEnable bit
        interruptConfig = interruptConfig | (self.interruptEnable << 1)
        # Write the new interrupt configure byte
        self._i2c.writeByte(self.address, self.INTERRUPT_CONFIG, interruptConfig)
    
    # -------------------------------------------------------
    # disableInterrupt()
    # 
    # Interrupt will no longer be configured to trigger when the
    # pir is detecting.
    def disableInterrupt(self):
        """
            Clear the interruptEnable bit of the INTERRUPT_CONFIG register
            :return: Nothing
            :rtype: Void
        """
        # First, read the INTERRUPT_CONFIG register
        interruptConfig = self._i2c.readByte(self.address, self.INTERRUPT_CONFIG)
        self.interruptEnable = 0
        # Clear the interruptEnable bit
        interruptConfig = interruptConfig & ~(1 << 1)
        # Write the new interrupt configure byte
        self._i2c.writeByte(self.address, self.INTERRUPT_CONFIG, interruptConfig)

    # -------------------------------------------------------
    # available()
    #
    # Returns the eventAvailble bit. This bit is set to 1 if a
    # pir detect or remove event occurred
    def available(self):
        """
            Return the eventAvailable bit of the EVENT_STATUS register
            
            :return: eventAvailable bit
            :rtye: bool
        """
        # First, read EVENT_STATUS register
        pirStatus = self._i2c.readByte(self.address, self.EVENT_STATUS)
        # Convert to binary and clear all bits but the eventAvailable bit
        self.eventAvailable = bin(pirStatus) & 0x02

        # Return eventAvailable bit as a bool
        return bool(self.eventAvailable)
    
    # -------------------------------------------------------
    # clearEventBits()
    # 
    # Sets all pir status bits (rawObjectDetected, objectRemoved, 
    # and eventAvailable) to zero.
    def clearEventBits(self):
        """
            Clear the rawObjectDetected, objectRemove, objectDetect, and eventAvailable
            bits of the EVENT_STATUS register
            :return: Nothing
            :rtype: Void
        """
        # First, read EVENT_STATUS register
        pirStatus = self._i2c.readByte(self.address, self.EVENT_STATUS)
        # Convert to binary and clear the last four bits
        pirStatus = bin(pirStatus) & ~(0x08)
        # Write to EVENT_STATUS register
        self._i2c.writeByte(self.address, self.EVENT_STATUS, pirStatus)
    
    # -------------------------------------------------------
    # resetInterruptConfig()
    #
    # Resets the interrupt configuration back to defaults.
    def resetInterruptConfig(self):
        """
            Enable detect and removed interrupts and clear the
            eventAvailable bit of EVENT_STATUS register
            :return: Nothing
            :rtype: Void
        """
        self.interruptEnable = 1
        # write 0b1 to the INTERRUPT_CONFIG register
        self._i2c.writeByte(self.address, self.INTERRUPT_CONFIG, 0b1)
        self.eventAvailable = 0
        # Clear objectRemove, rawObjectDetected too
        # TODO: not sure if this is right
        self.objectRemove = 0
        self.objectDetect = 0
        self.rawObjectDetected = 0
        # Clear the EVENT_STATUS register by writing a 0
        self._i2c.writeByte(self.address, self.EVENT_STATUS, 0x00)
    
    # -------------------------------------------------------
    # isDetectedQueueFull()
    #
    # Returns true if queue of pir detect timestamps is full,
    # and false otherwise.
    def isDetectedQueueFull(self):
        """
            Returns the isFull bit of the DETECTED_QUEUE_STATUS register
            :return: isFull
            :rtype: bool
        """
        # First, read the DETECTED_QUEUE_STATUS register
        detectedQueueStat = self._i2c.readByte(self.address, self.DETECTED_QUEUE_STATUS)
        # Convert to binary and clear all bits but isFull
        self.isFull = bin(detectedQueueStat) & ~(0xFE)
        # Return isFull as a bool
        return bool(self.isFull)
    
    # -------------------------------------------------------
    # isDetectedQueueEmpty()
    #
    # Returns true if the queue of pir detect timestamps is
    # empty, and false otherwise.
    def isDetectedQueueEmpty(self):
        """
            Returns the isEmpty bit of the DETECTED_QUEUE_STATUS register
            
            :return: isEmpty
            :rtype: bool
        """
        # First, read the DETECTED_QUEUE_STATUS register
        detectedQueueStat = self._i2c.readByte(self.address, self.DETECTED_QUEUE_STATUS)
        # Convert to binary and clear all bits but isEmpty
        self.isEmpty = bin(detectedQueueStat) & ~(0xFD)
        # Shift isEmpty to the zero bit
        self.isEmpty = self.isEmpty >> 1
        # Return isEmpty as a bool
        return bool(self.isEmpty)

    # ------------------------------------------------------
    # timeSinceLastDetect()
    #
    # Returns how many milliseconds it has been since the last
    # detect event. Since this returns a 32-bit int, it will 
    # roll over about every 50 days.
    def timeSinceLastDetect(self):
        """
            Returns the four bytes of DETECTED_QUEUE_FRONT.
            Time in milliseconds.
            :return: DETECTED_QUEUE_FRONT
            :rtype: int
        """
        # TODO: not sure if this will work because this read might return a list?
        return self._i2c.readBlock(self.address, self.DETECTED_QUEUE_FRONT, 4)

    # -------------------------------------------------------
    # timeSinceFirstDetect()
    #
    # Returns how many milliseconds it has been since the first 
    # detect event. Since this returns a 32-bit int, it will 
    # roll over about every 50 days.
    def timeSinceFirstDetect(self):
        """
            Returns the four bytes of DETECTED_QUEUE_BACK.
            Time in milliseconds
            :return: DETECTED_QUEUE_BACK
            :rtype: int
        """
        return self._i2c.readBlock(self.address, self.DETECTED_QUEUE_BACK, 4)

    # -------------------------------------------------------
    # popDetectedQueue()
    #
    # Returns the oldest value in the queue (milliseconds since 
    # first pir detect event), and then removes it.
    def popDetectedQueue(self):
        """
            Returns contents of DETECTED_QUEUE_BACK register and 
            writes a 1 to popRequest bit of DETECTED_QUEUE_STATUS
            register.
            :return: DETECTED_QUEUE_BACK
            :rtype: int
        """
        # Get the time in milliseconds since the pir was first detect
        tempData = self.timeSinceFirstDetect()
        # Read DETECTED_QUEUE_STATUS register
        detectedQueueStat = self._i2c.readByte(self.address, self.DETECTED_QUEUE_STATUS)
        self.popRequest = 1
        # Set popRequest bit to 1
        detectedQueueStat = detectedQueueStat | (self.popRequest << 2)
        self._i2c.writeByte(self.address, self.DETECTED_QUEUE_STATUS, detectedQueueStat)
        return tempData
    
    # -------------------------------------------------------
    # isRemovedQueueFull()
    #
    # Returns true if queue of pir remove timestamps is full,
    # and false otherwise.
    def isRemovedQueueFull(self):
        """
            Returns the isFull bit of the DETECTED_QUEUE_STATUS register
            :return: isFull
            :rtype: bool
        """
        # First, read the DETECTED_QUEUE_STATUS register
        removeedQueueStat = self._i2c.readByte(self.address, self.DETECTED_QUEUE_STATUS)
        # Convert to binary and clear all bits but isFull
        self.isFull = bin(removeedQueueStat) & ~(0xFE)
        # Return isFull as a bool
        return bool(self.isFull)
    
    # -------------------------------------------------------
    # isRemovedQueueEmpty()
    #
    # Returns true if the queue of pir remove timestamps is
    # empty, and false otherwise.
    def isRemovedQueueEmpty(self):
        """
            Returns the isEmpty bit of the DETECTED_QUEUE_STATUS register
            
            :return: isEmpty
            :rtype: bool
        """
        # First, read the DETECTED_QUEUE_STATUS register
        removeedQueueStat = self._i2c.readByte(self.address, self.DETECTED_QUEUE_STATUS)
        # Convert to binary and clear all bits but isEmpty
        self.isEmpty = bin(removeedQueueStat) & ~(0xFD)
        # Shift isEmpty to the zero bit
        self.isEmpty = self.isEmpty >> 1
        # Return isEmpty as a bool
        return bool(self.isEmpty)

    # ------------------------------------------------------
    # timeSinceLastRemove()
    #
    # Returns how many milliseconds it has been since the last
    # remove event. Since this returns a 32-bit int, it will 
    # roll over about every 50 days.
    def timeSinceLastRemove(self):
        """
            Returns the four bytes of DETECTED_QUEUE_FRONT.
            Time in milliseconds.
            :return: DETECTED_QUEUE_FRONT
            :rtype: int
        """
        # TODO: not sure if this will work because this read might return a list?
        return self._i2c.readBlock(self.address, self.DETECTED_QUEUE_FRONT, 4)

    # -------------------------------------------------------
    # timeSinceFirstRemove()
    #
    # Returns how many milliseconds it has been since the first 
    # remove event. Since this returns a 32-bit int, it will 
    # roll over about every 50 days.
    def timeSinceFirstRemove(self):
        """
            Returns the four bytes of DETECTED_QUEUE_BACK.
            Time in milliseconds
            :return: DETECTED_QUEUE_BACK
            :rtype: int
        """
        return self._i2c.readBlock(self.address, self.DETECTED_QUEUE_BACK, 4)

    # -------------------------------------------------------
    # popRemoveedQueue()
    #
    # Returns the oldest value in the queue (milliseconds since 
    # first pir remove event), and then removes it.
    def popRemoveedQueue(self):
        """
            Returns contents of DETECTED_QUEUE_BACK register and 
            writes a 1 to popRequest bit of DETECTED_QUEUE_STATUS
            register.
            :return: DETECTED_QUEUE_BACK
            :rtype: int
        """
        # Get the time in milliseconds since the pir was first remove
        tempData = self.timeSinceFirstRemove()
        # Read DETECTED_QUEUE_STATUS register
        removeedQueueStat = self._i2c.readByte(self.address, self.DETECTED_QUEUE_STATUS)
        self.popRequest = 1
        # Set popRequest bit to 1
        removeedQueueStat = removeedQueueStat | (self.popRequest << 2)
        self._i2c.writeByte(self.address, self.DETECTED_QUEUE_STATUS, removeedQueueStat)
        return tempData