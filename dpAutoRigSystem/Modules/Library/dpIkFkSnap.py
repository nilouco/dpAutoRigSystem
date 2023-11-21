###
#
#   THANKS to:
#       Renaud Lessard
#
#   Based on:
#       https://github.com/renaudll/omtk/blob/9b756fb9e822bf03b4c643328a283d29187298fd/omtk/animation/ikfkTools.py
#   
###


# importing libraries:
from maya import cmds
from maya.api import OpenMaya
import math

DP_IKFKSNAP_VERSION = 2.0



class IkFkSnapClass(object):
    def __init__(self, netName, worldRef, fkCtrlList, ikCtrlList, ikJointList, revFootAttrList, *args):
        # defining variables:
        self.worldRef = worldRef
        self.ikFkBlendAttr = cmds.getAttr(self.worldRef+".ikFkBlendAttrName")
        self.ikBeforeCtrl = fkCtrlList[0]
        self.ikPoleVectorCtrl = ikCtrlList[0]
        self.ikExtremCtrl = ikCtrlList[1]
        self.fkCtrlList = fkCtrlList[1:]
        self.ikJointList = ikJointList[1:-1]
        self.revFootAttrList = revFootAttrList
        # calculate the initial ikFk extrem offset
        self.extremOffsetMatrix = self.getOffsetMatrix(self.ikExtremCtrl, self.fkCtrlList[-1])
        # store data
        self.ikFkState = round(cmds.getAttr(self.worldRef+"."+self.ikFkBlendAttr), 0)
        self.ikFkSnapNet = cmds.createNode("network", name=netName+"_IkFkSnap_Net")
        self.storeIkFkSnapData()
        self.job = cmds.scriptJob(attributeChange=(self.worldRef+"."+self.ikFkBlendAttr, self.jobChangedIkFk), killWithScene=True, compressUndo=True)
    

    def getOffsetMatrix(self, wm, wim, *args):
        """ Return the offset matrix (multiplied matrices) from given world and inverse matrices.
        """
        aM = OpenMaya.MMatrix(cmds.getAttr(wm+".worldMatrix[0]"))
        bM = OpenMaya.MMatrix(cmds.getAttr(wim+".worldInverseMatrix[0]"))
        return (aM * bM)


    def storeIkFkSnapData(self, *args):
        """ Store all the needed attributes data to snap ik and fk into the network node.
        """
        # add
        cmds.addAttr(self.ikFkSnapNet, longName="dpNetwork", attributeType="bool")
        cmds.addAttr(self.ikFkSnapNet, longName="dpIkFkSnapNet", attributeType="bool")
        cmds.addAttr(self.ikFkSnapNet, longName="ikFkState", attributeType="short")
        cmds.addAttr(self.ikFkSnapNet, longName="worldRef", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikBeforeCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikPoleVectorCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikExtremCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="fkCtrlList", multi=True)
        cmds.addAttr(self.ikFkSnapNet, longName="ikJointList", multi=True)
        cmds.addAttr(self.ikFkSnapNet, longName="ikFkBlendAttr", dataType="string")
        cmds.addAttr(self.ikFkSnapNet, longName="extremOffset", attributeType="matrix")
        # set
        cmds.setAttr(self.ikFkSnapNet+".dpNetwork", 1)
        cmds.setAttr(self.ikFkSnapNet+".dpIkFkSnapNet", 1)
        cmds.setAttr(self.ikFkSnapNet+".ikFkState", self.ikFkState)
        cmds.setAttr(self.ikFkSnapNet+".ikFkBlendAttr", self.ikFkBlendAttr, type="string")
        cmds.setAttr(self.ikFkSnapNet+".extremOffset", self.extremOffsetMatrix, type="matrix")
        # connect
        cmds.addAttr(self.worldRef, longName="ikFkSnapNet", attributeType="message")
        cmds.connectAttr(self.ikFkSnapNet+".message", self.worldRef+".ikFkSnapNet", force=True)
        cmds.connectAttr(self.worldRef+".message", self.ikFkSnapNet+".worldRef", force=True)
        cmds.connectAttr(self.ikBeforeCtrl+".message", self.ikFkSnapNet+".ikBeforeCtrl", force=True)
        cmds.connectAttr(self.ikPoleVectorCtrl+".message", self.ikFkSnapNet+".ikPoleVectorCtrl", force=True)
        cmds.connectAttr(self.ikExtremCtrl+".message", self.ikFkSnapNet+".ikExtremCtrl", force=True)
        for f, fkCtrl in enumerate(self.fkCtrlList):
            cmds.connectAttr(fkCtrl+".message", self.ikFkSnapNet+".fkCtrlList["+str(f)+"]", force=True)
        for i, ikJoint in enumerate(self.ikJointList):
            cmds.connectAttr(ikJoint+".message", self.ikFkSnapNet+".ikJointList["+str(i)+"]", force=True)


    def jobChangedIkFk(self, *args):
        """
        """
        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        print("YESSSSS, changed ikFk attr here", self.ikFkSnapNet)
        self.ikFkState = cmds.getAttr(self.ikFkSnapNet+".ikFkState")
        print("self.ikFkState =", self.ikFkState)
        currentValue = cmds.getAttr(self.worldRef+"."+self.ikFkBlendAttr)
        
        if self.ikFkState == 0: #ik
            if currentValue >= 0.001:
                self.changeIkFkAttr(0, False)
                self.snapIkToFk()
                self.changeIkFkAttr(1, True)
        else: #fk
            if currentValue < 0.999:
                self.changeIkFkAttr(1, False)
                self.snapFkToIk()
                self.changeIkFkAttr(0, True)
        

    def changeIkFkAttr(self, ikFkValue, setState, *args):
        """ 0 = ik
            1 = fk
        """
        plugged = cmds.listConnections(self.worldRef+"."+self.ikFkBlendAttr, source=True, destination=False, plugs=True)
        if plugged:
            cmds.setAttr(plugged[0], ikFkValue)
        else:
            cmds.setAttr(self.worldRef+"."+self.ikFkBlendAttr, ikFkValue)
        if setState:
            self.ikFkState = ikFkValue
            cmds.setAttr(self.ikFkSnapNet+".ikFkState", ikFkValue)


    def snapIkToFk(self, *args):
        """ Switch from ik to fk keeping the same position.
        """
