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

## This file lists all of the message types including their unique IDs.  When you create a new
#  message type, you must add it to this file before it can be sent/received over the network.
#  The actual order of messages here doesn't matter, since we're using a dict to store them all, but
#  for readability's sake, try to keep them in reasonable order.
#
#  You must make two entries for every type.  One entry is keyed by number and has the type as the value,
#  and the other entry is keyed by the string for the type and has the number as the value.  You must
#  also make the constant for the type, using that constant in your two entries.

M_LOGIN = 1
M_LOGIN_S = 'login'
M_LOGOUT = 2
M_LOGOUT_S = 'logout'

M_ACK = 3
M_ACK_S = 'ack'

M_PING = 4
M_PING_S = 'ping'

## Returns a new message id.  This is used internally, do not use it externally.
__msgId = 0
def get_id():
    global __msgId
    
    __msgId += 1
    
    return __msgId


## This is a list of message types that don't require a player to be logged in before the server will
#  respond.  The default for all messages is that they require a player to be logged in.
noLogin = [
    M_LOGIN,
]


ml = {}

## Login messages
import login_pb2
ml[M_LOGIN] = login_pb2.Login
ml[M_LOGIN_S] = M_LOGIN
ml[M_LOGOUT] = login_pb2.Logout
ml[M_LOGOUT_S] = M_LOGOUT

## Ack message
import ack_pb2
ml[M_ACK] = ack_pb2.Ack
ml[M_ACK_S] = M_ACK

## Ping messages
import ping_pb2
ml[M_PING] = ping_pb2.Ping
ml[M_PING_S] = M_PING


