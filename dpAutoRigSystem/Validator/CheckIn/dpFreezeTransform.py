# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from importlib import reload
reload(dpBaseValidatorClass)

# global variables to this module:
CLASS_NAME = 'FreezeTransform'
TITLE = 'v015_allFreeze'
DESCRIPTION = 'v016_allFreezeDesc'
ICON = '/Icons/dp_validatorFt.png'

dpFreezeTransform_Version = 1.0


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

        def objFreezed(obj, attrList, compValue):
            for attr in attrList:
                if cmds.getAttr(obj+'.'+attr) != compValue:
                    return False
            return True

        def unlockAttributes(obj, attrList):
            for attr in attrList:
                if animCurvesList:
                    if obj+'_'+attr in animCurvesList:
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
            allObjectList = filter(lambda obj: cmds.objectType(obj) == 'transform', objList)
        if len(allObjectList) == 0:
            allObjectList = cmds.ls(selection=False, cameras=False, type='transform', long=True)
        # analisys transformations
        if len(allObjectList) > 0:
            animCurvesList = cmds.ls(type='animCurve')
            zeroAttrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
            oneAttrList = ['scaleX', 'scaleY', 'scaleZ']
            for idx, obj in enumerate(allObjectList):
                if cmds.objExists(obj):
                    # run for translates and rotates
                    translateAndRotateFreezed = objFreezed(obj, zeroAttrList, 0)
                    # run for scales
                    scaleFreezed = objFreezed(obj, oneAttrList, 1)
                self.checkedObjList.append(obj)
                if translateAndRotateFreezed and scaleFreezed:
                    self.foundIssueList.append(False)
                    self.resultOkList.append(True)
                else:
                    self.foundIssueList.append(True)
                    self.resultOkList.append(False)
                    self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v018_foundTransform']+obj)
                    toFixList.append((obj, idx))
            if self.verifyMode == False and len(toFixList) > 0:
                
                for obj in toFixList:
                    unlocked = unlockAttributes(obj[0], zeroAttrList)
                    unlocked = unlockAttributes(obj[0], oneAttrList)

                    if unlocked:
                        try:
                            cmds.makeIdentity(obj[0], apply=True, translate=True, rotate=True, scale=True)
                            if objFreezed(obj[0], zeroAttrList, 0) and objFreezed(obj[0], oneAttrList, 1):
                                self.foundIssueList[obj[1]] = False
                                self.resultOkList[obj[1]] = True
                                self.messageList.append(self.dpUIinst.langDic[self.dpUIinst.langName]['v019_freezedTransform']+obj[0])
                            else:
                                raise Exception('Freeze Failed')
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
