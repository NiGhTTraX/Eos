#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from eos.const.eos import Location, State
from eos.fit.holder import Holder


class Module(Holder):
    """Ship's module from any slot."""

    __slots__ = ('__charge',)

    def __init__(self, typeId, state=State.offline, charge=None):
        Holder.__init__(self, typeId, state)
        self.__charge = charge

    @property
    def _location(self):
        return Location.ship

    @property
    def _other(self):
        """Purely service property, used in fit link tracker registry"""
        return self.charge

    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, newCharge):
        # All charges getting assigned must be unbound
        if newCharge is not None and newCharge._fit is not None:
            raise ValueError(newCharge)
        oldCharge = self.charge
        if oldCharge is not None:
            if self._fit is not None:
                self._fit._removeHolder(oldCharge)
            oldCharge.container = None
        self.__charge = newCharge
        if newCharge is not None:
            newCharge.container = self
            if self._fit is not None:
                self._fit._addHolder(newCharge)
