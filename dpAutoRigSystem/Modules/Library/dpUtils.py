# importing libraries:
import maya.cmds as cmds
import maya.OpenMaya as om
import os
import sys
import re
import cProfile
import shutil
import urllib
import zipfile
import StringIO
import webbrowser


# UTILS functions:
def findEnv(key, path):
    """ Find and return the environ directory of this system.
    """
    envStr = os.environ[key]
    
    dpARPath = findPath("dpAutoRig.py")

    splitEnvList = []
    if os.name == "posix":
        splitEnvList = envStr.split(":")
    else:
        splitEnvList = envStr.split(";")
    envPath = ""

    if splitEnvList:
        splitEnvList = filter(lambda x: x != "" and x != ' ' and x != None, splitEnvList)
        for env in splitEnvList:
            env = os.path.abspath(env) # Fix crash when there's relative path in os.environ
            if env in dpARPath:
                try:
                    envPath = dpARPath.split(env)[1][+1:].split(path)[0][:-1].replace('/','.')
                except:
                    pass
                if len(env) < 4:
                    envPath = dpARPath.split(env)[1][0:].split(path)[0][:-1].replace('/','.')
                    return envPath+"."+path
                break
    # if we are here, we must return a default path:
    splitEnvList = envStr.rpartition(path)
    if os.name == "posix":
        if envPath != "":
            envPath = envPath+".dpAutoRigSystem"
        else:
            envPath = "dpAutoRigSystem"
    else:
        if ":" in envPath:
            envPath = splitEnvList[0][splitEnvList[0].rfind(":")-1:]
    if envPath == "" or envPath == " " or envPath == None:
        return path
    return envPath


def findPath(filename):
    """ Find and return the absolute path of the fileName.
    """
    stringPath   = str(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename))
    correctPath  = stringPath.replace("\\", "/")
    if os.name == "posix":
        absolutePath = stringPath[0:stringPath.rfind("/")]
    else:
        absolutePath = correctPath[correctPath.find("/")-2:correctPath.rfind("/")]
    return absolutePath


def findAllFiles(path, dir, ext):
    """ Find all files in the directory with the extension.
        Return a list of all module names (without '.py' extension).
    """
    fileDir = path + "/" + dir
    allFilesList = os.listdir(fileDir)
    # select only files with extension:
    pyFilesList = []
    for file in allFilesList:
        if file.endswith(".py") and str(file) != "__init__.py":
            pyFilesList.append(str(file)[:-3])
    return pyFilesList


def findAllModules(path, dir):
    """ Find all modules in the directory.
        Return a list of all module names (without '.py' extension).
    """
    allPyFilesList = findAllFiles(path, dir, ".py")
    moduleList = []
    # removing "__init__":
    for file in allPyFilesList:
        #Ensure base class are skipped
        if file != "dpBaseClass" and file != "dpLayoutClass" and file != "dpBaseControlClass":
            moduleList.append(file)
    return moduleList


def findAllModuleNames(path, dir):
    """ Find all modules names for this directory.
        Return a list with the valid modules and valid modules names.
    """
    validModules = findAllModules(path, dir)
    validModuleNames = []
    #guideFolder = (path+"/"+dir).partition("/Modules/")[2]
    guideFolder = findEnv("PYTHONPATH", "dpAutoRigSystem")+".Modules"
    for m in validModules:
        mod = __import__(guideFolder+"."+m, {}, {}, [m])
        reload(mod)
        validModuleNames.append(mod.CLASS_NAME)
    return(validModules, validModuleNames)


