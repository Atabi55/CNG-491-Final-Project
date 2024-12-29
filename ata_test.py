from gpiozero import AngularServo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

def func1():
    s1.min()
    sleep(1.5)
    s1.mid()
    sleep(1.5)
    s1.max()
    sleep(1.5)
    
    s2.min()
    sleep(1.5)
    s2.mid()
    sleep(1.5)
    s2.max()
    sleep(1.5)

#s1 = AngularServo(14)
#s2 = AngularServo(15)

my_factory = PiGPIOFactory()#pin factory to reduce servo jitter??

#s1 = AngularServo(14, min_pulse_width=0.65/1000, max_pulse_width=2.3/1000, pin_factory=my_factory)
#s2 = AngularServo(15, min_pulse_width=0.65/1000, max_pulse_width=2.3/1000, pin_factory=my_factory)

s1 = AngularServo(14, min_pulse_width=1/1000, max_pulse_width=2/1000, pin_factory=my_factory)
s2 = AngularServo(15, min_pulse_width=1/1000, max_pulse_width=2/1000, pin_factory=my_factory)

while True:
    func1()
