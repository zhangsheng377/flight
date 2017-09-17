def read_single_keypress():
    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)  # save old state
    attrs_save = termios.tcgetattr(fd)
    attrs = list(
        attrs_save)  # make raw - the way to do this comes from the termios(3) man page.  # copy the stored version to update
    attrs[0] &= ~(
        termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)  # iflag
    attrs[1] &= ~termios.OPOST  # oflag
    attrs[2] &= ~(termios.CSIZE | termios.PARENB)  # cflag
    attrs[2] |= termios.CS8
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN)  # lflag
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)  # turn off non-blocking
    try:
        ret = sys.stdin.read(1)  # read a single keystroke  # returns a single character
    except KeyboardInterrupt:
        ret = 0
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)  # restore old state
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret


# broad 12,16,18,22 = bcm 18,23,24,25
p_roll = 18
p_pitch = 23
p_throttle = 24
p_yaw = 25

dma_channel = 0
subcycle_time_us = 20000
pulse_incr_us = 3


def pwm_update(servo, pin, dc):
    print("pwm_update dc : ", dc)
    print("pwm_update dc*subcycle_time_us : ", dc * subcycle_time_us)
    print("pwm_update dc*subcycle_time_us/100 : ", dc * subcycle_time_us / 100)
    dcc = int(dc * subcycle_time_us / 100 / pulse_incr_us) * pulse_incr_us
    print("pwm_update dcc pin : ", dcc, pin)
    servo.set_servo(pin, dcc)


def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv

    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(p_roll, GPIO.OUT)
    GPIO.setup(p_pitch, GPIO.OUT)
    GPIO.setup(p_throttle, GPIO.OUT)
    GPIO.setup(p_yaw, GPIO.OUT)

    from RPIO import PWM
    servo = PWM.Servo(dma_channel, subcycle_time_us, pulse_incr_us)
    print("servo init success")

    dc_min = 5.0 - 0.25
    dc_max = 10.0 - 0.25
    dc_step = (dc_max - dc_min) / 100.0
    dc_roll = (dc_max - dc_min) / 2.0
    dc_pitch = (dc_max - dc_min) / 2.0
    dc_throttle = dc_min
    dc_yaw = (dc_max - dc_min) / 2.0

    def dc_change(dc, type):
        if (type == '-'):
            dc -= dc_step
        elif (type == '+'):
            dc += dc_step
        if (dc < dc_min):
            dc = dc_min
        elif (dc > dc_max):
            dc = dc_max
        return dc

    print("pwm_update start")
    pwm_update(servo, p_roll, dc_roll)
    print("pwm_update start1")
    pwm_update(servo, p_pitch, dc_pitch)
    pwm_update(servo, p_throttle, dc_throttle)
    pwm_update(servo, p_yaw, dc_yaw)
    print("pwm_update end")

    print("stop_servo start")
    servo.stop_servo(p_roll)
    servo.stop_servo(p_pitch)
    servo.stop_servo(p_throttle)
    servo.stop_servo(p_yaw)
    print("stop_servo end")


if __name__ == "__main__":
    main()