#        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        if cmds.getAttr(self.worldRef+".ikFkSnap"):
            self.bakeFollowRotation(self.ikBeforeCtrl)
            self.bakeFollowRotation(self.fkCtrlList[0])
            # snap fk ctrl to ik jnt
            for ctrl, jnt in zip(self.fkCtrlList, self.ikJointList):
                cmds.xform(ctrl, matrix=(cmds.xform(jnt, matrix=True, query=True, worldSpace=True)), worldSpace=True)
            # change to ik
#            self.changeIkFkAttr(1)
#            cmds.setAttr(self.ikFkSnapNet+".ikFkState", 1)
            

    def snapFkToIk(self, *args):
        """ Switch from fk to ik keeping the same position.
        """
#        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        if cmds.getAttr(self.worldRef+".ikFkSnap"):
            self.bakeFollowRotation(self.ikBeforeCtrl)
            # extrem ctrl
            fkM = OpenMaya.MMatrix(cmds.getAttr(self.fkCtrlList[-1]+".worldMatrix[0]"))
            toIkM = self.extremOffsetMatrix * fkM
            cmds.xform(self.ikExtremCtrl, matrix=list(toIkM), worldSpace=True)
            # poleVector ctrl
            posRef = cmds.xform(self.fkCtrlList[1], rotatePivot=True, query=True, worldSpace=True)
            posS = cmds.xform(self.fkCtrlList[0], rotatePivot=True, query=True, worldSpace=True)
            posM = posRef
            posE = cmds.xform(self.fkCtrlList[-1], rotatePivot=True, query=True, worldSpace=True)
            posRefPos = self.getSwivelMiddle(posS, posM, posE)
            posDir = self.utilsSubVectors(posM, posRefPos)
            self.utilsNormalizeVector(posDir)
            fSwivelDistance = self.utilsDistanceVectors(posS, posE) / cmds.getAttr(self.worldRef+".scaleX")
            posSwivel = self.utilsAddVectors(self.utilsMultiScalarVector(posDir, fSwivelDistance), posRef)
            cmds.xform(self.ikPoleVectorCtrl, translation=posSwivel, worldSpace=True)
            # reset footRoll attributes
            userDefAttrList = cmds.listAttr(self.ikExtremCtrl, userDefined=True, keyable=True)
            if userDefAttrList:
                for attr in userDefAttrList:
                    for revFootAttr in self.revFootAttrList:
                        if revFootAttr in attr:
                            cmds.setAttr(self.ikExtremCtrl+"."+attr, 0)
            # change to fk
