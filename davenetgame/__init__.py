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


## @page concepts Concepts and Details
#
# @tableofcontents
# 
# Dave's Stupid Game Network Library is a general-purpose network library for games that provides
# its own basic protocol while also providing for virtually any custom protocol to be created.
# Out of the box, the library, referred to informally as 'davenetgame', provides services to connect
# clients and servers, maintain those connections, create, sync, and destroy game objects, and
# for players to chat with one another.  Additional functionality is available for the game
# developer, and the mechanisms presented here discuss exactly that.
# 
# @section messages Messages
# 
# At the heart of any network protocol, there are the actual messages sent over the wire.
# Davenetgame comes with a number of messages that take care of all of the housekeeping for you,
# while also providing for basic object synchronization.  Messages are encoded/decoded by Google's
# Protobuffer suite, so that creating a new message is pretty simple: just write a .proto file.
# After creating a message, you have to register the message type with the message list, then
# register callback functions to handle the message.  But don't sweat it, too much.  The library
# comes with all of the messages you'll need, in most cases, and you don't have to worry about
# creating new ones.  In particular, the messages already ready are:
# 
# * Login/Logout
# * Ack
# * Ping
# * Chat
# * Object create/delete/sync
# * Command
# 
# Callbacks exist already for each of these, as well as network events, so that you can handle
# them as needed for your game and focus on writing the game instead of writing network code.
# To use them, simply inherit ClientCallback for clients and ServerCallback for servers and overload
# the appropriate members of these classes to take the actions you need to take in response to
# each of these messages.
# 
# @section events Events
# 
# After messages, various network events will occur.  For example, the most basic login procedure
# is for a client to connect to a server, receive a sync for game object types (more on this later),
# and then is ready to join the game.  At that point, a login event is generated, and the login
# callback on the server is called.  This triggers the server to let the client know its logged in,
# so the client also calls the login callback.  For the server, this is when you'd create your
# player object and either spawn them, or, well, do whatever fits your game the best.  For the
# client, this is where you might switch to the in-game UI and start showing the action on the
# server.
# 
# Other events come up as needed, and while you don't have to handle all of them on the client,
# you probably have to do something for each of them on the server.  This is a list of events
# available:
# 
# * Login/logout
# * Timeout
# 
# @section callbacks Callbacks
# 
# As previously stated, you won't be directly interacting with the callback system itself.  Instead,
# you'll be overloading class methods that are callbacks already registered in the system.  In the
# event that you need to interact with the callback system, you'll use the Register*Callback methods
# in whichever callback class you're working (either ClientCallback or ServerCallback).  Each
# callback function has two essential pieces of information: it's type (usually denoted as ctype
# in function arguments) and it's name.  The type is one of "message" or "event", depending on
# whether or not you're responding to a message or an event.  The name is the name of the message
# or event to which you're responding.  For example, to respond to a "chat" message, you'll register
# your callback using RegisterMessageCallback, and it's type will be "message", and it's name will
# be "chat".  All arguments passed to the callback are passed as a dictionary, so there are no
# bulky function signatures to memorize.  Simply familiarize yourself with what may or may not be
# in that dictionary when you write your callback.
# 
# Internally, callbacks are stored in the CallbackList object.  When something happens at the
# socket level, either as a result of a message being received or a series of messages being exchanged,
# the network object will create a callback object with all of the information needed for it to
# be used.  Then it will be added to a queue of callbacks, scheduled to be executed by the main
# thread.  The reason for the queue is because davenetgame supports running in a multi-threaded
# environment.  In that situation, the thread that handles the socket polling and maintaining
# connections (usually simply regularly pinging connections to see if they're still listening)
# runs separate from the main thread, and in order to be thread safe, callbacks have to be
# executed from within the main thread.  The exceptions to this are messages like pings and acks, 
# because those don't need to be escalated to the main thread, but do need an immediate response.
# 
# @section messagesdetail Messages, in detail
# 
# To write messages yourself, you'll need to consult the protobuffer documentation.
#
# The way davenetgame handles messages, well, it's pretty simple.  The Messages class stores
# each message type along with it's encoder/decoder, provided by protobuffer.  A message begins
# its life somewhere in your game.  For example, a login message is generated by the client
# after the player has selected a server to join.  Your code will call the ClientCallback object
# and tell it to login to the server and provide the server's address.  Then the Client object
# will go to the messageList (found in pedia.py) and get an encoded Login message.  Right before
# sending the message, the Client will prepend an integer indicating that it is a Login message.
# When the server receives the message, it will first parse out that integer at the beginning
# to determine what type of message it has received.  Then the server goes to the messageList
# (again, found in pedia.py) to get the parser that parses the message.  Then it gets the
# attributes from the message, things such as player name and colors, finds the callback
# for the login message and calls it, passing it a dictionary containing the attributes from
# the message.  In the standard implementation, this triggers the server sending an Ack message
# to the client, indicating that the client has joined the server.
#
# Ping messages are handled similarly.  The server sends ping messages every 100 milliseconds
# (default, but configurable), and when a client hasn't send a message to the server in a certain
# amount of time, then the server determines the client is no longer connected and generates
# a "timeout" *event*.  While that event results in a callback being called, if you created
# a *message* callback to handle a message called "timeout", that callback will not be called,
# because it is a *message* callback and the "timeout" event is an *event*, not a message.
#
# In any case, pings are handled automatically.  Most messages require more complicated handling,
# such as chat messages.  But chat messages are a special case.  You *can* handle the chat *message*
# if you want, but since davenetgame comes with the ability to use special commands in chat
# messages, you probably would rather handle the various "chat" *events* instead.
# 
# @section pings Pings, Good God, What are they good for?
#
# In game networking, there are two meanings of the word ping.  The most common usage is of
# the form of "I like that server, my ping is nice and low there".  In that meaning, you are
# referring to the time it takes for a message sent from the server to reach the client and
# be acked back to the server.  It's a round trip time for messages.  So a 46ms ping means it
# took 46 milliseconds for the server to send the ping to the client, the client to receive it, process
# it, generate and send an ack message, and for the server to receive and process the ack message.
# That's a simple, yet somewhat inaccurate, way of determining latency between the client and
# server and measuring the dreaded lag.
#
# The second meaning is more direct: a ping is simply the server saying "Hey, are you still
# there?"  When maintaining a connection, the server keeps track of several things.  These are:
#
# * The time at which the last ping was acked
# * The time at which the last message sent from the client was received
# * A running window of round-trip times for messages for the last few seconds
#
# If a client becomes unresponsive, then it is categorized based on how long it's been since
# the last message was received from the client, but the server has been sending messages in
# the meantime (usually sync messages with the occasional ping thrown in for good measure).
# A connections is considered OK if the client has said something in the last 10 seconds, even
# if it hasn't said anything since the last thing it said, and the server has sent 500 pings.
# A connection is considered UNRESPONSIVE at 10-20 seconds, and TIMINGOUT at 20-30 seconds.
# After that, the client is automatically considered disconnection, gets marked DISCONNECTED,
# and a timeout event is generated on the server.
#
# The "ping" that is reported to clients so that players can complain about lag (which they
# do almost as much as they complain about how much the game sucks, even though they won't
# stop playing) is an average of the running window of round-trip message times, which includes
# any messages, not just pings.  It does not take into account packet loss.  Combining the fact
# that it doesn't take packet loss into account with the naive averaging it does makes the
# ping reported fairly imprecise, but players expect to see their pings, and since all servers
# for a particular game calculate ping the same way, it's still a reasonable way to estimate
# network latency between a particular client and a particular server.
#
# @section packetloss Packet Loss, or how I learned to stop caring and love lag
#
# Packet loss is the phenomenon where, for whatever reason, occasional messages get lost between
# the client and the server.  There are a few things that you, as a game programmer, need to know
# about sockets, even though you've made the smart move to use davenetgame so you don't have
# to think about them.  Sockets aren't a solid connection.  The socket libraries used on
# computers all assume that the connection can be broken at any time, for any reason, by either
# side.  As a result of not only that decision but the reality of networks, it's not possible
# to be 100% certain that a message sent from the server is received by the client.  We have
# ack messages that the client sends when it receives a message from the server, but that message
# could get lost.  Since you never ack an ack, there's no way to tell the client that the server
# didn't receive the ack.  Additionally, at any given moment, there could be dozens of messages
# the server has sent that have been received or will be received, but haven't been acked yet,
# or have been acked but the acks haven't arrived at the server yet.
#
# As a result of all of these factors, it is impossible to calculate packet loss accurately.
# Sure, you can divide number of packets acked by number of packets sent, but you'll always
# get a number less than one.  You'll never get a perfect one.  Until the client logs out
# with a logout message that the server receives, anyway.  After the client logs out, then, and
# only then is it possible to determine with accuracy the packet loss for the connection.  Even
# then, there's still going to be a level of uncertainty because of the ack messages the client
# may have sent that the server didn't receive.
#
# Most games use UDP to communicate.  There are reasons for this, of course.  But before going
# into them, let's talk about TCP, or Transmission Control Protocol.  TCP promises that, as long
# as both sides of the connection are communicating, every packet sent will be received in the
# order in which it was sent.  That means error-checking is happening.  In extreme packet loss
# conditions, TCP can slow down a file transfer rate dramatically, but the file transfer will
# still take place.  In a game, the information in the messages is usually of timely importance,
# so the guarantees that TCP provides can actually hinder game performance.  Even in a situation
# with minimal packet loss, which is most of the time, TCP can significantly hinder the timely
# delivery of information.  It still guarantees the integrity of the information, and that's
# good for most applications.  Davenetgame will some day have a TCP option, in fact, because
# for some turn-based games, TCP is more reliable and convenient than UDP.  However, most
# networking games actually involve a lot of fast-changing situations, to the point where
# the timely delivery of messages is actually more important than the integrity of the information.
# Davenetgame defaults to UDP, or Universal Datagram Protocol, which does no error checking.
# If a message is lost, then there's no way to figure it out without implementing all of the
# stuff that TCP provides, and if you're going to do that, you might as well have used a TCP
# socket in the first place.
#
# As a result of all of this, object syncing has its own issues.  Since the likelihood that a
# message will get lost increases the bigger the message is, the preferred way to sync objects
# is to only sync them when changes are made, and then only sync the changes and not the
# entire object.  This creates a situation where, depending on the design of your objects and
# the flow of the game, missing sync messages can lead to a drift in accuracy in the client's
# simulation of the game due to missing information.  Davenetgame provides the option to
# periodically sync all of any changed object to make up for that possibility, but still doesn't
# promise that the message will get there.
#
# In the end, the best way to deal with packet loss is to simply turn off the game and go
# outside, get some sunlight and fresh air, and maybe take a bike ride, and wait until the
# internet weather improves.
#





