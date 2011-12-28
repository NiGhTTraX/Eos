from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestItmMod(TestCase):
    def testBuildSuccess(self):
        target = Expression(1, 24, value="Ship")
        tgtAttr = Expression(2, 22, attributeId=9)
        operator = Expression(3, 21, value="PostPercent")
        srcAttr = Expression(4, 22, attributeId=327)
        tgtSpec = Expression(5, 12, arg1=target, arg2=tgtAttr)
        optrTgt = Expression(6, 31, arg1=operator, arg2=tgtSpec)
        addMod = Expression(7, 6, arg1=optrTgt, arg2=srcAttr)
        rmMod = Expression(8, 58, arg1=optrTgt, arg2=srcAttr)
        infos, status = InfoBuilder().build(addMod, rmMod)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoDuration
        self.assertEqual(info.type, expType, msg="info type must be duration (ID {})".format(expType))
        self.assertFalse(info.gang, msg="info gang flag must be False")
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 9
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expTgtAttr = 327
        self.assertEqual(info.sourceAttributeId, expTgtAttr, msg="info source attribute ID must be {}".format(expTgtAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")
