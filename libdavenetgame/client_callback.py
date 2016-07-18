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

import getpass # for convenience

from libdavenetgame import client

class ClientCallback(object):
    __host = None
    __port = None
    __name = None
    __client = None

    def __init__(self, **args):
        self.__host = 'localhost'
        self.__port = 8888
        self.__name = getpass.getuser()
        
        if args.has_key('host'):
            self.SetHost = args['host']
        if args.has_key('port'):
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

        # @todo: Write the part that connects the callbacks to the client object

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
        
        
        