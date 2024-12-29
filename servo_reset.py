from gpiozero import AngularServo
from time import sleep

s1 = AngularServo(14, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
s2 = AngularServo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

sleep(1)
s1.mid()
print("Servo 1 reset")
sleep(1)
s2.mid()
print("Servo 2 reset")
sleep(1)
s1.angle = 20
sleep(1)
s2.angle = -70
sleep(1)
