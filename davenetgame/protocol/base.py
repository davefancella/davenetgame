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

from davenetgame import paths

## @class ProtocolBase
#
#  This class represents the base class for all protocols implemented by the library.  Typically,
#  it is expected that a protocol implementation will have two classes, one each for the client
#  and the server.  It's technically feasible that a basic protocol could be implemented in a
#  single subclass, but this is strongly frowned upon.  In order for a Protocol to function
#  properly, it must be associated with a Transport object.  This means that a Protocol should be
#  able to function regardless of the method by which packets are exchanged in a connection,
#  rendering some protocols more useful than others, depending on the underlying transport layer.
#  For example, implementing a file transfer protocol for a UDP transport layer is sensible,
#  but implementing one for a TCP transport layer may not be, unless you need to be able to
#  transfer files while still exchanging other game information, such as nSyncObjects.
class ProtocolBase(object):
    ## The host for this protocol.  Exactly what it means is determined by the subclass,
    #  but usually it means the host you're connecting to as a client, or the host you are as
    #  a server.
    __host = None
    
    ## The port for this protocol.  Exactly what it means is determined by the subclass,
    #  but usually it means the port you're connecting to as a client, or the port you are
    #  listening to as a server.  Default value assumes you're a server.
    __port = None
    
    ## Your username.  This is just here for convenience.
    __name = None

    ## The transport object for this protocol
    __transport = None
    
    ## The list of callback messages that have to be bound to the transport object.
    __callback_messages = None
    
    ## Designated whether or not this protocol is a core protocol, meaning whether or not 
    #  it can initiate, terminate, and maintain connections.  Default is false, you must
    #  explicitly set this in your subclass.
    __iscore = None
    
    ## The event callback function.  It will be called whenever a network even happens.
    __event_callback = None
    
    def __init__(self, **args):
        self.__host = 'localhost'
        self.__port = 8888
        self.__name = paths.GetUsername()
        
        if 'transport' in args:
            self.__transport = args['transport']
            
        self.__iscore = False
        
        if 'core' in args:
            self.__iscore = args['core']
            
        self.__callback_messages = []
        
        if self.__iscore:
            self.RegisterMessageCallback('ping', self.PingMessage)
            self.RegisterMessageCallback('ack', self.AckMessage)
            
    ## @name Callback Methods
    #
    #  These are the callback methods for particular messages.
    #@{
    
    ## Callback for ack messages.
    def AckMessage(self, **args):
        pass
    
    ## Callback for ping messages
    def PingMessage(self, **args):
        pass
    
    #@}
    
    ## Call to determine if this is the core protocol object.  Used by the EventDispatcher
    #  when there are multiple protocols to figure out which one to start.
    def IsCore(self):
        return self.__iscore
    
    def SetHost(self, host):
        self.__host = host
        
    def SetPort(self, port):
        # Ensure the port is always an int
        self.__port = int(port)

    def SetName(self, name):
        self.__name = name
        
    def Name(self):
        return self.__name

    def SetTransport(self, transport):
        self.__transport = transport
        
    def Transport(self):
        return self.__transport
    
    ## Bandwidth used
    def Bandwidth(self):
        self.__transport.AcquireLock()
        bw = self.__transport.BytesSent() + self.__transport.BytesReceived()
        self.__transport.ReleaseLock()
        
        return bw
    
    ## Bytes sent
    def BytesSent(self):
        self.__transport.AcquireLock()
        bw = self.__transport.BytesSent()
        self.__transport.ReleaseLock()
        
        return bw
    
    ## Bytes received
    def BytesReceived(self):
        self.__transport.AcquireLock()
        bw = self.__transport.BytesReceived()
        self.__transport.ReleaseLock()
        
        return bw
    
    ## Call this to register your one and only event callback
    def RegisterEventCallback(self, cb):
        self.__event_callback = cb
    
    ## Before you can start the Protocol, you must have a Transport object instantiated, and
    #  you must call SetTransport to tell the Protocol about it.  Then you must call this method
    #  to setup all the message callbacks.  Then, finally, you can start the protocol.
    def BindTransport(self):
        # TODO: make the object bind to the transport
        if self.__transport is not None:
            self.__setupCallbacks()
            
            # TODO: whatever else needs to be done
        else:
            pass
            #raise AnException

    ## When your protocol is setup, 
    #
    #  Your subclass should only implement this method if it provides for initiating and
    #  terminating a connection.  If it's simply an add-on protocol, like a Chat protocol,
    #  then you should not implement this method.  If it's an add-on protocol that *can*
    #  function on its own, then you must not depend on what happens in this method for
    #  the protocol to function, and you need to add some flags to ignore pings and acks.
    def Start(self):
        raise NotImplementedError

    def Stop(self):
        raise NotImplementedError

    ## The actual method called to start the protocol, used internally.
    def _start(self):
        self.__transport._start()
        self.Start()
        
    def _stop(self):
        self.__transport._stopI()
        self.Stop()

    ## Register a message callback.  Games *can* use this, but the mechanism isn't terribly useful.  
    #  For the most part,
    #  simply implement the required callback methods in this class to receive callbacks.  
    #  Required callbacks will
    #  throw an exception.
    def RegisterMessageCallback(self, name, func, options={}):
        self.__callback_messages.append([name, func, options])

    ## This method is called after the server is started to register all the callbacks that 
    #  will be used.
    def __setupCallbacks(self):
        for cb in self.__callback_messages:
            self.__transport.RegisterCallback(cb[0], cb[1], cb[2])

