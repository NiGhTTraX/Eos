#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from logging import getLogger
from logging.handlers import BufferingHandler
from unittest import TestCase


class TestLogHandler(BufferingHandler):
    """
    Custom logging handler class which helps to
    check log output without unnecessary actual
    output.
    """
    def __init__(self):
        # Capacity is zero, as we won't rely on
        # it when deciding when to flush data
        BufferingHandler.__init__(self, 0)

    def shouldFlush(self):
        return False

    def emit(self, record):
        self.buffer.append(record.__dict__)


class EosTestCase(TestCase):
    """
    Custom test case class, which incorporates several
    environment changes for ease of test process, namely:

    self.logHandler.buffer -- access to output generated
    by logging facility during test

    When overriding setUp and tearDown methods, make sure
    to call this class' original methods (before anything
    else is done for setUp, and after for tearDown).
    """

    def setUp(self):
        self.__removedLogHandlers = []
        logger = getLogger("eos")
        for handler in logger.handlers:
            self.__removedLogHandlers.append(handler)
            logger.removeHandler(handler)
        self.logHandler = TestLogHandler()
        logger.addHandler(self.logHandler)

    def tearDown(self):
        logger = getLogger("eos")
        logger.removeHandler(self.logHandler)
        self.logHandler.close()
        for handler in self.__removedLogHandlers:
            logger.addHandler(handler)
