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

import socket, select, struct

from davenetgame.transport import TransportBase

## This class implements the UDP Transport class.
class Udp(TransportBase):
    ## The socket object that will be polled.
    __socket = None
    
    def __init__(self, **args):
        super().__init__(**args)

    ## Call to start the client.
    def Start(self):
        error = False

        # Create the socket.
        try :
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Socket created')
        except OSError as msg:
            print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] )
            error = True
        
        # If this is a server socket, bind and listen for messages.
        if self.IsServer():
            # Bind socket to local host and port
            try:
                self.__socket.bind(self.ClientInfo() )
            except OSError as msg:
                print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                error = True
            if error is False:
                print('Socket bind complete')
                
        if error is True:
            print("An error occured creating the socket")
    
    ## Cleanup the socket.
    def Stop(self):
        self.__socket.close()
        del self.__socket
        self.__socket = None

    ## Polls the socket.
    def PollSocket(self):
        inF, outF, errF = select.select( [self.__socket],  [self.__socket], [self.__socket], 5)
        
        # Get each message one at a time and call its callbacks
        for ins in inF:
            # receive data from server (data, addr)
            data, addr = self.__socket.recvfrom(self.Buffersize())
            
            if not data: 
                break
            
            # TODO: Add the bandwidth calculation
            #self.__bandwidth += len(data)
                            
            padding = len(data) - 4
            formatString = "!I" + str(padding) + "s"
            theId, payload = struct.unpack(formatString, data)
            
            self.ProcessMessage(theId, payload, addr)
        
    ## Encode and send the message.
    def SendMessage(self, msg):
        # Encode the message
        payload = struct.pack("!I", msg['type']) + msg['message']
        
        ## TODO: do the bandwidth calculation
        #self.__bytessent += len(payload)
        
        self.__socket.sendto(payload, msg['connection'] )
                




