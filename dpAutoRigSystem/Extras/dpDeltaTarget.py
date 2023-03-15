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
    

    def getMeshShape(self, node, *args):
        """
        """
        print("Carretos in mesh")
        if cmds.objectType(node) != "mesh":
            childrenList = cmds.listRelatives(node, children=True, type="mesh")
            if childrenList:
                return childrenList[0]
        elif cmds.objectType(node) == "mesh":
            return node
        

    def getFather(self, node, *args):
        """
        """
        fatherList = cmds.listRelatives(node, allParents=True, type="transform")
        if fatherList:
            return fatherList[0]


    def dpRunDeltaExtractor(self, originalNode, posedNode, fixedNode, *args):
        """ Create the delta target.
        """
        # declaring variables
        deltaTransformDic, posedTransformDic, fixedTransformDic = {}, {}, {}
        attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']


        print("Monza Bonina =", originalNode, posedNode, fixedNode)
        deltaNode = cmds.duplicate(originalNode, name=originalNode+"_Delta_Tgt")[0]
        try:
            cmds.parent(deltaNode, world=True)
        except:
            pass
        
        deltaMesh = self.getMeshShape(deltaNode)
        posedMesh = self.getMeshShape(posedNode)
        fixedMesh = self.getMeshShape(fixedNode)
        print("Kombi Bonina MESHES =", deltaMesh, posedMesh, fixedMesh)

        # storing transformation data
        for attr in attrList:
            deltaTransformDic[attr] = cmds.getAttr(deltaNode+"."+attr)
            posedTransformDic[attr] = cmds.getAttr(posedNode+"."+attr)
            fixedTransformDic[attr] = cmds.getAttr(fixedNode+"."+attr)
            






        # WIP
        # get list of mesh vertice proccess
        # selecting meshes
        cmds.select([deltaMesh, posedMesh, fixedMesh])
        meshList = om.MSelectionList()
        om.MGlobal_getActiveSelectionList(meshList)
        
        # declaring from and to objects, dagPaths and vertice lists
        deltaObject = om.MObject()
        deltaDagPath = om.MDagPath()
        deltaVerticeList = om.MPointArray()
        
        posedObject = om.MObject()
        posedDagPath = om.MDagPath()
        posedVerticeList = om.MPointArray()
        
        fixedObject = om.MObject()
        fixedDagPath = om.MDagPath()
        fixedVerticeList = om.MPointArray()

        # getting dagPaths
        meshList.getDagPath(0, deltaDagPath, deltaObject)
        meshList.getDagPath(1, posedDagPath, posedObject)
        meshList.getDagPath(2, fixedDagPath, fixedObject)
        # getting open maya API mesh
        deltaMeshFn = om.MFnMesh(deltaDagPath)
        posedMeshFn = om.MFnMesh(posedDagPath)
        fixedMeshFn = om.MFnMesh(fixedDagPath)



        # WIP 2

        # verify the same number of vertices
        if deltaMeshFn.numVertices() == posedMeshFn.numVertices() and deltaMeshFn.numVertices() == fixedMeshFn.numVertices():
            print ("YES ai funciona segundo o Andre Megabrean!")
            

            # getting fromTransform father
            posedFather = self.getFather(posedNode)
            fixedFather = self.getFather(fixedNode)
            if posedFather:
                cmds.parent(posedNode, world=True)
            if fixedFather:
                cmds.parent(fixedNode, world=True)

            





            # put fromTransform in the same location then toTransform
           
            for attr in attrList:
                cmds.setAttr(deltaNode+"."+attr, lock=False)
                cmds.setAttr(posedNode+"."+attr, lock=False)
                cmds.setAttr(fixedNode+"."+attr, lock=False)
                if not "s" in attr:
                    cmds.setAttr(deltaNode+"."+attr, 0)
                    cmds.setAttr(posedNode+"."+attr, 0)
                    cmds.setAttr(fixedNode+"."+attr, 0)
                else:
                    cmds.setAttr(deltaNode+"."+attr, 1)
                    cmds.setAttr(posedNode+"."+attr, 1)
                    cmds.setAttr(fixedNode+"."+attr, 1)
            cmds.delete(cmds.parentConstraint(deltaNode, posedNode, maintainOffset=False))
            cmds.delete(cmds.scaleConstraint(deltaNode, posedNode, maintainOffset=False))
            cmds.delete(cmds.parentConstraint(deltaNode, fixedNode, maintainOffset=False))
            cmds.delete(cmds.scaleConstraint(deltaNode, fixedNode, maintainOffset=False))
            

            
            # getting vertices as points
            deltaMeshFn.getPoints(deltaVerticeList)
            posedMeshFn.getPoints(posedVerticeList)
            fixedMeshFn.getPoints(fixedVerticeList)
            
            


            # progress window
            progressAmount = 0
            cmds.progressWindow(title='Match Mesh Data', progress=progressAmount, status='Tranfering: 0%', isInterruptable=True)
            cancelled = False
            
            # transfer vetex position from FROM mesh to TO mesh selected
            nbVertice = fixedVerticeList.length()
            for i in range(0, fixedVerticeList.length()):
                # update progress window
                progressAmount += 1
                # check if the dialog has been cancelled
                if cmds.progressWindow(query=True, isCancelled=True):
                    cancelled = True
                    break
                cmds.progressWindow(edit=True, maxValue=nbVertice, progress=progressAmount, status=('Transfering: ' + repr(progressAmount) + ' vertex'))
                
                # transfer data
                deltaX = fixedVerticeList[i].x - posedVerticeList[i].x
                deltaY = fixedVerticeList[i].y - posedVerticeList[i].y
                deltaZ = fixedVerticeList[i].z - posedVerticeList[i].z
                cmds.move(deltaX, deltaY, deltaZ, deltaMesh+".vtx["+str(i)+"]", absolute=True)
            
            cmds.progressWindow(endProgress=True)





            if posedFather:
                cmds.parent(posedNode, posedFather)
            if fixedFather:
                cmds.parent(fixedNode, fixedFather)
            # restore transformation data
            for attr in attrList:
                cmds.setAttr(originalNode+"."+attr, deltaTransformDic[attr])
                cmds.setAttr(posedNode+"."+attr, posedTransformDic[attr])
                cmds.setAttr(fixedNode+"."+attr, fixedTransformDic[attr])
            

