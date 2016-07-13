#!/bin/sh

#    This file is part of Dave's Stupid Network Game Library.
#
#    Dave's Stupid Network Game Library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Dave's Stupid Network Game Library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dave's Stupid Network Game Library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  00111-1307  USA
#
#    Dave's Stupid Network Game Library is copyright 2016 by Dave Fancella


# Builds the game, whatever stuff has to be processed.  This is a quick and dirty solution,
# only intended for early development.  It should be replaced with a proper setup.py file at some point.

echo "Building Dave's Stupid Network Game Library"
echo

case $1 in
    "clean")
        echo "Deleting protobuf generated files..."
        find ./libdavenetgame -name "*_pb2.py" -print0 | xargs -0 rm -rf
        echo "Deleting python byte-compiled files..."
        find ./libdavenetgame -name "*.pyc" -print0 | xargs -0 rm -rf
        ;;
    "build")
        cd ./libdavenetgame/messages
        pwd
        echo "Building protocol files"
        for a in *.proto
        do
            echo "Building $a"
            protoc -I=./ --python_out=./ ./$a
        done
        ;;
    *)
        echo "Usage: $0 build|clean"
esac


