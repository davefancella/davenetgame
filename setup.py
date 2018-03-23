#!/usr/bin/env python3

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

#!/usr/bin/env python3

from distutils.core import setup

setup(name="davenetgame",
      version='1.0',
      description="Dave's Stupid Network Game Library is a network library designed for games, written in pure python.",
      author='Dave Fancella',
      author_email='dave@davefancella.com',
      url='http://www.davefancella.com/',
      packages=[
                'davenetgame',
                'davenetgame/messages',
                ],
     )


