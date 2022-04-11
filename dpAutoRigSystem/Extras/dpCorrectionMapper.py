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

        # call main UI function
        self.dpCorrectionMapperCloseUI()
        self.dpCorrectionMapperUI()
    

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
        correctionMapperLayout = cmds.columnLayout('correctionMapperLayout', adjustableColumn=True, columnOffset=("left", 10))
        cmds.separator(style='none', height=10, width=100, parent=correctionMapperLayout)
        
        correctionMapperLayoutA = cmds.rowColumnLayout('correctionMapperLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=correctionMapperLayout)
        self.create_BT = cmds.button('create_BT', label=self.langDic[self.langName]['i158_create'], command=self.dpCreateCorrectionMapper, backgroundColor=(0.7, 1.0, 0.7), parent=correctionMapperLayoutA)
        self.create_TF = cmds.textField('create_TF', editable=True, parent=correctionMapperLayoutA)
        cmds.separator(style='in', height=15, width=100, parent=correctionMapperLayout)
        
    



    def dpCreateCorrectionMapper(self, name=None, *args):
        """ Create nodes to calculate the correction we want to mapper to fix.
        """
        if not name:
            name = cmds.textField(self.create_TF, query=True, text=True)
            if not name:
                name = "CorrectionMapper"
        name = dpUtils.resolveName(name, self.netSuffix)
        
        print("Name = ", name)

        net = cmds.createNode("network", name=name)
        cmds.addAttr(net, longName="dpNetwork", attributeType="bool")
        cmds.addAttr(net, longName="dpCorrectionMapper", attributeType="bool")
        cmds.setAttr(net+".dpNetwork", 1)
        cmds.setAttr(net+".dpCorrectionMapper", 1)
