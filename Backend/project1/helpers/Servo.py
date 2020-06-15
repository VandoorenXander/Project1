import RPi.GPIO as GPIO
import time


class servo:
    def servobewegen(self,servo):
        p=GPIO.PWM(servo,50) 
        p.start(1023*1.0/20)
        time.sleep(10)
        p.stop(1023*1.5/20)
