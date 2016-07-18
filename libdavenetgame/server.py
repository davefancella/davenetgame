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

## This file contains the basic Server class, which creates a UDP server capable of handling multiple
#  connections.  It allows unauthenticated access to a Lobby and can transfer to a Game.  Authentication
#  should be handled by a subclass or something like that.

import socket
import threading
import select, time
import struct

from libdavenetgame import connection
from libdavenetgame.messages import pedia
## Use mp to access the constants and lists in messageList
from libdavenetgame.messages import messageList as mp

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
    
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        
        self.__pedia = pedia.getPedia()
        
        self.__continue = False
    
        self.__connections = connection.nConnectionList()

    ## Returns the list of connections from the server
    def GetConnectionList(self):
        return self.__connections

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
        #now keep talking with the client
        while self.__continue:
            inF, outF, errF = select.select( [self.__socket],  [self.__socket], [self.__socket], 5)
            
            for ins in inF:
                # receive data from client (data, addr)
                d = self.__socket.recvfrom(1024)
                data = d[0]
                addr = d[1]
                
                if not data: 
                    break
                
                padding = len(data) - 4
                formatString = "!I" + str(padding) + "s"
                theId, payload = struct.unpack(formatString, data)
                
                if addr not in self.__connections:
                    if theId not in mp.noLogin:
                        # You must be logged in, and you aren't, so discard the message and ignore it.
                        continue
                    else:
                        buf = self.__pedia.GetMessageType(theId)()
                        buf.ParseFromString(payload)
                        
                        # Login the user, send a response
                        if theId == mp.M_LOGIN:
                            newCon = self.__connections.Create(addr, buf.player)
                            newCon.Login(buf)
                            print "User " + buf.player + " has logged in."
                            
                        continue
                
                # Now that we've established the user is connected, get the connection for the user.
                con = self.__connections.GetConnection(addr)
                buf = self.__pedia.GetMessageType(theId)()
                
                buf.ParseFromString(payload)
                
                if theId == mp.M_LOGIN:
                    # Ignore login requests from users already logged in
                    pass
                elif theId == mp.M_LOGOUT:
                    print "User " + con.player() + " has logged out."
                    # @todo Add the callback for calling into the game so the game can respond to logouts.
                    self.__connections.Remove(con)
                    
                print buf
            
            # Maintain connections.  At this point, all that the connections will do is queue up their
            # own internal messages, which will be flushed later.
            self.__connections.maintain(time.time() )
            
            # Send messages queued up by each connection.  Send one to each connection, going round-robin
            # until all connections have been serviced.
            while self.__connections.HasOutgoing():
                for con in self.__connections:
                    if con.HasOutgoing():
                        print "Sending message for connection", con
                        msg = con.NextOutgoing()
                        
                        msg.id = mp.get_id()
                        msg.mtype = self.__pedia.GetTypeID(msg)
                        payload = msg.SerializeToString()
                        
                        # Encode the message
                        payload = struct.pack("!I", msg.mtype) + payload
                        
                        self.__socket.sendto(payload, con.info() )
            
            time.sleep(0.01)
            
        self.__socket.close()


