#!/usr/bin/env python

'''

    This file is part of Dave's Stupid Network Game Library.

    Dave's Stupid Network Game Library is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Dave's Stupid Network Game Library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Dave's Stupid Network Game Library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  00111-1307  USA

    Dave's Stupid Network Game Library is copyright 2016 by Dave Fancella

'''

import time, sys, os

stdout = None
stderr = None

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
    
    
    
    