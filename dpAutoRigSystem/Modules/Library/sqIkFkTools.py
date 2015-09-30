try:
    from sstk.libs import libSerialization
except:
    import libSerialization

import pymel.core as pymel
from maya import cmds
import logging, functools

# Ensure we always deal with pynodes
def _cast_string_to_pynode(val):
    if isinstance(val, pymel.PyNode): return val
    if isinstance(val, basestring): 
        if not cmds.objExists(val):
            raise Exception("Can't find object {0}".format(val))
        return pymel.PyNode(val)
    if isinstance(val, list): return [_cast_string_to_pynode(subval) for subval in val]
    raise IOError("Invalid argument {0}, expected type string or PyNode, got {1}".format(subval, type(subval)))

# Ensure we always deal with attributes
def _cast_string_to_attribute(val):
    if isinstance(val, pymel.Attribute): return val
    if isinstance(val, basestring): 
        if not cmds.objExists(val):
            raise Exception("Can't find attribute {0}".format(val))
        return pymel.Attribute(val)
    if isinstance(val, list): return [_cast_string_to_attribute(subval) for subval in val]
    raise IOError("Invalid argument {0}, expected type string or Attribute, got {1}".format(subval, type(subval)))

class IkFkNetwork(object):
    _state_ik = 0.0
    _state_fk = 1.0

    def init(self, ikCtrl, ikCtrlSwivel, ikChain, fkCtrls, attState, iEndIndex=2, footRollAtts=[], otherCtrls=[]):
        # Validate arguments
        self.ikCtrl       = _cast_string_to_pynode(ikCtrl)
        self.ikCtrlSwivel = _cast_string_to_pynode(ikCtrlSwivel)
        self.ikChain      = _cast_string_to_pynode(ikChain)
        self.fkCtrls      = _cast_string_to_pynode(fkCtrls)
        self.iEndIndex    = iEndIndex
        self.attState     = _cast_string_to_attribute(attState)
        self.footRollAtts = _cast_string_to_attribute(footRollAtts)
        self.otherCtrls   =_cast_string_to_pynode(otherCtrls) # The only goal of this attribute is to use additional control to detect a limb

        # Compute transform offset between ikCtrl and corresponding fkCtrl
        fkHandCtrl = self.fkCtrls[self.iEndIndex]
        self.ikCtrlOffset = self.ikCtrl.getMatrix(worldSpace=True) * fkHandCtrl.getMatrix(worldSpace=True).inverse()

    def _get_swivel_middle(self, posS, posM, posE):
        fLengthS = posM.distanceTo(posS)
        fLengthE = posM.distanceTo(posE)
        fLengthRatio = fLengthS / (fLengthS+fLengthE)
        return (posE - posS) * fLengthRatio + posS

    def snapIkToFk(self):
        # Set ikCtrl transform
        tmCtrlFk = self.fkCtrls[self.iEndIndex].getMatrix(worldSpace=True)
        self.ikCtrl.setMatrix(self.ikCtrlOffset * tmCtrlFk, worldSpace=True)

        # Set ikCtrlSwivel transform
        posRef = self.fkCtrls[self.iEndIndex-1].getTranslation(space='world')
        posS = self.fkCtrls[0].getTranslation(space='world')
        posM = self.fkCtrls[self.iEndIndex-1].getTranslation(space='world')
        posE = self.fkCtrls[self.iEndIndex].getTranslation(space='world')
        posRefPos = self._get_swivel_middle(posS, posM, posE)
        posDir = posM - posRefPos
        posDir.normalize()
        fSwivelDistance = posS.distanceTo(posE)
        posSwivel = posDir * fSwivelDistance + posRef

        self.ikCtrl.setMatrix(self.ikCtrlOffset * tmCtrlFk, worldSpace=True)
        self.ikCtrlSwivel.setTranslation(posSwivel, space='world')

        # Reset footroll attributes
        if hasattr(self, 'footRollAtts'): # Hack: libSerialization don't write the attribute if it's empty wich can cause a crash
            for att in self.footRollAtts:
                att.set(0)

    def snapFkToIk(self):
        for ctrl, jnt in zip(self.fkCtrls, self.ikChain):
            ctrl.setMatrix(jnt.getMatrix(worldSpace=True), worldSpace=True)
        

    def switchToIk(self):
        if self.attState.get() != self._state_ik:
            self.snapIkToFk()
            self.attState.set(self._state_ik)

    def switchToFk(self):
        if self.attState.get() != self._state_fk:
            self.snapFkToIk()
            self.attState.set(self._state_fk)