def findLastNumber(nameList, basename):
    """ Find the highest number in the name list.
        Return its highest number.
    """
    # work with rigged modules in the scene:
    existValue = 0
    numberList = []
    # list all transforms and find the existing value in them names:
    transformList = cmds.ls(selection=False, transforms=True)
    for transform in transformList:
        if basename in transform:
            endNumber = transform.partition(basename)[2]
            if "_" in endNumber and not ":" in endNumber:
                number = endNumber[:endNumber.find("_")]
                try:
                    if int(number) not in numberList:
                        numberList.append(int(number))
                except ValueError:
                    pass

    numberList.sort()
    numberList.reverse()

    if numberList:
        # get the greather valuer (first):
        existValue = numberList[0]

    # work with created guides in the scene:
    lastValue = 0
    for n in nameList:
        # verify if there the basename in the name:
        if n.find(basename) == 0:
            # get the number in the end of the basename:
            suffix = n.partition(basename)[2]
            # verify if the got suffix has numbers:
            if re.match("^[0-9]*$", suffix):
                # store this numbers as integers:
                numberElement = int(suffix)
                # verify if this got number is greather than the last number (value) in order to return them:
                if numberElement > lastValue:
                    lastValue = numberElement

    # analysis which value must be returned:
    if lastValue > existValue:
        finalValue = lastValue
    else:
        finalValue = existValue
    return finalValue


def findModuleLastNumber(className, typeName):
    """ Find the last used number of this type of module.
        Return its highest number.
    """
    # work with rigged modules in the scene:
    numberList = []
    guideTypeCount = 0
    # list all transforms and find the existing value in them names:
    transformList = cmds.ls(selection=False, transforms=True)
    for transform in transformList:
        if cmds.objExists(transform+"."+typeName):
            if cmds.getAttr(transform+"."+typeName) == className:
                numberList.append(className)
        # try check if there is a masterGrp and get its counter:
        if cmds.objExists(transform+".masterGrp") and cmds.getAttr(transform+".masterGrp") == 1:
            guideTypeCount = cmds.getAttr(transform+'.dp'+className+'Count')
    if(guideTypeCount > len(numberList)):
        return guideTypeCount
    else:
        return len(numberList)
    
    
def normalizeText(enteredText="", prefixMax=4):
    """ Analisys the enteredText to conform it in order to use in Application (Maya).
        Return the normalized text.
    """
    normalText = ""
    # analisys if it starts with number or has a whitespace or special character:
    if re.match("[0-9]", enteredText) or re.search("\s", enteredText[:len(enteredText)-1]) or re.search("\W", enteredText):
        return normalText
    # just add a underscore at the end for one character entered:
    #elif len(enteredText) == 1 and enteredText != " " and enteredText != "_":
    #    normalText = enteredText+"_"
    # edit this to have only a maximum of 'prefixMax' digits:
    else:
        if len(enteredText) < prefixMax:
            prefixMax = len(enteredText)
        for m in range(0, prefixMax):
            if enteredText[m] != " " and enteredText[m] != "_":
                normalText = enteredText[:m+1]
    return normalText


def useDefaultRenderLayer():
    """ Analisys if must use the Default Render Layer (masterLayer) checking the option in the UI.
        Set to use it if need.
    """
    # analisys to use the defaultRenderLayer:
    useDefaultRL = cmds.checkBox('defaultRenderLayerCB', query=True, value=True)
    if useDefaultRL:
        cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')


def zeroOut(transformList=[]):
    """ Create a group over the transform, parent the transform in it and set zero all transformations of the transform node.
        If don't have a transformList given, try to get the current selection.
        Return a list of names of the zeroOut groups.
    """
    zeroList = []
    if not transformList:
        transformList = cmds.ls(selection=True)
    if transformList:
        for transform in transformList:
            zero = cmds.duplicate(transform, name=transform+'_Zero')[0]
            zeroUserAttrList = cmds.listAttr(zero, userDefined=True)
            if zeroUserAttrList:
                for zUserAttr in zeroUserAttrList:
                    try:
                        cmds.deleteAttr(zero+"."+zUserAttr)
                    except:
                        pass
            allChildrenList = cmds.listRelatives(zero, allDescendents=True, children=True, fullPath=True)
            if allChildrenList:
                cmds.delete(allChildrenList)
            cmds.parent(transform, zero, absolute=True)
            zeroList.append(zero)
    return zeroList


