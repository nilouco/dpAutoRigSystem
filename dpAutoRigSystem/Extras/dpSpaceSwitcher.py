import math
import maya.cmds as cmds
import pymel.core as pymel
import maya.OpenMaya as om
from ..Modules.Library import dpControls as ctrlUtil
from ..Modules.Library import dpUtils as utils


# global variables to this module:
CLASS_NAME = "SpaceSwitcher"
TITLE = "m047_colorOver"
DESCRIPTION = "m048_coloOverDesc"
ICON = ""

class SpaceSwitcher:

    """
    This class is used to setup a spaceSwitch system on a node
    """

    def __init__(self):
        self.aDrivers = []
        self.nDriven = None
        self.nSwConst = None #SpaceSwitch constraint for the system
        self.nSwConstRecept = None #Space Switch receiver
        self.nSwOff = None #Space Switch offset
        self.iActiveWeight = 0
        tempWorld = pymel.ls("dp_sp_worldNode")
        if tempWorld:
            self.worldNode = tempWorld[0]
        else:
            self.worldNode = None

    def setup_space_switch(self):
            aCurSel = pymel.selected()
            aParent = aCurSel[0:-1]
            bContinue = False
            #Create the worldNode
            if (not self.worldNode):
                self.worldNode = pymel.createNode("transform", n="dp_sp_worldNode")
                ctrlUtil.setLockHide([self.worldNode.__melobject__()], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

            self.aDrivers.append(self.worldNode)

            if (len(aCurSel) == 0):
                pymel.informBox("Space Switcher", "You need to choose at least the node to constraint")
            #The user only selected the driven node, so create a space switch between it's parent and the world
            elif (len(aCurSel) == 1):
                self.nDriven = aCurSel[0]
                bContinue = True
            else:
                self.nDriven = aCurSel[-1]
                bContinue = True

            if bContinue:
                #Setup the intermediate node to manage the spaceSwitch
                self.nSwConstRecept = pymel.PyNode(utils.zeroOut(transformList=[self.nDriven.__melobject__()])[0])
                self.nSwConstRecept.rename(self.nDriven.name() + "_SW_Const")
                m4Driven = self.nDriven.getMatrix(worldSpace=True)
                self.nSwConstRecept.setMatrix(m4Driven, worldSpace=True)
                self.nDriven.setParent(self.nSwConstRecept)

                #Create the parent constraint for the first node, but add the other target manually
                self.nSwConst = pymel.parentConstraint(self.worldNode, self.nSwConstRecept, n=self.nDriven.name() + "_SpaceSwitch_Const", mo=True)
                pymel.setKeyframe(self.nSwConst.getWeightAliasList()[0], t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[0].targetOffsetTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[0].targetOffsetRotate, t=0, ott="step")
                self.add_target(aParent)

    def add_target(self, aNewParent, firstSetup=False):
        iNbTgt = len(self.nSwConst.getWeightAliasList())
        aExistTgt = self.nSwConst.getTargetList()
        bContinue = True

        if aExistTgt:
            for nTgt in aExistTgt:
                if (nTgt in aNewParent) and bContinue:
                    pymel.informBox("Space Switcher", "Cannot add target " + nTgt.name() + " because it is already added to the list of parent")
                    bContinue = False

        if bContinue:
            for nParent in aNewParent:
                #First, calculate the offset between the parent and the driven node
                vTrans = self._get_tm_offset(nParent, type="t")
                vRot = self._get_tm_offset(nParent, type="r")

                #Connect the new target manually in the parent constraint
                if (iNbTgt == 0):
                    self.nSwConst.addAttr(nParent.name() + "W" + str(iNbTgt), at="double", min=0, max=1, dv=1, k=True, h=False)
                else:
                    self.nSwConst.addAttr(nParent.name() + "W" + str(iNbTgt), at="double", min=0, max=1, dv=0, k=True, h=False)

                pymel.connectAttr(nParent.parentMatrix, self.nSwConst.target[iNbTgt].targetParentMatrix)
                pymel.connectAttr(nParent.scale, self.nSwConst.target[iNbTgt].targetScale)
                pymel.connectAttr(nParent.rotateOrder, self.nSwConst.target[iNbTgt].targetRotateOrder)
                pymel.connectAttr(nParent.rotate, self.nSwConst.target[iNbTgt].targetRotate)
                pymel.connectAttr(nParent.rotatePivotTranslate, self.nSwConst.target[iNbTgt].targetRotateTranslate)
                pymel.connectAttr(nParent.rotatePivot, self.nSwConst.target[iNbTgt].targetRotatePivot)
                pymel.connectAttr(nParent.translate, self.nSwConst.target[iNbTgt].targetTranslate)
                #Link the created attributes to the weight value of the target
                nConstTgtWeight = pymel.Attribute(self.nSwConst.name() + "." + nParent.name() + "W" + str(iNbTgt))
                pymel.connectAttr(nConstTgtWeight, self.nSwConst.target[iNbTgt].targetWeight)

                '''
                #Set the offset information
                self.nSwConst.target[iNbTgt].targetOffsetTranslateX.set(vTrans[0])
                self.nSwConst.target[iNbTgt].targetOffsetTranslateY.set(vTrans[1])
                self.nSwConst.target[iNbTgt].targetOffsetTranslateZ.set(vTrans[2])
                self.nSwConst.target[iNbTgt].targetOffsetRotateX.set(vRot[0])
                self.nSwConst.target[iNbTgt].targetOffsetRotateY.set(vRot[1])
                self.nSwConst.target[iNbTgt].targetOffsetRotateZ.set(vRot[2])
                '''

                #Need to be setted with cmds, because pymel give strange error
                cmds.setAttr("%s.target[%s].targetOffsetTranslateX"%(self.nSwConst.__melobject__(), iNbTgt), vTrans[0])
                cmds.setAttr("%s.target[%s].targetOffsetTranslateY"%(self.nSwConst.__melobject__(), iNbTgt), vTrans[1])
                cmds.setAttr("%s.target[%s].targetOffsetTranslateZ"%(self.nSwConst.__melobject__(), iNbTgt), vTrans[2])
                cmds.setAttr("%s.target[%s].targetOffsetRotateX"%(self.nSwConst.__melobject__(), iNbTgt), vRot[0])
                cmds.setAttr("%s.target[%s].targetOffsetRotateY"%(self.nSwConst.__melobject__(), iNbTgt), vRot[1])
                cmds.setAttr("%s.target[%s].targetOffsetRotateZ"%(self.nSwConst.__melobject__(), iNbTgt), vRot[2])

                pymel.setKeyframe(nConstTgtWeight, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetTranslate, t=0, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iNbTgt].targetOffsetRotate, t=0, ott="step")
                self.aDrivers.append(nParent)
                iNbTgt += 1


    def _get_tm_offset(self, nParent, type="t"):
        mStart = om.MMatrix()
        mEnd =  om.MMatrix()

        wmStart = nParent.worldMatrix.get().__melobject__()
        wmEnd = self.nDriven.worldMatrix.get().__melobject__()

        om.MScriptUtil().createMatrixFromList(wmStart,mStart)
        om.MScriptUtil().createMatrixFromList(wmEnd,mEnd)

        mOut = om.MTransformationMatrix(mEnd * mStart.inverse())

        if type == "t":
            vTran = om.MVector(mOut.getTranslation(om.MSpace.kTransform))
            return vTran.x,vTran.y,vTran.z
        if type == "r":
            ro = self.nDriven.rotateOrder.get()
            vRot = om.MEulerRotation(mOut.eulerRotation().reorder(ro))
            return math.degrees(vRot.x), math.degrees(vRot.y), math.degrees(vRot.z)


    def do_switch(self, iIdx):
        fCurTime = pymel.currentTime()
        #Just try to update the offset of the parent constraint before the switch
        aWeight = self.nSwConst.getWeightAliasList()
        if (len(aWeight) > iIdx):
            if (self.iActiveWeight != iIdx):
                self.iActiveWeight = iIdx
                #Update constraint offset of the next index in the constraint
                pymel.parentConstraint(self.aDrivers[iIdx], self.nSwConst, mo=True, e=True)
                #Key the offset to prevent offset problem when coming back to the same parent
                pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetTranslate, t=fCurTime, ott="step")
                pymel.setKeyframe(self.nSwConst.target[iIdx].targetOffsetRotate, t=fCurTime, ott="step")
                for i,wAlias in enumerate(aWeight):
                    if (i == iIdx):
                        wAlias.set(1.0)
                    else:
                        wAlias.set(0.0)
                #Set a keyframe on the weight to keep the animation
                pymel.setKeyframe(aWeight, t=fCurTime, ott="step")
                
        else:
            print "Cannot switch target, index is bigger than the number of target"


#test = SpaceSwitcher()
#test.doSwitch(0)
#test.doSwitch(1)