from ..config import DEBUG

LOG_PREFIX = "Tomato Time"


def debug(*msg):
    if DEBUG:
        print("[%s %s]" % (LOG_PREFIX, "Debug"), " ".join([str(x) for x in msg]))


def info(*msg):
    print("[%s %s]" % (LOG_PREFIX, "Info"), " ".join([str(x) for x in msg]))


def warning(*msg):
    print("[%s %s]" % (LOG_PREFIX, "Warning"), " ".join([str(x) for x in msg]))


def error(*msg):
    print("[%s %s]" % (LOG_PREFIX, "Error"), " ".join([str(x) for x in msg]))
