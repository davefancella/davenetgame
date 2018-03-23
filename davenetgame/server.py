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

## This file contains the basic Server class, which creates a UDP server capable of handling multiple
#  connections.  It allows unauthenticated access to a Lobby and can transfer to a Game.  Authentication
#  should be handled by a subclass or something like that.

import socket
import threading
import select, time
import struct

from davenetgame import connection
from davenetgame.messages import pedia
## Use mp to access the constants and lists in messageList
from davenetgame.messages import messageList as mp

## This class implements the game server network layer.
class nServer(threading.Thread):
    ## The host the server listens on.  It'll most likely be an IP address, but it can
    #  be a qdn.
    __host = None
    
    ## The port the server listens on
    __port = None
    
    ## The socket
    __socket = None
    
    ## Do we continue the thread?
    __continue = None
    
    ## This is the list of message types
    __pedia = None
    
    ## The list of current connections
    __connections = None

    ## This is the lock that must be called to avoid thread collisions
    __lock = None
    
    ## Bytes received
    __bytesreceived = None
    
    ## Bytes sent
    __bytessent = None
    
    ## Buffer size, used for all connections, since you can't know which connection has sent you a packet
    #  until you do the socket read.
    __buffersize = None
    
    ## The list of callbacks that will be called.
    __callbacks = None
    
    ## The queue of callbacks waiting to be called.  This list is populated from inside the server thread and executed
    #  during the server's update method, which is called from the main thread.
    __callbackqueue = None
        
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        
        self.__pedia = pedia.getPedia()
        
        self.__continue = False
    
        self.__connections = connection.nConnectionList()
        
        self.__lock = threading.RLock()
        
        self.__bytesreceived = 0
        self.__bytessent = 0
        
        self.__buffersize = 1024
        
        self.__callbacks = {}
        
        self.__callbackqueue = []

    ## Register a callback function with the server.  The callback will be executed in the main thread, not the
    #  server network polling thread.  A Callback object is expected here, where in server_callback the expected
    #  object is the function object.  There must be a timestep argument because when the callback is called,
    #  the timestep will be sent.  Other arguments needed will be named by the callbacks.
    def RegisterCallback(self, cbObj):
        self.__callbacks[cbObj.name()] = cbObj
    
    ## Returns a new callback instance with args set to args, which must be a list
    def GetCallback(self, cb, args):
        newObj = self.__callbacks[cb].new(callback=self.__callbacks[cb].getcallback() )
        newObj.setargs(*args)
        
        return newObj

    ## Appends a callback object to the callbackqueue.
    def AppendCallback(self, cb):
        self.__callbackqueue.append(cb)

    ## Returns the list of connections from the server
    def GetConnectionList(self):
        return self.__connections

    ## Updates the server.  This runs from inside the game thread, not the server thread.
    def Update(self, timestep):
        self.__connections.Update(timestep)
        
        while len(self.__callbackqueue) > 0:
            a = self.__callbackqueue.pop(0)

            a.callback()

    def ListenOn(self, host, port):
        self.__host = host
        self.__port = port

    ## Call to start the server.
    def Start(self):
        # Create the socket
        if self.__host is not None:
            if self.__port is not None:
                error = False
                # create the socket
                # Datagram (udp) socket
                try :
                    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    print 'Socket created'
                except socket.error, msg :
                    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                    error = True
                
                # Bind socket to local host and port
                try:
                    self.__socket.bind((self.__host, self.__port))
                except socket.error , msg:
                    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                    error = True
                if error is False:
                    print 'Socket bind complete'
                else:
                    print "An error occured creating the socket"
            else:
                # Raise an exception indicating no port was given
                pass
        else:
            # Raise an exception indicating no address was given
            pass
        
        if error is False:
            self.__continue = True
            
            self.start()

    ## Stops the server.  It may still take a few seconds or so.  If blocking is "True", then the call will
    #  block until the server has shut down.
    def Stop(self, blocking=False):
        self.__continue = False
    
        if blocking:
            self.join()

    ## Starts the server.  Don't call this directly, instead call Start().
    def run(self):
        while self.__continue:
            inF, outF, errF = select.select( [self.__socket],  [self.__socket], [self.__socket], 5)
            
            for ins in inF:
                # receive data from client (data, addr)
                data, addr = self.__socket.recvfrom(self.__buffersize)
                
                if not data: 
                    break
                
                self.__bytesreceived += len(data)
                
                padding = len(data) - 4
                formatString = "!I" + str(padding) + "s"
                theId, payload = struct.unpack(formatString, data)
                
                # Handle all messages first that don't require being logged in.
                if addr not in self.__connections:
                    if theId not in mp.noLogin:
                        # You must be logged in, and you aren't, so discard the message and ignore it.
                        continue
                    else:
                        buf = self.__pedia.GetMessageType(theId)()
                        buf.ParseFromString(payload)
                        
                        # Login the user, send a response
                        if theId == mp.M_LOGIN:
                            newCon = self.__connections.Create(addr, buf.player, self)
                            newCon.Login(buf)
                            
                        continue
                
                # Now that we've established the user is connected, get the connection for the user.
                con = self.__connections.GetConnection(addr)
                buf = self.__pedia.GetMessageType(theId)()
                
                buf.ParseFromString(payload)
                
                # Logins and logouts are handled here, but everything else is handled by the
                # nConnection objects.
                if theId == mp.M_LOGIN:
                    # Ignore login requests from users already logged in
                    pass
                elif theId == mp.M_LOGOUT:
                    cb = self.GetCallback('logout', [time.time(), con] )
                    self.AppendCallback(cb)

                    self.__connections.Remove(con)
                else:
                    # Delegate to the connection objects to handle everything else.
                    con.AddIncoming(buf)
            
            # Maintain connections.  At this point, all that the connections will do is queue up their
            # own internal messages, which will be flushed later.
            self.__connections.maintain(time.time() )
            
            # Send messages queued up by each connection.  Send one to each connection, going round-robin
            # until all connections have been serviced.
            while self.__connections.HasOutgoing():
                for con in self.__connections:
                    if con.HasOutgoing():
                        msg = con.NextOutgoing()
                        
                        # Only assign an id if an id hasn't already been assigned
                        if msg.id == 0:
                            msg.id = mp.get_id()
                        theMType = self.__pedia.GetTypeID(msg)
                        msg.mtype = theMType
                        payload = msg.SerializeToString()
                        
                        # Encode the message
                        payload = struct.pack("!I", msg.mtype) + payload
                        
                        self.__bytessent += len(payload)
                        
                        self.__socket.sendto(payload, con.info() )
                        
                        del msg
            
            # Look for timeout connections and remove them
            for a in self.__connections.GetStatus(connection.C_TIMEOUT):
                cb = self.GetCallback('timeout', [time.time(), a.player() ] )
                self.AppendCallback(cb)
                
                self.__connections.Remove(con)
                
            
            time.sleep(0.01)
            
        self.__socket.close()


