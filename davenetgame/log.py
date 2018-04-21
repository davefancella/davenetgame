#!/usr/bin/env python3

'''

   Copyright 2016 Dave Fancella

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

'''

import time, sys, os

import inspect

# Set the log level.  0 is no logging, while negative numbers are debug messages not useful
# for logging.
loglevel = -5

stdout = None
stderr = None

def stack():
    global loglevel
    
    if loglevel == -5:
        print("Current call stack:")
        for a in reversed(inspect.stack() ):
            if a.filename.startswith("/usr/lib"):
                pass
            else:
                print("   " + a.function + " from file " + a.filename + " at line: " + str(a.lineno) )


def logger(errfile, logfile):
    global stdout, stderr
    
    stderr = open(errfile,  'a+')
    stdout = open(logfile,  'a+')
    
    sys.stdout = stdout
    sys.stderr = stderr

def errwriter(message):
    global stderr
  
    stderr.write(time.strftime('%Y.%m.%d.%H.%M.%S: '))
    stderr.write(message)
  
def logwriter(message):
    global stdout, stderr
    
    stdout.write(time.strftime('%Y.%m.%d.%H.%M.%S: '))
    stdout.write(message)
    stdout.write('\n')
    
    
    
    
