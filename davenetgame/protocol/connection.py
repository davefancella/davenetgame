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
class ConnectionBase(object):
    ## The host for this connection
    __host = None
    ## The port for this connection
    __port = None
    ## The ID for this connection
    __id = None
    ## The user's name for this connection
    __player = None
    ## The owner of this connection.  It should be the socket poller that generates message and
    #  event callback calls.
    __owner = None
    ## The list of outgoing messages to this connection.
    __outgoing = None
    
    ## The list of incoming messages to this connection.
    __incoming = None
    
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
    
    ## Local copy of the pedia
    __pedia = None
    
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
    #  @param owner the owner of this connection.  It should be a socket polling object.
    def __init__(self, **args):
        global C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT

        self.__host = args['host']
        self.__port = args['port']
        self.__owner = args['owner']
 
        self.__id = GetConId()
        
        self.__outgoing = []
        self.__incoming = []
        
        self.__status = C_OK
        self.__lastping = time.time()
        self.__lastrecv = time.time()
        
        self.__pedia = pedia.getPedia()
        
        self.__pinglist = []
        self.__acklist = []
        
        self.__msgintervals = []
        
        self.__conping = 0.0
        
    ## The id for this connection
    def id(self):
        return self.__id
    
    ## Returns the pedia object.  Used mainly by subclasses
    def Pedia(self):
        return self.__pedia
    
    ## Returns the current status of the connection
    def Status(self):
        return self.__status
    
    ## Returns the connection ping
    def GetConnectionPing(self):
        return self.__conping
        
    ## Updates the connection.  This is separate from the maintain call.  The maintain call is in the server thread,
    #  while update is called from the main thread.  This is used to pump the callback list and get the callbacks
    #  called.
    def Update(self, timestep):
        pass
        
    ## Returns the owner of this connection.
    def Owner(self):
        return self.__owner
    
    ## Acquires a lock.  Used for thread safety.
    def AcquireLock(self):
        self.__owner.AcquireLock()
        
    ## Releases a lock.  Used for thread safety.
    def ReleaseLock(self):
        self.__owner.ReleaseLock()
    
    ## All of the logic for maintaining a connection is kept here, but the actual message 
    #  sending isn't handled here.  The timestep parameter should be a timestamp from the 
    #  server.  This runs in the server thread, so it should keep itself in its own space and 
    #  not bother anything else.  Use the incoming and outgoing message queues to exchange 
    #  information with the rest of the app, making sure to use the __lock object to avoid 
    #  thread collisions on the queues.
    def maintain(self, timestep):
        # First, process incoming messages.  We do this first so that the housekeeping messages
        # received are all processed before updating the connection status and sending new pings.
        ackList = []
        self.AcquireLock()
        while self.HasIncoming():
            msg = None
            msg = self.__incoming.pop(0)
            
            #print ":", len(self.__incoming), msg
            
            # If we've received a message, so mark lastrecv accordingly
            self.__lastrecv = timestep
            
            # First, build a list of message id's that will need to be acked.
            # Check the message type and respond to housekeeping messages.
            if msg.mtype == mp.M_ACK:
                # Don't ack an ack!
                # First we'll search the ping list.  These are pings waiting to be acked.  We'll remove each
                # one from the list as they're acked.
                pingAcked = False
                cleaned_list = []
                for replyId in msg.replied:
                    for x in self.__pinglist:
                        if x[0] == replyId:
                            # This means we've received a ping ack, and treat it as though we've pinged.
                            pingAcked = True
                            
                            pingInterval = timestep - x[1]
                            
                            self.__msgintervals.append(pingInterval)
                        else:
                            # If this ping isn't acked, keep it in the list
                            cleaned_list.append(x)
                    self.__pinglist = cleaned_list
                    cleaned_list = []
                    # Now do the same thing, looking through non-ping messages.
                    # @@todo make this actually work
                    for x in self.__acklist:
                        if x[0] == replyId:
                            # We actually treat every ack we receive as evidence of a healthy connection, and
                            # update accordingly.
                            pingAcked = True
                            
                            # Here is where the stuff goes for calculating ping                            
                            pingInterval = timestep - x[1]
                            
                            self.__msgintervals.append(pingInterval)
                        else:
                            # If this message isn't acked, keep it in the list
                            cleaned_list.append(x)
                    self.__acklist = cleaned_list
                if pingAcked:
                    self.__lastping = timestep
            else:
                ackList.append(msg.id)
                #pass
        
        self.ReleaseLock()
            
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
        ackList = []
        
        # Clean out the ping list of expired pings.
        cleaned_list = [ x for x in self.__pinglist if (timestep - x[1]) < 2.0 ]
        self.__pinglist = cleaned_list
        
        # Now, send pings and update connection status.
        if (timestep - self.__lastping) > 0.98:
            self.Ping(timestep)

        timeinterval = timestep - self.__lastrecv
        
        # Update the status of this connection based on how long since we've heard from the
        # other side.
        global C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT
        
        if timeinterval < 10.0:
            self.__status = C_OK
        elif (timeinterval >= 10.0) and (timeinterval < 20.0):
            self.__status = C_SILENT
        elif (timeinterval >= 20.0) and (timeinterval < 30.0):
            self.__status = C_TIMINGOUT
        elif (timeinterval >= 30.0):
            self.__status = C_TIMEOUT
    
        # Calculate the connection's ping and store it, after first filtering out intervals that won't be used this time.
        while len(self.__msgintervals) > 10:
            self.__msgintervals.pop(0)
        
        # Avoid a division by zero error that should never happen
        if len(self.__msgintervals) > 0:
            self.__conping = sum(self.__msgintervals)/len(self.__msgintervals)

    ## Pings the other side
    def Ping(self, timestep):
        thePing = self.__pedia.GetMessageType(mp.M_PING)()
        thePing.mtype = mp.M_PING
        thePing.timestamp = timestep
        
        self.__lastping = timestep
        
        theId = self.AddOutgoing(thePing, timestep)
        self.__pinglist.append( [theId, timestep] )
        
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
        if timestep is None:
            msg.timestamp = time.time()
        
        msg.id = mp.get_id()
        
        self.AcquireLock()
        self.__outgoing.append(msg)
        self.ReleaseLock()
        
        return msg.id

    ## Gets the next outgoing message.
    def NextOutgoing(self):
        self.AcquireLock()
        ret = self.__outgoing.pop(0)
        self.ReleaseLock()
        
        return ret
    
    ## Adds an incoming message to the queue.
    def AddIncoming(self, msg):
        if msg.mtype == mp.M_ACK and len(msg.replied) == 0:
            raise Exception
        self.AcquireLock()
        self.__incoming.append(msg)
        self.ReleaseLock()
        
    ## Returns True if there are incoming messages to process, false otherwise.
    def HasIncoming(self):
        if len(self.__incoming) > 0:
            return True
                
        return False
        
    ## Returns a tuple of the connection information suitable for passing to a socket.
    def info(self):
        return (self.host(), self.port() )
    
    ## Returns the host for the connection.
    def host(self):
        return self.__host
    
    ## Returns the port for the connection.
    def port(self):
        return self.__port
    
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

