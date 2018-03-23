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

## This file contains the basic Client class, which creates a UDP client capable of connecting to
#  the UDP server created by this library.

import socket
import threading
import select, time
import struct

from davenetgame.messages import pedia
from davenetgame import connection
from davenetgame.messages import messageList as mp

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
    
    ## This is the status of our current connection to the server
    __status = None
    
    ## The last time we've received anything from the server
    __lastrecv = None
    
    ## The time the last ping was sent
    __lastping = None
    
    ## Pings waiting to be acked
    __pinglist = None
    
    ## The status of the connection
    __status = None
    
    ## Bandwidth used by the connection.  This is bytes received.
    __bandwidth = None
    
    ## Bytes send.
    __bytessent = None
    
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        
        self.__pedia = pedia.getPedia()
        
        self.__continue = False
    
        self.__incoming = []
        self.__outgoing = []
        
        self.__msgId = 0
        
        self.__lock = threading.RLock()
        
        self.__status = connection.C_DISCONNECTED
        self.__lastrecv = time.time()
        self.__lastping = time.time()
        self.__pinglist = []
        
        self.__bandwidth = 0
        
        self.__bytessent = 0

    def SetServer(self, host, port):
        self.__host = host
        self.__port = port

    def BytesSent(self):
        return self.__bytessent
    
    def BytesReceived(self):
        return self.__bandwidth

    ## Returns the status of the client.
    def Status(self):
        return self.__status

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
                    print('Socket created')
                except OSError as msg:
                    print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] )
                    error = True
                
            else:
                # Raise an exception indicating no port was given
                pass
        else:
            # Raise an exception indicating no address was given
            pass
        
        if error is False:
            self.__continue = True
            
            self.__status = connection.C_OK
            
            self.start()

    ## Stops the client.  It may still take a few seconds or so.  If blocking is "True", then the call will
    #  block until the server has shut down.  The default behavior is to block, because it really doesn't make
    #  sense not to block in most cases.  Be careful, because you may have the main thread ending
    #  with no knowledge of whether or not the client thread has ended.  In that situation, Join() is
    #  provided so you can call this one non-blocking, do your thing, then call Join here to be sure the
    #  thread exits before you end the main program.
    #
    #  @param blocking: If True, this call will block.  If False, it returns immediately and the thread will
    #                   stop itself on its own.  
    def Stop(self, blocking=True):
        self.__continue = False
    
        if blocking:
            self.join()

    ## Call this to join the thread and wait until it closes.  Be careful doing this, because if you haven't
    #  signaled in any way that the thread should end, then your process will continue forever.
    def Join(self):
        self.join()

    ## Call to simply send a ping.
    def SendPing(self):
        thePing = self.__pedia.GetMessageType(mp.M_PING_S)()
        thePing.mtype = mp.M_PING
        self.__lastping = time.time()
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
        ackList = []
        timestep = time.time()
        while len(self.__incoming) > 0:
            self.__lastrecv = timestep
            self.__lock.acquire()
            a = self.__incoming.pop(0)
            self.__lock.release()
            theId, buf = a[0], a[1]
            
            # If the message isn't an ack, put it in the acklist.  Don't ack an ack!
            if theId != mp.M_ACK:
                ackList.append( buf )
            else:
                # @todo: add the stuff to track messages that need to be acked by the server
                pass
        
        if len(ackList) > 0:
            # Ack all incoming messages that need it, determined above.
            theAck = self.__pedia.GetMessageType(mp.M_ACK)()
            theAck.mtype = mp.M_ACK
            for a in ackList:
                theAck.replied.append(a.id)
            # Disable the following line to stop acks from happening.  Useful to test the server's connection
            # maintenance.
            self.AddOutgoing(theAck)
        
        # Do your own maintenance.
        # The client pings every two seconds, but has the same timeout rules otherwise.
        if (timestep - self.__lastping) > 1.98:
            self.SendPing()
            
            # This loop should only happen if there's either an extreme amount of packet loss, the client
            # has disconnected, or the pings aren't being acked properly.  However, even if the client
            # has disconnected, this loop still shouldn't run because the client times out after 30 seconds.
            while len(self.__pinglist) > 65:
                self.__pinglist.pop(0)

        # Now, send pings and update connection status.
        timeinterval = timestep - self.__lastrecv
        
        # Update the status of this connection based on how long since we've heard from the server.
        if timeinterval < 10.0:
            self.__status = connection.C_OK
        elif (timeinterval >= 10.0) and (timeinterval < 20.0):
            self.__status = connection.C_SILENT
        elif (timeinterval >= 20.0) and (timeinterval < 30.0):
            self.__status = connection.C_TIMINGOUT
        elif (timeinterval >= 30.0):
            self.__status = connection.C_TIMEOUT
    

    ## Sends outgoing messages.
    def __send_outgoing(self):
        self.__lock.acquire()
        for b in self.__outgoing:
            msgType = self.__pedia.GetTypeID(b)
            b.mtype = msgType
            bufpayload = b.SerializeToString()
            payload = struct.pack("!I", msgType) + bufpayload

            self.__bytessent += len(payload)

            self.__socket.sendto(payload, (self.__host, self.__port) )
        self.__outgoing = []
        
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
                
                self.__bandwidth += len(data)
                
                # Discard the unusual packet sent from someone to this connection that isn't the server
                # we've connected to.  This may cause problems with dns lookups which we'll have to fix
                # when they come up.
                #if addr[0] != self.__host:
                #    break
                
                padding = len(data) - 4
                formatString = "!I" + str(padding) + "s"
                theId, payload = struct.unpack(formatString, data)
                buf = self.__pedia.GetMessageType(theId)()
                buf.ParseFromString(payload)
                
                # Now we have the message parsed into an object.  What do we do with it?
                # Answer: put it in a list.  When all packets are appropriately listed, then
                # we'll go through each one and do something about them.
                self.__incoming.append( [theId, buf] )
            
            self.__process_incoming()
            
            self.__send_outgoing()
            
            time.sleep(0.01)
        
        self.__send_outgoing()
        
        self.__socket.close()





