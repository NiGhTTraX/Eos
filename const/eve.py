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


"""
This file holds IDs of multiple EVE's entities.
"""


from eos.util.enum import Enum


class Attribute(metaclass=Enum):
    """Attribute ID holder"""
    mass = 4
    powerOutput = 11
    lowSlots = 12
    medSlots = 13
    hiSlots = 14
    cpuOutput = 48
    power = 30
    capacity = 38
    cpu = 50
    agility = 70
    launcherSlotsLeft = 101
    turretSlotsLeft = 102
    emDamage = 114
    explosiveDamage = 116
    kineticDamage = 117
    thermalDamage = 118
    volume = 161
    radius = 162
    requiredSkill1 = 182
    requiredSkill2 = 183
    requiredSkill3 = 184
    missileDamageMultiplier = 212
    requiredSkill1Level = 277
    requiredSkill2Level = 278
    requiredSkill3Level = 279
    skillLevel = 280
    droneCapacity = 283
    implantness = 331
    maxActiveDrones = 352
    maxGroupActive = 763
    maxGroupOnline = 978
    boosterness = 1087
    upgradeCapacity = 1132
    rigSlots = 1137
    upgradeCost = 1153
    droneBandwidth = 1271
    droneBandwidthUsed = 1272
    requiredSkill4 = 1285
    requiredSkill4Level = 1286
    requiredSkill5Level = 1287
    requiredSkill6Level = 1288
    requiredSkill5 = 1289
    requiredSkill6 = 1290
    canFitShipGroup1 = 1298
    canFitShipGroup2 = 1299
    canFitShipGroup3 = 1300
    canFitShipGroup4 = 1301
    canFitShipType1 = 1302
    canFitShipType2 = 1303
    canFitShipType3 = 1304
    canFitShipType4 = 1305
    subSystemSlot = 1366
    maxSubSystems = 1367
    fitsToShipType = 1380
    maxGroupFitted = 1544
    rigSize = 1547
    allowedDroneGroup1 = 1782
    allowedDroneGroup2 = 1783


class Type(metaclass=Enum):
    """Item ID holder"""
    characterStatic = 1381
    missileLauncherOperation = 3319  # Skill
    capitalShips = 20533  # Skill


class Group(metaclass=Enum):
    """Group ID holder"""
    character = 1
    effectBeacon = 920


class Category(metaclass=Enum):
    """Category ID holder"""
    ship = 6
    module = 7
    charge = 8
    skill = 16
    drone = 18
    implant = 20
    subsystem = 32


class Effect(metaclass=Enum):
    """Effect ID holder"""
    loPower = 11
    hiPower = 12
    medPower = 13
    online = 16
    launcherFitted = 40
    turretFitted = 42
    rigSlot = 2663
    subSystem = 3772


class EffectCategory(metaclass=Enum):
    """Effect category ID holder"""
    passive = 0  # Applied when item is just present in fit - implants, skills, offlined modules
    active = 1  # Applied only when module is activated
    target = 2  # Applied onto selected target
    area = 3  # No effects with this category, so actual impact is unknown
    online = 4  # Applied when module at least onlined
    overload = 5  # Applied only when module is overloaded
    dungeon = 6  # Dungeon effects, several effects exist in this category, but not assigned to any item
    system = 7  # System-wide effects, like WH and incursion


