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

import time

from libdavenetgame.messages import pedia
## Use mp to access the constants and lists in messageList
from libdavenetgame.messages import messageList as mp

## These are constants associated with connections.  They generally give the status of the connection.
C_OK = 0
## The connection hasn't responded to pings for 10 seconds
C_SILENT = 1
## The connection hasn't responded to pings for 20 seconds
C_TIMINGOUT = 2
## The connection hasn't responded to pings for 30 seconds.  No further timeout codes will be stored
#  because the connection should be terminated.
C_TIMEOUT = 3


## The last ID assigned to a connection
__lastId = 0

def GetConId():
    global __lastId
    
    __lastId += 1
    
    return __lastId

## This class represents a single connection.  On the server, it's a client connection.  On the client,
#  it's only the server and may not be used at all.  Connections know nothing about sockets.
class nConnection(object):
    ## The host for this connection
    __host = None
    ## The port for this connection
    __port = None
    ## The ID for this connection
    __id = None
    ## The user's name for this connection
    __player = None
    
    ## The list of outgoing messages to this connection.
    __outgoing = None
    
    ## The status of the current connection
    __status = None
    
    ## The time of the last ping
    __lastping = None
    
    ## All pings that haven't been acked yet, by ID.
    __pinglist = None
    
    ## Local copy of the pedia
    __pedia = None
    
    ## These are pings that are waiting to be answered.  About 60 seconds worth of pings are kept.
    #  Only the ID is kept, because that's all that's sent by the ack packet.
    __pings = None

    ## When you instantiate an nConnection, you must give it a host and port.  There's
    #  no such thing as a connection without one.
    def __init__(self, host, port, player):
        self.__host = host
        self.__port = port
        self.__player = player
        self.__id = GetConId()
        
        self.__outgoing = []
        
        self.__status = C_OK
        self.__lastping = time.time()
        
        self.__pedia = pedia.getPedia()
        
        self.__pings = []
        
    ## The id for this connection
    def id(self):
        return self.__id
        
    ## All of the logic for maintaining a connection is kept here, but the actual message sending isn't
    #  handled here.  The timestep parameter should be a timestamp from the server.
    def maintain(self, timestep):
        if (timestep - self.__lastping) > 0.98:
            self.Ping(timestep)
            
            # This loop should only happen if there's either an extreme amount of packet loss, the client
            # has disconnected, or the pings aren't being acked properly.  However, even if the client
            # has disconnected, this loop still shouldn't run because the client times out after 30 seconds.
            while len(self.__pings) > 65:
                self.__pings.pop(0)
    
    ## Tell the connection to login, which at this time consists of sending a LoginAck to the connected
    #  client and starting connection maintenance.
    def Login(self, loginPacket):
        msg = self.__pedia.GetMessageType(mp.M_ACK)()
        msg.mtype = mp.M_ACK
        msg.replied.append(loginPacket.id)
        
        self.AddOutgoing(msg)
    
    ## Pings the other side
    def Ping(self, timestep):
        thePing = self.__pedia.GetMessageType(mp.M_PING)()
        thePing.mtype = mp.M_PING
        thePing.timestamp = timestep
        
        self.__lastping = timestep
        
        theId = self.AddOutgoing(thePing, timestep)
        self.__pings.append(theId)
        
        print "Ping sent."
    
    ## Checks if the connection has outgoing messages to send
    def HasOutgoing(self):
        if len(self.__outgoing) > 0:
            return True
        
        return False
    
    ## Adds an outgoing message to be sent next time update is called.
    #  The msg parameter should be the actual message that will be sent, e.g. the google buffer class.
    #  The id and timestamp will be assigned as it's added to the queue.  Once queued, the message is ready
    #  to send.
    def AddOutgoing(self, msg, timestep=None):
        msg.id = mp.get_id()
        if timestep is None:
            msg.timestamp = time.time()
        
        self.__outgoing.append(msg)
        
        return msg.id

    ## Gets the next outgoing message.
    def NextOutgoing(self):
        return self.__outgoing.pop(0)
        
    ## Returns a tuple of the connection information suitable for passing to a socket.
    def info(self):
        return (self.host(), self.port() )
    
    ## Returns the host for the connection.
    def host(self):
        return self.__host
    
    ## Returns the port for the connection.
    def port(self):
        return self.__port
    
    ## Returns the player for the connection
    def player(self):
        return self.__player
    
    def setPlayer(self, name):
        self.__player = name
    
    ## Return a string for the connection
    def __str__(self):
        return self.__player + "@" + self.__host + ":" + str(self.__port)
    
    def __eq__(self, other):
        if type(other) == type(self):
            ## This is the main comparison, the other two are simply integrity checks.  Or this is a bug.
            if self.__id == other.__id:
                if other.host() == self.__host:
                    if other.port() == self.__port:
                        return True
        elif type(other) == tuple:
            if self.__host == other[0]:
                if self.__port == other[1]:
                    return True
        
        return False
        

## This class is a list of connections.  It behaves like a list, and ideally should be able
#  to be used exactly like a list.
class nConnectionList(object):
    __connections = None
    
    def __init__(self):
        self.__connections = []
        
    ## Create a new connection that points to the address given by address.
    def Create(self, address, player):
        if address not in self.__connections:
            newCon = nConnection(address[0], address[1], player)
            self.append(newCon)
            
            return newCon
        
    ## Remove the connection listed
    def Remove(self, con):
        aCon = None
        
        for a in range(len(self.__connections) ):
            if self.__connections[a] == con:
                aCon = self.__connections.pop(a)
                break
        del aCon
        
    def append(self, item):
        self.__connections.append(item)
        
    def pop(self, item = None):
        if item is None:
            return self.__connections.pop()
        
        return self.__connections.pop(item)

    def __iter__(self):
        for a in self.__connections:
            yield a

    ## Called by the server to maintain connections, send pings and so forth to see who's still connected.
    def maintain(self, timestep):
        for a in self.__connections:
            a.maintain(timestep)

    ## Returns true if any connection has outgoing messages to send
    def HasOutgoing(self):
        for a in self.__connections:
            if a.HasOutgoing():
                return True

    ## Returns the connection for the host:port combination
    def GetConnection(self, con):
        for a in self.__connections:
            if con == a:
                return a

    ## Returns True if the con is in the list, where con is a tuple of (host, port).
    def hasConnection(self, con):
        if type(con) is tuple:
            for a in self.__connections:
                if con == a:
                    return True
                
        return False
        
        
        
        
        
        
        
        
