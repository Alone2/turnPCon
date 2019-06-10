import RPi.GPIO as GPIO
import time

# Pins defined
PC_RELAY_PIN = 1
BUTTON_PIN = 1

def setupEvents():
    # use Board numbering
    GPIO.setmode(GPIO.BOARD)
    # Port X is connected via relay to a PC
    my_pc = PC(PC_RELAY_PIN)
    # The button is connected to pin Y
    but = Button(BUTTON_PIN, my_pc)

class PC:
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT)
    
    def on(self):
        GPIO.output(self.port, True)
        time.sleep(300)
        GPIO.output(self.port, False)

    def kill(self):
        GPIO.output(self.port, False)
        time.sleep(1000)
        GPIO.output(self.port, False)

class Button:
    def __init__(self, port, aPc):
        self.pc = aPc
        self.port = port
        self.started = 0
        
        GPIO.setup(self.port, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.rising, bouncetime=50)
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self.falling, bouncetime=50)
    
    def rising(self):
        self.started = time.time()

    def falling(self):
        difference = time.time() -self.started

        if difference > 5:
            self.pc.kill()
            return
        self.pc.on()

if __name__ == "__main__":
    try:
        setupEvents()
    except:
        GPIO.cleanup()
