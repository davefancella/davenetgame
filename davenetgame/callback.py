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
#  This file implements the callback interface used to inform games that they've received net
#  events.  The game can provide their own functions/methods to be called, but for the most 
#  part, inheriting nClientCallback and nServerCallback should be sufficient.
#
#  The Callback class is used internally only and should not be used by games.
#
#  Your callback's name should be the message or event to which it applies.  For example, if you
#  want to respond to Chat messages, the name of that message will be "chat", so your callback
#  should be named "chat".  Callbacks without names will never be called.
#
#  Regardless of where your callback will be called from, it will be passed a list of keyword
#  arguments.  If your callback is used to process network messages, the arguments will be the
#  actual members of the message.  In other situations, the callback arguments will be specified
#  by the documentation for the appropriate situation.
class Callback(object):
    ## The function that will be called.
    __callback = None
    ## The name of the callback.
    __name = None
    ## The argument list for when the callback is executed
    __args = None
    
    def __init__(self, **args):
        if 'callback' in args:
            self.__callback = args['callback']
        
        self.__name = args['name']
        
        self.__args = {}

    def name(self):
        return self.__name

    ## When the callback is queued, call this to set the arguments that it'll need when called.
    #  It takes a keyword list corresponding to the network message that's being responded to,
    #  or the specific network event in the event that there's no network message associated.
    def setargs(self, **args):
        self.__args = args

    def setname(self, name):
        self.__name = name
        
    def setcallback(self, callback):
        self.__callback = callback
    
    ## Actually calls the callback.
    #
    #  @param args A dictionary containing the arguments intended.  It will override the __args
    #              member, in the event of a conflict.
    def callback(self, **args):
        if len(args) = 0:
            self.__callback(**self.__args)
        else:
            self.__callback(**args)
        
    def getcallback(self):
        return self.__callback
        
    ## Returns a copy of this object, setting the arguments to **args
    @classmethod
    def new(cls, **args):
        newObj = cls(**args)
        
        return newObj

