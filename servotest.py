from gpiozero import AngularServo
from time import sleep

# Initialize the servo on GPIO pin 14
# min_pulse_width and max_pulse_width may need to be adjusted for your servo
#14, 15
servo1 = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo2 = AngularServo(15, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
# Function to set the servo angle
def set_angleHorizontal(angle):
    servo1.angle = angle
    sleep(1)
def set_angleVertical(angle):
    servo2.angle = angle
    sleep(1)
def servoTester1():
    i = 0
    n = 0
    while n < 30:
        #angle = int(input("Enter angle (0 to 180): "))  # User input for angle
        set_angleHorizontal(i)  # Set servo to entered angle
        set_angleVertical(150-i)
        print(i," ",n)
        i += 10
        n += 1
        if i == 150:
            i = 0
        #if int(input("")) == -1: break
def horizonTest():
    set_angleHorizontal(0)
    print("horizontal at 0")
    set_angleHorizontal(30)
    print("horizontal at 30")
    set_angleHorizontal(60)
    print("horizontal at 60")
    set_angleHorizontal(90)
    print("horizontal at 90")
    set_angleHorizontal(120)
    print("horizontal at 120")
    set_angleHorizontal(150)
    print("horizontal at 150")

    
def verticalTest():
    set_angleVertical(0)
    print("vertical at 0")
    set_angleVertical(30)
    print("vertical at 30")
    set_angleVertical(60)
    print("vertical at 60")
    set_angleVertical(90)
    print("vertical at 90")
    set_angleVertical(120)
    print("vertical at 120")
    set_angleVertical(150)
    print("vertical at 150")

# Main program loop
horizonTest()
verticalTest()
#servoTester1()

