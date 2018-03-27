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

import getpass # for convenience

from davenetgame import client
from davenetgame import connection

class ClientCallback(object):
    __host = None
    __port = None
    __name = None
    __client = None

    def __init__(self, **args):
        self.__host = 'localhost'
        self.__port = 8888
        self.__name = getpass.getuser()
        
        if 'host' in args:
            self.SetHost = args['host']
        if 'port' in args:
            self.SetPort = args['port']
            
    def SetHost(self, host):
        self.__host = host
        
    def SetPort(self, port):
        # Ensure the port is always an int
        self.__port = int(port)

    ## Starts the client, initiating a connection to the server.  Don't do this until you've set the host
    #  and port number correctly!
    def Start(self):
        self.__client = client.nClient()
        self.__client.SetServer(self.__host, self.__port)
        self.__client.Start()
        
        self.__client.Login(self.__name)

        # @@todo Write the part that connects the callbacks to the client object

    ## Stops the client.  Call will block until the client thread has stopped.
    def Stop(self):
        self.Logout()
        self.__client.Stop(True)
        
        # delete the client object, so that if we start again, we can create a new one.
        self.__client = None

    ## Logs out of the server, but keeps the client object active.  Probably no reason you should call this,
    #  but it is used internally.
    def Logout(self):
        self.__client.Logout()
        
    ## Manually pings the server.  Probably no reason you should call this, either, but it's used by the test
    #  client for testing purposes.
    def SendPing(self):
        self.__client.SendPing()
    
    ## Bandwidth used
    def Bandwidth(self):
        return self.__client.BytesSent() + self.__client.BytesReceived()
    
    ## Bytes sent
    def BytesSent(self):
        return self.__client.BytesSent()
    
    ## Bytes received
    def BytesReceived(self):
        return self.__client.BytesReceived()
    
    ## Returns a string indicating the status of the connection.
    def StatusString(self):
        return connection.statuslist[self.__client.Status()][1]
        
        
