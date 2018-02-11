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

## nSyncObject is the class from which game objects that need to be synced must inherit.  After initializing
#  the class, you must declare which attributes will be synced over the network.  Afterwards, you can modify
#  those attributes at will and the network layer will automatically send out sync messages.  Note that you
#  cannot sync objects from the client to the server, so modifying attributes on the client is only useful
#  when you are predicting the action for players, but the client objects still need to inherit this class
#  so they can receive sync messages.
class nSyncObject(object):
    ## The list of attributes that are to be synced
    __attributes = None

    ## Attribute values and other metadata associated with them
    __attributevalues = None
    
    def __init__(self):
        self.__attributes = {}

        theList = GetSyncList()

        nextId = theList.GetNextId()

    ## Add an attribute for this object.
    #
    #  @param newAttribute a dictionary that contains the information about the attribute.  POssible keys are
    #                      as follows:
    #                           'name' : The name of the attribute.
    #                           'type' : The type of the attribute.  Must be a type object.
    #                           'static' : Indicates that the value cannot be changed.  Default is False.
    def AddAttribute(self, newAttribute):
        pass    
        

## nSyncList holds the list of game objects that are to be synced over the network.  Periodically,
#  when an nSyncObject is changed, the network layer will automatically generate an send sync packets.

class nSyncList(object):
    ## holds the list of objects
    __syncobjects = None
    

    def __init__(self):
        self.__syncobjects = []

    def AddSyncObject(self, obj):
        self.__syncobjects.insert(obj)

    def DeleteSyncObject(self, obj):
        pass

__synclist = None

## Returns the nSyncList object.  Used internally by the network library, should not be used by games.
def GetSyncList():    
    global __synclist

    if __synclist == None:
        __synclist = nSyncList()

    return __synclist





     
