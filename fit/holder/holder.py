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


from eos.fit.attributeCalculator import MutableAttributeMap


class Holder:
    """
    Base holder class inherited by all classes that
    need to keep track of modified attributes.

    Positional arguments:
    typeId -- typeID of item, which is supposed to be
    base item for holder
    state -- state which this holder takes during initialization
    """

    __slots__ = ('__typeId', '__state', 'attributes', '__fit', '__type')

    def __init__(self, typeId, state):
        # TypeID of item this holder is supposed to wrap
        self.__typeId = typeId
        # Keeps current state of the holder
        self.__state = state
        # Special dictionary subclass that holds modified attributes
        # and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Which fit this holder is bound to
        self.__fit = None
        # Which type this holder wraps
        self.__type = None
        ## Keeps current target of holder
        #self.__target = None

    @property
    def item(self):
        return self.__type

    @property
    def _fit(self):
        return self.__fit

    @_fit.setter
    def _fit(self, newFit):
        self.__fit = newFit
        self._refreshContext()

    def _refreshContext(self):
        """
        Each time holder's context is changed (holder's
        fit or fit's eos), this method should be called;
        it will refresh data which belongs to certain
        context and which is not actual outside of it.
        """
        self.attributes.clear()
        try:
            cacheHandler = self.__fit.eos._cacheHandler
        except AttributeError:
            self.__type = None
        else:
            self.__type = cacheHandler.getType(self.__typeId)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, newState):
        if newState == self.state:
            return
        # When holder is assigned to some fit, ask fit to perform
        # fit-specific state switch of our holder
        if self._fit is not None:
            self._fit._holderStateSwitch(self, newState)
        self.__state = newState

#    @property
#    def target(self):
#        """Get target, onto which holder is applied"""
#        return self.__target
#
#    @target.setter
#    def target(self, newTarget):
#        """Project holder onto target"""
#        if self.item.isTargeted is True:
#            self.__target = newTarget
#        else:
#            raise TargetException("attempt to project holder with non-projectable item")

    @property
    def trackingSpeed(self):
        """Get tracking speed of holder"""
        return self.__getItemSpecificAttr('_trackingSpeedAttributeId')

    @property
    def optimalRange(self):
        """Get optimal range of holder"""
        return self.__getItemSpecificAttr('_rangeAttributeId')

    @property
    def falloffRange(self):
        """Get falloff range of holder"""
        return self.__getItemSpecificAttr('_falloffAttributeId')

    @property
    def cycleTime(self):
        return self.__getItemSpecificAttr('_durationAttributeId')

    def __getItemSpecificAttr(self, attrName):
        """Get holder attribute, which is referred by item"""
        attrId = getattr(self.item, attrName, None)
        if attrId is not None:
            try:
                attrValue = self.attributes[attrId]
            except KeyError:
                attrValue = None
        else:
            attrValue = None
        return attrValue
