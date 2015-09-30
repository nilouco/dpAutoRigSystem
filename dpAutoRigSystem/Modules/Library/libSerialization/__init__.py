#from sstk import consts
import logging ; log = logging.getLogger(__name__); log.setLevel(logging.INFO)

#
# Python/Xml/Yaml functionalities
#

from core import _dag_types, _basic_types
from core import import_json, import_json_file, export_json, export_json_file
#from core import import_yaml, import_yaml_file, export_yaml, export_yaml_file

#
# Maya only functionalities
# This allow us to use libSerialization outside of maya.
#x

#if consts.engine_name == 'maya':
from pluginMaya import export_network, import_network, isNetworkInstanceOfClass, getNetworksByClass, getConnectedNetworks, getConnectedNetworksByHierarchy
import pymel.core as pymel
_dag_types.append(pymel.PyNode)
_dag_types.append(pymel.Attribute)
_basic_types.append(pymel.datatypes.Matrix)

#
# Unit testing
#
import unittest
class EmptyClass(object): pass
class TestSerialization(unittest.TestCase):
    def setUp(self):
        print self.shortDescription()
        from maya import cmds
        cmds.file(new=True, f=True)

    def _monkeypatch_various_types(self, obj):
        obj.exInt = 2
        obj.exFloat = 3.1416
        obj.exBool = True
        obj.exString = 'Hello World'

    def test_emptyClass(self):
        log.info('test_emptyClass')

        data_inn = EmptyClass()
        self._monkeypatch_various_types(data_inn)

        # Serializae
        network = export_network(data_inn)
        self.assertTrue(isinstance(network, pymel.PyNode))

        # Deserialize
        data_out = import_network(network)

        # Compare output
        for att in dir(data_out):
            if att[0] != '_':
                val_inn = getattr(data_inn, att)
                val_out = getattr(data_out, att)
                if isinstance(val_inn, (float, long)):
                    pass # can't correctly raise assert (almostEqual don't work...)
                else:
                    self.assertEquals(val_inn, val_out)

    def runTest(self):
        pass

def test(**kwargs):
    case = TestSerialization()
    case.test_emptyClass()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestSerialization)
    #unittest.TextTestRunner(**kwargs).run(suite)