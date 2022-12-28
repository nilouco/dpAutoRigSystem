# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from ..Modules.Library import dpUtils


DPPUBLISHER_VERSION = 1.0


class Publisher(object):
    def __init__(self, dpUIinst, ui=True, verbose=True):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = dpUIinst.langDic
        self.langName = dpUIinst.langName
        self.ui = ui
        self.verbose = verbose
        self.publisherName = self.langDic[self.langName]['m046_publisher']


    def mainUI(self, *args):
        """ This is the main method to load the Publisher UI.
        """
        
        #WIP
        self.ui = True
        self.closeUI()
        

        # window
        publisher_winWidth  = 380
        publisher_winHeight = 300
        cmds.window('dpPublisherWindow', title=self.publisherName+" "+str(DPPUBLISHER_VERSION), widthHeight=(publisher_winWidth, publisher_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpPublisherWindow')
        # create UI layout and elements:
        publisherLayout = cmds.columnLayout('publisherLayout', adjustableColumn=True, columnOffset=("both", 10))
        publisherLayoutA = cmds.rowColumnLayout('publisherLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent=publisherLayout)
        self.publishBT = cmds.button('publishBT', label=self.langDic[self.langName]['i216_publish'], command=partial(self.runPublishing, self.ui, self.verbose), backgroundColor=(0.75, 0.75, 0.75), parent=publisherLayoutA)
        
        self.createTF = cmds.textField('createTF', editable=True, parent=publisherLayoutA)
        cmds.text("infoTxt", label=self.langDic[self.langName]['i217_publishDesc'], align="left", height=30, font='boldLabelFont', parent=publisherLayout)
        cmds.separator(style='none', height=10, width=100, parent=publisherLayout)
        
        # comments
        # file path
        # file name
        # version
        # ignore validation checkBox
        # diagnose?
        # verbose = see log (none, simple or complete)
        # fromUI ?




    def closeUI(self, *args):
        """ Delete existing Publisher window if it exists.
        """
        if cmds.window('dpPublisherWindow', query=True, exists=True):
            cmds.deleteUI('dpPublisherWindow', window=True)
    

    def runPublishing(self, fromUI, verbose, *args):
        """ Start the publishing process running the checked validators.
        """
        foundIssue = False
        toCheckValidatorList = [self.dpUIinst.checkInInstanceList, self.dpUIinst.checkOutInstanceList, self.dpUIinst.checkAddOnsInstanceList]
        for validatorList in toCheckValidatorList:
            if validatorList:
                validationResultDataList = self.dpUIinst.runSelectedValidators(validatorList, True, False, True)
                if validationResultDataList[1]: #found issue
                    stoppedMessage = self.langDic[self.langName]['v020_publishStopped']+" "+validatorList[validationResultDataList[2]].guideModuleName
                    mel.eval('warning \"'+stoppedMessage+'\";')
                    cmds.progressWindow(endProgress=True)
                    foundIssue = True
                    break
        if not foundIssue:
            print ("good, merci")
            



        # TODO result window = log here


        self.closeUI()
