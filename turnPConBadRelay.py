import RPi.GPIO as GPIO
import time
import json

# Pins defined
PC_RELAY_PIN = 11
BUTTON_PIN = 38

def setupEvents():
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
        print("GPIO cleanup done")

class PC:
    def __init__(self, port):
        self.port = port
        print("New PC at port " + str(self.port))
    
    def on(self):
        print("Started starting Computer - Port " + str(self.port))
        GPIO.setup(self.port, GPIO.OUT)
        time.sleep(1)
        GPIO.setup(self.port, GPIO.IN)
        print("Started Computer " + str(self.port))

    def kill(self):
        print("Started killing Computer - Port " + str(self.port))
        GPIO.setup(self.port, GPIO.OUT)
        time.sleep(10)
        GPIO.setup(self.port, GPIO.IN)
        print("Killed Computer - Port " + str(self.port))

class Button:
    def __init__(self, port, aPc):
        self.pc = aPc
        self.port = port
        self.started = 0
        
        GPIO.setup(self.port, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising)
    
    def rising(self, evnt):
        print("Button port " + str(self.port) + " pressed")
        self.started = time.time()

        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self.falling)

    def falling(self, evnt):
        print("Button port " + str(self.port) + " released")
        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising)

        difference = time.time() - self.started
        self.started = 0

        if difference > 5:
            self.pc.kill()
            return
        self.pc.on()

if __name__ == "__main__":
    setupEvents()
