# importing libraries:
from maya import cmds
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils


# global variables to this module:    
CLASS_NAME = "CorrectionMapper"
TITLE = "m068_correctionMapper"
DESCRIPTION = "m069_correctionMapperDesc"
ICON = "/Icons/dp_correctionMapper.png"

DPCORRECTIONMAPPER_VERSION = 2.0


class CorrectionMapper(object):
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ui = ui
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.correctionMapperName = self.langDic[self.langName]['m068_correctionMapper']
        self.netSuffix = "CrMap_Net"
        self.correctionMapperGrp = "CorrectionMapper_Grp"
        self.crMapList = []
        self.net = None

        # call main UI function
        if self.ui:
            self.dpCorrectionMapperCloseUI()
            self.dpCorrectionMapperUI()
            self.dpPopulateMapperNetUI()
        

    def dpCorrectionMapperCloseUI(self, *args):
        """ Delete existing CorrectionMapper window if it exists.
        """
        if cmds.window('dpCorrectionMapperWindow', query=True, exists=True):
            cmds.deleteUI('dpCorrectionMapperWindow', window=True)


    def dpCorrectionMapperUI(self, *args):
        """ CorrectionMapper UI layout and elements.
            This is based in the old dpPoseReader, now without PyMEL or Qt.
        """
        correctionMapper_winWidth  = 380
        correctionMapper_winHeight = 300
        cmds.window('dpCorrectionMapperWindow', title=self.correctionMapperName+" "+str(DPCORRECTIONMAPPER_VERSION), widthHeight=(correctionMapper_winWidth, correctionMapper_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpCorrectionMapperWindow')
        
        # create UI layout and elements:
        correctionMapperLayout = cmds.columnLayout('correctionMapperLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.separator(style='none', height=10, width=100, parent=correctionMapperLayout)
        
        cmds.text("NEW NEW", align="left", height=20, font='boldLabelFont', parent=correctionMapperLayout)
        correctionMapperLayoutA = cmds.rowColumnLayout('correctionMapperLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=correctionMapperLayout)
        self.create_BT = cmds.button('create_BT', label=self.langDic[self.langName]['i158_create'], command=self.dpCreateCorrectionMapper, backgroundColor=(0.7, 1.0, 0.7), parent=correctionMapperLayoutA)
        self.create_TF = cmds.textField('create_TF', editable=True, parent=correctionMapperLayoutA)
        cmds.separator(style='in', height=15, width=100, parent=correctionMapperLayout)

        cmds.text("Existing", align="left", height=20, font='boldLabelFont', parent=correctionMapperLayout)
        self.existingMapperTSL = cmds.textScrollList('existingMapperTSL', width=20, allowMultiSelection=False, selectCommand=self.actualizeMapperEditLayout, parent=correctionMapperLayout)
        cmds.separator(style='none', height=10, width=100, parent=correctionMapperLayout)

        self.editSelectedMapperLayout = cmds.frameLayout('editSelectedMapperLayout', label=self.langDic[self.langName]['i011_editSelected'], collapsable=True, collapse=False, parent=correctionMapperLayout)
        

    def renameMapperNodes(self, oldName, name, *args):
        """ List all connected nodes by message into the network and rename it using given parameters.
        """
        messageAttrList = []
        attrList = cmds.listAttr(self.net)
        for attr in attrList:
            if cmds.getAttr(self.net+"."+attr, type=True) == "message":
                messageAttrList.append(attr)
        if messageAttrList:
            for messageAttr in messageAttrList:
                connectedNodeList = cmds.listConnections(self.net+"."+messageAttr)
                if connectedNodeList:
                    childrenList = cmds.listRelatives(connectedNodeList[0], children=True, allDescendents=True)
                    cmds.rename(connectedNodeList[0], connectedNodeList[0].replace(oldName, name))
                    if childrenList:
                        for children in childrenList:
                            try:
                                cmds.rename(children, children.replace(oldName, name))
                            except:
                                pass


    def changeName(self, name=None, *args):
        """ Edit name of the current network node selected.
            If there isn't any given name, it will try to get from the UI.
            Returns the name result.
        """
        oldName = cmds.getAttr(self.net+".name")
        if not name:
            name = cmds.textFieldGrp(self.nameTFG, query=True, text=True)
        if name:
            name = dpUtils.resolveName(name, self.netSuffix)[0]
            self.renameMapperNodes(oldName, name)
            cmds.setAttr(self.net+".name", name, type="string")
            self.net = cmds.rename(self.net, self.net.replace(oldName, name))
            self.dpPopulateMapperNetUI()
            #self.actualizeMapperEditLayout() #Bug: if we call this method here it will crash Maya! Error report: 322305477
        return name


    def dpRecreateSelectedMapperUI(self, node=None, *args):
        """ It will recreate the mapper layout for the selected network node.
        """
        # TODO: edit selected mapper layout elements:

        currentName = cmds.getAttr(self.net+".name")
        self.selectedMapperLayout = cmds.columnLayout('selectedMapperLayout', adjustableColumn=True, parent=self.editSelectedMapperLayout)
#        nameLayoutA = cmds.rowColumnLayout('nameLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=self.selectedMapperLayout)
        self.nameTFG = cmds.textFieldGrp("nameTFG", label='Name', text=currentName, editable=True, changeCommand=self.changeName, parent=self.selectedMapperLayout)
        cmds.text("Axis")
        cmds.text("Extract Axis Order")
        cmds.text("Value")
        cmds.text("Start")
        cmds.text("End")




        
    def actualizeMapperEditLayout(self, *args):
        """ TODO write description here please
        """
        #WIP
        self.dpClearEditMapperLayout()
        selList = cmds.textScrollList(self.existingMapperTSL, query=True, selectItem=True)
        if selList:
            cmds.select(selList[0])
            self.net = selList[0]
        self.dpRecreateSelectedMapperUI()
        



    
    def dpPopulateMapperNetUI(self, *args):
        """ Check existing network node to populate UI.
        """
        currentNetList = cmds.ls(selection=False, type="network")
        if currentNetList:
            self.crMapList = []
            for item in currentNetList:
                if cmds.objExists(item+".dpNetwork"):
                    if cmds.getAttr(item+".dpNetwork") == 1:
                        if cmds.objExists(item+".dpCorrectionMapper"):
                            if cmds.getAttr(item+".dpCorrectionMapper") == 1:
                                
                                #TODO validate correctionMapper node integrity
                                
                                self.crMapList.append(item)
            if self.crMapList:
                cmds.textScrollList(self.existingMapperTSL, edit=True, removeAll=True)
                cmds.textScrollList(self.existingMapperTSL, edit=True, append=self.crMapList)
                cmds.textScrollList(self.existingMapperTSL, edit=True, deselectAll=True)
                cmds.textScrollList(self.existingMapperTSL, edit=True, selectItem=self.net)



    def dpClearEditMapperLayout(self, *args):
        """ Just clean up the selected mapper layout.
        """
        try:
            cmds.deleteUI(self.selectedMapperLayout)
        except:
            pass




    def dpCreateMapperLocator(self, name, toAttach, *args):
        """ Creates a space locator, zeroOut it to receive a parentConstraint.
            Return the locator to use it as a reader node to the system.
        """
        if cmds.objExists(toAttach):
            loc = cmds.spaceLocator(name=name+"_Loc")[0]
            grp = dpUtils.zeroOut([loc])[0]
            cmds.parentConstraint(toAttach, grp, maintainOffset=False, name=grp+"_PaC")
            cmds.parent(grp, dpUtils.getNodeByMessage("mapperDataGrp", self.net))
            return loc
        else:
            print("Object not exists:", toAttach)




    def dpCreateCorrectionMapper(self, nodeList=None, name=None, *args):
        """ Create nodes to calculate the correction we want to mapper to fix.
        """
        # loading Maya matrix node
        loadedQuatNode = dpUtils.checkLoadedPlugin("quatNodes", self.langDic[self.langName]['e014_cantLoadQuatNode'])
        loadedMatrixPlugin = dpUtils.checkLoadedPlugin("matrixNodes", self.langDic[self.langName]['e002_matrixPluginNotFound'])
        if loadedQuatNode and loadedMatrixPlugin:
            if not nodeList:
                nodeList = cmds.ls(selection=True)
            if nodeList:
                if len(nodeList) == 2:
                    origNode = nodeList[0]
                    actionNode = nodeList[1]

                    cmds.undoInfo(openChunk=True)

                    # main group
                    if not cmds.objExists(self.correctionMapperGrp):
                        self.correctionMapperGrp = cmds.group(empty=True, name=self.correctionMapperGrp)
                        cmds.addAttr(self.correctionMapperGrp, longName="dpCorrectionMapperGrp", attributeType="bool")
                        cmds.setAttr(self.correctionMapperGrp+".dpCorrectionMapperGrp", 1)
                        self.ctrls.setLockHide([self.correctionMapperGrp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        scalableGrp = dpUtils.getNodeByMessage("scalableGrp")
                        if scalableGrp:
                            cmds.parent(self.correctionMapperGrp, scalableGrp)

                    # naming
                    if not name:
                        name = cmds.textField(self.create_TF, query=True, text=True)
                        if not name:
                            name = "CorrectionMapper"
                    mapName, name = dpUtils.resolveName(name, self.netSuffix)
                    
                    # create the container of the system data
                    self.net = cmds.createNode("network", name=name)
                    cmds.addAttr(self.net, longName="dpNetwork", attributeType="bool")
                    cmds.addAttr(self.net, longName="dpCorrectionMapper", attributeType="bool")
                    cmds.addAttr(self.net, longName="name", dataType="string")
                    cmds.addAttr(self.net, longName="axis", attributeType='enum', enumName="+X:-X:+Y:-Y:+Z:-Z")
                    cmds.addAttr(self.net, longName="axisName", dataType="string")
                    cmds.addAttr(self.net, longName="extractAxisOrder", attributeType='enum', enumName="XYZ:YZX:ZXY:XZY:YXZ:ZYX")
                    cmds.addAttr(self.net, longName="extractAxisOrderName", dataType="string")
                    cmds.addAttr(self.net, longName="axisPositive", attributeType="bool")
                    cmds.addAttr(self.net, longName="startValue", attributeType="long")
                    cmds.addAttr(self.net, longName="endValue", attributeType="long")
                    messageAttrList = ["mapperDataGrp", "extractAngleMM", "extractAngleDM", "extractAngleQtE", "extractAngleMD", "extractAngleActiveMD", "smallerThanOneCnd", "overZeroCnd", "origLoc", "actionLoc"]
                    for messageAttr in messageAttrList:
                        cmds.addAttr(self.net, longName=messageAttr, attributeType="message")
                    
                    cmds.setAttr(self.net+".dpNetwork", 1)
                    cmds.setAttr(self.net+".dpCorrectionMapper", 1)
                    cmds.setAttr(self.net+".name", mapName, type="string")

                    cmds.setAttr(self.net+".axisName", "X", type="string")
                    cmds.setAttr(self.net+".extractAxisOrderName", "XYZ", type="string")
                    cmds.setAttr(self.net+".axisPositive", 1)
                    cmds.setAttr(self.net+".endValue", 180)


                    mapperDataGrp = cmds.group(empty=True, name=mapName+"_Grp")
                    cmds.connectAttr(mapperDataGrp+".message", self.net+".mapperDataGrp", force=True)
                    cmds.parent(mapperDataGrp, self.correctionMapperGrp)
                    

                    origLoc = self.dpCreateMapperLocator(mapName+"_Orig", origNode)
                    actionLoc = self.dpCreateMapperLocator(mapName+"_Action", actionNode)
                    


                    #WIP:

                    # if rotate extration option:
                    # write a new dpUtils function to generate these matrix nodes here:

                    extractAngleMM = cmds.createNode("multMatrix", name=mapName+"_ExtractAngle_MM")
                    extractAngleDM = cmds.createNode("decomposeMatrix", name=mapName+"_ExtractAngle_DM")
                    extractAngleQtE = cmds.createNode("quatToEuler", name=mapName+"_ExtractAngle_QtE")
                    extractAngleMD = cmds.createNode("multiplyDivide", name=mapName+"_ExtractAngle_MD")
                    extractAngleActiveMD = cmds.createNode("multiplyDivide", name=mapName+"_ExtractAngle_Active_MD")
                    smallerThanOneCnd = cmds.createNode("condition", name=mapName+"_ExtractAngle_SmallerThanOne_Cnd")
                    overZeroCnd = cmds.createNode("condition", name=mapName+"_ExtractAngle_OverZero_Cnd")

                    cmds.setAttr(extractAngleMD+".operation", 2)
                    cmds.setAttr(smallerThanOneCnd+".operation", 5) #less or equal
                    cmds.setAttr(smallerThanOneCnd+".secondTerm", 1)
                    cmds.setAttr(overZeroCnd+".secondTerm", 0)
                    cmds.setAttr(overZeroCnd+".colorIfFalseR", 0)
                    cmds.setAttr(overZeroCnd+".operation", 3) #greater or equal

                    cmds.connectAttr(actionLoc+".worldMatrix[0]", extractAngleMM+".matrixIn[0]", force=True)
                    cmds.connectAttr(origLoc+".worldInverseMatrix[0]", extractAngleMM+".matrixIn[1]", force=True)
                    cmds.connectAttr(extractAngleMM+".matrixSum", extractAngleDM+".inputMatrix", force=True)

                    
                    # setup the rotation affection
                    cmds.connectAttr(extractAngleDM+".outputRotateY", extractAngleMD+".input1X", force=True)
                    cmds.connectAttr(self.net+".endValue", extractAngleMD+".input2X", force=True)
                    cmds.connectAttr(extractAngleMD+".outputX", smallerThanOneCnd+".firstTerm", force=True)
                    cmds.connectAttr(extractAngleMD+".outputX", smallerThanOneCnd+".colorIfTrueR", force=True)
                    cmds.connectAttr(smallerThanOneCnd+".outColorR", overZeroCnd+".firstTerm", force=True)
                    cmds.connectAttr(smallerThanOneCnd+".outColorR", overZeroCnd+".colorIfTrueR", force=True)
                    

                    # node for manual activation connection
                    # TODO create a way to avoid manual connection here, maybe using the UI new tab?
                    cmds.connectAttr(overZeroCnd+".outColorR", extractAngleActiveMD+".input1X", force=True)

                    
                    
                    
                    # serialize message attributes
                    cmds.connectAttr(extractAngleMM+".message", self.net+".extractAngleMM", force=True)
                    cmds.connectAttr(extractAngleDM+".message", self.net+".extractAngleDM", force=True)
                    cmds.connectAttr(extractAngleQtE+".message", self.net+".extractAngleQtE", force=True)
                    cmds.connectAttr(extractAngleMD+".message", self.net+".extractAngleMD", force=True)
                    cmds.connectAttr(extractAngleActiveMD+".message", self.net+".extractAngleActiveMD", force=True)
                    cmds.connectAttr(smallerThanOneCnd+".message", self.net+".smallerThanOneCnd", force=True)
                    cmds.connectAttr(overZeroCnd+".message", self.net+".overZeroCnd", force=True)
                    cmds.connectAttr(origLoc+".message", self.net+".origLoc", force=True)
                    cmds.connectAttr(actionLoc+".message", self.net+".actionLoc", force=True)
                    


                    
                    if self.ui:
                        self.dpPopulateMapperNetUI()
                        self.actualizeMapperEditLayout()
                        

                    cmds.undoInfo(closeChunk=True)
                    
                    
                    

                else:
                    print("Select first the father node and then the child node, please")
            else:
                print("Need to select 2 items to calculate interactions, please")
        else:
            print("Can't continue without load quatNodes and matrixNodes plugins, sorry.")
            

        #WIP:
        
        


        #TODO
        # auto connect
            # load input node and attribute
            # find output blendShape node and attribute
        # receive data to process without any dialog box
        # ui update button?
        # ui command to change axis, extractAxisOrder
        # rename data?
        # reconnect axis on change
        # set axis order change
        # set values change
        # add Delete system itself button
        # expose network attributes in the channel box?
        # connect all nodes by message to net container node
        # prepare code to run without any UI dependence
        # change values attributes to float
        # refresh button/ auto refresh
        # clear create name text field?
        # delete button