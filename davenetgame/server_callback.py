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

import sys
from time import sleep
import threading

import readline

from davenetgame import server
from davenetgame import connection
from davenetgame import callback
 
## This class implements the basic server callback object.  You should inherit this class and 
#  add methods as needed to respond to callbacks.  The callbacks themselves will come from 
#  within the same thread as your game loop, so you will have to call update() on the 
#  callback object.
#
#  To start a basic server, you'd do something like this:
#  ~~~~~~~~~~~~~{.py}
#  from davenetgame import server_callback
#   
#  HOST = ''   # Symbolic name meaning all available interfaces
#  PORT = 8888 # Arbitrary non-privileged port
#  
#  theServer = server_callback.ServerCallback(host = HOST,
#                                          port = PORT)
#  theServer.StartServer()
#  keepGoing = True
#  
#  try:
#      while(keepGoing) :
#          theServer.Update(time.time() )
#          
#  except KeyboardInterrupt:
#      print("Quitting due to keyboard interrupt")
#  
#  theServer.Stop()
#  ~~~~~~~~~~~~~
#
#  For something a bit more advanced, you'd inherit ServerCallback, overload any methods you 
#  need, including any required methods, then simply call Update() from inside your game loop 
#  to update the server.  That gets your callbacks called, syncs game objects, and lets you 
#  continue running your simulation.
#
#  The network layer itself runs in its own thread, and from there it maintains connections, 
#  pinging clients periodically, and sending/receiving all network messages.  Then it queues 
#  up the callbacks, usually to specific connections, so that they can be safely run
#  in your main thread.

class ServerCallback(object):
    __host = None
    __port = None
    __console = None
    __server = None
    __consolecommands = None
    __callback_events = None
    __callback_messages = None
 
    ## Constructor.  Pass it a dictionary with any of the following keys to initialize them:
    #      host : the host that will be listened to by the socket.
    #      port : the port on which the socket will listen
    #      name : the name of the server
    def __init__(self, **args):
        self.__host = ''
        self.__port = 8888
        self.__console = ConsoleInput()
        self.__name = "Test Server"
        self.__consolecommands = []
        
        self.__callback_events = []
        self.__callback_messages = []
        
        if 'host' in args:
            self.SetHost(args['host'])
        if 'port' in args:
            self.SetPort(args['port'] )
        if 'name' in args:
            self.SetName(args['name'])

        # Register the standard commands available to every game server.
        self.RegisterCommand('show', self.consoleShow, "show (connections)", "Show whatever you want to see.")
        self.RegisterCommand('help', self.consoleHelp, "help [command]", "print(this helpful text.  Alternately, type in a command to see its helpful text.")
        self.RegisterCommand('quit', self.consoleQuit, "quit", "Quit the server.")

        self.RegisterMessageCallback('login', self.LoginMessage)
        self.RegisterEventCallback('login', self.LoginEvent)
        self.RegisterMessageCallback('logout', self.LogoutMessage)
        self.RegisterEventCallback('logout', self.LogoutEvent)
        self.RegisterEventCallback('timeout', self.TimeoutEvent)

    ## @name Regular API
    #
    #@{

    ## Call to set the host that the server will listen on.
    def SetHost(self, host):
        self.__host = host

    ## Call to set the server's name
    def SetName(self, _name):
        self.__name = _name

    ## Call to set the port that the server will listen on.
    def SetPort(self, port):
        # Ensure that port is always an integer, even if the caller accidentally passes a string
        self.__port = int(port)

    ## Call to start the server.  Also starts the console.
    def StartServer(self):
        self.__console.Start()
        self.__server = server.nServer(owner = self)
        self.__setupCallbacks()
        
        self.__server.ListenOn(self.__host, self.__port)

        self.__server.Start()

        print("Starting " + self.__name + ".")
        
    ## Call to stop the server.  Stops the console as well.
    def Stop(self):
        self.__server.Stop(True)
        self.__console.Stop()
        
    ## Must be called periodically to keep the network layer going.  Pass it time.time() 
    #  to give it
    #  a timestep.
    def Update(self, timestep):
        try:
            while self.__console.HasPending():
                msg = self.__console.pop()
                args = msg.split(" ")
                
                command = args.pop(0)
                
                command = command.lower()
                
                # Ignore simple presses of enter
                if command == '':
                    continue

                foundcommand = False
                for a in self.__consolecommands:
                    if a.command() == command:
                        a.callback(*args)
                        foundcommand = True
                
                if not foundcommand:
                    print("Command not recognized: " + command)
                
            # Update the server.  This is where the callbacks will get called.
            self.__server.Update(timestep)
                
        except KeyboardInterrupt:
            print("Quitting due to keyboard interrupt")
    #@}
       
    ## @name Callback Methods
    #
    #  These are the callback methods for particular events or messages.  If you need to
    #  customize the behavior of these callbacks, and you probably will for some, then override
    #  them in your subclass.
    #@{
    
    ## Callback for login messages.
    def LoginMessage(self, **args):
        pass
    
    def LogoutMessage(self, **args):
        pass
    
    ## This callback is called when a user has successfully logged in.  Default implementation 
    #  just prints to stdout.
    def LoginEvent(self, **args):
        print("User " + connection.player() + " has logged in.")

    def LogoutEvent(self, **args):
        print("User " + connection.player() + " has logged out.")

    def TimeoutEvent(self, **args):
        print("User " + playername + " has timed out.")
        
    def ChatMessage(self, **args):
        print(connection.player() + ": ")

    #@}
    
    ## @name Internal
    #
    #  These methods are for internal use only.  Users should not use them unless there's
    #  absolutely no other way to do whatever it is they're trying to do, and they haven't
    #  figured out they shouldn't do it, whatever it is.
    #@{

    ## Register an event callback.  Games *can* use this, but the mechanism isn't terribly useful.  
    #  For the most part,
    #  simply implement the required callback methods in this class to receive callbacks.  
    #  Required callbacks will
    #  throw an exception.
    def RegisterEventCallback(self, name, func, options={}):
        self.__callback_events.append([name, func, options])

    ## Register a message callback.  Games *can* use this, but the mechanism isn't terribly useful.  
    #  For the most part,
    #  simply implement the required callback methods in this class to receive callbacks.  
    #  Required callbacks will
    #  throw an exception.
    def RegisterMessageCallback(self, name, func, options={}):
        self.__callback_messages.append([name, func, options])

    ## This method is called after the server is started to register all the callbacks that 
    #  will be used.
    def __setupCallbacks(self):
        for cb in self.__callback_events:
            self.Owner().RegisterEventCallback(cb[0], cb[1], cb[2])
        for cb in self.__callback_messages:
            self.Owner().RegisterMessageCallback(cb[0], cb[1], cb[2])
    #@}

    ## @name Console API
    #
    #  These methods give access to the built-in server console and the various commands that
    #  can be created.
    #@{
    
    ## Console command: show
    def consoleShow(self, *args):
        if len(args) != 1:
            print("Usage: show (connections)")
        else:
            if args[0] == "connections":
                if len(self.__server.GetConnectionList() ) == 0:
                    print("There are no connections at this time.")
                else:
                    for a in self.__server.GetConnectionList():
                        print("%3s: %40s  %10s %4s" % (a.id(), 
                                                       str(a), 
                                                       connection.statuslist[a.Status()][1],
                                                       int(a.GetConnectionPing() * 1000) ))
            else:
                print("Unknown thing to show: " + args[0])
    
    ## Console command: help
    def consoleHelp(self, *args):
        if len(args) > 0:
            for a in self.__consolecommands:
                if a.command() == args[0]:
                    print("%10s : %s" % (args[0], a.helplong() ))
                    print("%13s %s" % (" ", a.helpshort() ))
                    print
            else:
                print("Command not found.")
        else:
            for a in self.__consolecommands:
                print("%10s : %s" % (a.command(), a.helplong() ))
                print("%13s %s" % (" ", a.helpshort() ))
                print()


    ## Console command: quit
    def consoleQuit(self, *args):
        pass
        #if theClient is not None:
        #    theClient.Logout()
        #    theClient.Stop(True)
        #    theClient = None
        keepGoing = False

    ## Call to register console commands with the server.  The library implements a number of standard
    #  commands, but games may need their own commands.  In that case, you will need your own callbacks.
    def RegisterCommand(self, command, callback, helpshort, helplong):
        self.__consolecommands.append(ConsoleCommand(
                command = command,
                callback = callback,
                helpshort = helpshort,
                helplong = helplong
            )
        )
    #@}

        
