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
        self.ikFkState = cmds.getAttr(self.ikFkSnapNet+".ikFkState")
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
            # get joint chain positions
            startPos  = cmds.xform(self.fkCtrlList[0], query=True, worldSpace=True, rotatePivot=True) #shoulder, leg
            cornerPos = cmds.xform(self.fkCtrlList[1], query=True, worldSpace=True, rotatePivot=True) #elbow, knee
            endPos    = cmds.xform(self.fkCtrlList[2], query=True, worldSpace=True, rotatePivot=True) #wrist, ankle
            # calculate distances (joint lenghts)
            upperLimbLen = self.utilsDistanceVectors(startPos, cornerPos)
            lowerLimbLen = self.utilsDistanceVectors(cornerPos, endPos)
            chainLen = upperLimbLen+lowerLimbLen
            # ratio of placement of the middle joint
            pvRatio = upperLimbLen / chainLen
            # calculate the position of the base middle locator
            pvBasePosX = (endPos[0] - startPos[0]) * pvRatio+startPos[0]
            pvBasePosY = (endPos[1] - startPos[1]) * pvRatio+startPos[1]
            pvBasePosZ = (endPos[2] - startPos[2]) * pvRatio+startPos[2]
            # working with vectors
            cornerBasePosX = cornerPos[0] - pvBasePosX
            cornerBasePosY = cornerPos[1] - pvBasePosY
            cornerBasePosZ = cornerPos[2] - pvBasePosZ
            # magnitude of the vector
            magDir = math.sqrt(cornerBasePosX**2+cornerBasePosY**2+cornerBasePosZ**2)
            # normalize the vector
            normalDirX = cornerBasePosX / magDir
            normalDirY = cornerBasePosY / magDir
            normalDirZ = cornerBasePosZ / magDir
            # calculate the poleVector position by multiplying the unitary vector by the chain length
            pvDistX = normalDirX * chainLen
            pvDistY = normalDirY * chainLen
            pvDistZ = normalDirZ * chainLen
            # get the poleVector position
            pvPosX = pvBasePosX+pvDistX
            pvPosY = pvBasePosY+pvDistY
            pvPosZ = pvBasePosZ+pvDistZ
            # place poleVector controller in the correct position
            cmds.move(pvPosX, pvPosY, pvPosZ, self.ikPoleVectorCtrl, objectSpace=False, worldSpaceDistance=True)
            
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
                father = cmds.listRelatives(ctrl, parent=True, type="transform")[0]
                negativeScale = cmds.getAttr(father+".scaleX")
                if negativeScale == -1:
                    cmds.setAttr(father+".scaleX", 1)
                    cmds.setAttr(father+".scaleY", 1)
                    cmds.setAttr(father+".scaleZ", 1)
                ctrlOffset = self.getOffsetXform(ctrl, father)
                cmds.xform(ctrl, matrix=list(ctrlOffset), worldSpace=False)
                cmds.xform(ctrl, translation=[0, 0, 0], worldSpace=False)
                # disable autoClavicle and keyframe it
                cmds.setAttr(ctrl+"."+followAttr, 0)
                cmds.setKeyframe(ctrl, attribute=("rotateX", "rotateY", "rotateZ", followAttr))
                if negativeScale == -1:
                    cmds.setAttr(father+".scaleX", -1)
                    cmds.setAttr(father+".scaleY", -1)
                    cmds.setAttr(father+".scaleZ", -1)


    ###
    # Code from dpUtils
    ###

    def utilsDistanceVectors(serlf, u, v, *args):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)