def originedFrom(objName="", attrString=""):
    """ Add attribute as string and set is as attrName got.
    """
    if objName != "" and attrString != "":
        cmds.addAttr(objName, longName="originedFrom", dataType='string')
        cmds.setAttr(objName+".originedFrom", attrString, type='string')


def getOriginedFromDic():
    """ List all transforms in the scene, verify if there is an originedFrom string attribute and store it value in a dictionary.
        Return a dictionary with originedFrom string as keys and transform nodes as values of these keys.
    """
    originedFromDic = {}
    allTransformList = cmds.ls(selection=False, type="transform")
    if allTransformList:
        for transform in allTransformList:
            if cmds.objExists(transform+".originedFrom"):
                tempOriginedFrom = cmds.getAttr(transform+".originedFrom")
                if tempOriginedFrom:
                    if not ";" in tempOriginedFrom:
                        originedFromDic[tempOriginedFrom] = transform
                    else:
                        tempOriginedFromList = tempOriginedFrom.split(";")
                        for orignedFromString in tempOriginedFromList:
                            originedFromDic[orignedFromString] = transform
    return originedFromDic


def addHook(objName="", hookType="staticHook"):
    """ Add attribute as boolean and set it as True = 1.
    """
    if objName != "":
        cmds.addAttr(objName, longName=hookType, attributeType='bool')
        cmds.setAttr(objName+"."+hookType, 1)


