import subprocess
from bluetooth import *
import bluetooth._bluetooth as bluez
import re
import time
from pybtooth import BluetoothManager, constants
bm = BluetoothManager()
connected = bm.getConnectedDevices()

for device in connected:
    print (device.get("Address"))

while(1):
    result = subprocess.run(['hcitool', 'rssi',  '40:4e:36:5a:46:6e'], stdout=subprocess.PIPE)    
    #print(result.stdout)
    try:
        new = int(re.search(r'-\d+', str(result.stdout)).group())
    except:
        new = int(re.search(r'\d+', str(result.stdout)).group())
    #print(new)
    if(new < -18 and new > -22):
        print("Not in the living room")
    elif(new < -22):
        print("In Corbins room?")
    else:
        print("In liveing room or kitchen")
    time.sleep(2)