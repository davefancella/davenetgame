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

from davenetgame.dispatch.base import DispatcherBase

## @file dispatcher
#
#  This file contains the standard, generic EventDispatcher class.  It's the one you use if
#  the library doesn't support your preferred game engine, or if you'd rather manage the library
#  independently of your game engine.

## This is the standard EventDispatcher.
class EventDispatcher(DispatcherBase):
    pass


## This is a special server-oriented EventDispatcher that provides for an interactive console
#  on the server when run in a terminal.  This is probably most useful for testing the library,
#  though it's not unheard of for a server to run in a terminal and have a console.
class EventDispatcherServer(DispatcherBase):
    __console = None
    __consolecommands = None

    def __init__(self, **args):
        self.__console = ConsoleInput()
        self.__consolecommands = []
        
        # Register the standard commands available to every game server.
        self.RegisterCommand('show', self.consoleShow, "show (connections)", "Show whatever you want to see.")
        self.RegisterCommand('help', self.consoleHelp, "help [command]", "print(this helpful text.  Alternately, type in a command to see its helpful text.")
        self.RegisterCommand('quit', self.consoleQuit, "quit", "Quit the server.")

    def Start(self):
        self.__console.Start()
        super().Start()

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



