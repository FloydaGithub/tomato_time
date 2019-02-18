DEBUG = True
LOG_PREFIX = 'Tomato Time'


def debug(msg):
    if DEBUG:
        print('[%s %s]' % (LOG_PREFIX, 'Debug'), msg)


def info(msg):
    print('[%s %s]' % (LOG_PREFIX, 'Info'), msg)


def warning(msg):
    print('[%s %s]' % (LOG_PREFIX, 'Warning'), msg)


def error(msg):
    print('[%s %s]' % (LOG_PREFIX, 'Error'), msg)
