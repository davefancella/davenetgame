#!/usr/bin/env python

'''

    @version $Id: __init__.py,v 1.2 2005/01/14 00:52:36 davidfancella Exp $

    This file is part of Dave's Stupid Python Library.

    Dave's Stupid Python Library is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Dave's Stupid Python Library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Dave's Stupid Python Library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

	Dave's Stupid Python Library is copyright 2006 by Dave Fancella

'''

# a collection of functions to handle paths

import os
import sys
#import log

_allpaths = {}

_appdirname = None

def DirSep():
    return os.linesep

def UnHome(path):
    return os.path.expanduser(path)

def ListDir(path, includeDirs=True, includeFiles = True):
    listing = []
    if os.path.isdir(path):
        for a in os.listdir( UnHome(path) ):
            if os.path.isdir(os.path.join(path, a) ):
                if includeDirs is True:
                    listing.append(a)
            else:
                if includeFiles is True:
                    listing.append( a )
        listing.sort()
    return listing

def GetLastPathElement(path):
    base, tail = os.path.split(path)
    return tail

def GetDir(path):
    base, tail = os.path.split(path)
    return base

def GetMimeExtension(path):
    lastpart = GetLastPathElement(path)
    base, tail = os.path.splitext(lastpart)
    if len(tail) > 0:
        return tail[1:].lower()
    else:
        return ""

## Returns a string containing the current username
def GetUsername():
    if sys.platform == "win32":
        try:
            return win32api.GetUserName()
        except:
            return "Player 1"
    else:
        return pwd.getpwuid(os.getuid())[0]

## Return the asset path desired.  If targetFile is not none, then it will join the filename to the asset path,
# returning a complete path to the file you want.
# @param path the program asset path desired, such as 'resource', 'civilizations', or 'flags'.
# @param targetFile Filename to join to the asset path, in which case the path returned points
#                               at this file.  Defaults to None.
# @todo make GetPath throw an exception or something instead if a path isn't known
def GetPath(path, targetFile=None):
    global _allpaths
    
    if _allpaths.has_key(path):
        if targetFile is None:
            return _allpaths[path]
        else:
            return JoinPaths(_allpaths[path], targetFile)
    else:
        print "Don't know path '" + path + "'!"
        print _allpaths
        return None

def Exists(path):
    return os.path.exists(path)

def ModifiedTime(path):
    statresults = os.stat(path)
    
    return statresults.st_mtime

def IsDir(path):
    return os.path.isdir(path)

def IsFile(path):
    return os.path.isfile(path)

def GetIcon(icon):
    return JoinPaths(GetPath('graphics'), icon)

## InitializePaths initializes this module.  It must be called before any of the
#   really useful functions here can be used.
#   @param appDirName the name for application-specific directories.
#   @param thePaths a dictionary containing the paths you want to define and
#          strings to define them using / as a directory separator.  It will be
#          replaced with platform-specific directory separators.
def InitializePaths(appDirName, thePaths):
    global _allpaths
    global _appdirname

    _appdirname = appDirName

    # First determine where we're running from
    if sys.platform == 'win32':
        __home = os.path.expanduser('~/')
        __basepath = ''
        __share = ''
        __lib = ''
        __etc = 'etc'
    else:
        __basepath = sys.path[0]
        __home = os.path.expanduser('~')
        # installed to some system prefix
        if __basepath.startswith(sys.prefix):
            __share = os.path.join('share', appDirName)
            __lib = os.path.join('lib', 'lib' + appDirName)
            __etc = 'etc'
        # installed to any arbitrary prefix
        if  __basepath.endswith('/lib'):
            __basepath = os.path.dirname(__basepath)
            __share = os.path.join('share', appDirName)
            __lib = os.path.join('lib', 'lib' + appDirName)
            __etc = 'etc'
        # run from source directory
        else:
            __share = ''
            __lib = ''
            __etc = 'etc'
            
    # Now we need to iterate through the caller's paths and set each of them
    # up in _allpaths
    templist = []
    for key, value in thePaths.iteritems():
        templist.append( [key, value.split("/") ] )

    # We have to iterate this way so the caller can have dependencies on previous
    # path definitions
    # todo: make it so that the caller can use previous paths in the new path definition
    #       this is low priority, I can copy and paste and make it work fine anyway.
    while len(templist) > 0:
        key, valueList = templist.pop(0)
        skipMe = False
        for a in range(len(valueList) ):
            valueList[a] = valueList[a].replace('__basepath', __basepath)
            valueList[a] = valueList[a].replace('__etc', __etc)
            valueList[a] = valueList[a].replace('__share', __share)
            valueList[a] = valueList[a].replace('__lib', __lib)
            valueList[a] = valueList[a].replace('__home', __home)
            # This one should never be used for share.  This module takes care of
            # it already.
            valueList[a] = valueList[a].replace('__appname', appDirName)
        _allpaths[key] = JoinPaths( *valueList )
    
def GetAppDirName():
    global _appdirname
    
    return _appdirname

def JoinPaths(*args):
    return os.path.normpath(os.path.expanduser(os.path.join(*args) ) )

# Returns True on success and False on failure
def MkDir(path, permissions = 0775):
    path = os.path.expanduser(path)
    if Exists(path):
        raise errors.DirectoryExistsError("Tried to create directory '" + path + "', but the path already exists!")
    
    try:
        os.makedirs(path, permissions )
        #log.Application("Created new directory: '" + path + "', with permissions '" + str(oct(permissions) ) + "'")
    except:
        #log.Error("Error creating new directory: '" + path + "', with permissions '" + str(permissions) + "'")
        raise errors.PathError("An unknown error has occured while creating directory '" + path + "' with permissions '" + str(permissions) + "'")

def OpenFile(path, mode):
    try:
        fp = open(path, mode)
        return fp
    except:
        #log.Error("Error opening file " + str(path) + " for mode '" + str(mode) + "'.")
        return None

def Walk(path):
    return os.walk(path)



