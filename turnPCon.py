import RPi.GPIO as GPIO
import time

# Pins defined
PC_RELAY_PIN = 40
BUTTON_PIN = 38

def setupEvents():
    # use Board numbering
    GPIO.setmode(GPIO.BOARD)
    # Port PC_RELAY_PIN is connected via relay to a PC
    my_pc = PC(PC_RELAY_PIN)
    # The button is connected to pin BUTTON_PIN
    but = Button(BUTTON_PIN, my_pc)

class PC:
    def __init__(self, port):
        print("New PC at port " + str(self.port))
        self.port = port
        GPIO.setup(self.port, GPIO.OUT)
    
    def on(self):
        print("Started starting Computer - Port " + str(self.port))
        GPIO.output(self.port, True)
        time.sleep(1)
        GPIO.output(self.port, False)
        print("Started Computer " + str(self.port))

    def kill(self):
        print("Started killing Computer - Port " + str(self.port))
        GPIO.output(self.port, True)
        time.sleep(10)
        GPIO.output(self.port, False)
        print("Killed Computer - Port " + str(self.port))

class Button:
    def __init__(self, port, aPc):
        self.pc = aPc
        self.port = port
        self.started = 0
        
        GPIO.setup(self.port, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising, bouncetime=50)
    
    def rising(self, evnt):
        print("Button port " + str(self.port) + " pressed")
        self.started = time.time()

        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self.falling, bouncetime=50)

    def falling(self, evnt):
        print("Button port " + str(self.port) + " released")
        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising, bouncetime=50)

        difference = time.time() - self.started
        self.started = 0

        if difference > 5:
            self.pc.kill()
            return
        self.pc.on()

if __name__ == "__main__":
    setupEvents()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("GPIO cleanup done")
