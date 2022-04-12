# importing libraries:
from maya import cmds
from ..Modules.Library import dpUtils


# global variables to this module:    
CLASS_NAME = "CorrectionMapper"
TITLE = "m068_correctionMapper"
DESCRIPTION = "m069_correctionMapperDesc"
ICON = "/Icons/dp_correctionMapper.png"

DPCORRECTIONMAPPER_VERSION = 2.0


class CorrectionMapper(object):
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.correctionMapperName = self.langDic[self.langName]['m068_correctionMapper']
        self.netSuffix = "CrMap_Net"
        self.crMapList = []

        # call main UI function
        self.dpCorrectionMapperCloseUI()
        self.dpCorrectionMapperUI()
        self.dpPopulateUI()
    

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
         




        
    def actualizeMapperEditLayout(self, *args):
        """ TODO write description here please
        """
        #WIP
        print ("wip to load editable field in the UI here")
        sel = cmds.textScrollList(self.existingMapperTSL, query=True, selectItem=True)
        cmds.select(sel)
        print("net selected = ", sel)
        



    
    def dpPopulateUI(self, *args):
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






    def dpCreateCorrectionMapper(self, name=None, *args):
        """ Create nodes to calculate the correction we want to mapper to fix.
        """
        # loading Maya matrix node
        loadedQuatNode = dpUtils.checkLoadedPlugin("quatNodes", self.langDic[self.langName]['e014_cantLoadQuatNode'])
        loadedMatrixPlugin = dpUtils.checkLoadedPlugin("matrixNodes", self.langDic[self.langName]['e002_matrixPluginNotFound'])
        if loadedQuatNode and loadedMatrixPlugin:
            # naming
            if not name:
                name = cmds.textField(self.create_TF, query=True, text=True)
                if not name:
                    name = "CorrectionMapper"
            mapName, name = dpUtils.resolveName(name, self.netSuffix)
            
            print("Name = ", name)
            print("mapName = ", mapName)

            net = cmds.createNode("network", name=name)
            cmds.addAttr(net, longName="dpNetwork", attributeType="bool")
            cmds.addAttr(net, longName="dpCorrectionMapper", attributeType="bool")
            cmds.addAttr(net, longName="name", dataType="string")
            cmds.addAttr(net, longName="axis", attributeType='enum', enumName="+X:-X:+Y:-Y:+Z:-Z")
            cmds.addAttr(net, longName="axisName", dataType="string")
            cmds.addAttr(net, longName="extractAxisOrder", attributeType='enum', enumName="XYZ:YZX:ZXY:XZY:YXZ:ZYX")
            cmds.addAttr(net, longName="extractAxisOrderName", dataType="string")
            cmds.addAttr(net, longName="axisPositive", attributeType="bool")
            cmds.addAttr(net, longName="startValue", attributeType="long")
            cmds.addAttr(net, longName="endValue", attributeType="long")

            cmds.setAttr(net+".dpNetwork", 1)
            cmds.setAttr(net+".dpCorrectionMapper", 1)
            cmds.setAttr(net+".name", mapName, type="string")

            
            cmds.setAttr(net+".axisName", "X", type="string")
            cmds.setAttr(net+".extractAxisOrderName", "XYZ", type="string")
            cmds.setAttr(net+".axisPositive", 1)
            cmds.setAttr(net+".endValue", 180)



            self.dpPopulateUI()
            cmds.textScrollList(self.existingMapperTSL, edit=True, deselectAll=True)
            cmds.textScrollList(self.existingMapperTSL, edit=True, selectItem=net)
            self.actualizeMapperEditLayout()
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