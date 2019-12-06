# importing libraries:
import maya.cmds as cmds

# global variables to this module:    
CLASS_NAME = "IkFkSnap"
TITLE = "m065_ikFkSnap"
DESCRIPTION = "m066_ikFkSnapDesc"
ICON = "/Icons/dp_ikFkSnap.png"

DPIKFK_VERSION = "1.2"

class IkFkSnap():
    def __init__(self, dpUIinst, langDic, langName, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        # importing Library
        loadedPlugin = False
        try:
            #from sstk.maya.animation import sqIkFkTools
            self.sqIkFkTools = __import__("sstk.maya.animation.sqIkFkTools", {}, {}, ["sqIkFkTools"])
            loadedPlugin = True
        except:
            try:
                self.sqIkFkTools = __import__("dpAutoRigSystem.Modules.Library.sqIkFkTools", {}, {}, ["sqIkFkTools"])
                loadedPlugin = True
            except:
                print "Error loading sqIkFkTools.",
        if loadedPlugin:
            # call main function
            self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Call UI.
        """
        self.dpIkFkSnapUI()
    
    
    def IkToFkSnap(self, *args):
        """ Change selected chaine from Ik to Fk snapping.
        """
        self.sqIkFkTools.switchToFk()
        
        
    def FkToIkSnap(self, *args):
        """ Change selected chaine from Fk to Ik snapping.
        """
        self.sqIkFkTools.switchToIk()
    
    
    def dpIkFkSnapUI(self, *args):
        """ Show a little window with buttons to change from Ik to Fk or from Fk to Ik snapping.
        """
        # creating ikFkSnap Window:
        if cmds.window('dpIkFkSnapWindow', query=True, exists=True):
            cmds.deleteUI('dpIkFkSnapWindow', window=True)
        ikFkSnap_winWidth  = 205
        ikFkSnap_winHeight = 50
        dpIkFkSnapWin = cmds.window('dpIkFkSnapWindow', title='IkFkSnap '+DPIKFK_VERSION, iconName='dpIkFkSnap', widthHeight=(ikFkSnap_winWidth, ikFkSnap_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        ikFkSnapLayout = cmds.columnLayout('ikFkSnapLayout', adjustableColumn=True, parent=dpIkFkSnapWin)
        # creating buttons:
        cmds.button('ikToFkSnap_BT', label="Ik --> Fk", backgroundColor=(0.8, 0.8, 1.0), command=self.IkToFkSnap, parent=ikFkSnapLayout)
        cmds.button('fkToIkSnap_BT', label="Fk --> Ik", backgroundColor=(1.0, 0.8, 0.8), command=self.FkToIkSnap, parent=ikFkSnapLayout)
        # call colorIndex Window:
        cmds.showWindow(dpIkFkSnapWin)