## This class represents a connection to a server from the client.
class ClientConnection(ConnectionBase):
    def __init__(self, **args):
        super().__init__(**args)

## This class represents a single connection on the server with a client.  Currently, only one
#  player per connected client is supported.
class ServerConnection(ConnectionBase):
    ## When you instantiate an nConnection, you must give it a host and port.  There's
    #  no such thing as a connection without one.
    def __init__(self, **args):
        super().__init__(**args)
        global C_OK, C_SILENT, C_TIMINGOUT, C_TIMEOUT
        
        self.__player = args['player']
            
    ## Tell the connection to login, which at this time consists of sending an ack to the connected
    #  client and starting connection maintenance.
    def Login(self, loginPacket):
        # Send the ack.
        msg = self.Pedia().GetMessageType('ack')()
        msg.mtype = self.Pedia().GetMessageId('ack')
        msg.replied.append(loginPacket.id)
        
        self.AddOutgoing(msg)
        
        self.Owner().AddEvent('login', loginPacket)
        
    ## Returns the player for the connection
    def player(self):
        return self.__player
    
    def setPlayer(self, name):
        self.__player = name
    

## This class is a list of connections on the server.  It behaves like a list, and ideally should be able
#  to be used exactly like a list.
class ServerConnectionList(object):
    __connections = None
    
    def __init__(self):
        self.__connections = []
        
    def __len__(self):
        return len(self.__connections)
        
    ## Create a new connection that points to the address given by address.
    def Create(self, address, player, server):
        if address not in self.__connections:
            newCon = ServerConnection(address[0], address[1], player, server)
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

    ## Called by the server to maintain connections, send pings and so forth to see who's still connected.
    def maintain(self, timestep):
        for a in self.__connections:
            a.maintain(timestep)

    ## Called by the main thread to update connections.  This is mostly needed to implement the callback interface.
    def Update(self, timestep):
        for a in self.__connections:
            a.Update(timestep)

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
        
        
        
        
        
        
        
        
