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


def pwm_update(p, dc):
    p.ChangeDutyCycle(dc)


def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)

    dc_min = 5.0
    dc_max = 75.0
    dc_step = (dc_max - dc_min) / 100.0
    dc_roll = (dc_max - dc_min) / 2.0
    dc_pitch = (dc_max - dc_min) / 2.0
    dc_throttle = 0.0
    dc_yaw = (dc_max - dc_min) / 2.0

    p_roll = GPIO.PWM(12, 50)  # channel=12 frequency=50Hz
    p_roll.start(dc_roll)
    p_pitch = GPIO.PWM(16, 50)
    p_pitch.start(dc_pitch)
    p_throttle = GPIO.PWM(18, 50)
    p_throttle.start(dc_throttle)
    p_yaw = GPIO.PWM(22, 50)
    p_yaw.start(dc_yaw)

    while True:
        ch = read_single_keypress()
        print(ch, ord(ch))
        if (ch == '\x1b'):  # cannot display
            break
        if (ch == 'w'):
            dc_pitch = dc_change(dc_pitch, '-')
        elif (ch == 's'):
            dc_pitch = dc_change(dc_pitch, '+')
        elif (ch == 'a'):
            dc_roll = dc_change(dc_roll, '-')
        elif (ch == 'd'):
            dc_roll = dc_change(dc_roll, '+')
        elif (ch == 'h'):
            dc_throttle = dc_change(dc_throttle, '-')
        elif (ch == 'j'):
            dc_throttle = dc_change(dc_throttle, '+')
        elif (ch == 'k'):
            dc_yaw = dc_change(dc_yaw, '+')
        elif (ch == 'l'):
            dc_yaw = dc_change(dc_yaw, '-')
        pwm_update(p_roll, dc_roll)
        pwm_update(p_pitch, dc_pitch)
        pwm_update(p_throttle, dc_throttle)
        pwm_update(p_yaw, dc_yaw)

    p_roll.stop()
    p_pitch.stop()
    p_throttle.stop()
    p_yaw.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    main()
