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


from unittest import TestCase

from eos.eve.type import Type
from eos.tests.attributeCalculator.helper import ShipItem


class TestDetached(TestCase):
    """Test access to item attributes when it's not attached to any fit"""

    def testAttributeAccess(self):
        type_ = Type(1, attributes={56: 50})
        module = ShipItem(type_)
        attrValue = module.attributes[56]
        expValue = 50
        self.assertEqual(attrValue, expValue, "attribute value must be {}".format(expValue))