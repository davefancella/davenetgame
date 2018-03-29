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

## @class ProtocolBase
#
#  This class represents the base class for all protocols implemented by the library.  Typically,
#  it is expected that a protocol implementation will have two classes, one each for the client
#  and the server.  It's technically feasible that a basic protocol could be implemented in a
#  single subclass, but this is strongly frowned upon.  In order for a Protocol to function
#  properly, it must be associated with a Transport object.  This means that a Protocol should be
#  able to function regardless of the method by which packets are exchanged in a connection,
#  rendering some protocols more useful than others, depending on the underlying transport layer.
#  For example, implementing a file transfer protocol for a UDP transport layer is sensible,
#  but implementing one for a TCP transport layer may not be, unless you need to be able to
#  transfer files while still exchanging other game information, such as nSyncObjects.
class ProtocolBase(object):
    def __init__(self, **args):
        pass



