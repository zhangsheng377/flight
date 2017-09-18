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

subcycle_time_us = 20000


def pwm_update(pi, pin, dc):
    dcc = int(dc * subcycle_time_us / 100)
    pi.set_PWM_dutycycle(pin, dcc)


def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv

    import pigpio
    pi = pigpio.pi()
    pi.set_PWM_frequency(p_roll, 50)
    pi.set_PWM_frequency(p_pitch, 50)
    pi.set_PWM_frequency(p_throttle, 50)
    pi.set_PWM_frequency(p_yaw, 50)
    pi.set_PWM_range(p_roll, subcycle_time_us)
    pi.set_PWM_range(p_pitch, subcycle_time_us)
    pi.set_PWM_range(p_throttle, subcycle_time_us)
    pi.set_PWM_range(p_yaw, subcycle_time_us)

    dc_min = 4.55
    dc_max = 10.45
    dc_step = (dc_max - dc_min) / 1000.0
    dc_roll = (dc_max - dc_min) / 2.0
    dc_pitch = (dc_max - dc_min) / 2.0
    dc_throttle = dc_min * 1.01
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
        pwm_update(pi, p_roll, dc_roll)
        pwm_update(pi, p_pitch, dc_pitch)
        pwm_update(pi, p_throttle, dc_throttle)
        pwm_update(pi, p_yaw, dc_yaw)
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

    pi.set_PWM_dutycycle(p_roll, 0)
    pi.set_PWM_dutycycle(p_pitch, 0)
    pi.set_PWM_dutycycle(p_throttle, 0)
    pi.set_PWM_dutycycle(p_yaw, 0)
    pi.stop()


if __name__ == "__main__":
    main()