# taken from omtk.animation.ikfkTools
def CallFnOnNetworkByClass(_sFn, _sCls):
    fnFilter = lambda x: libSerialization.isNetworkInstanceOfClass(x, _sCls)
    networks = libSerialization.getConnectedNetworks(pymel.selected(), key=fnFilter, recursive=False)
    for network in networks:
        rigPart = libSerialization.import_network(network)

        if not hasattr(rigPart, _sFn):
            logging.warning("Can't find attribute {0} in {1}".format(_sFn, network)); continue

        try:
            getattr(rigPart, _sFn)()
        except Exception, e:
            print str(e)

switchToIk = functools.partial(CallFnOnNetworkByClass, 'switchToIk', 'IkFkNetwork')
switchToFk = functools.partial(CallFnOnNetworkByClass, 'switchToFk', 'IkFkNetwork')

'''
from sstk.maya.animation import sqIkFkTools
from sstk.libs import libSerialization

# Usage example (arm)
data = sqIkFkTools.IkFkNetwork()
data.init(
    'L_Arm_Wrist_Ik_Ctrl',
    'L_Arm_Elbo_Ik_Ctrl',
    ['L_Arm_Shoulder_Ik_Jxt', 'L_Arm_Elbow_Ik_Jxt', 'L_Arm_Wrist_Ik_Jxt'],
    ['L_Arm_Shoulder_Fk_Ctrl', 'L_Arm_Elbow_Fk_Ctrl', 'L_Arm_Wrist_Fk_Ctrl'],
    'Option_Ctrl.L_arm',
    otherCtrls=[
        'L_Up_Arm_Off_Ctrl',
        'L_Down_Arm_Off_Ctrl',
        'L_Arm_Off_Ctrl',
        'L_Arm_Wrist_ToParent_Ctrl'
    ]
)
net = libSerialization.export_network(data)

# Usage example (leg)
data = sqIkFkTools.IkFkNetwork()
data.init(
    'L_Leg_Ankle_Ik_Ctrl',
    'L_Leg_Kne_Ik_Ctrl',
    ['L_Leg_Leg_Ik_Jxt', 'L_Leg_Knee_Ik_Jxt', 'L_Leg_Ankle_Ik_Jxt', 'L_Foot_Middle_Jxt'],
    ['L_Leg_Leg_Fk_Ctrl', 'L_Leg_Knee_Fk_Ctrl', 'L_Leg_Ankle_Fk_Ctrl', 'L_Foot_Middle_Ctrl'],
    'Option_Ctrl.L_leg',
    footRollAtts=[
        'L_Leg_Ankle_Ik_Ctrl.outside_roll',
        'L_Leg_Ankle_Ik_Ctrl.outside_spin',
        'L_Leg_Ankle_Ik_Ctrl.inside_roll',
        'L_Leg_Ankle_Ik_Ctrl.inside_spin',
        'L_Leg_Ankle_Ik_Ctrl.heel_roll',
        'L_Leg_Ankle_Ik_Ctrl.heel_spin',
        'L_Leg_Ankle_Ik_Ctrl.toe_roll',
        'L_Leg_Ankle_Ik_Ctrl.toe_spin',
        'L_Leg_Ankle_Ik_Ctrl.ball_roll',
        'L_Leg_Ankle_Ik_Ctrl.ball_turn',
        'L_Leg_Ankle_Ik_Ctrl.ball_spin',
        'L_Leg_Ankle_Ik_Ctrl.foot_roll',
        'L_Leg_Ankle_Ik_Ctrl.side_roll'
    ],
    otherCtrls=[
        'L_Up_Leg_Off_Ctrl',
        'L_Down_Leg_Off_Ctrl',
        'L_Leg_Off_Ctrl',
        'L_Leg_Ankle_ToParent_Ctrl',
        'L_Foot_Middle_Ctrl'
    ]
)
net = libSerialization.export_network(data)

#data.switchToFk()
#data.switchToIk()
'''
