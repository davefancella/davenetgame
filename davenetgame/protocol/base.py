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

import time

from davenetgame import paths
from davenetgame import pedia
from davenetgame import exceptions
from davenetgame.protocol import connection

## These are constants associated with connections.  They generally give the status of the connection.
C_OK = 0
## The connection hasn't responded to pings for 10 seconds
C_SILENT = 1
## The connection hasn't responded to pings for 20 seconds
C_TIMINGOUT = 2
## The connection hasn't responded to pings for 30 seconds.  No further timeout codes will be stored
#  because the connection should be terminated.
C_TIMEOUT = 3
## You are currently not connected to a server
C_DISCONNECTED = 4

## This is a list of connection statuses to be shown to the user.  It's the format [status, useful text],
#  where the index is one of the above constants.
statuslist = [
    ['C_OK', "Ok"],
    ['C_SILENT', "Silent"],
    ['C_TIMINGOUT', "Timing Out"],
    ['C_TIMEOUT', "Timed out"],
    ['C_DISCONNECTED', "Disconnected"]
]


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
    
    ## The local message list object.
    __pedia = None
    
    ## Outgoing messages.  This should be a list of dictionary objects containing a message
    #  class, ready to serialize and send, and a connection to send it to.
    __outgoing_messages = None
    
    ## This is used on the server to maintain a list of connections.  The client uses it, too,
    #  but only keeps one connection on it.  Use ConnectionList() or Connection() to access either
    #  the entire list, or the first connection in the list.
    __connection_list = None
    
    def __init__(self, **args):
        self.__host = 'localhost'
        self.__port = 8888
        self.__name = paths.GetUsername()
        
        if 'transport' in args:
            self.__transport = args['transport']
            
        self.__iscore = False
        
        if 'core' in args:
            self.__iscore = args['core']
            
        self.__pedia = pedia.getPedia()
        
        self.__outgoing_messages = []
        
        self.__callback_messages = []
        
        if self.__iscore:
            self.__connection_list = connection.ConnectionList()

            self.RegisterMessageCallback('ping', self.PingMessage)
            self.RegisterMessageCallback('ack', self.AckMessage)
    
    def Pedia(self):
        return self.__pedia
    
    ## Acks a message
    def Ack(self, msgId, connection):
        theMsg = self.Pedia().GetMessageObject('ack')
        theMsg.replied = msgId
        
        self.AddOutgoingMessage(theMsg, connection)
    
    def ConnectionList(self):
        return self.__connection_list
    
    def Connection(self):
        if len(self.__connection_list) == 1:
            return self.__connection_list[0]
        elif len(self.__connection_list) == 0:
            return None
        else:
            raise exceptions.dngExceptionNotImplemented('Connection list has more than one item on it.')
    
    ## Maintain connections.
    def MaintainConnections(self):
        # If there are no connections, nothing should happen here.
        for con in self.__connection_list:
            self.MaintainConnection(con)
    
    ## Maintain one single connection
    def MaintainConnection(self, con):
        timestep = time.time()
        
        ''' Commented out for now, may need it again later
        # Now, ack all the messages that were received and aren't acks.  Don't ack an ack!
        # ackList is built above from messages that aren't acks and get mostly ignored above.
        if len(ackList) > 0:
            Nmsg = self.__pedia.GetMessageType(mp.M_ACK)()
            Nmsg.mtype = mp.M_ACK
            for nid in ackList:
                Nmsg.replied.append(nid)
            
            self.AddOutgoing(Nmsg)
        
        # Make sure the acklist is empty after this point
        ackList = None
        ackList = [] '''
        
        # Clean out the ping list of expired pings.
        #cleaned_list = [ x for x in self.__pinglist if (timestep - x[1]) < 2.0 ]
        #self.__pinglist = cleaned_list
        
        # Now, send pings and update connection status.
        #if (timestep - con.lastping() ) > 0.98:
        #    self.Ping(timestep)

        timeinterval = timestep - con.lastrecv()
        
        # Update the status of this connection based on how long since we've heard from the
        # other side.
        global C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT
        
        if timeinterval < 10.0:
            con.set_status(C_OK)
        elif (timeinterval >= 10.0) and (timeinterval < 20.0):
            con.set_status(C_SILENT)
        elif (timeinterval >= 20.0) and (timeinterval < 30.0):
            con.set_status(C_TIMINGOUT)
        elif (timeinterval >= 30.0):
            con.set_status(C_TIMEOUT)
    
        # Calculate the connection's ping and store it, after first filtering out intervals that won't be used this time.
        #while len(self.__msgintervals) > 10:
        #    self.__msgintervals.pop(0)
        
        con.CalculatePing()
        
    ## Adds an outgoing message to the queue.
    #
    #  @param msg the message object to send
    #  @param connection the connection to which it will be sent.
    def AddOutgoingMessage(self, msg, connection):
        self.__outgoing_messages.append({ 'message' : msg,
                                          'connection' : connection
                                        }
                                    )
    
    ## Returns a list of outgoing messages.  These have to be retrieved from each Protocol object
    #  associated with the transport and combined into one list where each item is 
    #  of the following format:
    #      'message' : the serialized message
    #      'type' : the TypeID for the message
    #      'connection' : a (host,port) tuple that is the connection to which the message
    #                     must be sent.
    def GetOutgoingMessages(self):
        retList = []
        
        # First, go to all other protocol objects and get their messages.
        # TODO: Implement this
        
        # Now, get all the messages from this protocol object
        while len(self.__outgoing_messages) > 0:
            msg = self.__outgoing_messages.pop(0)

            theMsg = { 'message' : msg['message'].SerializeToString(),
                       'type' : msg['message'].mtype,
                       'connection' : msg['connection'].info() }
            
            retList.append(theMsg)
        
        return retList
    
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

    def Host(self):
        return self.__host
    
    def Port(self):
        return self.__port

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
    def BindTransport(self, transport = None):
        if transport is not None:
            self.__transport = transport
            
        # TODO: make the object bind to the transport
        if self.__transport is not None:
            self.__setupCallbacks()
            
            # TODO: whatever else needs to be done
        else:
            raise exceptions.dngExceptionNotImplemented('Cannot bind protocol to transport: there is no transport.')

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
