# Test file for Wdm1

import win32file, win32api, sys
sys.path += ["DeviceDriverAccess/Release"]

from DeviceDriverAccess import GetDeviceViaInterface

from struct import *

# Constants for Wdm1
WDM1_GUID = pack("LHHBBBBBBBB", 0x1ef8a96b, 0x6c26, 0x42a4, 0xb9, 0x19, 0x82, 0x50, 0x93, 0x13, 0xbc, 0x5b)

FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
METHOD_IN_DIRECT = 1
METHOD_OUT_DIRECT = 2
METHOD_NEITHER = 3
FILE_ANY_ACCESS = 0

ZERO_BUFFER = 0x801
REMOVE_BUFFER = 0x802
GET_BUFFER_SIZE = 0x803
GET_BUFFER = 0x804
UNRECOGNISED = 0x805
GET_BUILDTIME = 0x806
RPN_PUSH = 0x807
RPN_POP = 0x808
RPN_ADD = 0x809
RPN_SUB = 0x810
RPN_MULT = 0x811
RPN_DIV = 0x812
RPN_GETDIVREST = 0x813
RPN_DUPLI = 0x814

def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

class HWDevice:    
    def __init__(self,guid):
        self.guid = guid
        self.drvHnd = None
        self.OpenDrv()

    def OpenDrv(self):
        """
        Open a handle to the device driver. If the driver is already open,
        close it first an reopen it.
        """
        self.CloseDrv()
        try:
            name = GetDeviceViaInterface(self.guid)
        except:
            raise IOError (1, "Wdm1 Device not found")

        desiredAccess = win32file.GENERIC_READ | win32file.GENERIC_WRITE
        self.drvHnd = win32file.CreateFile(name,
                                           desiredAccess,
                                           win32file.FILE_SHARE_WRITE,
                                           None,
                                           win32file.OPEN_EXISTING,
                                           0,
                                           0)

    def CloseDrv(self):
        """
        Close the handle to device driver
        """
        if self.drvHnd is not None:
            win32file.CloseHandle(self.drvHnd)
            self.drvHnd = None

    def Write(self, string):
        win32file.WriteFile(self.drvHnd, string, None)

    def Read(self, numofbytes=1):
        hr, result = win32file.ReadFile(self.drvHnd, numofbytes, None)
        return result

    def SetFilePointer(self, distance):
        win32file.SetFilePointer(self.drvHnd, distance, win32file.FILE_BEGIN)

    def DeviceIoControl(self, function, input):      
        
        IOCTL_USB_GET_DEVICE_DESCRIPTOR = CTL_CODE(FILE_DEVICE_UNKNOWN, function, METHOD_BUFFERED, FILE_ANY_ACCESS)

        try:
            result = win32file.DeviceIoControl(self.drvHnd, IOCTL_USB_GET_DEVICE_DESCRIPTOR, input, 512)        
        except win32file.error, e:
            print "problem with driver or stack over/underflow"
            print "Unexpected error:", e
            result = 0

        return result


d = HWDevice(WDM1_GUID)

print "Clear buffer ..."
d.DeviceIoControl(REMOVE_BUFFER,"")

bufferLength = d.DeviceIoControl(GET_BUFFER_SIZE,"")
result, = unpack('i', bufferLength)
print "Buffer length should be zero. Buffer Length = %d" % result

print "Write buffer ('Hello World Buffer! :D') ..."
d.Write("Hello World Buffer! :D")

bufferLength = d.DeviceIoControl(GET_BUFFER_SIZE,"")
result, = unpack('i', bufferLength)
print "Buffer length after write = %d" % result

print "Read 5 bytes from buffer ..."
result = d.Read(5)
print "Read bytes = %s" % result

print "Move FilePointer 5 bytes back ..."
d.SetFilePointer(5)

print "Read 50 bytes from buffer ..."
result = d.Read(50)
print "Read bytes = %s" % result

print "Clear buffer ..."
d.DeviceIoControl(REMOVE_BUFFER,"")

bufferLength = d.DeviceIoControl(GET_BUFFER_SIZE,"")
result, = unpack('i', bufferLength)
print "Buffer length should be zero. Buffer Length = %d" % result

dateTime = d.DeviceIoControl(GET_BUILDTIME,"")
print dateTime

print "push and pop"
d.DeviceIoControl(RPN_PUSH, pack("I", 5));
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print result

print "push and add and pop"
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH, pack("I", 5));
d.DeviceIoControl(RPN_ADD, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print result

print "push and sub and pop"
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH, pack("I", 2));
d.DeviceIoControl(RPN_SUB, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print result

print "push and mult and pop"
d.DeviceIoControl(RPN_PUSH,  pack("I", 10));
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH,  pack("I", 3));
d.DeviceIoControl(RPN_MULT, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print "5*3 = %d" % result

print "push and invalid div and pop"
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH,  pack("I", 3));
d.DeviceIoControl(RPN_DIV, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print "5 / 3 = %d" % result

print "push and invalid div 0 and pop"
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH,  pack("I", 0));
d.DeviceIoControl(RPN_DIV, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print "5 / 0 = %d" % result


print "push to the limit"
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH,  pack("I", 0));
d.DeviceIoControl(RPN_PUSH,  pack("I", 0));
d.DeviceIoControl(RPN_PUSH,  pack("I", 0));
d.DeviceIoControl(RPN_PUSH,  pack("I", 0));


print "pop to zero"
d.DeviceIoControl(RPN_POP, "");
d.DeviceIoControl(RPN_POP, "");
d.DeviceIoControl(RPN_POP, "");
d.DeviceIoControl(RPN_POP, "");
d.DeviceIoControl(RPN_POP, "");
d.DeviceIoControl(RPN_POP, "");

print "push and getdivrest and pop"
d.DeviceIoControl(RPN_PUSH,  pack("I", 5));
d.DeviceIoControl(RPN_PUSH,  pack("I", 3));
d.DeviceIoControl(RPN_GETDIVREST, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print "5 modulo 3 = %d" % result

print "duplicate"
d.DeviceIoControl(RPN_PUSH,  pack("I", 11));
d.DeviceIoControl(RPN_PUSH,  pack("I", 12));
d.DeviceIoControl(RPN_DUPLI, "");
value = d.DeviceIoControl(RPN_POP, "");
result, = unpack('i', value)
print "should be 12 = %d" % result

d.CloseDrv()
