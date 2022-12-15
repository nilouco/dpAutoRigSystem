# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:
CLASS_NAME = 'FreezeTransform'
TITLE = 'v015_freezeTransform'
DESCRIPTION = 'v016_freezeTranformDesc'
ICON = '/Icons/dp_freezeTransform.png'

dpFreezeTransform_Version = 1.4


class FreezeTransform(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs['CLASS_NAME'] = CLASS_NAME
        kwargs['TITLE'] = TITLE
        kwargs['DESCRIPTION'] = DESCRIPTION
        kwargs['ICON'] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)

    def runValidator(self, verifyMode=True, objList=None, *args):
        ''' Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        '''
        # starting
        self.verifyMode = verifyMode
        self.startValidation()

        # ---
        # --- validator code --- beginning

        def checkFrozenObject(obj, attrList, compValue):
            for attr in attrList:
                if cmds.getAttr(obj+'.'+attr) != compValue:
                    return False
            return True

        def unlockAttributes(obj, attrList):
            for attr in attrList:
                if self.animCurvesList:
                    if obj+'_'+attr in self.animCurvesList:
                        return False
                    else:
                        cmds.setAttr(obj+'.'+attr, lock=False)
                else:
                    cmds.setAttr(obj+'.'+attr, lock=False)
            return True

        def canNotFreezeMsg(obj):
            self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v017_freezeError'] + obj+'.')

        allObjectList = []
        toFixList = []
        if objList:
            allObjectList = list(filter(lambda obj: cmds.objectType(obj) == 'transform', objList))
        if len(allObjectList) == 0:
            allObjectList = cmds.ls(selection=False, type='transform', long=True)
        # analisys transformations
        if len(allObjectList) > 0:
            progressAmount = 0
            maxProcess = len(allObjectList)
            self.animCurvesList = cmds.ls(type='animCurve')
            zeroAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
            oneAttrList = ['scaleX', 'scaleY', 'scaleZ']
            camerasList = ['|persp', '|top', '|side', '|front', '|bottom', '|back', '|left']
            allValidObjs = list(filter(lambda obj: obj not in camerasList, allObjectList))
            for idx, obj in enumerate(allValidObjs):
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.langDic[self.dpUIinst.langName][self.title]+': '+repr(progressAmount)))
                if cmds.objExists(obj):
                    # run for translates and rotates
                    frozenTR = checkFrozenObject(obj, zeroAttrList, 0)
                    # run for scales
                    frozenS = checkFrozenObject(obj, oneAttrList, 1)
                    self.checkedObjList.append(obj)
                    if frozenTR and frozenS:
                        self.foundIssueList.append(False)
                        self.resultOkList.append(True)
                    else:
                        self.foundIssueList.append(True)
                        self.resultOkList.append(False)
                        self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v018_foundTransform']+obj)
                        toFixList.append((obj, idx))
            if not self.verifyMode and len(toFixList) > 0: #one item to fix
                for obj in toFixList:
                    if unlockAttributes(obj[0], zeroAttrList) and unlockAttributes(obj[0], oneAttrList):
                        try:
                            cmds.makeIdentity(obj[0], apply=True, translate=True, rotate=True, scale=True)
                            if checkFrozenObject(obj[0], zeroAttrList, 0) and checkFrozenObject(obj[0], oneAttrList, 1):
                                self.foundIssueList[obj[1]] = False
                                self.resultOkList[obj[1]] = True
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v019_frozenTransform']+obj[0])
                            else:
                                raise Exception('Freeze Tranform Failed')
                        except:
                            canNotFreezeMsg(obj[0])
                    else:
                        canNotFreezeMsg(obj[0])

        # --- validator code --- end
        # ---

        # finishing
        self.finishValidation()
        return self.dataLogDic

    def startValidation(self, *args):
        ''' Procedures to start the validation cleaning old data.
        '''
        dpBaseValidatorClass.ValidatorStartClass.cleanUpToStart(self)

    def finishValidation(self, *args):
        ''' Call main base methods to finish the validation of this class.
        '''
        dpBaseValidatorClass.ValidatorStartClass.updateButtonColors(self)
        dpBaseValidatorClass.ValidatorStartClass.reportLog(self)
        dpBaseValidatorClass.ValidatorStartClass.endProgressBar(self)
