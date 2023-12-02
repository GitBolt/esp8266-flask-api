try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network
import gc

import utime

ssid = ''
password = ''

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig()[0])

import ntptime

ntptime.host = "pool.ntp.org"

def log_event(event):
    with open("medication_log.txt", "a") as log_file:
        log_file.write(event)
    log_file.close()
    
try:
  print("Local time before synchronization: %s" %str(utime.localtime()))
  log_event(str(utime.localtime()))
  ntptime.settime()
  print("Local time after synchronization: %s" %str(utime.localtime()))
  log_event(str(utime.localtime()) + "\n")
except Exception as e:
  print("Error syncing time", e)

gc.collect()


