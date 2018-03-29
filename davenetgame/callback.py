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

## The callback list object.  This object stores a list of callbacks.  It is used internally
#  to store registered callbacks by the Transport object as well as the Protocol object.  It
#  can be used by an EventDispatcher object as well, but is not required.
#
#  By default, callbacks are stored as lists for the event to which they refer.  This means
#  that multiple callbacks can be registered for the same event, and they will be called in
#  arbitrary order, unless specified otherwise by callback options.
class CallbackList(object):
    ## The actual callback list
    __callbacks = None
    
    def __init__(self):
        super().__init__()
        
        self.__callbacks = {
        }

    ## Register a callback.
    #
    #  @param name the name of the callback.  It should be a specific message or event type,
    #               such as "chat" or "login" or "timeout".
    #  @param func the function that will be called.  It should take a keyword list of arguments.
    #  @param options the options for the callback, which depends on the callbck type.
    def RegisterCallback(self, name, func, options={}):
        if name not in self.__callbacks:
            self.__callbacks[name] = []
            
        self.__callbacks[name].append({
                                'callback' : func,
                                'options' : options,
                                } )

    ## Gets the list of callback objects for a specific name.  These callback objects can
    #  then be executed immediately, if desired, or scheduled to be executed later, for example
    #  by a different thread.  See Callback for more information.
    # 
    #  @param name the name of the callback.
    def GetCallbacks(self, name):
        if name in self.__callbacks:
            retList = []
            for a in self.__callbacks[name]:
                retList.append( callback.Callback(name=name, 
                                        callback=a['callback'], 
                                        options=a['options'] ) )
            return retList

        # @todo Throw an exception here for not finding the callback type.
        return None
    
    ## Returns the options for the specified callback.  It does not return the actual callback
    #  itself, just the options for it.  Note that only the options for the first registered
    #  callback are returned, and those are usually supplied by the library.
    def GetCallbackOptions(self, name):
        if name in self.__callbacks:
            return self.__callbacks[name][0]['options']
            
        # @todo EXCEPTIONS EVERYWHERE NEED THEM EVERYWHERE!!!!
        return None
    

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
    #  @param args An optional dictionary containing any additional arguments intended for the
    #              callback.  It will be added to the local __args member, if provided.
    def Call(self, **args):
        theArgs = self.__args
        if len(args) > 0:
            for key, value in args:
                theArgs[key] = value
        
        self.__callback(**theArgs)

