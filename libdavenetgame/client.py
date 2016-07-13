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

## This file contains the basic Client class, which creates a UDP client capable of connecting to
#  the UDP server created by this library.

import socket
import threading
import select, time
import struct

from libdavenetgame.messages import pedia
from libdavenetgame.messages import messageList as mp

## This class implements the game server network layer.
class nClient(threading.Thread):
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
    
    ## Incoming messages
    __incoming = None
    
    ## Outgoing messages
    __outgoing = None
    
    ## This is the last used message id
    __msgId = None
    
    ## This is the lock that must be called to avoid thread collisions
    __lock = None
    
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        
        self.__pedia = pedia.getPedia()
        
        self.__continue = False
    
        self.__incoming = []
        self.__outgoing = []
        
        self.__msgId = 0
        
        self.__lock = threading.RLock()

    def SetServer(self, host, port):
        self.__host = host
        self.__port = port

    ## Call to start the client.
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
    def Stop(self, blocking=True):
        self.__continue = False
    
        if blocking:
            print "Waiting for client thread to stop"
            self.join()

    ## Call to simply send a ping.
    def SendPing(self):
        thePing = self.__pedia.GetMessageType(mp.M_PING_S)()
        thePing.mtype = mp.M_PING
        self.AddOutgoing(thePing)

    ## Call to send a login to the server, but it can only be done after the client has been started
    def Login(self, name):
        theLogin = self.__pedia.GetMessageType(mp.M_LOGIN_S)()
        theLogin.player = name
        theLogin.mtype = mp.M_LOGIN
        
        self.AddOutgoing(theLogin)

    ## Call to send a logout to the server, but it can only be done after the client has been started
    def Logout(self):
        theLogin = self.__pedia.GetMessageType(mp.M_LOGOUT)()
        theLogin.mtype = mp.M_LOGOUT
        
        self.AddOutgoing(theLogin)

    ## Adds an outgoing message to be sent next time the socket becomes available
    #  The msg parameter should be the actual message that will be sent, e.g. the google buffer class.
    #  The id will be assigned as it's added to the queue.
    def AddOutgoing(self, msg):
        msg.id = self.__get_id()
        msg.timestamp = time.time()
        
        self.__lock.acquire()
        self.__outgoing.append(msg)
        self.__lock.release()

    ## Returns a new message id.  This is used internally, do not use it externally.
    def __get_id(self):
        self.__msgId += 1
        
        return self.__msgId

    ## Process incoming messages
    def __process_incoming(self):
        pass

    ## Sends outgoing messages.
    def __send_outgoing(self):
        self.__lock.acquire()
        while len(self.__outgoing) > 0:
            b = self.__outgoing.pop(0)
            
            msgType = self.__pedia.GetTypeID(b)
            b.mtype = msgType
            bufpayload = b.SerializeToString()
            payload = struct.pack("!I", msgType) + bufpayload
            self.__socket.sendto(payload, (self.__host, self.__port) )
        self.__lock.release()

    ## Starts the server.  Don't call this directly, instead call Start().
    def run(self):
        #now keep talking with the client
        while self.__continue:
            inF, outF, errF = select.select( [self.__socket],  [self.__socket], [self.__socket], 5)
            
            for ins in inF:
                # receive data from server (data, addr)
                d = self.__socket.recvfrom(1024)
                data = d[0]
                addr = d[1]
                
                if not data: 
                    break
                
                # Discard the unusual packet sent from someone to this connection that isn't the server
                # we've connected to.  This may cause problems with dns lookups which we'll have to fix
                # when they come up.
                #if addr[0] != self.__host:
                #    break
                
                padding = len(data) - 4
                formatString = "!I" + str(padding) + "s"
                theId, payload = struct.unpack(formatString, data)
                print theId
                buf = self.__pedia.GetMessageType(theId)()
                buf.ParseFromString(payload)
                
                # Now we have the message parsed into an object.  What do we do with it?
                # Answer: put it in a list.  When all packets are appropriately listed, then
                # we'll go through each one and do something about them.
                self.__incoming.add( [theId, buf] )
            
            self.__process_incoming()
            
            self.__send_outgoing()
            
            time.sleep(0.01)
        
        self.__send_outgoing()
        
        self.__socket.close()

'''
     
    try :
        #Set the whole string
        s.sendto(msg, (host, port))
         
        # receive data from client (data, addr)
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]
         
        print 'Server reply : ' + reply
     
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
'''