#            self.changeIkFkAttr(0)
#            cmds.setAttr(self.ikFkSnapNet+".ikFkState", 0)
    

    def getSwivelMiddle(self, posS, posM, posE):
        """ Return the middle position from given start, middle and end vectors to find poleVector placement.
        """
        fLengthS = self.utilsDistanceVectors(posM, posS)
        fLengthE = self.utilsDistanceVectors(posM, posE)
        fLengthRatio = fLengthS / (fLengthS+fLengthE)
        return self.utilsAddVectors(self.utilsMultiScalarVector(self.utilsSubVectors(posE, posS), fLengthRatio), posS)


    def getOffsetXform(self, wm, wim, *args):
        """ Return the offset xform matrix (multiplied matrices) from given xform matrices.
        """
        aM = OpenMaya.MMatrix(cmds.getAttr(wm+".xformMatrix"))
        bM = OpenMaya.MMatrix(cmds.getAttr(wim+".xformMatrix"))
        return (aM * bM)


    def bakeFollowRotation(self, ctrl, *args):
        """ Set clavicle rotation from offset xform calculus.
            Also set rotation keyframe.
        """
        if cmds.objExists(ctrl+".followAttrName"): #stored attribute name to avoid run procedure without dpAR language dictionary
            followAttr = cmds.getAttr(ctrl+".followAttrName")
            if cmds.getAttr(ctrl+"."+followAttr):
                ctrlOffset = self.getOffsetXform(ctrl, cmds.listRelatives(ctrl, parent=True, type="transform")[0])
                cmds.xform(ctrl, matrix=list(ctrlOffset), worldSpace=False)
                cmds.xform(ctrl, translation=[0, 0, 0], worldSpace=False)
                # disable autoClavicle and keyframe it
                cmds.setAttr(ctrl+"."+followAttr, 0)
                cmds.setKeyframe(ctrl, attribute=("rotateX", "rotateY", "rotateZ", followAttr))


    ###
    # Code from dpUtils
    ###

    def utilsMagnitude(self, v, *args):
        """ Returns the square root of the sum of power 2 from a given vector.
        """
        return math.sqrt(pow(v[0], 2)+pow(v[1], 2)+pow(v[2], 2))
    
    
    def utilsNormalizeVector(self, v, *args):
        """ Returns the normalized given vector.
        """
        vMag = self.utilsMagnitude(v)
        return [v[i]/vMag for i in range(len(v))]
    

    def utilsDistanceVectors(serlf, u, v, *args):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)


    def utilsAddVectors(self, u, v, *args):
        """ Returns the addition of 2 given vectors.
        """
        return [u[i]+v[i] for i in range(len(u))]
        
        
    def utilsSubVectors(self, u, v, *args):
        """ Returns the substration of 2 given vectors.
        """
        return [u[i]-v[i] for i in range(len(u))]
        

    def utilsMultiScalarVector(self, u, scalar, *args):
        """ Returns the vector scaled by a scalar number.
        """
        return [u[i]*scalar for i in range(len(u))]
