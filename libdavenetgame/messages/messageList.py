#!/usr/bin/env python

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


