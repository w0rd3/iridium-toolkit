#!/usr/bin/env python3
# vim: set ts=4 sw=4 tw=0 et fenc=utf8 pm=:

import sys
import os
# import getopt

# options = "h:"

# try:
#     arguments, values = getopt.getopt(options)
#     for currentArgument, currentValue in arguments:
#         if currentArgument in ("-h"):
#             print ("Usage: ./voc-cluster.py [input file] [path to output]")
# except getopt.error as err:
#     # output error, and return with an error code
#     print (str(err))

class Frame:
    def __init__(self, f, f_alt, ts, line):
        self.f = f
        self.ts = ts
        self.line = line
        self.f_alt = f_alt
def clean():
    path=sys.argv[2]
    os.system('rm ' + path + '/fail-*')

# def export():
#     path=sys.argv[2]
#     os.system('ls ' + path + '/call-*.parsed > ' + path + '/index.txt')
#     os.system('for arg in $(< ' + path + '/index.txt); do ~/iridium-toolkit/play-iridium-ambe "$arg"; done')
calls = []

for line in open(sys.argv[1]):
    if 'VOC: ' in line:
        sl = line.split()
        ts = float(sl[2])/1000. # seconds
        f = int(sl[3])/1000. # kHz
        frame = Frame(f, 0, ts, line)

        for call in calls:
            last_frame = call[-1]

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

call_id = 0
for call in calls[::-1]:
    if abs(call[0].ts - call[-1].ts) < 1:
        continue

    samples = [frame.line for frame in call]
    path = sys.argv[2]
    filename = path + '/call-%04d.parsed' % call_id
    open(filename, "w").writelines(samples)
    is_voice = os.system('./check-sample ' + filename) == 0

    if not is_voice:
        os.system('mv ' + filename + ' ' + path + '/fail-%d.parsed' % call_id)
    call_id += 1

    if is_voice:
        os.system('./play-iridium-ambe ' + filename)
        
clean()