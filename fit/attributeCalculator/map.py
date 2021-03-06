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


from math import exp

from eos.const.eos import Operator
from eos.const.eve import Category, Attribute
from eos.data.cache.handler.exception import AttributeFetchError
from eos.util.keyedSet import KeyedSet
from .exception import BaseValueError, AttributeMetaError, OperatorError


# Stacking penalty base constant, used in attribute calculations
penaltyBase = 1 / exp((1 / 2.67) ** 2)

# Items belonging to these categories never have
# their effects stacking penalized
penaltyImmuneCategories = (Category.ship, Category.charge, Category.skill, Category.implant, Category.subsystem)

# Tuple with penalizable operators
penalizableOperators = (Operator.preMul, Operator.postMul, Operator.postPercent, Operator.preDiv, Operator.postDiv)

# Map which helps to normalize modifiers
normalizationMap = {Operator.preAssignment: lambda val: val,
                    Operator.preMul: lambda val: val,
                    Operator.preDiv: lambda val: 1 / val,
                    Operator.modAdd: lambda val: val,
                    Operator.modSub: lambda val: -val,
                    Operator.postMul: lambda val: val,
                    Operator.postDiv: lambda val: 1 / val,
                    Operator.postPercent: lambda val: val / 100 + 1,
                    Operator.postAssignment: lambda val: val}

# List operator types, according to their already normalized values
assignments = (Operator.preAssignment, Operator.postAssignment)
additions = (Operator.modAdd, Operator.modSub)
multiplications = (Operator.preMul, Operator.preDiv, Operator.postMul, Operator.postDiv, Operator.postPercent)


