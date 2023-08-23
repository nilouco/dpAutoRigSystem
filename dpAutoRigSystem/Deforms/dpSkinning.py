# importing libraries:
from maya import cmds
from ..Modules.Library import dpUtils

DP_SKINNING_VERSION = 1.0


class Skinning(object):
    def __init__(self, dpUIinst, *args, **kwargs):
        """ Initialize the class.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        

    def validateGeoList(self, geoList, mode=None, *args):
        """ Check if the geometry list from UI is good to be skinned, because we can get issue if the display long name is not used.
        """
        if geoList:
            for i, item in enumerate(geoList):
                if item in geoList[:i]:
                    self.dpUIinst.info('i038_canceled', 'e003_moreThanOneGeo', item, 'center', 205, 270)
                    return False
                elif not cmds.objExists(item):
                    self.dpUIinst.info('i038_canceled', 'i061_notExists', item, 'center', 205, 270)
                    return False
                elif not mode:
                    try:
                        inputDeformerList = cmds.findDeformers(item)
                        if inputDeformerList:
                            for deformerNode in inputDeformerList:
                                if cmds.objectType(deformerNode) == "skinCluster":
                                    self.dpUIinst.info('i038_canceled', 'i285_alreadySkinned', item, 'center', 205, 270)
                                    return False
                    except:
                        pass
        return True
    

    def skinFromUI(self, mode=None, *args):
        """ Skin the geometries using the joints, reading from UI the selected items of the textScrollLists or getting all items if nothing selected.
        """
        # log window
        logWin = cmds.checkBox(self.dpUIinst.allUIs["displaySkinLogWin"], query=True, value=True)

        # get joints to be skinned:
        uiJointSkinList = cmds.textScrollList(self.dpUIinst.allUIs["jntTextScrollLayout"], query=True, selectItem=True)
        if not uiJointSkinList:
            uiJointSkinList = cmds.textScrollList(self.dpUIinst.allUIs["jntTextScrollLayout"], query=True, allItems=True)
        
        # check if all items in jointSkinList exists, then if not, show dialog box to skinWithoutNotExisting or Cancel
        jointSkinList, jointNotExistingList = [], []
        if uiJointSkinList:
            for item in uiJointSkinList:
                if cmds.objExists(item):
                    jointSkinList.append(item)
                else:
                    jointNotExistingList.append(item)
        if jointNotExistingList:
            notExistingJointMessage = self.dpUIinst.lang['i069_notSkinJoint'] +"\n\n"+ ", ".join(str(jntNotExitst) for jntNotExitst in jointNotExistingList) +"\n\n"+ self.dpUIinst.lang['i070_continueSkin']
            btYes = self.dpUIinst.lang['i071_yes']
            btNo = self.dpUIinst.lang['i072_no']
            confirmSkinning = cmds.confirmDialog(title='Confirm Skinning', message=notExistingJointMessage, button=[btYes,btNo], defaultButton=btYes, cancelButton=btNo, dismissString=btNo)
            if confirmSkinning == btNo:
                jointSkinList = None
        
        # get geometries to be skinned:
        geomSkinList = cmds.textScrollList(self.dpUIinst.allUIs["modelsTextScrollLayout"], query=True, selectItem=True)
        if not geomSkinList:
            geomSkinList = cmds.textScrollList(self.dpUIinst.allUIs["modelsTextScrollLayout"], query=True, allItems=True)
        
        # check if we have repeated listed geometries in case of the user choose to not display long names:
        if self.validateGeoList(geomSkinList, mode):
            if jointSkinList and geomSkinList:
                for geomSkin in geomSkinList:
                    if (mode == "Add"):
                        cmds.skinCluster(geomSkin, edit=True, addInfluence=jointSkinList, toSelectedBones=True, lockWeights=True, weight=0.0)
                    elif (mode == "Remove"):
                        cmds.skinCluster(geomSkin, edit=True, removeInfluence=jointSkinList, toSelectedBones=True)
                    else: # None = create a new skinCluster node
                        baseName = dpUtils.extractSuffix(geomSkin)
                        skinClusterName = baseName+"_SC"
                        if "|" in skinClusterName:
                            skinClusterName = skinClusterName[skinClusterName.rfind("|")+1:]
                        cmds.skinCluster(jointSkinList, geomSkin, toSelectedBones=True, dropoffRate=4.0, maximumInfluences=3, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False, name=skinClusterName)
                print(self.dpUIinst.lang['i077_skinned'] + ', '.join(geomSkinList))
                if logWin:
                    self.dpUIinst.info('i028_skinButton', 'i077_skinned', '\n'.join(geomSkinList), 'center', 205, 270)
                cmds.select(geomSkinList)
        else:
            print(self.dpUIinst.lang['i029_skinNothing'])
            if logWin:
                self.dpUIinst.info('i028_skinButton', 'i029_skinNothing', ' ', 'center', 205, 270)