def hook():
    """ Mount a dictionary with guide modules hierarchies.
        Return a dictionary with the father and children lists inside of each guide like:
        {guide{'guideModuleNamespace':"...", 'guideModuleName':"...", 'guideCustomName':"...", 'guideMirrorAxis':"...", 'guideMirrorName':"...", 'fatherGuide':"...", 'fatherNode':"...", 'fatherModule':"...", 'fatherCustomName':"...", 'fatherMirrorAxis':"...", 'fatherMirrorName':"...", 'fatherGuideLoc':"...", 'childrenList':[...]}}
    """
    hookDic = {}
    allList = cmds.ls(type='transform')
    for item in allList:
        if cmds.objExists(item+".guideBase") and cmds.getAttr(item+".guideBase") == 1:
            # module info:
            guideModuleNamespace = item[:item.find(":")]
            guideModuleName      = item[:item.find("__")]
            guideInstance        = item[item.rfind("__")+2:item.find(":")]
            guideCustomName      = cmds.getAttr(item+".customName")
            guideMirrorAxis      = cmds.getAttr(item+".mirrorAxis")
            tempAMirrorName      = cmds.getAttr(item+".mirrorName")
            guideMirrorName      = [tempAMirrorName[0]+"_" , tempAMirrorName[len(tempAMirrorName)-1:]+"_"]
            
            # get children:
            guideChildrenList = []
            childrenList = cmds.listRelatives(item, allDescendents=True, type='transform')
            if childrenList:
                for child in childrenList:
                    if cmds.objExists(child+".guideBase"):
                        if cmds.getAttr(child+".guideBase"):
                            if cmds.getAttr(child+".guideBase") == 1:
                                guideChildrenList.append(child)
                    if cmds.objExists(child+".hookNode"):
                        hookNode = cmds.getAttr(child+".hookNode")
            
            # get father:
            guideParentList = []
            fatherNodeList = []
            parentNode = ""
            parentList = cmds.listRelatives(item, parent=True, type='transform')
            if parentList:
                nextLoop = True
                while nextLoop:
                    if cmds.objExists(parentList[0]+".guideBase") and cmds.getAttr(parentList[0]+".guideBase") == 1:
                        guideParentList.append(parentList[0])
                        nextLoop = False
                    else:
                        if not fatherNodeList:
                            fatherNodeList.append(parentList[0])
                        parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
                        if parentList:
                            nextLoop = True
                        else:
                            nextLoop = False
                if guideParentList:
                    # father info:
                    guideParent      = guideParentList[0]
                    fatherModule     = guideParent[:guideParent.find("__")]
                    fatherInstance   = guideParent[guideParent.rfind("__")+2:guideParent.find(":")]
                    fatherCustomName = cmds.getAttr(guideParent+".customName")
                    fatherMirrorAxis = cmds.getAttr(guideParent+".mirrorAxis")
                    tempBMirrorName  = cmds.getAttr(guideParent+".mirrorName")
                    fatherMirrorName = [tempBMirrorName[0]+"_" , tempBMirrorName[len(tempBMirrorName)-1:]+"_"]
                    if fatherNodeList:
                        fatherGuideLoc = fatherNodeList[0][fatherNodeList[0].find("Guide_")+6:]
                    else:
                        guideParentChildrenList = cmds.listRelatives(guideParent, children=True, type='transform')
                        if guideParentChildrenList:
                            for guideParentChild in guideParentChildrenList:
                                if cmds.objExists(guideParentChild+'.nJoint'):
                                    if cmds.getAttr(guideParentChild+'.nJoint') == 1:
                                        if guideParent[:guideParent.rfind(":")] in guideParentChild:
                                            fatherNodeList = [guideParentChild]
                                            fatherGuideLoc = guideParentChild[guideParentChild.find("Guide_")+6:]
                
                # parentNode info:
                parentNode = cmds.listRelatives(item, parent=True, type='transform')[0]
            
            # mounting dictionary:
            if guideParentList and guideChildrenList:
                hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":guideParent, "fatherNode":fatherNodeList[0], "fatherModule":fatherModule, "fatherInstance":fatherInstance, "fatherCustomName":fatherCustomName, "fatherMirrorAxis":fatherMirrorAxis, "fatherMirrorName":fatherMirrorName, "fatherGuideLoc":fatherGuideLoc, "parentNode":parentNode, "childrenList":guideChildrenList}
            elif guideParentList:
                hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":guideParent, "fatherNode":fatherNodeList[0], "fatherModule":fatherModule, "fatherInstance":fatherInstance, "fatherCustomName":fatherCustomName, "fatherMirrorAxis":fatherMirrorAxis, "fatherMirrorName":fatherMirrorName, "fatherGuideLoc":fatherGuideLoc, "parentNode":parentNode, "childrenList":[]}
            elif guideChildrenList:
                hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":"", "fatherNode":"", "fatherModule":"", "fatherInstance":"", "fatherCustomName":"", "fatherMirrorAxis":"", "fatherMirrorName":"", "fatherGuideLoc":"", "parentNode":parentNode, "childrenList":guideChildrenList}
            else:
                hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":"", "fatherNode":"", "fatherModule":"", "fatherInstance":"", "fatherCustomName":"", "fatherMirrorAxis":"", "fatherMirrorName":"", "fatherGuideLoc":"", "parentNode":parentNode, "childrenList":[]}
    return hookDic


def clearNodeGrp(nodeGrpName='dpAR_GuideMirror_Grp', attrFind='guideBaseMirror', unparent=False):
    """ Check if there is any node with the attribute attrFind in the nodeGrpName and then unparent its children and delete it.
    """
    if cmds.objExists(nodeGrpName):
        foundChildrenList = []
        childrenList = cmds.listRelatives(nodeGrpName, children=True, type="transform")
        if childrenList:
            for child in childrenList:
                if cmds.objExists(child+"."+attrFind) and cmds.getAttr(child+"."+attrFind) == 1:
                    foundChildrenList.append(child)
        if len(foundChildrenList) != 0:
            if unparent:
                for item in foundChildrenList:
                    cmds.parent(item, world=True)
                cmds.delete(nodeGrpName)
        else:
            cmds.delete(nodeGrpName)


