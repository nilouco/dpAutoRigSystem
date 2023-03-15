# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya as om
from functools import partial

# global variables to this module:
CLASS_NAME = "DeltaTarget"
TITLE = "m214_deltaTarget"
DESCRIPTION = "m215_deltaTargetDesc"
ICON = "/Icons/dp_deltaTarget.png"

DPDT_VERSION = "1.0"

class DeltaTarget(object):
    def __init__(self, dpUIinst, langDic, langName, ui=True, *args, **kwargs):
        self.langDic = langDic
        self.langName = langName
        self.ui = ui
        if self.ui:
            # call main function
            self.dpDeltaTargetUI(self)
    
    
    def dpDeltaTargetUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating deltaTargetUI Window:
        if cmds.window('dpDeltaTargetWindow', query=True, exists=True):
            cmds.deleteUI('dpDeltaTargetWindow', window=True)
        targetMirror_winWidth  = 305
        targetMirror_winHeight = 250
        dpTargetMirrorWin = cmds.window('dpDeltaTargetWindow', title=self.langDic[self.langName]["m214_deltaTarget"]+" "+DPDT_VERSION, widthHeight=(targetMirror_winWidth, targetMirror_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        deltaTargetLayout = cmds.columnLayout('deltaTargetLayout')
        # buttons
        self.originalModelBT = cmds.textFieldButtonGrp("originalModelBT", label=self.langDic[self.langName]["i043_origModel"], text="", buttonCommand=partial(self.dpLoadMesh, 0), buttonLabel=self.langDic[self.langName]["i187_load"], parent=deltaTargetLayout)
        self.posedModelBT = cmds.textFieldButtonGrp("posedModelBT", label=self.langDic[self.langName]["i269_posedModel"], text="", buttonCommand=partial(self.dpLoadMesh, 1), buttonLabel=self.langDic[self.langName]["i187_load"], parent=deltaTargetLayout)
        self.fixedModelBT = cmds.textFieldButtonGrp("fixedModelBT", label=self.langDic[self.langName]["i270_fixedModel"], text="", buttonCommand=partial(self.dpLoadMesh, 2), buttonLabel=self.langDic[self.langName]["i187_load"], parent=deltaTargetLayout)
        # do it
        cmds.button(label=self.langDic[self.langName]["i054_targetRun"], annotation=self.langDic[self.langName]["i053_targetRunDesc"], width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.dpPrepareData, parent=deltaTargetLayout)
        # call targetMirrorUI Window:
        cmds.showWindow(dpTargetMirrorWin)
    

    def dpPrepareData(self, *args):
        """
        """
        if self.ui:
            originalData = cmds.textFieldButtonGrp(self.originalModelBT, query=True, text=True)
            posedData = cmds.textFieldButtonGrp(self.posedModelBT, query=True, text=True)
            fixedData = cmds.textFieldButtonGrp(self.fixedModelBT, query=True, text=True)
            if originalData and posedData and fixedData:
                print("Affrisiaxxseit")
                self.dpRunDeltaExtractor(originalData, posedData, fixedData)


    
    def dpLoadMesh(self, buttonType, *args):
        """ Load selected object as model type
        """
        selectedList = cmds.ls(selection=True)
        if selectedList:
            if self.dpCheckGeometry(selectedList[0]):
                if buttonType == 0:
                    cmds.textFieldButtonGrp(self.originalModelBT, edit=True, text=selectedList[0])
                elif buttonType == 1:
                    cmds.textFieldButtonGrp(self.posedModelBT, edit=True, text=selectedList[0])
                else: #2
                    cmds.textFieldButtonGrp(self.fixedModelBT, edit=True, text=selectedList[0])
        else:
            print("Original Model > None")
    
    
    def dpCheckGeometry(self, item, *args):
        isGeometry = False
        if item:
            if cmds.objExists(item):
                childList = cmds.listRelatives(item, children=True)
                if childList:
                    try:
                        itemType = cmds.objectType(childList[0])
                        if itemType == "mesh":
                            isGeometry = True
                        else:
                            mel.eval("warning \""+item+" "+self.langDic[self.langName]["i058_notGeo"]+"\";")
                    except:
                        mel.eval("warning \""+self.langDic[self.langName]["i163_sameName"]+" "+item+"\";")
                else:
                    mel.eval("warning \""+self.langDic[self.langName]["i059_selTransform"]+" "+item+" "+self.langDic[self.langName]["i060_shapePlease"]+"\";")
            else:
                mel.eval("warning \""+item+" "+self.langDic[self.langName]["i061_notExists"]+"\";")
        else:
            mel.eval("warning \""+self.langDic[self.langName]["i062_notFound"]+" "+item+"\";")
        return isGeometry
    
    
    def dpRunDeltaExtractor(self, originalData, posedData, fixedData, *args):
        """ Create the delta target.
        """
        print("Monza Bonina =", originalData, posedData, fixedData)
        deltaTgt = cmds.duplicate(originalData, name=originalData+"_Delta_Tgt")

