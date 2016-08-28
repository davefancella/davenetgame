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

## @file
#
#  This file implements the callback interface used to inform games that they've received net events.  The game can
#  provide their own functions/methods to be called, but for the most part, inheriting nClientCallback and nServerCallback
#  should be sufficient.

## The base class for callback objects.  Derived classes should be named TypeCallback, where "Type" is a camelcase
#  name, such as Login, Logout, Chat, etc.  The all lowercase string for type will be used internally to reference
#  the callback.
class Callback(object):
    ## The function that will be called.
    __callback = None
    ## The name of the callback.
    __name = None
    ## The argument list for when the callback is executed
    __args = None
    
    def __init__(self, **args):
        if args.has_key('callback'):
            self.__callback = args['callback']
        
        self.__name = args['name']
        
        self.__args = []

    def name(self):
        return self.__name

    ## When the callback is queued, call this to set the arguments that it'll need when called.  It takes the argument
    #  list for the function.
    def setargs(self, *args):
        self.__args = args

    def setname(self, name):
        self.__name = name
        
    def setcallback(self, callback):
        self.__callback = callback

    def callback(self):
        self.__callback(*self.__args)
        
    def getcallback(self):
        return self.__callback
        
    ## Returns a copy of this object, setting the arguments to *args
    @classmethod
    def new(cls, **args):
        newObj = cls(**args)
        
        return newObj

## The login callback class
class LoginCallback(Callback):
    def __init__(self, **args):
        super(LoginCallback, self).__init__(name="login", **args)

## The logout callback class
class LogoutCallback(Callback):
    def __init__(self, **args):
        super(LogoutCallback, self).__init__(name="logout", **args)

## The timeout callback class
class TimeoutCallback(Callback):
    def __init__(self, **args):
        super(TimeoutCallback, self).__init__(name="timeout", **args)






