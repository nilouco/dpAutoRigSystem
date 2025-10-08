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

DP_IKFKSNAP_VERSION = 2.03



class IkFkSnapClass(object):
    def __init__(self, dpUIinst, netName, worldRef, fkCtrlList, ikCtrlList, ikJointList, revFootAttrList, uniformScaleAttr, dpDev=False, *args):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.netName = netName
        self.worldRef = worldRef
        self.ikFkBlendAttr = cmds.getAttr(self.worldRef+".ikFkBlendAttrName")
        self.ikBeforeCtrl = fkCtrlList[0]
        self.ikPoleVectorCtrl = ikCtrlList[0]
        self.ikExtremCtrl = ikCtrlList[1]
        self.ikExtremSubCtrl = ikCtrlList[2]
        self.fkCtrlList = fkCtrlList[1:]
        self.ikJointList = ikJointList[1:-1]
        self.revFootAttrList = revFootAttrList
        self.uniformScaleAttr = uniformScaleAttr
        # calculate the initial ikFk extrem offset
        self.extremOffsetMatrix = self.getOffsetMatrix(self.ikExtremCtrl, self.fkCtrlList[-1])
        # store data
        self.ikFkState = round(cmds.getAttr(self.worldRef+"."+self.ikFkBlendAttr), 0)
        self.ikFkSnapNet = cmds.createNode("network", name=self.netName+"_IkFkSnap_Net")
        self.dpUIinst.customAttr.addAttr(0, [self.ikFkSnapNet]) #dpID
        self.dpID = cmds.getAttr(self.ikFkSnapNet+".dpID")
        self.storeIkFkSnapData()
        if dpDev:
            cmds.scriptJob(attributeChange=(self.worldRef+"."+self.ikFkBlendAttr, self.jobChangedIkFk), killWithScene=False, compressUndo=True)
        else:
            self.generateScriptNode()
    

    ###
    # ---------------------------------
    # Code to development or creating a new module instance
    ###

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
        cmds.addAttr(self.ikFkSnapNet, longName="dpIkFkSnapNetName", dataType="string")
        cmds.addAttr(self.ikFkSnapNet, longName="ikFkState", attributeType="short")
        cmds.addAttr(self.ikFkSnapNet, longName="worldRef", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikBeforeCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikPoleVectorCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikExtremCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="ikExtremSubCtrl", attributeType="message")
        cmds.addAttr(self.ikFkSnapNet, longName="fkCtrlList", multi=True)
        cmds.addAttr(self.ikFkSnapNet, longName="ikJointList", multi=True)
        cmds.addAttr(self.ikFkSnapNet, longName="revFootAttrList", dataType="string")
        cmds.addAttr(self.ikFkSnapNet, longName="uniformScaleAttr", dataType="string")
        cmds.addAttr(self.ikFkSnapNet, longName="ikFkBlendAttr", dataType="string")
        cmds.addAttr(self.ikFkSnapNet, longName="extremOffset", attributeType="matrix")
        cmds.addAttr(self.worldRef, longName="ikFkSnapNet", attributeType="message")
        # set
        cmds.setAttr(self.ikFkSnapNet+".dpNetwork", 1)
        cmds.setAttr(self.ikFkSnapNet+".dpIkFkSnapNet", 1)
        cmds.setAttr(self.ikFkSnapNet+".dpIkFkSnapNetName", self.netName, type="string")
        cmds.setAttr(self.ikFkSnapNet+".ikFkState", self.ikFkState)
        cmds.setAttr(self.ikFkSnapNet+".ikFkBlendAttr", self.ikFkBlendAttr, type="string")
        cmds.setAttr(self.ikFkSnapNet+".extremOffset", self.extremOffsetMatrix, type="matrix")
        cmds.setAttr(self.ikFkSnapNet+".revFootAttrList", ';'.join(self.revFootAttrList), type="string")
        cmds.setAttr(self.ikFkSnapNet+".uniformScaleAttr", self.uniformScaleAttr, type="string")
        # connect
        cmds.connectAttr(self.ikFkSnapNet+".message", self.worldRef+".ikFkSnapNet", force=True)
        cmds.connectAttr(self.worldRef+".message", self.ikFkSnapNet+".worldRef", force=True)
        cmds.connectAttr(self.ikBeforeCtrl+".message", self.ikFkSnapNet+".ikBeforeCtrl", force=True)
        cmds.connectAttr(self.ikPoleVectorCtrl+".message", self.ikFkSnapNet+".ikPoleVectorCtrl", force=True)
        cmds.connectAttr(self.ikExtremCtrl+".message", self.ikFkSnapNet+".ikExtremCtrl", force=True)
        cmds.connectAttr(self.ikExtremSubCtrl+".message", self.ikFkSnapNet+".ikExtremSubCtrl", force=True)
        for f, fkCtrl in enumerate(self.fkCtrlList):
            cmds.connectAttr(fkCtrl+".message", self.ikFkSnapNet+".fkCtrlList["+str(f)+"]", force=True)
        for i, ikJoint in enumerate(self.ikJointList):
            cmds.connectAttr(ikJoint+".message", self.ikFkSnapNet+".ikJointList["+str(i)+"]", force=True)


    ###
    # ---------------------------------
    # Code to use by the scriptJob included in the scriptNode
    ###

    def jobChangedIkFk(self, *args):
        """ Just call snap function to set as well or update the ikFkState.
        """
        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        currentValue = cmds.getAttr(self.worldRef+"."+self.ikFkBlendAttr)
        if cmds.getAttr(self.worldRef+".ikFkSnap"):
            self.ikFkState = cmds.getAttr(self.ikFkSnapNet+".ikFkState")
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
            self.resetShear(list(set([self.ikExtremCtrl] + self.fkCtrlList)))
        else:
            if currentValue <= 0.5: #ik
                cmds.setAttr(self.ikFkSnapNet+".ikFkState", 0)
            else: #fk
                cmds.setAttr(self.ikFkSnapNet+".ikFkState", 1)


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
        self.bakeFollowRotation(self.ikBeforeCtrl)
        self.bakeFollowRotation(self.fkCtrlList[0])
        self.transferAttrFromTo(self.ikExtremCtrl, self.fkCtrlList[2], [self.uniformScaleAttr])
        # snap fk ctrl to ik jnt
        for ctrl, jnt in zip(self.fkCtrlList, self.ikJointList):
            cmds.xform(ctrl, matrix=(cmds.xform(jnt, matrix=True, query=True, worldSpace=True)), worldSpace=True)


    def snapFkToIk(self, *args):
        """ Switch from fk to ik keeping the same position.
        """
        self.bakeFollowRotation(self.ikBeforeCtrl)
        self.zeroKeyAttrValue(self.ikExtremCtrl, ["twist"])
        self.zeroKeyAttrValue(self.ikExtremSubCtrl, ["tx", "ty", "tz", "rx", "ry", "rz"])
        self.transferAttrFromTo(self.fkCtrlList[2], self.ikExtremCtrl, [self.uniformScaleAttr])
        # extrem ctrl
        fkM = OpenMaya.MMatrix(cmds.getAttr(self.fkCtrlList[-1]+".worldMatrix[0]"))
        toIkM = OpenMaya.MMatrix(self.extremOffsetMatrix) * fkM #need redefine to load matrix in scriptNode
        cmds.xform(self.ikExtremCtrl, matrix=list(toIkM), worldSpace=True)
        # poleVector ctrl
        startPos, cornerPos, endPos, chainLen, pvRatio = self.getChainPosition()
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


    def zeroKeyAttrValue(self, ctrl, attrList, *args):
        """ Set zero value and keyframe the given attributes in the controller.
        """
        for attr in attrList:
            if cmds.objExists(ctrl+"."+attr):
                if cmds.getAttr(ctrl+"."+attr):
                    cmds.setAttr(ctrl+"."+attr, 0)
                    cmds.setKeyframe(ctrl, attribute=attr)


    def transferAttrFromTo(self, fromCtrl, toCtrl, attrList):
        """ It compares the attributes to transfer values from/to given controllers and keyframe them.
        """
        for attr in attrList:
            if cmds.objExists(fromCtrl+"."+attr) and cmds.objExists(toCtrl+"."+attr):
                fromValue = cmds.getAttr(fromCtrl+"."+attr)
                toValue = cmds.getAttr(toCtrl+"."+attr)
                if not fromValue == toValue:
                    cmds.setAttr(toCtrl+"."+attr, fromValue)
                    cmds.setKeyframe(toCtrl, attribute=attr)


    def resetShear(self, ctrlList, *args):
        """ Set zero to all shear attributes in main controllers affected by possible stretch.
        """
        startLength = cmds.getAttr(self.ikExtremCtrl+".startChainLength")
        currentLength = self.getChainPosition()[3] #chainLen
        if currentLength == startLength:
            for ctrl in ctrlList:
                cmds.setAttr(ctrl+".shearXY", 0)
                cmds.setAttr(ctrl+".shearXZ", 0)
                cmds.setAttr(ctrl+".shearYZ", 0)
    

    def getChainPosition(self, *args):
        """ Return the start, coner and end position, the chain lenght and poleVector Ratio values as a list,
            based on the fkCtrlList.
        """
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
        return [startPos, cornerPos, endPos, chainLen, pvRatio]


    ###
    # ---------------------------------
    # Code from dpUtils
    ###

    def utilsDistanceVectors(serlf, u, v, *args):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)


    ###
    # ---------------------------------
    # Code to scriptNode
    ###

    def generateScriptNode(self, *args):
        """ Create a scriptNode to store the ikFkSnap code into it.
        """
        ikFkSnapCode = '''
from maya import cmds
from maya.api import OpenMaya
import math
DP_IKFKSNAP_VERSION = '''+str(DP_IKFKSNAP_VERSION)+'''

class IkFkSnap(object):
    def __init__(self, ikFkSnapNet, *args):
        self.ikFkSnapNet = ikFkSnapNet
        self.reloadNetData()
        cmds.scriptJob(attributeChange=(self.worldRef+"."+self.ikFkBlendAttr, self.jobChangedIkFk), killWithScene=False, compressUndo=True)

    def reloadNetData(self):
        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        self.ikFkState = cmds.getAttr(self.ikFkSnapNet+".ikFkState")
        self.ikFkBlendAttr = cmds.getAttr(self.worldRef+".ikFkBlendAttrName")
        self.uniformScaleAttr = cmds.getAttr(self.ikFkSnapNet+".uniformScaleAttr")
        self.ikBeforeCtrl = cmds.listConnections(self.ikFkSnapNet+".ikBeforeCtrl")[0]
        self.ikPoleVectorCtrl = cmds.listConnections(self.ikFkSnapNet+".ikPoleVectorCtrl")[0]
        self.ikExtremCtrl = cmds.listConnections(self.ikFkSnapNet+".ikExtremCtrl")[0]
        self.ikExtremSubCtrl = cmds.listConnections(self.ikFkSnapNet+".ikExtremSubCtrl")[0]
        self.fkCtrlList = cmds.listConnections(self.ikFkSnapNet+".fkCtrlList")
        self.ikJointList = cmds.listConnections(self.ikFkSnapNet+".ikJointList")
        self.revFootAttrList = list(cmds.getAttr(self.ikFkSnapNet+".revFootAttrList").split(";"))
        self.extremOffsetMatrix = cmds.getAttr(self.ikFkSnapNet+".extremOffset")

    def jobChangedIkFk(self, *args):
        """ Just call snap function to set as well or update the ikFkState.
        """
        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        currentValue = cmds.getAttr(self.worldRef+"."+self.ikFkBlendAttr)
        if cmds.getAttr(self.worldRef+".ikFkSnap"):
            self.ikFkState = cmds.getAttr(self.ikFkSnapNet+".ikFkState")
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
            self.resetShear(list(set([self.ikExtremCtrl] + self.fkCtrlList)))
        else:
            if currentValue <= 0.5: #ik
                cmds.setAttr(self.ikFkSnapNet+".ikFkState", 0)
            else: #fk
                cmds.setAttr(self.ikFkSnapNet+".ikFkState", 1)

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
        self.bakeFollowRotation(self.ikBeforeCtrl)
        self.bakeFollowRotation(self.fkCtrlList[0])
        self.transferAttrFromTo(self.ikExtremCtrl, self.fkCtrlList[2], [self.uniformScaleAttr])
        # snap fk ctrl to ik jnt
        for ctrl, jnt in zip(self.fkCtrlList, self.ikJointList):
            cmds.xform(ctrl, matrix=(cmds.xform(jnt, matrix=True, query=True, worldSpace=True)), worldSpace=True)
    
    def snapFkToIk(self, *args):
        """ Switch from fk to ik keeping the same position.
        """
        self.bakeFollowRotation(self.ikBeforeCtrl)
        self.zeroKeyAttrValue(self.ikExtremCtrl, ["twist"])
        self.zeroKeyAttrValue(self.ikExtremSubCtrl, ["tx", "ty", "tz", "rx", "ry", "rz"])
        self.transferAttrFromTo(self.fkCtrlList[2], self.ikExtremCtrl, [self.uniformScaleAttr])
        # extrem ctrl
        fkM = OpenMaya.MMatrix(cmds.getAttr(self.fkCtrlList[-1]+".worldMatrix[0]"))
        toIkM = OpenMaya.MMatrix(self.extremOffsetMatrix) * fkM
        cmds.xform(self.ikExtremCtrl, matrix=list(toIkM), worldSpace=True)
        # poleVector ctrl
        startPos, cornerPos, endPos, chainLen, pvRatio = self.getChainPosition()
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

    def zeroKeyAttrValue(self, ctrl, attrList, *args):
        """ Set zero value and keyframe the given attributes in the controller.
        """
        for attr in attrList:
            if cmds.objExists(ctrl+"."+attr):
                if cmds.getAttr(ctrl+"."+attr):
                    cmds.setAttr(ctrl+"."+attr, 0)
                    cmds.setKeyframe(ctrl, attribute=attr)

    def transferAttrFromTo(self, fromCtrl, toCtrl, attrList):
        """ It compares the attributes to transfer values from/to given controllers and keyframe them.
        """
        for attr in attrList:
            if cmds.objExists(fromCtrl+"."+attr) and cmds.objExists(toCtrl+"."+attr):
                fromValue = cmds.getAttr(fromCtrl+"."+attr)
                toValue = cmds.getAttr(toCtrl+"."+attr)
                if not fromValue == toValue:
                    cmds.setAttr(toCtrl+"."+attr, fromValue)
                    cmds.setKeyframe(toCtrl, attribute=attr)

    def resetShear(self, ctrlList, *args):
        """ Set zero to all shear attributes in main controllers affected by possible stretch.
        """
        startLength = cmds.getAttr(self.ikExtremCtrl+".startChainLength")
        currentLength = self.getChainPosition()[3] #chainLen
        if currentLength == startLength:
            for ctrl in ctrlList:
                cmds.setAttr(ctrl+".shearXY", 0)
                cmds.setAttr(ctrl+".shearXZ", 0)
                cmds.setAttr(ctrl+".shearYZ", 0)

    def getChainPosition(self, *args):
        """ Return the start, coner and end position, the chain lenght and poleVector Ratio values as a list,
            based on the fkCtrlList.
        """
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
        return [startPos, cornerPos, endPos, chainLen, pvRatio]

    def utilsDistanceVectors(serlf, u, v, *args):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)

# fire scriptNode
for net in cmds.ls(type="network"):
    if cmds.objExists(net+".dpNetwork") and cmds.getAttr(net+".dpNetwork") == 1:
        if cmds.objExists(net+".dpIkFkSnapNet") and cmds.getAttr(net+".dpIkFkSnapNet") == 1:
            if cmds.objExists(net+".dpID") and cmds.getAttr(net+".dpID") == "'''+self.dpID+'''":
                IkFkSnap(net)
'''
        sn = cmds.scriptNode(name=self.netName+'_IkFkSnap_SN', sourceType='python', scriptType=2, beforeScript=ikFkSnapCode)
        self.dpUIinst.customAttr.addAttr(0, [sn]) #dpID
        cmds.addAttr(self.ikFkSnapNet, longName="ikFkSnapScriptNode", attributeType="message")
        cmds.addAttr(sn, longName="ikFkSnapNet", attributeType="message")
        cmds.connectAttr(sn+".message", self.ikFkSnapNet+".ikFkSnapScriptNode", force=True)
        cmds.connectAttr(self.ikFkSnapNet+".message", sn+".ikFkSnapNet", force=True)
        cmds.scriptNode(sn, executeBefore=True)
