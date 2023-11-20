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
from . import dpUtils

DP_IKFKSNAP_VERSION = 2.0



class IkFkSnapClass(object):
    def __init__(self, netName, worldRef, fkCtrlList, ikCtrlList, ikJointList, revFootAttrList, ui=True, *args):
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
        self.ikFkSnapNet = cmds.createNode("network", name=netName+"_IkFkSnap_Net")
        self.storeIkFkSnapData()
        
        # TODO build scriptNode
        

        # call main function
        if ui:
            self.dpIkFkSnapUI(self)
    

    def getOffsetMatrix(self, wm, wim, *args):
        """ Return the offset matrix (multiplied matrices) from given world and inverse matrices.
        """
        aM = OpenMaya.MMatrix(cmds.getAttr(wm+".worldMatrix[0]"))
        bM = OpenMaya.MMatrix(cmds.getAttr(wim+".worldInverseMatrix[0]"))
        return (aM * bM)


    def getOffsetXform(self, wm, wim, *args):
        """ Return the offset xform matrix (multiplied matrices) from given xform matrices.
        """
        aM = OpenMaya.MMatrix(cmds.getAttr(wm+".xformMatrix"))
        bM = OpenMaya.MMatrix(cmds.getAttr(wim+".xformMatrix"))
        return (aM * bM)


    def storeIkFkSnapData(self, *args):
        """ Store all the needed attributes data to snap ik and fk into the network node.
        """
        # add
        cmds.addAttr(self.ikFkSnapNet, longName="dpNetwork", attributeType="bool")
        cmds.addAttr(self.ikFkSnapNet, longName="dpIkFkSnapNet", attributeType="bool")
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


#####
# to del
#
#
    def dpCloseIkFkSnapUI(self, *args):
        if cmds.window(self.worldRef+'dpIkFkSnapWindow', query=True, exists=True):
            cmds.deleteUI(self.worldRef+'dpIkFkSnapWindow', window=True)
#
#
#
#####
#

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
#
# to del
#
##
#
#
    def dpIkFkSnapUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating dpIkFkSnapUI Window:
        self.dpCloseIkFkSnapUI()
        ikFkSnap_winWidth  = 175
        ikFkSnap_winHeight = 75
        dpIkFkSnapWin = cmds.window(self.worldRef+'dpIkFkSnapWindow', title=self.worldRef+str(DP_IKFKSNAP_VERSION), widthHeight=(ikFkSnap_winWidth, ikFkSnap_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        ikFkSnapLayout = cmds.columnLayout('ikFkSnapLayout', columnOffset=("left", 30))
        cmds.separator(style='none', height=7, parent=ikFkSnapLayout)
        cmds.button(label="Fk -> iK", annotation="", width=110, backgroundColor=(0.45, 1.0, 0.6), command=self.snapFkToIk, parent=ikFkSnapLayout)
        cmds.separator(style='in', height=10, width=110, parent=ikFkSnapLayout)
        cmds.button(label="ik -> Fk", annotation="", width=110, backgroundColor=(1.0, 0.45, 0.45), command=self.snapIkToFk, parent=ikFkSnapLayout)
        
        # call dpIkFkSnapUI Window:
        cmds.showWindow(dpIkFkSnapWin)
#
#
##
####


    def changeIkFkAttr(self, ikFkValue, *args):
        """ 0 = ik
            1 = fk
        """
        plugged = cmds.listConnections(self.worldRef+"."+self.ikFkBlendAttr, source=True, destination=False, plugs=True)
        if plugged:
            cmds.setAttr(plugged[0], ikFkValue)
        else:
            cmds.setAttr(self.worldRef+"."+self.ikFkBlendAttr, ikFkValue)


    def snapIkToFk(self, *args):
        """ Switch from ik to fk keeping the same position.
        """
        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        if cmds.getAttr(self.worldRef+".ikFkSnap"):
            self.bakeFollowRotation(self.ikBeforeCtrl)
            self.bakeFollowRotation(self.fkCtrlList[0])
            # snap fk ctrl to ik jnt
            for ctrl, jnt in zip(self.fkCtrlList, self.ikJointList):
                cmds.xform(ctrl, matrix=(cmds.xform(jnt, matrix=True, query=True, worldSpace=True)), worldSpace=True)
            # change to fk
            self.changeIkFkAttr(1)
            


    def snapFkToIk(self, *args):
        """ Switch from fk to ik keeping the same position.
        """
        self.worldRef = cmds.listConnections(self.ikFkSnapNet+".worldRef")[0]
        if cmds.getAttr(self.worldRef+".ikFkSnap"):
            self.bakeFollowRotation(self.ikBeforeCtrl)
            # extrem ctrl
            fkM = OpenMaya.MMatrix(cmds.getAttr(self.fkCtrlList[-1]+".worldMatrix[0]"))
            toIkM = self.extremOffsetMatrix * fkM
            cmds.xform(self.ikExtremCtrl, matrix=list(toIkM), worldSpace=True)
            # poleVector ctrl
            posRef = cmds.xform(self.fkCtrlList[1], translation=True, query=True, worldSpace=True)
            posS = cmds.xform(self.fkCtrlList[0], translation=True, query=True, worldSpace=True)
            posM = posRef
            posE = cmds.xform(self.fkCtrlList[-1], translation=True, query=True, worldSpace=True)
            posRefPos = self.getSwivelMiddle(posS, posM, posE)
            posDir = dpUtils.subVectors(posM, posRefPos)
            dpUtils.normalizeVector(posDir)
            fSwivelDistance = dpUtils.distanceVectors(posS, posE)
            posSwivel = dpUtils.addVectors(dpUtils.multiScalarVector(posDir, fSwivelDistance), posRef)
            #posSwivel = [posDir[0]*fSwivelDistance+posRef[0], posDir[1]*fSwivelDistance+posRef[1], posDir[2]*fSwivelDistance+posRef[2]]
            cmds.xform(self.ikPoleVectorCtrl, translation=posSwivel, worldSpace=True)
            # reset footRoll attributes
            userDefAttrList = cmds.listAttr(self.ikExtremCtrl, userDefined=True, keyable=True)
            if userDefAttrList:
                for attr in userDefAttrList:
                    for revFootAttr in self.revFootAttrList:
                        if revFootAttr in attr:
                            cmds.setAttr(self.ikExtremCtrl+"."+attr, 0)
            # change to ik
            self.changeIkFkAttr(0)
    

    def getSwivelMiddle(self, posS, posM, posE):
        """ Return the middle position from given start, middle and end vectors to find poleVector placement.
        """
        fLengthS = dpUtils.distanceVectors(posM, posS)
        fLengthE = dpUtils.distanceVectors(posM, posE)
        fLengthRatio = fLengthS / (fLengthS+fLengthE)
        return dpUtils.addVectors(dpUtils.multiScalarVector(dpUtils.subVectors(posE, posS), fLengthRatio), posS)
        #return [(posE[0]-posS[0])*fLengthRatio+posS[0], (posE[1]-posS[1])*fLengthRatio+posS[1], (posE[2]-posS[2])*fLengthRatio+posS[2]]
