#!/usr/bin/env python3

import sys, datetime, math, os

class Frame:
    def __init__(self, f, f_alt, ts, line, et, ls_epoch, epoch, timeraw, timestamp, hmsf, ymd, timeint):
        self.f = f
        self.ts = ts
        self.line = line
        self.f_alt = f_alt
        self.et = et
        self.ls_epoch = ls_epoch
        self.epoch = epoch
        self.timeraw = timeraw
        self.timestamp = timestamp
        self.hmsf = hmsf
        self.ymd = ymd
        self.timeint = timeint

calls = []

for line in open(sys.argv[1]):
#for line in open('/home/a04/iridium-toolkit/data/output-test.parsed'):
    if 'VOC: ' in line:
        sl = line.split()
        ts = float(sl[2])/1000. # seconds
        f = int(sl[3])/1000. # kHz
        et = str(sl[1])
        ls_epoch = [ x for x in et if x.isdigit()]
        epoch = int("".join(ls_epoch))/1000
        timeraw = int(epoch + ts)
        timestamp = datetime.datetime.utcfromtimestamp(timeraw)
        hmsf = math.trunc(int(timestamp.strftime("%H%M%S%f"))/1000000)
        ymd = int(timestamp.strftime("%Y%m%d"))
        timeint = str(hmsf) + '-' + str(ymd)
        frame = Frame(f, 0, ts, line, et, ls_epoch, epoch, timeraw, timestamp, hmsf, ymd, timeint)

        # for line in open(sys.argv[1]):
        
        for call in calls:
            last_frame = call[-1]
            first_frame = call[0]

            # If the last frame is not more than 20 kHz and 20 seconds "away"
            if (last_frame.f_alt and abs(last_frame.f_alt - frame.f) < 40 or abs(last_frame.f - frame.f) < 20) and abs(last_frame.ts - frame.ts) < 20:
                if "handoff_resp" in sl[8]:
                    fields = sl[8].split(',')
                    sband_dn = int(fields[7].split(':')[1])
                    access = int(fields[8].split(':')[1].split(']')[0])
                    #print sband_dn, access
                    frame.f_alt = (1616000000 + 333333 * (sband_dn - 1) + 41666 * (access - 0.5) + 52000) / 1000
                call.append(frame)
                # First call that matches wins
                break
                
            
        else:
            # If no matching call is available create a new one
            calls.insert(0,[frame])
            # print(calls[1])
t_length = str(last_frame.timeraw - first_frame.timeraw)
print('First Epoch: ' + str(first_frame.timeraw) + ' UTC: ' + str(first_frame.timestamp))
print('Last Epoch: ' + str(last_frame.timeraw) + ' UTC: ' + str(last_frame.timestamp))
print('Call Duration: ' + t_length + ' sec')