## This class implements console commands.  To create a new console command, simply make an instance of
#  this class, giving all the keyword arguments in the constructor.
#      @param 'command' : the name of the command, what the user types to use it.
#      @param 'callback' : a function that will process the command when the user types it.
#      @param 'helpshort' : short help text, usually one line of text, preferably not more than 50 characters.
#                    In output, it will be prepended with "Usage: "
#      @param 'helplong' : long help text, can be as long as needed, as many lines as needed.  Do not put
#                   line endings, however.  Those will be added as needed.  You may put line endings to
#                   signify paragraph breaks, if need be.
class ConsoleCommand(object):
    __command = None
    __callback = None
    __helpshort = None
    __helplong = None
    
    def __init__(self, **args):
        # Ensure the command is always lowercase
        self.__command = args['command'].strip().lower()
        self.__callback = args['callback']
        self.__helpshort = args['helpshort']
        self.__helplong = args['helplong']

    def callback(self, *args):
        self.__callback(*args)
        
    def command(self):
        return self.__command
        
    def helpshort(self):
        return self.__helpshort
    
    def helplong(self):
        return self.__helplong

## This class makes the console input non-blocking.
class ConsoleInput(threading.Thread):
    ## This is the lock that must be called to avoid thread collisions
    __lock = None
    
    ## This is a queue of commands, unparsed.
    __pcommands = None
    
    def __init__(self, **args):
        threading.Thread.__init__(self, **args)
        self.__lock = threading.RLock()
        self.__pcommands = []

    ## Call to start the client.
    def Start(self):
        self.__continue = True
            
        self.start()

    ## Stops the server.  It may still take a few seconds or so.  If blocking is "True", then the call will
    #  block until the server has shut down.
    def Stop(self, blocking=False):
        self.__continue = False
    
        if blocking:
            self.join()

    ## Returns true if there are pending lines from stdin to work with
    def HasPending(self):
        if len(self.__pcommands) > 0:
            return True
        
        return False

    ## Starts the console input.  Don't call this directly, instead call Start().
    def run(self):
        while self.__continue:
            msg = input('')
            self.__lock.acquire()
            self.__pcommands.append(msg.strip() )
            self.__lock.release()
            
            sleep(0.01)

    ## Pops the first item off the commands list and returns it.
    def pop(self):
        theCommand = None
        
        if len(self.__pcommands) > 0:
            self.__lock.acquire()
            theCommand = self.__pcommands.pop(0)
            self.__lock.release()
            
        return theCommand