class Operand(metaclass=Enum):
    """Expression operand ID holder"""
    add = 1  # Add two numbers to return result, used in conditions
    addGangGrpMod = 2  # Applies modification to items of gang-mates (not used in any effect), filtered by group, format: [(groupFilter.targetAttribute).(operator)].AGGM(sourceAttribute)
    addGangItmMod = 3  # Applies modification directly to ships gang-mates, format: ((targetAttribute).(operator)).AGIM(sourceAttribute)
    addGangOwnSrqMod = 4  # Applies modification to items of gang-mates (not used in any effect), filtered by owner and skill requirement
    addGangSrqMod = 5  # Applies modification to items of gang-mates, filtered by skill requirement, format: (skillRequirement.targetAttribute).(operator)).AGRSM(sourceAttribute))
    addItmMod = 6  # Applies modification directly to some item, format: ((location->targetAttribute).(operator)).AIM(sourceAttribute)
    addLocGrpMod = 7  # Applies modification to items belonging to some location, filtered by group, format: ((location..groupFilter->targetAttribute).(operator)).ALGM(sourceAttribute)
    addLocMod = 8  # Applies modification to all items belonging to some location, format: ((location->targetAttribute).(operator)).ALM(sourceAttribute)
    addLocSrqMod = 9  # Applies modification to items belonging to some location, filtered by skill requirement, format: ((location[skillRequirement]->targetAttribute).(operator)).ALRSM(sourceAttribute)
    and_ = 10  # Logical AND operator
    addOwnSrqMod = 11  # Applies modification to items belonging to some location, filtered by owner of source, format: ((location[skillRequirement]->targetAttribute).(operator)).AORSM(sourceAttribute)
    itmAttr = 12  # Joins target items and attribute into target definition, format: location->targetAttribute
    attack = 13  # Special operand, handles turret attack
    cargoScan = 14  # Special operand, used to define cargo scan
    cheatTeleDock = 15  # Special operand, handles GM tools
    cheatTeleGate = 16  # Special operand, handles GM tools
    splice = 17  # Executes two statements, format: expression1; expression2
    dec = 18  # Decreases value for some attribute by value of another one
    aoeDecloak = 19  # Special operand, defines area-of-effect decloak
    defOptr = 21  # Define operator, text in expressionValue field
    defAttr = 22  # Define attribute, integer in expressionAttributeID field
    defBool = 23  # Define boolean constant, boolean in expressionValue field
    defLoc = 24  # Define location, text in expressionValue field
    defGrp = 26  # Define group, integer in expressionGroupID field
    defInt = 27  # Defines an integer constant, integer in expressionValue field
    defType = 29  # Define a type, integer in expressionTypeID field
    ecmBurst = 30  # Special operand, used in ECM Burst effects
    optrTgt = 31  # Joins operator and target (attribute of possibly filtered items) definitions, format: (location->targetAttribute).(operator)
    aoeDmg = 32  # Special operand, defines area-of-effect damage for modules like smartbombs and old doomsday
    eq = 33  # Check for equality, used in conditions
    grpAttr = 34  # Joins group and attribute into target definition, format: groupFilter.targetAttribute
    itmAttrCond = 35  # Joins target item and its attribute, used in conditions
    getType = 36  # Gets type of item in arg1
    greater = 38  # Check for arg1 being greater than arg2, used in conditions
    greaterEq = 39  # Check for arg1 being greater than or equal to arg2, used in conditions
    genAttr = 40  # Generic attribute reference, doesn't join anything, just refers attribute definition
    ifThen = 41  # If-then construct
    inc = 42  # Increases value of some attribute by the value of another one
    missileLaunch = 44  # Special operand, handles missile launching
    defenderLaunch = 45  # Special operand, handles defender missile launching
    fofLaunch = 47  # Special operand, handles friend-or-foe missile launching
    locGrp = 48  # Joins location and group definitions into single filter, format: location..group
    locSrq = 49  # Joins location and skill requirement definitions into single filter, format: location[skillRequirement]
    mine = 50  # Special operand, handles transfer of ore from asteroid to cargo
    or_ = 52  # Logical OR operand, also used as else clause in if-then constructions
    powerBooster = 53  # Special operand, defines cap booster effect
    rmGangGrpMod = 54  # Undos modification from items of gang-mates, filtered by group, format: [(groupFilter.targetAttribute).(operator)].RGGM(sourceAttribute)
    rmGangItmMod = 55  # Undos modification directly from ships gang-mates, format: ((targetAttribute).(operator)).RGIM(sourceAttribute)
    rmGangOwnSrqMod = 56  # Undos modification from items of gang-mates, filtered by owner and skill requirement
    rmGangSrqMod = 57  # Undos modification from items of gang-mates, filtered by skill requirement, format: (skillRequirement.targetAttribute).(operator)).RGRSM(sourceAttribute))
    rmItmMod = 58  # Undos modification directly from some item, format: ((location->targetAttribute).(operator)).RIM(sourceAttribute)
    rmLocGrpMod = 59  # Undos modification from items belonging to some location, filtered by group, format: ((location..groupFilter->targetAttribute).(operator)).RLGM(sourceAttribute)
    rmLocMod = 60  # Undos modification from all items belonging to some location, format: ((location->targetAttribute).(operator)).RLM(sourceAttribute)
    rmLocSrqMod = 61  # Undos modification from items belonging to some location, filtered by skill requirement, format: ((location[skillRequirement]->targetAttribute).(operator)).RLRSM(sourceAttribute)
    rmOwnSrqMod = 62  # Undos modification from items belonging to some location, filtered by owner of source, format: ((location[skillRequirement]->targetAttribute).(operator)).RORSM(sourceAttribute)
    srqAttr = 64  # Joins skill requirement and attribute into target definition, format: skillRequirement.targetAttribute
    assign = 65  # Direct assignment to one attribute value of another one
    shipScan = 66  # Special operand, used to define ship scan
    sub = 68  # Subtracts one number from another and returns result, used in conditions
    surveyScan = 69  # Special operand, used to define ore scan
    tgtHostile = 70  # Special operand, used in auto-targeting systems
    tgtSilent = 71  # Special operand, used in passive targeting systems
    toolTgtSkills = 72  # Special operand, most likely checks if you have enough skills to use currently loaded charge, or have enough skills to work with current target
    userError = 73  # In erroneous cases, raises user error provided in arg1
    vrfTgtGrp = 74  # Special operand, used to verify if target can have effect's carrier applied onto it, otherwise raises error
