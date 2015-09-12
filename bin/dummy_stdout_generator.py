#! /usr/bin/python3
import random
import sys
import time

while True:
    sys.stdout.write( "%02x " % random.randint(0,255) )
    sys.stdout.flush()
    sys.stderr.write( "%02x " % random.randint(0,255) )
    sys.stderr.flush()
    t = random.randint(0,2) 
    #print(t)
    time.sleep(t)
