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

## @file
#
#  This file contains the exceptions used by the library.  A few standard exceptions are also put here,
#  with the hope that an app developer will only ever need to import this file for exceptions.

## Transparently pass this exception on to the rest of the library.
#KeyboardInterrupt = exceptions.KeyboardInterrupt

## The base class for all library exceptions
class dngException(Exception):
    pass

## Raise this exception when you haven't yet implemented a specific exception type, but need
#  to raise an exception anyway
class dngExceptionNotImplemented(dngException):
    pass

## This exception is thrown when a required callback method hasn't been implemented.
class dngCallbackNotImplemented(dngException, NotImplementedError):
    pass

## Thrown when someone tries to set an nSyncObject's attribute to a type that is not compatible
#  with the declared type when the attribute was declared.
class dngSyncAttributeTypeError(dngException, TypeError):
    pass

## Thrown when someone tries to add an attribute to an nSyncObject that has already been added.
class dngSyncObjectAttributeError(dngException, Exception):
    pass





