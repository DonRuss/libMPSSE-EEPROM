
# Simple reading and writing to a small EEPROM using the MPSSE library and a FT232 in Python
#
# The EEPROM is a 256 byte device located at 0x50 on the bus.  It is
# AT24C02 – 2-Wire Bus Serial EEPROM (Atmel)
# 256 bytes / 2 kilobit – 8 bytes / page
# http://www.atmel.com/devices/AT24C02.aspx
#
# Project started from:  http://buildingelectronics.blogspot.com/2017/09/talking-i2c-via-ftdi-ft2232h-with-python.html 
#
# Note that the libMPSSE.dll file must be in the project directory and must match your Python implementation.
#
# Don Russ 7/29/2019

import struct
import ctypes
import time

class ChannelConfig(ctypes.Structure):
    _fields_ = [("ClockRate",   ctypes.c_int),
                ("LatencyTimer",ctypes.c_ubyte),
                ("Options",     ctypes.c_int)]

class I2C_TRANSFER_OPTION(object):
    START_BIT           = 0x01
    STOP_BIT            = 0x02
    BREAK_ON_NACK       = 0x04
    NACK_LAST_BYTE      = 0x08
    FAST_TRANSFER_BYTES = 0x10
    FAST_TRANSFER_BITS  = 0x20
    FAST_TRANSFER       = 0x30
    NO_ADDRESS          = 0x40



#Create the Python wrapper around the MPSSE library using CTYPES
libMPSSE            = ctypes.cdll.LoadLibrary("libMPSSE.dll")

# This is one way to create the byte string variable
values              = [0x03, 0x00]
raw                 = struct.pack("%dB"%len(values),*values)


#Initialize some of the variables that are used when the MPSSE Library is called
chn_count           = ctypes.c_int()
chn_conf            = ChannelConfig(400000,5,0) # 400kHz 
chn_no              = 0 #Assume only one device
handle              = ctypes.c_void_p()
bytes_transfered    = ctypes.c_int()
buf                 = ctypes.create_string_buffer(raw,len(raw))
mode                = I2C_TRANSFER_OPTION.START_BIT|I2C_TRANSFER_OPTION.STOP_BIT|I2C_TRANSFER_OPTION.FAST_TRANSFER_BYTES|I2C_TRANSFER_OPTION.BREAK_ON_NACK # We use fast transfer when we can and break on NACK 

# Note that with Break on NAK the ctypes.byref(bytes_transfered) may return a number smaller than the number of bytes sent but the transfer may not hang and timeout.
    
ret = libMPSSE.I2C_GetNumChannels(ctypes.byref(chn_count)) # Used as an example. We assume only one device in the code.
print("Interface status:",ret,"   Number of channels:",chn_count)
ret = libMPSSE.I2C_OpenChannel(chn_no, ctypes.byref(handle)) # Here we open the channel and get the handel for that channel
print("I2C_OpenChannel status:",ret,"   Interface Handle:",hex(ctypes.c_void_p.from_buffer(handle).value) ) # Print the status and the memory location of the libMPSSE routine in HEX
ret = libMPSSE.I2C_InitChannel(handle,ctypes.byref(chn_conf)) # Configure the FT232 to be I2C at 400kHz
print("I2C_InitChannel status:",ret)


I2Caddress = 0x50    # Base address of the EEPROM on the I2C bus
byte_buf=b'\x00'*16  # Create a byte buffer that is one page long

# libMPSSE.I2C_DeviceWrite(handle, I2Caddress, Number of Bytes to transfer, Byte String, Number of Bytes Written returned, mode)

ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 5, b'\x00\xDE\xAD\xBE\xEF', ctypes.byref(bytes_transfered), mode) # Write some dead cow to the EEPROM at page 0 

ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 1, b'\x00', ctypes.byref(bytes_transfered), mode)  # Write the page address to the EEPROM
ret = libMPSSE.I2C_DeviceRead(handle, I2Caddress, 16, byte_buf, ctypes.byref(bytes_transfered), mode) # Read back the page from the EEPROM

hex_out = ""

for b in byte_buf:
    hex_out += "%02X " % b


print("\n")
print ("\n   00: ", hex_out,"\n")

print("I2C_DeviceWrite status:",ret, "Number of Bytes Transfered:",bytes_transfered) # Display the status of the transfer
ret = libMPSSE.I2C_CloseChannel(handle)
print("I2C_CloseChannel status:",ret)
print("\n")