class MutableAttributeMap:
    """
    Calculate, store and provide access to modified attribute values.

    Positional arguments:
    holder -- holder, to which this map is assigned
    """

    __slots__ = ('__holder', '__modifiedAttributes', '_capMap')

    def __init__(self, holder):
        # Reference to holder for internal needs
        self.__holder = holder
        # Actual container of calculated attributes
        # Format: {attribute ID: value}
        self.__modifiedAttributes = {}
        # This variable stores map of attributes which cap
        # something, and attributes capped by them. Initialized
        # to None to not waste memory, will be changed to dict
        # when needed.
        # Format {capping attribute ID: {capped attribute IDs}}
        self._capMap = None

    def __getitem__(self, attrId):
        # Special handling for skill level attribute
        if attrId == Attribute.skillLevel:
            # Attempt to return level attribute of holder
            try:
                val = self.__holder.level
            # Try regular way of getting attribute, if accessing
            # level attribute failed
            except AttributeError:
                pass
            else:
                return val
        # If carrier holder isn't assigned to any fit, then
        # we can use just item's original attributes
        if self.__holder._fit is None:
            val = self.__holder.item.attributes[attrId]
            return val
        # If value is stored, it's considered valid
        try:
            val = self.__modifiedAttributes[attrId]
        # Else, we have to run full calculation process
        except KeyError:
            try:
                val = self.__modifiedAttributes[attrId] = self.__calculate(attrId)
            except BaseValueError as e:
                msg = 'unable to find base value for attribute {} on item {}'.format(e.args[0], self.__holder.item.id)
                signature = (type(e), self.__holder.item.id, e.args[0])
                self.__holder._fit.eos._logger.warning(msg, childName='attributeCalculator', signature=signature)
                raise KeyError(attrId) from e
            except AttributeMetaError as e:
                msg = 'unable to fetch metadata for attribute {}, requested for item {}'.format(e.args[0], self.__holder.item.id)
                signature = (type(e), self.__holder.item.id, e.args[0])
                self.__holder._fit.eos._logger.error(msg, childName='attributeCalculator', signature=signature)
                raise KeyError(attrId) from e
            self.__holder._fit._linkTracker.clearHolderAttributeDependents(self.__holder, attrId)
        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attrId):
        # Seek for attribute in both modified attribute container
        # and original item attributes
        result = attrId in self.__modifiedAttributes or attrId in self.__holder.item.attributes
        return result

    def __iter__(self):
        for k in self.keys():
            yield k

    def __delitem__(self, attrId):
        # Clear the value in our calculated attributes dictionary
        try:
            del self.__modifiedAttributes[attrId]
        # Do nothing if it wasn't calculated
        except KeyError:
            pass
        # And make sure all other attributes relying on it
        # are cleared too
        else:
            self.__holder._fit._linkTracker.clearHolderAttributeDependents(self.__holder, attrId)

    def __setitem__(self, attrId, value):
        # Write value and clear all attributes relying on it
        self.__modifiedAttributes[attrId] = value
        self.__holder._fit._linkTracker.clearHolderAttributeDependents(self.__holder, attrId)

    def get(self, attrId, default=None):
        try:
            return self[attrId]
        except KeyError:
            return default

    def keys(self):
        # Return union of both keys which are already calculated in
        return self.__modifiedAttributes.keys() | self.__holder.item.attributes.keys()

    def clear(self):
        """Reset map to its initial state."""
        self.__modifiedAttributes.clear()
        self._capMap = None

    def __calculate(self, attrId):
        """
        Run calculations to find the actual value of attribute.

        Positional arguments:
        attrId -- ID of attribute to be calculated

        Return value:
        Calculated attribute value

        Possible exceptions:
        BaseValueError -- attribute cannot be calculated, as its
        base value is not available
        """
        # Attribute object for attribute being calculated
        try:
            attrMeta = self.__holder._fit.eos._cacheHandler.getAttribute(attrId)
        # Raise error if we can't get to getAttribute method
        # or it can't find requested attribute
        except (AttributeError, AttributeFetchError) as e:
            raise AttributeMetaError(attrId) from e
        # Base attribute value which we'll use for modification
        try:
            result = self.__holder.item.attributes[attrId]
        # If attribute isn't available on base item,
        # base off its default value
        except KeyError:
            result = attrMeta.defaultValue
            # If original attribute is not specified and default
            # value isn't available, raise error - without valid
            # base we can't go on
            if result is None:
                raise BaseValueError(attrId)
        # Container for non-penalized modifiers
        # Format: {operator: [values]}
        normalMods = {}
        # Container for penalized modifiers
        # Format: {operator: [values]}
        penalizedMods = {}
        # Now, go through all affectors affecting our holder
        for affector in self.__holder._fit._linkTracker.getAffectors(self.__holder, attrId=attrId):
            try:
                sourceHolder, modifier = affector
                operator = modifier.operator
                # Decide if it should be stacking penalized or not, based on stackable property,
                # source item category and operator
                penalize = (attrMeta.stackable is False and sourceHolder.item.categoryId not in penaltyImmuneCategories
                            and operator in penalizableOperators)
                try:
                    modValue = sourceHolder.attributes[modifier.sourceAttributeId]
                # Silently skip current affector: error should already
                # be logged by map before it raised KeyError
                except KeyError:
                    continue
                # Normalize operations to just three types:
                # assignments, additions, multiplications
                try:
                    normalizationFunc = normalizationMap[operator]
                # Raise error on any unknown operator types
                except KeyError as e:
                    raise OperatorError(operator) from e
                modValue = normalizationFunc(modValue)
                # Add value to appropriate dictionary
                if penalize is True:
                    modList = penalizedMods.setdefault(operator, [])
                else:
                    modList = normalMods.setdefault(operator, [])
                modList.append(modValue)
            # Handle operator type failure
            except OperatorError as e:
                msg = 'malformed modifier on item {}: unknown operator {}'.format(sourceHolder.item.id, e.args[0])
                signature = (type(e), sourceHolder.item.id, e.args[0])
                self.__holder._fit.eos._logger.warning(msg, childName='attributeCalculator', signature=signature)
                continue
        # When data gathering is complete, process penalized modifiers
        # They are penalized on per-operator basis
        for operator, modList in penalizedMods.items():
            penalizedValue = self.__penalizeValues(modList)
            modList = normalMods.setdefault(operator, [])
            modList.append(penalizedValue)
        # Calculate result of normal dictionary, according to operator order
        for operator in sorted(normalMods):
            modList = normalMods[operator]
            # Pick best modifier for assignments, based on highIsGood value
            if operator in assignments:
                result = max(modList) if attrMeta.highIsGood is True else min(modList)
            elif operator in additions:
                for modVal in modList:
                    result += modVal
            elif operator in multiplications:
                for modVal in modList:
                    result *= modVal
        # If attribute has upper cap, do not let
        # its value to grow above it
        if attrMeta.maxAttributeId is not None:
            try:
                maxValue = self[attrMeta.maxAttributeId]
            # If max value isn't available, don't
            # cap anything
            except KeyError:
                pass
            else:
                result = min(result, maxValue)
                # Let map know that capping attribute
                # restricts current attribute
                if self._capMap is None:
                    self._capMap = KeyedSet()
                # Fill cap map with data: capping attribute and capped attribute
                self._capMap.addData(attrMeta.maxAttributeId, attrId)
        return result

    def __penalizeValues(self, modList):
        """
        Calculate aggregated factor of passed factors, taking into
        consideration stacking penalty.

        Positional argument:
        modList -- list of factors

        Return value:
        Final aggregated factor of passed modList
        """
        # Gather positive modifiers into one chain, negative
        # into another
        chainPositive = []
        chainNegative = []
        for modVal in modList:
            # Transform value into form of multiplier - 1 for ease of
            # stacking chain calculation
            modVal -= 1
            if modVal >= 0:
                chainPositive.append(modVal)
            else:
                chainNegative.append(modVal)
        # Strongest modifiers always go first
        chainPositive.sort(reverse=True)
        chainNegative.sort()
        # Base final multiplier on 1
        listResult = 1
        for chain in (chainPositive, chainNegative):
            # Same for intermediate per-chain result
            chainResult = 1
            for position, modifier in enumerate(chain):
                # Ignore 12th modifier and further as non-significant
                if position > 10:
                    break
                # Apply stacking penalty based on modifier position
                chainResult *= 1 + modifier * penaltyBase ** (position ** 2)
            listResult *= chainResult
        return listResult
