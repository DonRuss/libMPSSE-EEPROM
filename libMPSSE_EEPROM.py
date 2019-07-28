

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


values              = [0x03, 0x00]
raw                 = struct.pack("%dB"%len(values),*values)

libMPSSE            = ctypes.cdll.LoadLibrary("libMPSSE.dll")
chn_count           = ctypes.c_int()
chn_conf            = ChannelConfig(400000,5,0)
chn_no              = 0
handle              = ctypes.c_void_p()
bytes_transfered    = ctypes.c_int()
buf                 = ctypes.create_string_buffer(raw,len(raw))

I2Caddress          = 0x38
mode                = I2C_TRANSFER_OPTION.START_BIT|I2C_TRANSFER_OPTION.STOP_BIT|I2C_TRANSFER_OPTION.FAST_TRANSFER_BYTES|I2C_TRANSFER_OPTION.BREAK_ON_NACK

    
ret = libMPSSE.I2C_GetNumChannels(ctypes.byref(chn_count))
print("status:",ret,"number of channels:",chn_count)
ret = libMPSSE.I2C_OpenChannel(chn_no, ctypes.byref(handle))
print("I2C_OpenChannel status:",ret,"handle:",handle)
ret = libMPSSE.I2C_InitChannel(handle,ctypes.byref(chn_conf))
print("I2C_InitChannel status:",ret)

#values              = [0x03, 0x00]
#raw                 = struct.pack("%dB"%len(values),*values)
#buf                 = ctypes.create_string_buffer(raw,len(raw))


def byteString( values ):
    raw                 = struct.pack("%dB"%len(values),*values)
    buf                 = ctypes.create_string_buffer(raw,len(raw))
    return buf;
    
def flasher():

    while True:
        print(".")
        time.sleep(0.300)

        ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 2, b'\x01\x55', ctypes.byref(bytes_transfered), mode)

        time.sleep(0.300)
        byte_buf = b'\x01\xAA'
        ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, len(byte_buf), byte_buf, ctypes.byref(bytes_transfered), mode)

        byte_buf=b'\x00'
        ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 1, b'\x01', ctypes.byref(bytes_transfered), mode)
        ret = libMPSSE.I2C_DeviceRead(handle, I2Caddress, 1, byte_buf, ctypes.byref(bytes_transfered), mode)

        print(byte_buf)


        #  ______________________________________________________________________________________________________________________________________________________________________________



ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, len(values), byteString([0x03, 0x00]), ctypes.byref(bytes_transfered), mode)

I2Caddress = 0x50
byte_buf=b'\x00'*20
#ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 1, b'\x00', ctypes.byref(bytes_transfered), mode)
#ret = libMPSSE.I2C_DeviceRead(handle, I2Caddress, 20, byte_buf, ctypes.byref(bytes_transfered), mode)


#ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 5, b'\x00\xDE\xAD\xBE\xEF', ctypes.byref(bytes_transfered), mode)

ret = libMPSSE.I2C_DeviceWrite(handle, I2Caddress, 1, b'\x00', ctypes.byref(bytes_transfered), mode)
ret = libMPSSE.I2C_DeviceRead(handle, I2Caddress, 16, byte_buf, ctypes.byref(bytes_transfered), mode)

hex_out = ""

for b in byte_buf:
    hex_out += "%02X " % b

print ("00: ", hex_out)


try:
    flasher()
except KeyboardInterrupt:

    print('\n\nKeyboard exception was received')
    print("I2C_DeviceWrite status:",ret, "transfered:",bytes_transfered)
    ret = libMPSSE.I2C_CloseChannel(handle)
    print("I2C_CloseChannel status:",ret)