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

import threading

from davenetgame import pedia
from davenetgame import callback

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

## The base class for connection objects.  It has all the stuff needed on both clients and
#  servers that is common to connections.  Don't use this class directly, use either
#  ServerConnection on the server or ClientConnection on the client.  Even then, you probably
#  don't need to worry about these things.  They're low level.
class Connection(object):
    ## The host for this connection
    __host = None
    ## The port for this connection
    __port = None
    ## The ID for this connection
    __id = None
    ## The player object for this connection
    __player = None
    
    ## The status of the current connection
    __status = None
    
    ## The time of the last ping sent
    __lastping = None
    
    ## The time the last message was received from the other side
    __lastrecv = None
    
    ## These are pings that are waiting to be answered.  About 60 seconds worth of pings are kept.
    #  Format of the items is [id, timestamp], where timestamp is when the ping was sent.
    __pinglist = None
    
    ## These are other messages that are waiting to be answered.
    #  Format of the items is [id, timestamp], where timestamp is when the message was sent.
    __acklist = None
    
    ## Time intervals for messages that were acked.  The server uses this to calculate the client's ping.
    __msgintervals = None
    
    ## The ping, as a float, for the connection.  This is calculated by taking an average of the time it took
    #  for a message to be acked, and only concerns messages that have been acked.  It could be a spurious value
    #  in more serious packet loss situations.
    #  @@todo make this calculation take into account packet loss.
    __conping = None
        
    ## Create a connection.
    #
    #  @param host the host at the other end of the connection.
    #  @param port the port at the other end of the connection
    def __init__(self, **args):
        global C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT

        self.__host = args['host']
        self.__port = args['port']
        
        if 'player' in args:
            self.__player = args['player']
 
        self.__id = GetConId()
        
        self.__status = C_OK
        self.__lastping = time.time()
        self.__lastrecv = time.time()
        
        self.__pinglist = []
        self.__acklist = []
        
        self.__msgintervals = []
        
        self.__conping = 0.0
        
    ## The id for this connection
    def id(self):
        return self.__id
    
    ## Change the id for this connection.  This is typically only used on the client after the
    #  server has sent it its new login information.
    def SetId(self, newId):
        self.__id = newId
    
    ## Returns the current status of the connection
    def Status(self):
        return self.__status
    
    ## Returns the connection ping
    def GetConnectionPing(self):
        return self.__conping

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
    
    ## @name Connection Maintenance
    #
    #  Accessors for maintaining the connection
    #@{
    def lastrecv(self):
        return self.__lastrecv
    
    def set_lastrecv(self, timestamp):
        self.__lastrecv = timestamp
    
    def status(self):
        return self.__status
    
    def set_status(self, status):
        self.__status = status
    
    def ping(self):
        return self.__conping
    
    def lastping(self):
        return self.__lastping
    
    def set_lastping(self, timestamp):
        self.__lastping = timestamp
    #@}
    
    def CalculatePing(self):
        # Avoid a division by zero error that should never happen
        if len(self.__msgintervals) > 0:
            self.__conping = sum(self.__msgintervals)/len(self.__msgintervals)
    
    
    ## Return a string for the connection
    def __str__(self):
        #return self.__player + "@" + self.__host + ":" + str(self.__port)
        return self.__host + ":" + str(self.__port)
    
    def __eq__(self, other):
        if type(other) == type(self):
            ## This is the main comparison, the other two are simply integrity checks.  Or this is a bug.
            if self.id() == other.id():
                if other.host() == self.__host:
                    if other.port() == self.__port:
                        return True
        elif type(other) == tuple:
            if self.__host == other[0]:
                if self.__port == other[1]:
                    return True
        
        return False
        

# Convenient line to copy the global statement for methods that need it.
# global C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT

## The last ID assigned to a connection
__lastId = 0

def GetConId():
    global __lastId
    
    __lastId += 1
    
    return __lastId


## This class is a list of connections on the server.  It behaves like a list, and ideally 
#  should be able to be used exactly like a list.
class ConnectionList(object):
    __connections = None
    
    def __init__(self):
        self.__connections = []
        
    def __len__(self):
        return len(self.__connections)
        
    def __getitem__(self, item):
        return self.__connections[item]
        
    ## Create a new connection that points to the address given by address.
    def Create(self, address, player):
        if address not in self.__connections:
            newCon = Connection(host=address[0], 
                                port=address[1], 
                                player=player)
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
        
    ## Get connections with the given status.
    #  @param status: one of C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT
    def GetStatus(self, status):
        theList = []
        for a in self.__connections:
            if a.Status() == status:
                theList.append(a)
        
        return theList
        
    def append(self, item):
        self.__connections.append(item)
        
    def pop(self, item = None):
        if item is None:
            return self.__connections.pop()
        
        return self.__connections.pop(item)

    def __iter__(self):
        for a in self.__connections:
            yield a

    ## Returns the connection for the host:port combination
    def GetConnection(self, con):
        for a in self.__connections:
            if con == a:
                return a

    ## Returns True if the con is in the list, where con is a tuple of (host, port).
    def HasConnection(self, con):
        if type(con) is tuple:
            for a in self.__connections:
                if con == a:
                    return True
                
        return False
        
        
        
        
        
        
        
        
