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






