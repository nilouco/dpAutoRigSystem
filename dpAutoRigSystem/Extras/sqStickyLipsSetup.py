#!/usr/bin/python
# -*- coding: utf-8 -*-

###################################################################
#
#    Company: Squeeze Studio Animation
#
#    Author: Danilo Pinheiro
#    Date: 2014-02-10
#    Updated: 2014-02-24
#
#    sqStickyLipsSetup.py
#
#    This script will create a Sticky Lips setup.
#
#######################################



# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from functools import partial


# global variables to this module:    
CLASS_NAME = "StickyLips"
TITLE = "m061_stickyLips"
DESCRIPTION = "m062_stickyLipsDesc"
ICON = "/Icons/sq_stickyLips.png"


SQSL_VERSION = "1.0"


class StickyLips():
    def __init__(self, dpUIinst, langDic, langName):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        # call main function
        self.dpMain(self)


    def dpMain(self, *args):
        self.edgeList = []
        self.baseCurve = []
        self.baseCurveA = []
        self.baseCurveB = []
        self.mainCurveA = []
        self.mainCurveB = []
        self.curveLenght = 0
        self.maxIter = 0
        self.clusterList = []
        self.receptList = []
        self.optionCtrl = "Option_Ctrl"
        self.wireNodeList = []
        
        if cmds.window('sqStickyLipsWindow', query=True, exists=True):
            cmds.deleteUI('sqStickyLipsWindow', window=True)
        cmds.window('sqStickyLipsWindow', title='sqStickyLips - v'+str(SQSL_VERSION)+' - UI', widthHeight=(300, 200), menuBar=False, sizeable=False, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('sqStickyLipsWindow')
        
        slLayoutColumn = cmds.columnLayout('slLayoutColumn', adjustableColumn=True)
        cmds.text("Load meshes:", align="left", parent=slLayoutColumn)
        slLayoutA = cmds.rowColumnLayout('slLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 160)], parent=slLayoutColumn)
        cmds.button(label="Recept A >>", command=partial(self.sqSLLoad, "A"), parent=slLayoutA)
        self.receptA_TF = cmds.textField(parent=slLayoutA)
        cmds.button(label="Recept B >>", command=partial(self.sqSLLoad, "B"), parent=slLayoutA)
        self.receptB_TF = cmds.textField(parent=slLayoutA)
        cmds.text("Select a closed edgeLoop and press the run button", parent=slLayoutColumn)
        cmds.button(label="RUN - Generate Sticky Lips", command=self.sqGenerateStickyLips, backgroundColor=[0.3, 1, 0.7], parent=slLayoutColumn)


    def sqSLLoad(self, recept, *args):
        if recept == "A":
            cmds.textField(self.receptA_TF, edit=True, text=cmds.ls(selection=True)[0])
        if recept == "B":
            cmds.textField(self.receptB_TF, edit=True, text=cmds.ls(selection=True)[0])

    
    def sqGetRecepts(self, receptA=None, receptB=None, *args):
        self.receptList = []
        self.receptList.append(receptA)
        self.receptList.append(receptB)
        if receptA == None:
            receptAName = cmds.textField(self.receptA_TF, query=True, text=True)
            if cmds.objExists(receptAName):
                self.receptList[0] = receptAName
        if receptB == None:
            receptBName = cmds.textField(self.receptB_TF, query=True, text=True)
            if cmds.objExists(receptBName):
                self.receptList[1] = receptBName
    
    
    def sqGenerateCurves(self, *args):
        self.edgeList = cmds.ls(selection=True, flatten=True)
        if not self.edgeList == None and not self.edgeList == [] and not self.edgeList == "":
            self.baseCurve = cmds.polyToCurve(name="baseCurve", form=2, degree=1)[0]
            cmds.select(self.baseCurve+".ep[*]")
            cmds.insertKnotCurve(cmds.ls(selection=True, flatten=True), constructionHistory=True, curveOnSurface=True, numberOfKnots=1, addKnots=False, insertBetween=True, replaceOriginal=True)
            
            pointListA, pointListB, sideA, sideB = self.sqGetPointLists()
            
            toDeleteList = []
            p = 2
            for k in range((sideA+2), (sideB-1)):
                if p%2 == 0:
                    toDeleteList.append(self.baseCurve+".cv["+str(k)+"]")
                    toDeleteList.append(self.baseCurve+".cv["+str(k+len(pointListA)-1)+"]")
                p = p+1
            q = 2
            m = sideA-2
            if m >= 0:
                while m >= 0:
                    if not m == sideA and not m == sideB:
                        if q%2 == 0:
                            toDeleteList.append(self.baseCurve+".cv["+str(m)+"]")
                    m = m-1
                    q = q+1
            
            cmds.delete(toDeleteList)
            cmds.insertKnotCurve([self.baseCurve+".u["+str(len(pointListA)-1)+"]", self.baseCurve+".ep["+str(len(pointListA)-1)+"]"], constructionHistory=True, curveOnSurface=True, numberOfKnots=1, addKnots=False, insertBetween=True, replaceOriginal=True)
            
            pointListA, pointListB, sideA, sideB = self.sqGetPointLists()
            
            posListA, posListB = [], []
            for i in range(0, len(pointListA)-1):
                posListA.append(cmds.xform(pointListA[i], query=True, worldSpace=True, translation=True))
                posListB.append(cmds.xform(pointListB[i], query=True, worldSpace=True, translation=True))
            
            self.mainCurveA = cmds.curve(name="StickyLips_Main_A_Crv", degree=1, point=posListA)
            self.mainCurveB = cmds.curve(name="StickyLips_Main_B_Crv", degree=1, point=posListB)
            
            cmds.rename(cmds.listRelatives(self.mainCurveA, children=True, shapes=True)[0], self.mainCurveA+"Shape")
            cmds.rename(cmds.listRelatives(self.mainCurveB, children=True, shapes=True)[0], self.mainCurveB+"Shape")
            
            cmds.select(self.mainCurveA+".cv[*]")
            self.curveLenght = len(cmds.ls(selection=True, flatten=True))
            cmds.select(clear=True)
            
            self.sqCheckCurveDirection(self.mainCurveA)
            self.sqCheckCurveDirection(self.mainCurveB)
            
            self.baseCurveA = cmds.duplicate(self.mainCurveA, name=self.mainCurveA.replace("_Main_", "_Base_"))[0]
            self.baseCurveB = cmds.duplicate(self.mainCurveB, name=self.mainCurveB.replace("_Main_", "_Base_"))[0]
            
            cmds.delete(self.baseCurve)
            self.maxIter = len(posListA)
            
            cmds.group(self.mainCurveA, self.mainCurveB, self.baseCurveA, self.baseCurveB, name="StickyLips_StaticData_Grp")
        else:
            mel.eval("warning \"Please, select an closed edgeLoop.\";")
        

    def sqCheckCurveDirection(self, thisCurve, *args):
        posMinX = cmds.xform(thisCurve+".cv[0]", query=True, worldSpace=True, translation=True)[0]
        posMaxX = cmds.xform(thisCurve+".cv["+str(self.curveLenght-1)+"]", query=True, worldSpace=True, translation=True)[0]
        if posMinX > posMaxX:
            cmds.reverseCurve(thisCurve, constructionHistory=False, replaceOriginal=True)


    def sqGetPointLists(self, *args):
        cmds.select(self.baseCurve+".cv[*]")
        pointList = cmds.ls(selection=True, flatten=True)
        
        minX = 0
        maxX = 0
        sideA = 0
        sideB = 0
        for i in range(0, len(pointList)):
            pointPosX = cmds.xform(pointList[i], query=True, worldSpace=True, translation=True)[0]
            if pointPosX < minX:
                minX = pointPosX
                sideA = i
            elif pointPosX > maxX:
                maxX = pointPosX
                sideB = i
        if sideA > sideB:
            sideC = sideA
            sideA = sideB
            sideB = sideC
        
        pointListA = pointList[sideA:(sideB+1)]
        pointListB = pointList[sideB:]
        for j in range(0, (sideA+1)):
            pointListB.append(pointList[j])
        
        return pointListA, pointListB, sideA, sideB
    
    
    def sqCreateClusters(self, curveA, curveB, *args):
        self.clusterList = []
        for i in range(1, self.curveLenght-1):
            self.clusterList.append(cmds.cluster([curveA+".cv["+str(i)+"]", curveB+".cv["+str(i)+"]"], name="StickyLips_"+str(`i-1`)+"_Cls")[1])
        return self.clusterList
    
    
    def sqGenerateMuscleLocators(self, *args):
        muscleLoaded = True
        if not cmds.pluginInfo('MayaMuscle.mll', query=True, loaded=True):
            muscleLoaded = False
            try:
                cmds.loadPlugin('MayaMuscle.mll')
                muscleLoaded = True
            except:
                print "Error: Can not load the Maya Muscle plugin!"
                pass
        if muscleLoaded:
            minIndex = 0
            minPosX = 1000000000000000 # just to avoid non centered characters
            minPosId = 0
            vertexPairList = []
            muscleLocatorList = []
            for e, edgeName in enumerate(self.edgeList):
                tempCompList = cmds.polyListComponentConversion(edgeName, fromEdge=True, toVertex=True)
                tempExpList = cmds.filterExpand(tempCompList, selectionMask=31, expand=True)
                vertexPairList.append(tempExpList)
                
                edgePosA = cmds.xform(tempExpList[0], query=True, worldSpace=True, translation=True)[0]
                edgePosB = cmds.xform(tempExpList[1], query=True, worldSpace=True, translation=True)[0]
                if edgePosA < minPosX:
                    minIndex = e
                    minPosX = edgePosA
                    minPosId = 0
                if edgePosB < minPosX:
                    minIndex = e
                    minPosX = edgePosB
                    minPosId = 1
                    
            usedIndexList = []
            usedIndexList.append(minIndex)
            
            lastIndexUp = minIndex
            lastIndexDown = 0
            
            upEdgeList = []
            upEdgeList.append(self.edgeList[minIndex])
            downEdgeList = []
            for i in range(0, len(vertexPairList)-1):
                if not i == minIndex:
                    if vertexPairList[i][0] in vertexPairList[minIndex][minPosId] or vertexPairList[i][1] in vertexPairList[minIndex][minPosId]:
                        downEdgeList.append(self.edgeList[i])
                        usedIndexList.append(i)
                        lastIndexDown = i
            
            for i in range(0, self.maxIter-2):
                for j in range(0, len(vertexPairList)):
                    if not j in usedIndexList:
                        if vertexPairList[j][0] in vertexPairList[lastIndexUp] or vertexPairList[j][1] in vertexPairList[lastIndexUp]:
                            upEdgeList.append(self.edgeList[j])
                            usedIndexList.append(j)
                            lastIndexUp = j
                            break
                for j in range(0, len(vertexPairList)):
                    if not j in usedIndexList:
                        if vertexPairList[j][0] in vertexPairList[lastIndexDown] or vertexPairList[j][1] in vertexPairList[lastIndexDown]:
                            downEdgeList.append(self.edgeList[j])
                            usedIndexList.append(j)
                            lastIndexDown = j
                            break
            
            upMinusDown = len(upEdgeList) - len(downEdgeList) 
            downMinusUp = len(downEdgeList) - len(upEdgeList)
            
            if upMinusDown > 1:
                for i in range(0, upMinusDown):
                    if not len(upEdgeList) == (self.maxIter-3):
                        downEdgeList.append(upEdgeList[len(upEdgeList)-1])
                        upEdgeList = upEdgeList[:-1]
            if downMinusUp > 1:
                for i in range(0, downMinusUp):
                    if not len(upEdgeList) == (self.maxIter-3):
                        upEdgeList.append(downEdgeList[len(downEdgeList)-1])
                        downEdgeList = downEdgeList[:-1]
            
            upEdgeList = upEdgeList[:self.maxIter-1]
            downEdgeList = downEdgeList[:self.maxIter-1]
            
            for k in range(0, self.maxIter-2):
                cmds.select([upEdgeList[k], downEdgeList[k]])
#                cmds.refresh()
#                cmds.pause(seconds=1)
                mel.eval("cMuscleSurfAttachSetup();")
                msa = cmds.rename("StickLips_"+str(k)+"_MSA")
                cmds.disconnectAttr(msa+"Shape.outRotate", msa+".rotate")
                cmds.setAttr(msa+".rotateX", 0)
                cmds.setAttr(msa+".rotateY", 0)
                cmds.setAttr(msa+".rotateZ", 0)
                muscleLocatorList.append(msa)
                cmds.parent(self.clusterList[k], msa, absolute=True)
    
    
    def sqSetClustersZeroScale(self, *arqs):
        if self.clusterList:
            for item in self.clusterList:
                cmds.setAttr(item+".scaleX", 0)
                cmds.setAttr(item+".scaleY", 0)
                cmds.setAttr(item+".scaleZ", 0)
    
    
    def sqCreateStikyLipsDeformers(self, *args):
        baseMesh = None
        mainCurveList = [self.mainCurveA, self.mainCurveB]
        for mainCurve in mainCurveList:
            if baseMesh == None:
                baseMesh = cmds.duplicate(self.receptList[0], name=self.receptList[0]+"Base")[0]
                cmds.setAttr(baseMesh+".visibility", 0)
            
            wrapNode = cmds.deformer(mainCurve, name="StickyLips_Wrap", type="wrap")[0]
            try:
                cmds.connectAttr(self.receptList[0]+".dropoff", wrapNode+".dropoff[0]", force=True)
                cmds.connectAttr(self.receptList[0]+".inflType", wrapNode+".inflType[0]", force=True)
                cmds.connectAttr(self.receptList[0]+".smoothness", wrapNode+".smoothness[0]", force=True)
                cmds.connectAttr(self.receptList[0]+"Shape.worldMesh[0]", wrapNode+".driverPoints[0]", force=True)
            except:
                pass
            
            cmds.connectAttr(baseMesh+"Shape.worldMesh[0]", wrapNode+".basePoints[0]", force=True)
            cmds.connectAttr(mainCurve+"Shape.worldMatrix[0]", wrapNode+".geomMatrix", force=True)
            cmds.setAttr(wrapNode+".maxDistance", 1)
            cmds.setAttr(wrapNode+".autoWeightThreshold", 1)
            cmds.setAttr(wrapNode+".exclusiveBind", 1)
            
        baseCurveList = [self.baseCurveA, self.baseCurveB]
        for c, baseCurve in enumerate(baseCurveList):
            wireNode = cmds.wire(self.receptList[1], name=baseCurve+"_Wire", groupWithBase=False, crossingEffect=0, localInfluence=0)[0]
            cmds.connectAttr(mainCurveList[c]+"Shape.worldSpace[0]", wireNode+".baseWire[0]", force=True)
            cmds.connectAttr(baseCurve+"Shape.worldSpace[0]", wireNode+".deformedWire[0]", force=True)
            self.wireNodeList.append(wireNode)
            
            wireLocList = []
            for i in range(0, self.maxIter):
                wireLocList.append(baseCurve+".u["+str(i)+"]")
            cmds.dropoffLocator(1, 1, wireNode, wireLocList)
    
    
    def sqCreateStickyLipsCtrlAttr(self, *args):
        if not cmds.objExists(self.optionCtrl):
            cmds.circle(name=self.optionCtrl, constructionHistory=False)
        cmds.addAttr(self.optionCtrl, longName='stickyLips', attributeType='bool')
        cmds.setAttr(self.optionCtrl+'.stickyLips', edit=True, keyable=True)
        
        for i in range(0, self.maxIter):
            cmds.addAttr(self.optionCtrl, longName="stickyLipsWireLocator"+str(i), attributeType='float', keyable=False)
        
        for i in range(0, self.maxIter):
            for wireNode in self.wireNodeList:
                cmds.connectAttr(self.optionCtrl+".stickyLipsWireLocator"+str(i), wireNode+".wireLocatorEnvelope["+str(i)+"]")
        
        slTextCurve = cmds.textCurves(ch=False, font="Arial|w400|h-08", text="StickyLips", name="StickyLips_Label_Txt")[0]
        if "Shape" in slTextCurve:
            slTextCurve = cmds.rename(slTextCurve, slTextCurve[:slTextCurve.find("Shape")])
        t = 0
        slCharTransformList = cmds.listRelatives(slTextCurve, children=True, type="transform")
        for charTransform in slCharTransformList:
            txValue = cmds.getAttr(charTransform+".tx")
            sLTextShapeList = cmds.listRelatives(charTransform, allDescendents=True, type="nurbsCurve")
            for i, textShape in enumerate(sLTextShapeList):
                textShape = cmds.rename(textShape, "StickyLips_Txt_"+str(t)+"Shape")
                cmds.parent(textShape, slTextCurve, shape=True, relative=True)
                cmds.move(txValue, 0, 0, textShape+".cv[:]", relative=True)
                t = t+1
            cmds.delete(charTransform)
        cmds.setAttr(slTextCurve+".translateX", -0.1)
        cmds.setAttr(slTextCurve+".translateY", 0.25)
        cmds.setAttr(slTextCurve+".scaleX", 0.1)
        cmds.setAttr(slTextCurve+".scaleY", 0.1)
        cmds.setAttr(slTextCurve+".scaleZ", 0.1)
        cmds.setAttr(slTextCurve+".template", 1)
        cmds.makeIdentity(slTextCurve, apply=True)
        
        sideNameList = ["L", "R"]
        for side in sideNameList:
            bg = cmds.circle(name=side+"_StickyLips_Bg", normal=(0,0,1), radius=1, degree=1, sections=4, constructionHistory=False)[0]
            cmds.setAttr(bg+".rotateZ", 45)
            cmds.setAttr(bg+".translateX", 0.5)
            cmds.makeIdentity(bg, apply=True)
            cmds.setAttr(bg+".scaleX", 0.85)
            cmds.setAttr(bg+".scaleY", 0.15)
            cmds.makeIdentity(bg, apply=True)
            cmds.setAttr(bg+".template", 1)
            
            self.sliderCtrl = cmds.circle(name=side+"_StickyLips_Ctrl", normal=(0,0,1), radius=0.1, degree=3, constructionHistory=False)[0]
            attrToHideList = ['ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
            for attr in attrToHideList:
                cmds.setAttr(self.sliderCtrl+"."+attr, edit=True, lock=True, keyable=False)
            cmds.transformLimits(self.sliderCtrl, translationX=(0,1), enableTranslationX=(1,1))
            
        distPos = 1.0 / self.maxIter
        for i in range(0, self.maxIter):
            lPosA = (i * distPos)
            lPosB = (lPosA + distPos)
            rPosB = 1 - (i * distPos)
            rPosA = (rPosB - distPos)
            if i > 0:
                lPosA = lPosA - (distPos*0.33)
                rPosA = rPosA - (distPos*0.33)
            cmds.setDrivenKeyframe(self.optionCtrl, attribute="stickyLipsWireLocator"+str(i), currentDriver=sideNameList[0]+"_StickyLips_Ctrl.translateX", driverValue=lPosA, value=0, inTangentType="linear", outTangentType="linear")
            cmds.setDrivenKeyframe(self.optionCtrl, attribute="stickyLipsWireLocator"+str(i), currentDriver=sideNameList[0]+"_StickyLips_Ctrl.translateX", driverValue=lPosB, value=1, inTangentType="linear", outTangentType="linear")
            cmds.setDrivenKeyframe(self.optionCtrl, attribute="stickyLipsWireLocator"+str(i), currentDriver=sideNameList[1]+"_StickyLips_Ctrl.translateX", driverValue=rPosA, value=0, inTangentType="linear", outTangentType="linear")
            cmds.setDrivenKeyframe(self.optionCtrl, attribute="stickyLipsWireLocator"+str(i), currentDriver=sideNameList[1]+"_StickyLips_Ctrl.translateX", driverValue=rPosB, value=1, inTangentType="linear", outTangentType="linear")
        
        lSliderGrp = cmds.group(sideNameList[0]+"_StickyLips_Ctrl", sideNameList[0]+"_StickyLips_Bg", name=sideNameList[0]+"_StickyLips_Ctrl_Grp")
        rSliderGrp = cmds.group(sideNameList[1]+"_StickyLips_Ctrl", sideNameList[1]+"_StickyLips_Bg", name=sideNameList[1]+"_StickyLips_Ctrl_Grp")
        cmds.setAttr(rSliderGrp+".rotateZ", 180)
        cmds.setAttr(rSliderGrp+".translateY", -0.25)
        sliderGrp = cmds.group(lSliderGrp, rSliderGrp, slTextCurve, name="StickyLips_Ctrl_Grp")
    
    
    def sqGenerateStickyLips(self, *args):
        self.sqGetRecepts()
        if self.receptList[0] == None or self.receptList[1] == None:
            mel.eval("warning \"Please, load ReceptA and ReceptB targets to continue.\";")
        else:
            self.sqGenerateCurves()
            self.sqCreateClusters(self.baseCurveA, self.baseCurveB)
            self.sqSetClustersZeroScale()
            self.sqGenerateMuscleLocators()
            self.sqCreateStikyLipsDeformers()
            self.sqCreateStickyLipsCtrlAttr()
            cmds.select(clear=True)
