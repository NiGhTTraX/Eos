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


from eos.const.eos import Slot, State
from eos.const.eve import Attribute, Effect, EffectCategory
from eos.util.cachedProperty import cachedproperty


class Type:
    """
    Type represents any EVE item. All characters, ships,
    incursion system-wide effects are actually items.
    """

    def __init__(self, typeId=None, groupId=None, categoryId=None,
                 durationAttributeId=None, dischargeAttributeId=None,
                 rangeAttributeId=None, falloffAttributeId=None,
                 trackingSpeedAttributeId=None, fittableNonSingleton=None,
                 attributes=None, effects=()):
        self.id = typeId

        # The groupID of the type, integer
        self.groupId = groupId

        # The category ID of the type, integer
        self.categoryId = categoryId

        # Defines cycle time
        self._durationAttributeId = durationAttributeId

        # Defines attribute, whose value will be used to drain ship's
        # capacitor each cycle
        self._dischargeAttributeId = dischargeAttributeId

        # Attribute with this ID defines optimal range of item
        self._rangeAttributeId = rangeAttributeId

        # Defines falloff attribute
        self._falloffAttributeId = falloffAttributeId

        # Defines tracking speed attribute
        self._trackingSpeedAttributeId = trackingSpeedAttributeId

        # Defines if multiple items of this type can be added to fit without packaging.
        # We use it to see if charge can be loaded into anything or not.
        self._fittableNonSingleton = bool(fittableNonSingleton) if fittableNonSingleton is not None else None

        # The attributes of this type, used as base for calculation of modified
        # attributes, thus they should stay immutable
        # Format: {attributeId: attributeValue}
        self.attributes = attributes if attributes is not None else {}

        # Iterable with effects this type has, they describe modifications
        # which this type applies
        self.effects = effects

    @property
    def modifiers(self):
        """ Get all modifiers spawned by item effects."""
        modifiers = []
        for effect in self.effects:
            for modifier in effect.modifiers:
                modifiers.append(modifier)
        return modifiers

    # Define attributes which describe item skill requirement details
    # Format: {item attribute ID: level attribute ID}
    __skillRqAttrs = {Attribute.requiredSkill1: Attribute.requiredSkill1Level,
                      Attribute.requiredSkill2: Attribute.requiredSkill2Level,
                      Attribute.requiredSkill3: Attribute.requiredSkill3Level,
                      Attribute.requiredSkill4: Attribute.requiredSkill4Level,
                      Attribute.requiredSkill5: Attribute.requiredSkill5Level,
                      Attribute.requiredSkill6: Attribute.requiredSkill6Level}

    @cachedproperty
    def requiredSkills(self):
        """
        Get skill requirements.

        Return value:
        Dictionary with IDs of skills and corresponding skill levels,
        which are required to use type
        """
        requiredSkills = {}
        for srqAttrId in self.__skillRqAttrs:
            # Skip skill requirement attribute pair if any
            # of them is not available
            try:
                srq = self.attributes[srqAttrId]
            except KeyError:
                continue
            try:
                srqLvl = self.attributes[self.__skillRqAttrs[srqAttrId]]
            except KeyError:
                continue
            requiredSkills[int(srq)] = int(srqLvl)
        return requiredSkills

    # Map effect category onto max state item can take
    # Format: {effect category ID: state ID}
    __effectStateMap = {EffectCategory.passive: State.offline,
                        EffectCategory.active: State.active,
                        EffectCategory.target: State.active,
                        EffectCategory.online: State.online,
                        EffectCategory.overload: State.overload,
                        EffectCategory.system: State.offline}

    @cachedproperty
    def maxState(self):
        """
        Get highest state this type is allowed to take.

        Return value:
        State class' attribute value, representing highest state
        """
        # All types can be at least offline,
        # even when they have no effects
        maxState = State.offline
        # We cycle through effects, because each effect isn't
        # guaranteed to produce modifier, thus effects are
        # more reliable data source
        for effect in self.effects:
            effectState = self.__effectStateMap[effect.categoryId]
            maxState = max(maxState, effectState)
        return maxState

    @cachedproperty
    def isTargeted(self):
        """
        Report if type is targeted or not. Targeted types cannot be
        activated w/o target selection.

        Return value:
        Boolean targeted flag
        """
        # Assume type is unable to target by default
        targeted = False
        for effect in self.effects:
            # If any of effects is targeted, then type is targeted
            if effect.categoryId == EffectCategory.target:
                targeted = True
                break
        return targeted

    # Format: {effect ID: slot ID}
    __effectSlotMap = {Effect.loPower: Slot.moduleLow,
                       Effect.hiPower: Slot.moduleHigh,
                       Effect.medPower: Slot.moduleMed,
                       Effect.launcherFitted: Slot.launcher,
                       Effect.turretFitted: Slot.turret,
                       Effect.rigSlot: Slot.rig,
                       Effect.subSystem: Slot.subsystem}

    @cachedproperty
    def slots(self):
        """
        Get types of slots this type occupies.

        Return value:
        Set with slot types
        """
        # Container for slot types item uses
        slots = set()
        for effect in self.effects:
            # Convert effect ID to slot type item takes
            try:
                slot = self.__effectSlotMap[effect.id]
            # Silently skip effect if it's not in map
            except KeyError:
                pass
            else:
                slots.add(slot)
        return slots
