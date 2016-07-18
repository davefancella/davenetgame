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

import exceptions

## @file
#
#  This file contains the exceptions used by the library.  A few standard exceptions are also put here,
#  with the hope that an app developer will only ever need to import this file for exceptions.

## Transparently pass this exception on to the rest of the library.
#KeyboardInterrupt = exceptions.KeyboardInterrupt

## The base class for all library exceptions
class dngException(Exception):
    pass

## This exception is thrown when a required callback method hasn't been implemented.
class dngCallbackNotImplemented(dngException, NotImplementedError):
    pass



