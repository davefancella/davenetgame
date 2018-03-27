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

## The callback list object.  This object stores the master list of all registered callbacks.
#  It is a singleton, so you can retrieve the list by calling GetCallbackList, however, this
#  should only be used internally.  Callbacks should normally be registered using the appropriate
#  methods in the client/server callback object, even though those objects are just going to
#  store the callbacks here anyway.
class CallbackList(object):
    ## The actual callback list
    __callbacks = None
    
    def __init__(self):
        super().__init__()
        
        self.__callbacks = {
                    "message" : {},
                    "event" : {},
        }

    ## Register a callback.
    #
    #  @param ctype the type of the callback.  Current choices are "message" and "event",
    #               referring, of course, to network messages and network events.
    #  @param name the name of the callback.  It should be a specific message or event type,
    #               such as "chat" or "login" or "timeout".
    #  @param func the function that will be called.  It should take a keyword list of arguments.
    #  @param options the options for the callback, which depends on the callbck type.
    def RegisterCallback(self, ctype, name, func, options={}):
        if ctype in self.__callbacks:
            if name not in self.__callbacks[ctype]:
                self.__callbacks[ctype][name] = {
                                    'callback' : func,
                                    'options' : options,
                                    }
            else:
                pass
                # @todo Raise an exception if someone tries to register more than one callback
                #       for the same ctype and name.
    
    ## Gets a callback object for a specific event/message.
    # 
    #  @param ctype the type of the callback, either 'message' or 'event'
    #  @param name the name of the callback.
    def GetCallback(self, ctype, name):
        if ctype in self.__callbacks:
            if name in self.__callbacks[ctype]:
                return callback.Callback(name=name, 
                                         callback=self.__callbacks[ctype][name]['callback'], 
                                         options=self.__callbacks[ctype][name]['options'] )
            else:
                pass
                # @todo Throw an exception here for not finding the callback.
        # @todo Throw an exception here for not finding the callback type.
        return None
    
    ## Returns the options for the specified callback.  It does not return the actual callback
    #  itself, just the options for it.
    def GetCallbackOptions(self, ctype, name):
        if ctype in self.__callbacks:
            if name in self.__callbacks[ctype]:
                return self.__callbacks[ctype][name]['options']
            
        # @todo EXCEPTIONS EVERYWHERE NEED THEM EVERYWHERE!!!!
        return None
    
__callbacklist = None

def GetCallbackList():
    global __callbacklist
    
    if __callbacklist is None:
        __callbacklist = CallbackList()
        
    return __callbacklist

## The callback class, used when a callback has to be queued up to be called from the main thread.
class Callback(object):
    ## The function that will be called.
    __callback = None
    ## The name of the callback.
    __name = None
    ## The argument list for when the callback is executed
    __args = None
    ## The options for the callback
    __options = None
    
    def __init__(self, **args):
        if 'callback' in args:
            self.__callback = args['callback']
        
        self.__options = {}
        if 'options' in args:
            self.__options = args['options']
        
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

