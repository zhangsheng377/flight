import time
import math
import mpu6050
import RPi.GPIO as GPIO

# Sensor initialization
mpu = mpu6050.MPU6050()
mpu.dmpInitialize()
mpu.setDMPEnabled(True)

# get expected DMP packet size for later comparison
packetSize = mpu.dmpGetFIFOPacketSize()

gap = 5
step = 0.1
pin_left_up = 31
pin_right_up = 33
pin_left_down = 35
pin_right_down = 37
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_left_up, GPIO.OUT, initial=False)
GPIO.setup(pin_right_up, GPIO.OUT, initial=False)
GPIO.setup(pin_left_down, GPIO.OUT, initial=False)
GPIO.setup(pin_right_down, GPIO.OUT, initial=False)
motor_left_up = GPIO.PWM(pin_left_up, 50)
motor_right_up = GPIO.PWM(pin_right_up, 50)
motor_left_down = GPIO.PWM(pin_left_down, 50)
motor_right_down = GPIO.PWM(pin_right_down, 50)
dutycycle_left_up = 100.0
dutycycle_right_up = 100.0
dutycycle_left_down = 100.0
dutycycle_right_down = 100.0
motor_left_up.start(dutycycle_left_up)
motor_right_up.start(dutycycle_right_up)
motor_left_down.start(dutycycle_left_down)
motor_right_down.start(dutycycle_right_down)
dutycycle_limit = 100.0
target_degree_pitch = 0.0
target_degree_roll = 0.0

while True:
    # Get INT_STATUS byte
    mpuIntStatus = mpu.getIntStatus()

    if mpuIntStatus >= 2:  # check for DMP data ready interrupt (this should happen frequently)
        # get current FIFO count
        fifoCount = mpu.getFIFOCount()

        # check for overflow (this should never happen unless our code is too inefficient)
        if fifoCount == 1024:
            # reset so we can continue cleanly
            mpu.resetFIFO()
            print('FIFO overflow!')

        # wait for correct available data length, should be a VERY short wait
        fifoCount = mpu.getFIFOCount()
        while fifoCount < packetSize:
            fifoCount = mpu.getFIFOCount()

        result = mpu.getFIFOBytes(packetSize)
        q = mpu.dmpGetQuaternion(result)
        g = mpu.dmpGetGravity(q)
        ypr = mpu.dmpGetYawPitchRoll(q, g)

        yaw = ypr['yaw'] * 180 / math.pi
        pitch = ypr['pitch'] * 180 / math.pi
        roll = ypr['roll'] * 180 / math.pi

        print(yaw, pitch, roll)

        # track FIFO count here in case there is > 1 packet available
        # (this lets us immediately read more without waiting for an interrupt)        
        fifoCount -= packetSize

        if pitch - target_degree_pitch > gap:
            dutycycle_right_up += step
            dutycycle_right_down += step
            dutycycle_left_up -= step
            dutycycle_left_down -= step
        elif pitch - target_degree_pitch < -gap:
            dutycycle_left_up += step
            dutycycle_left_down += step
            dutycycle_right_up -= step
            dutycycle_right_down -= step
        if roll - target_degree_roll > gap:
            dutycycle_left_up += step
            dutycycle_right_up += step
            dutycycle_left_down -= step
            dutycycle_right_down -= step
        elif roll - target_degree_roll < -gap:
            dutycycle_left_down += step
            dutycycle_right_down += step
            dutycycle_left_up -= step
            dutycycle_right_up -= step

        '''
        if dutycycle_left_up > 100.0:
            dutycycle_left_up = 100.0
        elif dutycycle_left_up < 0.0:
            dutycycle_left_up = 0.0
        if dutycycle_left_down > 100.0:
            dutycycle_left_down = 100.0
        elif dutycycle_left_down < 0.0:
            dutycycle_left_down = 0.0
        if dutycycle_right_up > 100.0:
            dutycycle_right_up = 100.0
        elif dutycycle_right_up < 0.0:
            dutycycle_right_up = 0.0
        if dutycycle_right_down > 100.0:
            dutycycle_right_down = 100.0
        elif dutycycle_right_down < 0.0:
            dutycycle_right_down = 0.0
        '''
        if dutycycle_left_up < 0.0:
            dutycycle_left_up = 0.0
        if dutycycle_right_up < 0.0:
            dutycycle_right_up = 0.0
        if dutycycle_left_down < 0.0:
            dutycycle_left_down = 0.0
        if dutycycle_right_down < 0.0:
            dutycycle_right_down = 0.0
        dutycycle_max = max(dutycycle_left_up, dutycycle_right_up, dutycycle_left_down, dutycycle_right_down)
        '''dutycycle_left_up = dutycycle_left_up / dutycycle_max * dutycycle_limit
        dutycycle_right_up = dutycycle_right_up / dutycycle_max * dutycycle_limit
        dutycycle_left_down = dutycycle_left_down / dutycycle_max * dutycycle_limit
        dutycycle_right_down = dutycycle_right_down / dutycycle_max * dutycycle_limit
        '''
        dutycycle_left_up = dutycycle_limit
        dutycycle_right_up = dutycycle_limit
        dutycycle_left_down = dutycycle_limit
        dutycycle_right_down = dutycycle_limit

        print(dutycycle_left_up, dutycycle_right_up, dutycycle_left_down, dutycycle_right_down)

        motor_left_up.ChangeDutyCycle(dutycycle_left_up)
        motor_right_up.ChangeDutyCycle(dutycycle_right_up)
        motor_left_down.ChangeDutyCycle(dutycycle_left_down)
        motor_right_down.ChangeDutyCycle(dutycycle_right_down)
