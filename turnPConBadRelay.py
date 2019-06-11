import RPi.GPIO as GPIO
import time
import json
import os.path
from datetime import datetime

# Pins defined
PC_RELAY_PIN = 11
BUTTON_PIN = 38

def setupEvents():
    #starting
    output.put("System starting...")
    GPIO.cleanup()
    # use Board numbering
    GPIO.setmode(GPIO.BOARD)
    # Port PC_RELAY_PIN is connected via relay to a PC
    my_pc = PC(PC_RELAY_PIN)
    # The button is connected to pin BUTTON_PIN
    but = Button(BUTTON_PIN, my_pc)
    
    # Look in file for request
    try:
        while True:
            f = open("order.json", "r")
            inhalt = json.loads(f.read())
            f.close()
            if not inhalt["on"] and not inhalt["kill"]:
                time.sleep(1)
                continue
            f = open("order.json", "w")
            if inhalt["on"]:
                my_pc.on()
            if inhalt["kill"]:
                my_pc.kill()
            
            new_inhalt = '{"on": false, "kill": false}'
            f.write(new_inhalt)
            f.close()
            
    except KeyboardInterrupt:
        GPIO.cleanup()
        output.put("GPIO cleanup done")

class output:
    @staticmethod
    def put(msg):
        t = datetime.now().strftime("%Y-%m-%d--%H:%M:%S.%f")
        msg = "[" + t + "] " + msg
        print(msg)
        if not os.path.isfile("pcON.log"):
            f = open("pcON.log", "w+")
            f.close()
        f = open("pcON.log", "r")
        stuff = f.read()
        f.close()
        f = open("pcON.log", "w")
        f.write(stuff + msg + "\n")
        f.close()

class PC:
    def __init__(self, port):
        self.port = port
        output.put("New PC at port " + str(self.port))
    
    def on(self):
        output.put("Started starting Computer - Port " + str(self.port))
        GPIO.setup(self.port, GPIO.OUT)
        time.sleep(1)
        GPIO.setup(self.port, GPIO.IN)
        output.put("Started Computer " + str(self.port))

    def kill(self):
        output.put("Started killing Computer - Port " + str(self.port))
        GPIO.setup(self.port, GPIO.OUT)
        time.sleep(10)
        GPIO.setup(self.port, GPIO.IN)
        output.put("Killed Computer - Port " + str(self.port))

class Button:
    def __init__(self, port, aPc):
        self.pc = aPc
        self.port = port
        self.started = 0
        
        GPIO.setup(self.port, GPIO.IN)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising)
    
    def rising(self, evnt):
        output.put("Button port " + str(self.port) + " pressed")
        self.started = time.time()

        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self.falling)

    def falling(self, evnt):
        output.put("Button port " + str(self.port) + " released")
        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising)

        difference = time.time() - self.started
        self.started = 0
        if difference < 0.06 or difference > 15:
            return
        if difference > 5:
            self.pc.kill()
            return
        self.pc.on()

if __name__ == "__main__":
    setupEvents()
