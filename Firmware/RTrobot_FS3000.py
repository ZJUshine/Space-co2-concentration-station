#!/usr/bin/env python3

# RTrobot FS3000 Test
# http://rtrobot.org

import fcntl
import array
import RPi.GPIO as GPIO
import numpy as np

I2C_SLAVE = 0x0703


class RTrobot_FS3000:
    FS3000_ADDRESS = (0x28)#0x28

    def __init__(self, i2c_no=0, i2c_addr=FS3000_ADDRESS):
        global FS3000_rb, FS3000_wb
        global calibration
        FS3000_rb = open("/dev/i2c-"+str(i2c_no), "rb", buffering=0)
        FS3000_wb = open("/dev/i2c-"+str(i2c_no), "wb", buffering=0)
        print("Thanks for using RTrobot module")
        fcntl.ioctl(FS3000_rb, I2C_SLAVE, i2c_addr)
        fcntl.ioctl(FS3000_wb, I2C_SLAVE, i2c_addr)

    def FS3000_ReadData(self):
        air_velocity_table = (0, 2.0, 3.0, 4.0, 5.0,
                                  6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 13.0, 15.0)
        adc_table = (409, 1203, 1597, 1908, 2187,
                         2400, 2629, 2801, 3006, 3178, 3309, 3563, 3686)
        fm_raw = self.FS3000_i2c_read()
        fm_level = 0
        fm_percentage = 0
        if fm_raw < adc_table[0] or fm_raw > adc_table[12]:
            return 0
        for i in range(13):
            if fm_raw > adc_table[i]:
                fm_level=i
        fm_percentage = (fm_raw - adc_table[fm_level]) / (adc_table[fm_level + 1] - adc_table[fm_level])
        return (air_velocity_table[fm_level + 1] - air_velocity_table[fm_level]) * fm_percentage + air_velocity_table[fm_level]

    ######################################i2C######################################

    def FS3000_i2c_read(self, delays=0.015):
        tmp = FS3000_rb.read(5)
        data = array.array('B', tmp)
        sum = 0x00
        for i in range(0, 5):
            sum += data[i]
        if sum & 0xff != 0x00:
            return 0x00
        else:
            return (data[1] * 256 + data[2]) & 0xfff
