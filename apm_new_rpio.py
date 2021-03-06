# import RPIO
from RPIO import PWM


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
p_roll = 12
p_pitch = 16
p_throttle = 18
p_yaw = 22

dma_channel = 0
subcycle_time_us = 20000
pulse_incr_us = 10


def pwm_update(servo, pin, dc):
    dcc = int(dc * subcycle_time_us / 100 / pulse_incr_us) * pulse_incr_us
    servo.set_servo(pin, dcc)


def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv

    '''RPIO.setmode(RPIO.BOARD)
    RPIO.setup(p_roll, RPIO.OUT)
    RPIO.setup(p_pitch, RPIO.OUT)
    RPIO.setup(p_throttle, RPIO.OUT)
    RPIO.setup(p_yaw, RPIO.OUT)'''

    servo = PWM.Servo()

    dc_min = 0.0
    dc_max = 100.0
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

    while True:
        ch = read_single_keypress()
        print(ch, ord(ch))
        if (ch == '\x1b'):  # cannot display
            break
        if (ch == 'w'):
            dc_pitch = dc_change(dc_pitch, '-')
            print("dc_pitch:", dc_pitch)
        elif (ch == 's'):
            dc_pitch = dc_change(dc_pitch, '+')
            print("dc_pitch:", dc_pitch)
        elif (ch == 'a'):
            dc_roll = dc_change(dc_roll, '-')
            print("dc_roll:", dc_roll)
        elif (ch == 'd'):
            dc_roll = dc_change(dc_roll, '+')
            print("dc_roll:", dc_roll)
        elif (ch == 'h'):
            dc_throttle = dc_change(dc_throttle, '-')
            print("dc_throttle:", dc_throttle)
        elif (ch == 'j'):
            dc_throttle = dc_change(dc_throttle, '+')
            print("dc_throttle:", dc_throttle)
        elif (ch == 'k'):
            dc_yaw = dc_change(dc_yaw, '+')
            print("dc_yaw:", dc_yaw)
        elif (ch == 'l'):
            dc_yaw = dc_change(dc_yaw, '-')
            print("dc_yaw:", dc_yaw)
        pwm_update(servo, p_roll, dc_roll)
        pwm_update(servo, p_pitch, dc_pitch)
        pwm_update(servo, p_throttle, dc_throttle)
        pwm_update(servo, p_yaw, dc_yaw)

    servo.stop_servo(p_roll)
    servo.stop_servo(p_pitch)
    servo.stop_servo(p_throttle)
    servo.stop_servo(p_yaw)


if __name__ == "__main__":
    main()