def getGuideChildrenList(nodeName):
    """ This function verify if there are guide children of the passed nodeName.
        It will return the guideChildrenList if it exists.
    """
    guideChildrenList = []
    if cmds.objExists(nodeName):
        childrenList = cmds.listRelatives(nodeName, allDescendents=True, type='transform')
        if childrenList:
            for child in childrenList:
                if cmds.objExists(child+".guideBase") and cmds.getAttr(child+".guideBase") == 1:
                    guideChildrenList.append(child)
    return guideChildrenList


def mirroredGuideFather(nodeName):
    """ This function verify if there is a mirrored guide as a father of the passed nodeName.
        Returns the mirrored guide father name if true.
    """
    parentList = cmds.listRelatives(nodeName, parent=True, type='transform')
    if parentList:
        nextLoop = True
        while nextLoop:
            if cmds.objExists(parentList[0]+".guideBase") and cmds.getAttr(parentList[0]+".guideBase") == 1 and cmds.getAttr(parentList[0]+".mirrorEnable") == 1 and cmds.getAttr(parentList[0]+".mirrorAxis") != "off":
                return parentList[0]
                nextLoop = False
            else:
                parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
                if parentList:
                    nextLoop = True
                else:
                    nextLoop = False


def getParentsList(nodeName):
    """ Get all parents.
        Return a list with all parents if they exists.
    """
    # get father:
    allParentsList = []
    parentList = cmds.listRelatives(nodeName, parent=True, type='transform')
    if parentList:
        nextLoop = True
        while nextLoop:
            allParentsList.append(parentList[0])
            parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
            if not parentList:
                nextLoop = False
    return allParentsList


def getModulesToBeRigged(instanceList):
    """ Get all valid loaded modules to be rigged (They are valid instances with namespaces in the scene, then they are not deleted).
        Return a list of modules to be rigged.
    """
    modulesToBeRiggedList = []
    allNamespaceList = cmds.namespaceInfo(listNamespace=True)
    for guideModule in instanceList:
        # verify integrity of the guideModule:
        if guideModule.verifyGuideModuleIntegrity():
            guideNamespaceName = guideModule.guideNamespace
            if guideNamespaceName in allNamespaceList:
                userGuideName = guideModule.userGuideName
                if not cmds.objExists(userGuideName+'_Grp'):
                    modulesToBeRiggedList.append(guideModule)
    return modulesToBeRiggedList


def getCtrlRadius(nodeName):
    """ Calculate and return the final radius to be used as a size of controls.
    """
    radius = float(cmds.getAttr(nodeName+".translateX"))
    parentList = getParentsList(nodeName)
    if (parentList):
        for parent in parentList:
            radius *= cmds.getAttr(parent+'.scaleX')
    return radius


def zeroOutJoints(jntList=None):
    """ Duplicate the joints, parent as zeroOut.
        Returns the father joints (zeroOuted).
        Deprecated = using zeroOut function insted.
    """
    resultList = []
    zeroOutJntSuffix = "_Jzt"
    if jntList:
        for jnt in jntList:
            if cmds.objExists(jnt):
                jxtName = jnt.replace("_Jnt", "").replace("_Jxt", "")
                if not zeroOutJntSuffix in jxtName:
                    jxtName += zeroOutJntSuffix
                dup = cmds.duplicate(jnt, name=jxtName)[0]
                deleteChildren(dup)
                clearDpArAttr([dup])
                cmds.parent(jnt, dup)
                resultList.append(dup)
    return resultList


def clearDpArAttr(itemList):
    """ Delete all dpAR (dpAutoRigSystem) attributes in this joint
    """
    dpArAttrList = ['dpAR_joint']
    if itemList:
        for item in itemList:
            for dpArAttr in dpArAttrList:
                if cmds.objExists(item+"."+dpArAttr):
                    cmds.deleteAttr(item+"."+dpArAttr)


