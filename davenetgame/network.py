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

import threading

from davenetgame import callback

## @file
#
#  Ok, so it seems silly at first to have a generic "network" module in a network library,
#  but this file contains the base class for both client and server objects.  There is a fair
#  amount of code shared.

class NetworkBase(threading.Thread):
    ## This is the lock that must be called to avoid thread collisions
    __lock = None
    
    ## Bytes received
    _bytesreceived = None
    
    ## Bytes sent
    _bytessent = None
    
    ## Buffer size, used for all connections, since you can't know which connection has sent 
    #  you a packet until you do the socket read, and you need this to do the read.
    _buffersize = None
    
    ## The list of callbacks that will be called.
    __callbacks = None
    
    ## The queue of callbacks waiting to be called.  This list is populated from inside the server thread and executed
    #  during the server's update method, which is called from the main thread.
    callbackqueue = None
    
    ## The owner of this Network object.
    __owner = None
        
    def __init__(self, **args):
        super().__init__(**args)

        if 'owner' in args:
            self.__owner = args['owner']

        self.__lock = threading.RLock()
        
        self._bytesreceived = 0
        self._bytessent = 0
        
        self._buffersize = 1024
        
        self.__callbacks = {}
        
        self.callbackqueue = []

    ## Register a message callback.
    #
    #  @param name the name of the callback.
    #  @param func the function that will be called.  It should take a keyword list of arguments.
    def RegisterMessageCallback(self, name, func, options={}):
        self._registerCallback("message", name, func, options)
        
    ## Register an event callback.
    #
    #  @param name the name of the callback.
    #  @param func the function that will be called.  It should take a keyword list of arguments.
    def RegisterEventCallback(self, name, func, options={}):
        self._registerCallback("event", name, func, options)
        
    ## Register a callback.  This is used internally only.  Please use the appropriate callback
    #  registration method for your purpose.
    def _registerCallback(self, ctype, name, func, options={}):
        cbList = callback.GetCallbackList()
        
        cbList.RegisterCallback(ctype, name, func, options)
    
    ## Gets a callback object for a specific event/message.
    def GetCallback(self, ctype, name):
        cbList = callback.GetCallbackList()
        
        return cbList.GetCallback(ctype, name)
    
    ## Appends a callback object to the callbackqueue.  Callbackqueue only takes event callbacks.
    #  Message callbacks are handled immediately from within the socket polling thread.
    def AppendCallback(self, cb):
        self.callbackqueue.append(cb)

    ## Used to acquire a lock when working with data structures shared with the main thread
    def AcquireLock(self):
        self.__lock.acquire()
    
    ## Used to release the lock when done working with data structures shared with the main thread
    def ReleaseLock(self):
        self.__lock.release()

