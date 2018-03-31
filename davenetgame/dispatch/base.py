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

from davenetgame import callback

## @file dispatcher
#
#  This file contains the base dispatcher class, used to connect the network library 
#  directly to the game.

class DispatcherBase(object):
    ## The list of protocols being used
    __protocols = None
    
    ## The core protocol being used
    __core_protocol = None
    
    ## The list of callback functions for events
    __callbacks = None
    
    def __init__(self, **args):
        self.__protocols = []
        
        self.__callbacks = callback.CallbackList()
        
        if 'protocols' in args:
            self.__protocols = args['protocols']
            
        self.__core_protocol = None
    
    ## Call this every time your game loop loops to keep events moving.  It is not optional.
    def Update(self, timestep):
        self.__core_protocol.Update(timestep)
    
    def AddProtocol(self, protocol):
        self.__protocols.append(protocol)
        
    def Start(self):
        for prot in self.__protocols:
            prot.RegisterEventCallback(self.ProcessEvent)
            if prot.IsCore():
                if self.__core_protocol is None:
                    self.__core_protocol = prot
        self.__core_protocol._start()
        
    def Stop(self):
        self.__core_protocol._stop()
        
    def ProcessEvent(self, event):
        for cb in self.GetCallbacks(event['type']):
            print(event)
            cb.setargs(event)
            cb.Call()

    ## Register an event callback.
    #
    #  @param etype the type of event for which this callback will be called.
    #  @param func the function that will be called.  It should take a keyword list of arguments.
    def RegisterCallback(self, etype, func, options={}):
        self.__callbacks.RegisterCallback(etype, func, options)
    
    ## Gets a callback list for a specific event/message.
    def GetCallbacks(self, etype):
        return self.__callbacks.GetCallbacks(etype)
    




