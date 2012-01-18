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


from eos.const import EffectCategory


class InfoContext:
    """Info context ID holder"""
    passive = 1  # Applied regardless of carrier holder's state
    online = 2  # Applied when carrier holder is at least in online state (i.e., in active and overloaded too)
    active = 3  # Applied when carrier holder is at least online
    overload = 4  # Applied only when carrier holder is overloaded
    projected = 5  # Applied when holder is activated on some target

    @classmethod
    def eve2eos(cls, effCatId):
        """Convert CCP's effect category ID name to info context ID"""
        # Format: {effect category ID: state ID}
        conversionMap = {EffectCategory.passive: cls.passive,
                         EffectCategory.active: cls.active,
                         EffectCategory.target: cls.projected,
                         EffectCategory.online: cls.online,
                         EffectCategory.overload: cls.overload,
                         EffectCategory.system: cls.projected}
        try:
            result = conversionMap[effCatId]
        except KeyError:
            result = None
        return result

class InfoRunTime:
    """Info modification type ID holder"""
    duration = 1
    pre = 2
    post = 3


class InfoLocation:
    """Location ID holder"""
    self_ = 1  # Target self, i.e. carrier of modification source
    character = 2  # Target character
    ship = 3  # Target ship
    target = 4  # Target currently locked and selected ship as target
    other = 5  # If used from charge, targets charge's container, is used from container, targets its charge
    area = 6  # No detailed data about this one, according to expressions, it affects everything on grid (the only expression using it is area-of-effect repair, but it's not assigned to any effects)
    space = 7  # Target stuff in space (e.g. your launched drones and missiles); this location is Eos-specific and not taken from EVE

    @classmethod
    def eve2eos(cls, name):
        """Convert CCP's location name to ID"""
        # Format: {location name: location ID}
        conversionMap = {"Self": cls.self_,
                         "Char": cls.character,
                         "Ship": cls.ship,
                         "Target": cls.target,
                         "Other": cls.other,
                         "Area": cls.area}
        result = conversionMap[name]
        return result


class InfoFilterType:
    """Info filter type ID holder"""
    all_ = 1  # Affects all items in target location
    group = 2  # Affects items in target location with additional filter by group
    skill = 3  # Affects items in target location with additional filter by skill requirement


class InfoOperator:
    """Info operator ID holder"""
    # Following operators are used in modifications
    # applied over some duration. We can deliberately assign
    # these some ID, but we need to make sure they're sorted
    # in the order they're kept here by python for proper
    # attribute calculation process
    preAssignment = 1
    preMul = 2
    preDiv = 3
    modAdd = 4
    modSub = 5
    postMul = 6
    postDiv = 7
    postPercent = 8
    postAssignment = 9
    # Following operators are for immediate modification
    increment = 10
    decrement = 11
    assignment = 12

    @classmethod
    def eve2eos(cls, name):
        """Convert CCP's operator name to ID"""
        # Format: {operator name: operator ID}
        conversionMap = {"PreAssignment": cls.preAssignment,
                         "PreMul": cls.preMul,
                         "PreDiv": cls.preDiv,
                         "ModAdd": cls.modAdd,
                         "ModSub": cls.modSub,
                         "PostMul": cls.postMul,
                         "PostDiv": cls.postDiv,
                         "PostPercent": cls.postPercent,
                         "PostAssignment": cls.postAssignment}
        result = conversionMap[name]
        return result


class InfoSourceType:
    """Info source value type ID holder"""
    attribute = 1
    value = 2


class Info:
    """
    The Info objects are the actual "Core" of eos,
    they are what eventually applies an effect onto a fit.
    Which causes modules to actually do useful(tm) things.
    They are typically generated by the InfoBuild class
    but nothing prevents a user from making some of his own and running them onto a fit
    """

    def __init__(self):
        # Describes conditions under which modification is applied.
        # Can be None or tree of ConditionAtom objects.
        self.conditions = None

        # Info is applied only when its holder exists in certain context
        self.context = None

        # Describes type of modification.
        # Can have InfoRunTime class' attribute value.
        self.runTime = None

        # Flag identifying local/gang change.
        # Can be either True or False.
        self.gang = False

        # Target location to change.
        # Can have InfoLocation class' attribute value.
        self.location = None

        # The filter type of the modification.
        # Can have InfoFilterType class' attribute value.
        self.filterType = None

        # The filter value of the modification.
        # For InfoFilterType.all must be None.
        # For InfoFilterType.group has some integer, referencing group via ID.
        # For InfoFilterType.skill has some integer, referencing type via ID, or const.Type.self_ to reference type of carrier.
        self.filterValue = None

        # Which operator should be applied.
        # Can have InfoOperator class' attribute value.
        self.operator = None

        # Which attribute will be affected by the operator on the target.
        # Keeps integer which references attribute via ID.
        self.targetAttribute = None

        # sourceValue type.
        # Can have InfoSourceType class' attribute value.
        self.sourceType = None

        # The value which is used as modification value for operation.
        # Keeps reference to attribute or any value CCP can define in expression
        # (boolean or integer).
        self.sourceValue = None