def deleteChildren(item):
    """ Delete all child of the item node passed as argument.
    """
    if(cmds.objExists(item)):
        childrenList = cmds.listRelatives(item, children=True, fullPath=True)
        if(childrenList):
            for child in childrenList:
                cmds.delete(child)


def setJointLabel(jointName, sideNumber, typeNumber, labelString):
    """ Set joint labelling in order to help Maya calculate the skinning mirror correctly.
        side:
            0 = Center
            1 = Left
            2 = Right
        type:
            18 = Other
    """
    cmds.setAttr(jointName+".side", sideNumber)
    cmds.setAttr(jointName+".type", typeNumber)
    if typeNumber == 18: #other
        cmds.setAttr(jointName+".otherType", labelString, type="string")


def extractSuffix(nodeName):
    """ Remove suffix from a node name and return the base name.
    """
    endSuffixList = ["_Mesh", "_mesh", "_MESH", "_msh", "_MSH", "_Geo", "_geo", "_GEO", "_Tgt", "_tgt", "_TGT", "_Ctrl", "_ctrl", "_CTRL", "_Grp", "_grp", "_GRP"]
    for endSuffix in endSuffixList:
        if nodeName.endswith(endSuffix):
            baseName = nodeName[:nodeName.rfind(endSuffix)]
            return baseName
    return nodeName


def filterName(name, itemList, separator):
    """ Filter list with the name or a list of name as a string separated by the separator (usually a space).
        Returns the filtered list.
    """
    filteredList = []
    multiFilterList = [name]
    if separator in name:
        multiFilterList = list(name.split(separator))
    for filterName in multiFilterList:
        if filterName:
            for item in itemList:
                if str(filterName) in item:
                    if not item in filteredList:
                        filteredList.append(item)
    return filteredList
    
    
def checkRawURLForUpdate(DPAR_VERSION, DPAR_RAWURL, *args):
    """ Check for update using raw url.
        Compares the remote version from GitHub to the current version.
        
        Returns a list with CheckedNumber and RemoteVersion or None.
        
        CheckedNumber:
                0 - the current version is up to date
                1 - there's a new version
                2 - remote file not found using given raw url
                3 - internet connection fail (probably)
                4 - error
                
        if we have an update to do:
            return [CheckedNumber, RemoteVersion, RemoteLog]
        if not or ok:
            return [CheckedNumber, None]
    """
    try:
        gotRemoteFile = False
        
        # getting dpAutoRig.py file from GitHub website using the Raw URL:
        remoteSource = urllib.urlopen(DPAR_RAWURL)
        remoteContents = remoteSource.readlines()
        
        # find the line with the version and compare them:
        for line in remoteContents:
            if "DPAR_VERSION = " in line:
                gotRemoteFile = True
                remoteVersion = line[16:-2] #these magic numbers filter only the version XX.YY.ZZ
                if remoteVersion == DPAR_VERSION:
                    # 0 - the current version is up to date
                    return [0, None, None]
                else:
                    # 1 - there's a new version
                    for extraLine in remoteContents:
                        if "DPAR_UPDATELOG = " in extraLine:
                            remoteLog = extraLine[18:-2] #these magic numbers filter only the log string sentence
                            return [1, remoteVersion, remoteLog]
                    return [1, remoteVersion, None]
        if not gotRemoteFile:
            # 2 - remote file not found using given raw url
            return [2, None, None]
    except:
        # 3 - internet connection fail (probably)
        return [3, None, None]
    # 4 - error
    return [4, None, None]


def visitWebSite(website, *args):
    """ Start browser with the given website address.
    """
    #webSiteString = "start "+website
    #os.popen(webSiteString)
    webbrowser.open(website, new=2)
    
    
