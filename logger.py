import sys
import time


class Logger:
    def __init__(self, logfile):
        self.logfile = logfile

    def message(self, s):
        lt = time.gmtime()
        s = "{0:02d}.{1:02d}.{2:04d} {3:02d}:{4:02d}:{5:02d} UTC: {6}\n".format(lt.tm_mday, lt.tm_mon, lt.tm_year,
                                                                                lt.tm_hour, lt.tm_min, lt.tm_sec, s)

        sys.stderr.write(s)
        sys.stderr.flush()

        open(self.logfile, "at").write(s)
