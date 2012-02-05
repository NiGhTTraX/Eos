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

from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.fit.attributeCalculator.exception import BadContainerException
from eos.fit.attributeCalculator.info.info import Info
from eos.fit.fit import Fit
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.helper import CharacterItem, ShipItem


class TestLocationFilterSelf(TestCase):
    """Test self-reference location for massive filtered modifications"""

    def setUp(self):
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.self_
        info.filterType = FilterType.all_
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(1, EffectCategory.passive)
        effect._Effect__infos = {info}
        self.fit = Fit(lambda attrId: {tgtAttr.id: tgtAttr, srcAttr.id: srcAttr}[attrId])
        # It doesn't matter holder of which type we're using,
        # the only thing which matters is its position in fit
        self.influenceSource = ShipItem(Type(1, effects={effect}, attributes={srcAttr.id: 20}))

    def testShip(self):
        self.fit._Fit__ship = self.influenceSource
        self.fit._addHolder(self.influenceSource)
        # Here we can use any holder which belongs to ship
        influenceTarget = ShipItem(Type(2, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        notExpValue = 100
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")

    def testCharacter(self):
        self.fit._Fit__character = self.influenceSource
        self.fit._addHolder(self.influenceSource)
        # Here we can use any holder which belongs to character
        influenceTarget = CharacterItem(Type(2, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        notExpValue = 100
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], notExpValue, msg="value must be modified")

    def testUnpositioned(self):
        # Here we do not position holder in fit, this way attribute
        # calculator won't know that source is 'owner' of some location
        # and will throw corresponding exception
        self.assertRaises(BadContainerException, self.fit._addHolder, self.influenceSource)