def checkLoadedPlugin(pluginName, exceptName=None, message="Not loaded plugin", *args):
    """ Check if plugin is loaded and try to load it.
        Returns True if ok (loaded)
        Returns False if not found or not loaded.
    """
    loadedPlugin = True
    if not (cmds.pluginInfo(pluginName, query=True, loaded=True)):
        loadedPlugin = False
        try:
            # Maya 2012
            cmds.loadPlugin(pluginName+".mll")
            loadedPlugin = True
        except:
            if exceptName:
                try:
                    # Maya 2013 or earlier
                    cmds.loadPlugin(exceptName+".mll")
                    loadedPlugin = True
                except:
                    pass
    if not loadedPlugin:
        print message, pluginName
    return loadedPlugin
    
    
def twistBoneMatrix(nodeA, nodeB, twistBoneName, twistBoneMD=None, axis='Z', inverse=True, *args):
    """ Create matrix nodes and quaternion to extract rotate.
        nodeA = father transform node
        nodeB = child transform node
        Returns the final multiplyDivide node created or given.
        Reference:
        https://bindpose.com/maya-matrix-nodes-part-2-node-based-matrix-twist-calculator/
    """
    twistBoneMM = cmds.createNode("multMatrix", name=twistBoneName+"_ExtractAngle_MM")
    twistBoneDM = cmds.createNode("decomposeMatrix", name=twistBoneName+"_ExtractAngle_DM")
    twistBoneQtE = cmds.createNode("quatToEuler", name=twistBoneName+"_ExtractAngle_QtE")
    cmds.connectAttr(nodeB+".worldMatrix[0]", twistBoneMM+".matrixIn[0]", force=True)
    if inverse:
        cmds.connectAttr(nodeA+".worldInverseMatrix[0]", twistBoneMM+".matrixIn[1]", force=True)
    else:
        cmds.connectAttr(nodeA+".worldMatrix[0]", twistBoneMM+".matrixIn[1]", force=True)
    cmds.connectAttr(twistBoneMM+".matrixSum", twistBoneDM+".inputMatrix", force=True)
    cmds.connectAttr(twistBoneDM+".outputQuat.outputQuat"+axis, twistBoneQtE+".inputQuat.inputQuat"+axis, force=True)
    cmds.connectAttr(twistBoneDM+".outputQuat.outputQuatW", twistBoneQtE+".inputQuat.inputQuatW", force=True)
    if twistBoneMD:
        cmds.connectAttr(twistBoneQtE+".outputRotate.outputRotate"+axis, twistBoneMD+".input2"+axis, force=True)
    else:
        twistBoneMD = cmds.createNode("multiplyDivide", name=twistBoneName+"_MD")
        cmds.connectAttr(twistBoneQtE+".outputRotate.outputRotate"+axis, twistBoneMD+".input2"+axis, force=True)
    return twistBoneMD
    


#Profiler decorator
DPAR_PROFILE_MODE = False
def profiler(func):
    def runProfile(*args, **kwargs):
        if DPAR_PROFILE_MODE:
            pProf = cProfile.Profile()
            try:
                pProf.enable()
                pResult = func(*args, **kwargs)
                pProf.disable()
                return pResult
            finally:
                pProf.print_stats()
        else:
            pResult = func(*args, **kwargs)
            return pResult
    return runProfile

'''
Open Maya Utils Functions
'''

def extract_world_scale_from_matrix(obj):
    world_matrix = cmds.getAttr(obj + ".worldMatrix")
    mMat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(world_matrix, mMat)
    mTransform = om.MTransformationMatrix(mMat)
    scale_util = om.MScriptUtil()
    scale_util.createFromDouble(0.0, 0.0, 0.0)
    ptr = scale_util.asDoublePtr()
    mTransform.getScale(ptr, om.MSpace.kWorld)

    x_scale = om.MScriptUtil.getDoubleArrayItem(ptr, 0)
    y_scale = om.MScriptUtil.getDoubleArrayItem(ptr, 1)
    z_scale = om.MScriptUtil.getDoubleArrayItem(ptr, 2)

    return [x_scale, y_scale, z_scale]
