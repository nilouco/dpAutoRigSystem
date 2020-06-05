###########################################################
#
#   jcRibbon.py
#
#   author: James do Carmo Correa
#   contact: james.2js@gmail.com
#   portfolio: james2js.blogspot.com
#   
#   This module will create a good ribbon system to be implemented by dpLimb.py
#
#   Thanks James :)
#
###########################################################


# importing libraries:
import maya.cmds as cmds
import dpUtils as utils
import dpControls


class RibbonClass:

    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ctrlRadius, curveDegree, *args):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrlRadius = ctrlRadius
        self.curveDegree = curveDegree
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        
        
    def addRibbonToLimb(self, prefix='', myName=None, oriLoc=None, iniJnt=None, skipAxis='y', num=5, mirror=True, side=0, arm=True, worldRef="worldRef", jointLabelAdd=0, *args):
        """ Create the Ribbon system to be added in the Limb module.
            Returns a dictionary with all nodes needed to be integrated.
        """
        if not oriLoc:
            oriLoc = cmds.ls(sl=True, l=True)[0]
        if not iniJnt:
            iniJnt = cmds.ls(sl=True)[1]
        
        if not prefix == '':
            if not prefix.endswith('_'):
                prefix+='_'
        skipa = ['x', 'y', 'z']
        skipa.remove(skipAxis)
        lista = []
        lista.append(iniJnt)
        lista.append(cmds.listRelatives(lista[0], c=True)[0])
        lista.append(cmds.listRelatives(lista[1], c=True)[0])
        auxLoc = cmds.duplicate(oriLoc, rr=True)
        midLoc = cmds.duplicate(oriLoc, rr=True)
        
        cmds.delete(cmds.parentConstraint(lista[1], auxLoc, mo=False, w=1))
        cmds.delete(cmds.aimConstraint(lista[2], auxLoc, mo=False, weight=2, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0)))
        cmds.delete(cmds.orientConstraint(oriLoc, auxLoc, mo=False, skip=skipa, weight=1))

        cmds.delete(cmds.parentConstraint(lista[1], midLoc, mo=False, w=1))

        cmds.delete(cmds.orientConstraint(oriLoc, midLoc, mo=False, skip=skipa, weight=1))
        
        upctrlList = self.createBendCtrl(prefix+'Up_'+myName+'_Off_Ctrl', r=self.ctrlRadius)
        upctrl = upctrlList[0]
        upctrlCtrl = upctrlList[1]
        downctrlList = self.createBendCtrl(prefix+'Down_'+myName+'_Off_Ctrl', r=self.ctrlRadius)
        downctrl = downctrlList[0]
        downctrlCtrl = downctrlList[1]
        elbowctrlList = self.createElbowCtrl(prefix+myName+'_Off_Ctrl', armStyle=arm)
        elbowctrl = elbowctrlList[0]
        elbowctrlCtrl = elbowctrlList[1]
        elbowctrlZero = elbowctrlList[2]
        
        cmds.addAttr(upctrlCtrl, longName="autoTwistBone", attributeType='float', min=0, defaultValue=0.75, max=1, keyable=True)
        cmds.addAttr(upctrlCtrl, longName="baseTwist", attributeType='float', keyable=True)
        cmds.addAttr(upctrlCtrl, longName="autoRotate", attributeType='float', min=0, defaultValue=0.5, max=1, keyable=True)
        cmds.addAttr(upctrlCtrl, longName="invert", attributeType='bool', defaultValue=0, keyable=False)
        cmds.addAttr(downctrlCtrl, longName="autoRotate", attributeType='float', min=0, defaultValue=0.5, max=1, keyable=True)
        cmds.addAttr(downctrlCtrl, longName="invert", attributeType='bool', defaultValue=0, keyable=False)
        
        if arm:
            upLimb = self.createRibbon(name=prefix+'Up_'+myName, axis=(0, 0, -1), horizontal=True, numJoints=num, v=False, guides=[lista[0], lista[1]], s=side, upCtrl=upctrlCtrl, worldRef=worldRef, jointLabelAdd=jointLabelAdd, jointLabelName='Up_'+myName)
            downLimb = self.createRibbon(name=prefix+'Down_'+myName, axis=(0, 0, -1), horizontal=True, numJoints=num, v=False, guides=[lista[1], lista[2]], s=side, firstLimb=False, worldRef=worldRef, jointLabelAdd=jointLabelAdd, jointLabelName='Down_'+myName)
            cmds.connectAttr(upctrlCtrl+".scaleX", upLimb['extraCtrlGrp']+".scaleX", force=True)
            cmds.connectAttr(upctrlCtrl+".scaleY", upLimb['extraCtrlGrp']+".scaleY", force=True)
            cmds.connectAttr(downctrlCtrl+".scaleX", downLimb['extraCtrlGrp']+".scaleX", force=True)
            cmds.connectAttr(downctrlCtrl+".scaleY", downLimb['extraCtrlGrp']+".scaleY", force=True)
        else:
            upLimb = self.createRibbon(name=prefix+'Up_'+myName, axis=(0, 0, 1), horizontal=True, numJoints=num, v=False, guides=[lista[0], lista[1]], s=side, upCtrl=upctrlCtrl, worldRef=worldRef, jointLabelAdd=jointLabelAdd, jointLabelName='Up_'+myName)
            downLimb = self.createRibbon(name=prefix+'Down_'+myName, axis=(0, 0, 1), horizontal=True, numJoints=num, v=False, guides=[lista[1], lista[2]], s=side, worldRef=worldRef, jointLabelAdd=jointLabelAdd, jointLabelName='Down_'+myName)
            cmds.connectAttr(upctrlCtrl+".scaleX", upLimb['extraCtrlGrp']+".scaleY", force=True)
            cmds.connectAttr(upctrlCtrl+".scaleY", upLimb['extraCtrlGrp']+".scaleX", force=True)
            cmds.connectAttr(downctrlCtrl+".scaleX", downLimb['extraCtrlGrp']+".scaleY", force=True)
            cmds.connectAttr(downctrlCtrl+".scaleY", downLimb['extraCtrlGrp']+".scaleX", force=True)
        cmds.connectAttr(upctrlCtrl+".scaleZ", upLimb['extraCtrlGrp']+".scaleZ", force=True)
        cmds.connectAttr(downctrlCtrl+".scaleZ", downLimb['extraCtrlGrp']+".scaleZ", force=True)
        
        cmds.delete(cmds.parentConstraint(oriLoc, upctrl, mo=False, w=1))
        cmds.delete(cmds.pointConstraint(upLimb['middleCtrl'], upctrl, mo=False, w=1))
        
        cmds.delete(cmds.parentConstraint(auxLoc, downctrl, mo=False, w=1))
        cmds.delete(cmds.pointConstraint(downLimb['middleCtrl'], downctrl, mo=False, w=1))
        
        cmds.delete(cmds.parentConstraint(midLoc, elbowctrl, mo=False, w=1))
        orientConst = cmds.orientConstraint(lista[0], lista[1], elbowctrl, mo=False, w=1)[0]
        cmds.setAttr(orientConst+".interpType", 2)
        
        cmds.delete(upLimb['constraints'][1])
        cmds.parentConstraint(elbowctrlCtrl, upLimb['locsList'][0], mo=True, w=1, name=upLimb['locsList'][0]+"_ParentConstraint")
        cmds.delete(upLimb['constraints'][3])
        cmds.pointConstraint(elbowctrlCtrl, upLimb['locsList'][3], mo=True, w=1, name=upLimb['locsList'][3]+"_PointConstraint")
        
        cmds.delete(downLimb['constraints'][0])
        cmds.parentConstraint(elbowctrlCtrl, downLimb['locsList'][2], mo=True, w=1, name=downLimb['locsList'][2]+"_ParentConstraint")
        cmds.delete(downLimb['constraints'][2])
        cmds.pointConstraint(elbowctrlCtrl, downLimb['locsList'][4], mo=True, w=1, name=downLimb['locsList'][4]+"_ParentConstraint")
        
        upPC = cmds.parentConstraint(cmds.listRelatives(upLimb['middleCtrl'], p=True)[0], elbowctrlCtrl, upctrl, mo=True, w=1, skipRotate=['x', 'y', 'z'], name=upctrl+"_ParentConstraint")[0]
        cmds.orientConstraint(cmds.listRelatives(upLimb['middleCtrl'], p=True)[0], upctrl, mo=True, w=1, name=upctrl+"_OrientConstraint")
        cmds.setAttr(upPC+'.interpType', 2)
        cmds.connectAttr(elbowctrlCtrl+'.autoBend', upPC+'.'+elbowctrlCtrl+'W1', force=True)
        cmds.parentConstraint(cmds.listRelatives(upctrl, c=True)[0], upLimb['middleCtrl'], mo=True, w=1, name=upLimb['middleCtrl']+"_ParentConstraint")
        
        downPC = cmds.parentConstraint(cmds.listRelatives(downLimb['middleCtrl'], p=True)[0], elbowctrlCtrl, downctrl, mo=True, w=1, skipRotate=['x', 'y', 'z'], name=downctrl+"_ParentConstraint")[0]
        cmds.orientConstraint(cmds.listRelatives(downLimb['middleCtrl'], p=True)[0], downctrl, mo=True, w=1, name=downctrl+"_OrientConstraint")
        cmds.setAttr(downPC+'.interpType', 2)
        cmds.connectAttr(elbowctrlCtrl+'.autoBend', downPC+'.'+elbowctrlCtrl+'W1', force=True)
        cmds.parentConstraint(cmds.listRelatives(downctrl, c=True)[0], downLimb['middleCtrl'], mo=True, w=1, name=downLimb['middleCtrl']+"_ParentConstraint")
        
        cmds.pointConstraint(lista[1], elbowctrl, mo=True, w=1, name=elbowctrl+"_PointConstraint")
        
        upJntGrp = cmds.listRelatives(upLimb['skinJointsList'][0], p=True, f=True)
        downJntGrp = cmds.listRelatives(downLimb['skinJointsList'][0], p=True, f=True)
        
        limbJoints = list(upLimb['skinJointsList'])
        limbJoints.extend(downLimb['skinJointsList'])
        
        jntGrp = cmds.group(limbJoints, n=prefix+myName+'_Jnts_Grp')
        '''
        Deactivate the segment scale compensate on the bone to prevent scaling problem in maya 2016
        It will prevent a double scale problem that will come from the upper parent in the rig
        '''
        if (int(cmds.about(version=True)[:4]) >= 2016):
            for nBone in limbJoints:
                cmds.setAttr(nBone+".segmentScaleCompensate", 0)
        
        for i in range(len(limbJoints)):
            limbJoints[i] = cmds.rename(limbJoints[i], prefix+myName+'_%02d_Jnt'%(i+1))
            cmds.addAttr(limbJoints[i], longName="dpAR_joint", attributeType='float', keyable=False)
        
        scaleGrp = cmds.group(upLimb['scaleGrp'], downLimb['scaleGrp'], jntGrp, n=prefix+myName+'_Ribbon_Scale_Grp')
        cmds.setAttr(upLimb['scaleGrp']+'.v', cmds.getAttr(upLimb['finalGrp']+'.v'))
        cmds.setAttr(downLimb['scaleGrp']+'.v', cmds.getAttr(downLimb['finalGrp']+'.v'))
        
        cmds.delete(upJntGrp, downJntGrp)
        
        staticGrp = cmds.group(upLimb['finalGrp'], downLimb['finalGrp'], n=prefix+myName+'_Ribbon_Static_Grp')
        
        ctrlsGrp = cmds.group(upctrl, downctrl, elbowctrl, upLimb['extraCtrlGrp'], downLimb['extraCtrlGrp'], n=prefix+myName+'_Ctrls_Grp')
        
        cmds.delete(midLoc, auxLoc)
        
        # organizing joint nomenclature ('_Jnt', '_Jxt') and skin attributes (".dpAR_joint")
        # in order to quickly skin using dpAR_UI
        for item in lista[:-1]:
            #fix joint name suffix
            if '_Jnt' in item:
                # remove dpAR skin attribute
                try:
                    cmds.deleteAttr(item+".dpAR_joint")
                except:
                    pass
                # rename joint
                cmds.rename(item, item.replace('_Jnt', '_Jxt'))
        
        # implementing pin setup to ribbon corner offset control:
        if elbowctrlList[2]:
            worldRefPC = cmds.parentConstraint(worldRef, elbowctrl, elbowctrlZero, mo=True)[0]
            pinRev = cmds.createNode('reverse', name=elbowctrlCtrl+"_Pin_Rev")
            cmds.connectAttr(elbowctrlCtrl+".pin", worldRefPC+"."+worldRef+"W0", force=True)
            cmds.connectAttr(elbowctrlCtrl+".pin", pinRev+".inputX", force=True)
            cmds.connectAttr(pinRev+".outputX", worldRefPC+"."+elbowctrl+"W1", force=True)
        
        # autoRotate by twistBone control setup:
        if upLimb['upTwistBoneMD']:
            cmds.connectAttr(upctrlCtrl+".autoRotate", upLimb['upTwistBoneMD']+".input1Z", force=True)
            cmds.connectAttr(upctrlCtrl+".invert", upLimb['twistBoneCnd']+".firstTerm", force=True)
        if upLimb['bottomTwistBoneMD']:
            cmds.connectAttr(upctrlCtrl+".autoRotate", upLimb['bottomTwistBoneMD']+".input1Z", force=True)
        if downLimb['upTwistBoneMD']:
            cmds.connectAttr(downctrlCtrl+".autoRotate", downLimb['upTwistBoneMD']+".input1Z", force=True)
            cmds.connectAttr(downctrlCtrl+".invert", downLimb['twistBoneCnd']+".firstTerm", force=True)
        if downLimb['bottomTwistBoneMD']:
            cmds.connectAttr(downctrlCtrl+".autoRotate", downLimb['bottomTwistBoneMD']+".input1Z", force=True)
        
        
        # WIP: not used this mirror by dpAR system because each module guide will create each own mirror
        if mirror:
            jnt = None
            if cmds.objExists(iniJnt.replace('Jxt', 'Jnt').replace('L_', 'R_')):
                jnt = iniJnt.replace('Jxt', 'Jnt').replace('L_', 'R_')
            else:
                jnt = iniJnt.replace('L_', 'R_')
            newOri = cmds.duplicate(oriLoc, rr=True)
            auxgrp = cmds.group(em=True, name='MirrorAux_Grp')
            
            cmds.parent(newOri, auxgrp)
            
            cmds.setAttr(auxgrp+'.sx', -1)
            cmds.parent(newOri, w=True)
            cmds.delete(auxgrp)
            grp = cmds.group(em=True, n='MirrorAuxGrp')
            cmds.delete(cmds.parentConstraint(newOri, grp, mo=False, w=1))
            cmds.parent(newOri, grp)
            cmds.makeIdentity(newOri, a=1, s=1)
            
            #addRibbonToLimb(prefix=prefix.replace('L_', 'R_'), myName=myName, oriLoc=newOri, iniJnt=jnt, num=num, mirror=False)
            
            cmds.delete(grp)

        # extraCtrlList:
        extraCtrlList = upLimb['extraCtrlList']
        extraCtrlList.extend(downLimb['extraCtrlList'])
        
        return {'scaleGrp':scaleGrp, 'staticGrp':staticGrp, 'ctrlsGrp':ctrlsGrp, 'bendGrpList':[upctrl, downctrl], 'ctrlList':[upctrlCtrl, downctrlCtrl, elbowctrlCtrl], 'extraBendGrp':[upLimb['extraCtrlGrp'], downLimb['extraCtrlGrp']], 'extraCtrlList':extraCtrlList, 'twistBoneMD':upLimb['twistBoneMD']}
    
    
    def createBendCtrl(self, myName='Bend_Ctrl', r=1, zero=True, *args):
        """ Create the Ribbon Bend control.
            Returns the group zeroOut and the control curve.
        """
        grp = None
        curve = self.ctrls.cvControl("id_038_RibbonBend", myName, r=self.ctrlRadius, d=self.curveDegree, rot=(0, 90, 0))
        self.dpUIinst.ctrls.setLockHide([curve], ['v'])
        if zero:
            grp = cmds.group(curve, n=myName+'_Grp')
        return [grp, curve]
    
    
    def createElbowCtrl(self, myName='Limb_Ctrl', zero=True, armStyle=True, *args):
        """ Create the Ribbon Corner (Elbow) control.
            Returns the group, the control curve and it's zeroOut group.
        """
        if armStyle:
            curve = self.ctrls.cvControl("id_039_RibbonCorner", myName, r=self.ctrlRadius, d=self.curveDegree, rot=(0, 90, 0))
        else:
            curve = self.ctrls.cvControl("id_039_RibbonCorner", myName, r=self.ctrlRadius, d=self.curveDegree, rot=(90, 0, 0))
        grp = None
        if zero:
            zero = cmds.group(curve, n=myName+'_Zero')
            grp = cmds.group(zero, n=myName+'_Grp')
            if armStyle:
                cmds.rotate(0, -90, -90, zero)
            else:
                cmds.rotate(-90, 0, -90, zero)
        cmds.addAttr(curve, longName='autoBend', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        cmds.addAttr(curve, longName='pin', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
        self.dpUIinst.ctrls.setLockHide([curve], ['sx', 'sy', 'sz', 'v'])
        return [grp, curve, zero]
    
    
    def createRibbon(self, axis=(0, 0, 1), name='RibbonSetup', horizontal=False, numJoints=3, guides=None, v=True, s=0, firstLimb=True, upCtrl=None, worldRef="worldRef", jointLabelAdd=0, jointLabelName="RibbonName", *args):
        """ Main method to create the Ribbon system.
            Returns results in a dictionary.
        """
        retDict = {}
        
        #define variables
        top_Loc = []
        mid_Loc = []
        bttm_Loc = []
        rb_Jnt = []
        drv_Jnt =[]
        fols = []
        aux_Jnt = []
        ribbon = ''
        extraCtrlList = []

        #define attributes
        limbManualVVAttr = self.langDic[self.langName]['m019_limb'].lower()+"Manual_"+self.langDic[self.langName]['c031_volumeVariation']
        limbVVAttr       = self.langDic[self.langName]['m019_limb'].lower()+"_"+self.langDic[self.langName]['c031_volumeVariation']
        limbMinVVAttr    = self.langDic[self.langName]['m019_limb'].lower()+"Min_"+self.langDic[self.langName]['c031_volumeVariation']

        #create a nurbsPlane based in the choose orientation option
        if horizontal:
            ribbon = cmds.nurbsPlane(ax=axis, w=numJoints, lr=(1/float(numJoints)), d=3, u=numJoints, v=1, ch=0, name=name+'_Plane')[0]
            cmds.rebuildSurface(ribbon, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, sv=1, du=3, dv=1, tol=0.01, fr=0, dir=1) 
        else:
            ribbon = cmds.nurbsPlane(ax=axis, w=1, lr=numJoints, d=3, u=1, v=numJoints, ch=0, name=name+'_Plane')[0]
            cmds.rebuildSurface(ribbon, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=1, du=1, dv=3, tol=0.01, fr=0, dir=0) 
        # make this ribbonNurbsPlane as not skinable from dpAR_UI:
        cmds.addAttr(ribbon, longName="doNotSkinIt", attributeType="bool", keyable=True)
        cmds.setAttr(ribbon+".doNotSkinIt", 1)
        #call the function to create follicles and joint in the nurbsPlane
        results = self.createFollicles(rib=ribbon, num=numJoints, name=name, horizontal=horizontal, side=s, jointLabelAdd=jointLabelAdd, jointLabelName=jointLabelName)
        rb_Jnt = results[0]
        fols = results[1]
        #create locator controls for the middle of the ribbon
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Pos_Loc')[0])
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Aim_Loc')[0])
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Off_Loc')[0])
        mid_Loc.append(cmds.spaceLocator(name=name+'_Mid_Up_Loc')[0])
        #parent correctly the middle locators
        cmds.parent(mid_Loc[2], mid_Loc[1], relative=True)
        cmds.parent(mid_Loc[1], mid_Loc[0], relative=True)
        cmds.parent(mid_Loc[3], mid_Loc[0], relative=True)
        #create the locators controls for the top of the ribbon
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Pos_Loc')[0])
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Aim_Loc')[0])
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Up_Loc')[0])
        top_Loc.append(cmds.spaceLocator(name=name+'_Top_Rot0_Loc')[0])
        #parent correctly the top locators
        cmds.parent(top_Loc[1], top_Loc[0], relative=True)
        cmds.parent(top_Loc[2], top_Loc[0], relative=True)
        cmds.parent(top_Loc[3], top_Loc[0], relative=True)
        #create the locators for the end of the ribbon
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bttm_Pos_Loc')[0])
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bttm_Aim_Loc')[0])
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bttm_Up_Loc')[0])
        bttm_Loc.append(cmds.spaceLocator(name=name+'_Bttm_Rot0_Loc')[0])
        #parent correctly the bottom locators
        cmds.parent(bttm_Loc[1], bttm_Loc[0], relative=True)
        cmds.parent(bttm_Loc[2], bttm_Loc[0], relative=True)
        cmds.parent(bttm_Loc[3], bttm_Loc[0], relative=True)
        
        #put the top locators in the same place of the top joint
        cmds.parent(top_Loc[0], fols[len(fols)-1], relative=True)
        cmds.parent(top_Loc[0], w=True)
        
        #put the bottom locators in the same place of the bottom joint
        cmds.parent(bttm_Loc[0], fols[0], relative=True)
        cmds.parent(bttm_Loc[0], w=True)
        cmds.select(clear=True)
        
        #create the joints that will be used to control the ribbon
        drv_Jnt = cmds.duplicate([rb_Jnt[0], rb_Jnt[(len(rb_Jnt)-1)/2], rb_Jnt[len(rb_Jnt)-1]])
        dup = cmds.duplicate([drv_Jnt[0], drv_Jnt[2]])
        drv_Jnt.append(dup[0])
        drv_Jnt.append(dup[1])
        #cmds.parent(drv_Jnt, w=True)
        for jnt in drv_Jnt:
            cmds.joint(jnt, e=True, oj='none', ch=True, zso=True);
            cmds.setAttr(jnt+'.radius', cmds.getAttr(jnt+'.radius')+0.5)
        #rename created joints
        drv_Jnt[0] = cmds.rename(drv_Jnt[0], name+'_Drv_Bttm_Jxt')
        drv_Jnt[1] = cmds.rename(drv_Jnt[1], name+'_Drv_Mid_Jxt')
        drv_Jnt[2] = cmds.rename(drv_Jnt[2], name+'_Drv_Top_Jxt')
        drv_Jnt[3] = cmds.rename(drv_Jnt[3], name+'_Drv_Bttm_End')
        drv_Jnt[4] = cmds.rename(drv_Jnt[4], name+'_Drv_Top_End')
        
        #place joints correctly accordaly with the user options choose
        if (horizontal and axis==(1, 0, 0)) or (horizontal and axis==(0, 0, 1)):
            cmds.setAttr(bttm_Loc[2]+'.translateY', 2)
            cmds.setAttr(top_Loc[2]+'.translateY', 2)
            cmds.setAttr(mid_Loc[3]+'.translateY', 2)
        elif (horizontal and axis==(0, 1, 0)) or (not horizontal and axis==(1, 0, 0)):
            cmds.setAttr(bttm_Loc[2]+'.translateZ', 2)
            cmds.setAttr(top_Loc[2]+'.translateZ', 2)
            cmds.setAttr(mid_Loc[3]+'.translateZ', 2)
        elif not horizontal and axis==(0, 1, 0) or (not horizontal and axis==(0, 0, 1)):
            cmds.setAttr(bttm_Loc[2]+'.translateX', 2)
            cmds.setAttr(top_Loc[2]+'.translateX', 2)
            cmds.setAttr(mid_Loc[3]+'.translateX', 2)
        elif horizontal and axis==(0, 0, -1):
            if firstLimb:
                cmds.setAttr(bttm_Loc[2]+'.translateY', 2)
                cmds.setAttr(top_Loc[2]+'.translateY', 2)
                cmds.setAttr(mid_Loc[3]+'.translateY', 2)
            else:
                cmds.setAttr(bttm_Loc[2]+'.translateY', 2)
                cmds.setAttr(top_Loc[2]+'.translateY', -2)
                cmds.setAttr(mid_Loc[3]+'.translateY', 2)
        
        #create auxiliary joints that will be used to control the ribbon
        aux_Jnt.append(cmds.duplicate(drv_Jnt[1], name=name+'_Jxt_Rot')[0])
        cmds.setAttr(aux_Jnt[0]+'.jointOrient', 0, 0, 0)
        cmds.setAttr(aux_Jnt[0]+'.rotateOrder', 5)
        aux_Jnt.append(cmds.duplicate(aux_Jnt[0], name=name+'_Jxt_Rot_End')[0])
        
        cmds.parent(aux_Jnt[1], mid_Loc[3])
        cmds.setAttr(aux_Jnt[1]+'.translate', 0, 0, 0)
        cmds.parent(aux_Jnt[1], aux_Jnt[0])
        cmds.parent(mid_Loc[3], aux_Jnt[1])
        #calculate the adjust for the new chain position
        dist = float(numJoints)/2.0
        end_dist = (1/float(numJoints))
        cmds.parent(drv_Jnt[3], drv_Jnt[0])
        cmds.parent(drv_Jnt[4], drv_Jnt[2])
        
        #adjust the joints orientation and position based in the options choose from user
        if horizontal and axis==(1, 0, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 90, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 90, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tz', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tz', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tz', dist)
            cmds.setAttr(drv_Jnt[4]+'.tz', -end_dist*dist)
        
        elif horizontal and axis==(0, 1, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tx', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tx', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tx', dist)
            cmds.setAttr(drv_Jnt[4]+'.tx', -end_dist*dist)
        
        elif horizontal and axis==(0, 0, 1):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tx', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tx', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tx', dist)
            cmds.setAttr(drv_Jnt[4]+'.tx', -end_dist*dist)
        
        elif horizontal and axis==(0, 0, -1):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, 0)
            
            cmds.setAttr(drv_Jnt[0]+'.tx', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tx', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tx', dist)
            cmds.setAttr(drv_Jnt[4]+'.tx', -end_dist*dist)
            
        elif not horizontal and axis==(1, 0, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, -90)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, -90)
        
            cmds.setAttr(drv_Jnt[0]+'.ty', -dist)
            cmds.setAttr(drv_Jnt[3]+'.ty', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.ty', dist)
            cmds.setAttr(drv_Jnt[4]+'.ty', -end_dist*dist)
            
        elif not horizontal and axis==(0, 1, 0):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 90, 0)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 90, 0)
        
            cmds.setAttr(drv_Jnt[0]+'.tz', -dist)
            cmds.setAttr(drv_Jnt[3]+'.tz', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.tz', dist)
            cmds.setAttr(drv_Jnt[4]+'.tz', -end_dist*dist)
            
        elif not horizontal and axis==(0, 0, 1):
            cmds.setAttr(drv_Jnt[0]+'.jointOrient', 0, 0, -90)
            cmds.setAttr(drv_Jnt[2]+'.jointOrient', 0, 0, -90)
        
            cmds.setAttr(drv_Jnt[0]+'.ty', -dist)
            cmds.setAttr(drv_Jnt[3]+'.ty', end_dist*dist)
            cmds.setAttr(drv_Jnt[2]+'.ty', dist)
            cmds.setAttr(drv_Jnt[4]+'.ty', -end_dist*dist)
        
        #fix the control locators position and orientation
        cmds.parent(top_Loc[0], drv_Jnt[2])
        cmds.setAttr(top_Loc[0]+'.translate', 0, 0, 0)
        cmds.parent(top_Loc[0], w=True)
        cmds.setAttr(top_Loc[0]+'.rotate', 0, 0, 0)
        
        cmds.parent(bttm_Loc[0], drv_Jnt[0])
        cmds.setAttr(bttm_Loc[0]+'.translate', 0, 0, 0)
        cmds.parent(bttm_Loc[0], w=True)
        cmds.setAttr(bttm_Loc[0]+'.rotate', 0, 0, 0)    
        
        cmds.parent(drv_Jnt[2], top_Loc[1])
        cmds.parent(drv_Jnt[1], mid_Loc[2])
        cmds.parent(drv_Jnt[0], bttm_Loc[1])
        
        cmds.parent(aux_Jnt[0], mid_Loc[0])
        #create a nurbs control in order to be used in the ribbon offset
        mid_Ctrl = self.ctrls.cvControl("Circle", name+'_MidCtrl', r=self.ctrlRadius, d=self.curveDegree, rot=(0, 90, 0))
        midCtrl = mid_Ctrl
        mid_Ctrl = cmds.group(n=mid_Ctrl+'_Grp', em=True)
        cmds.delete(cmds.parentConstraint(midCtrl, mid_Ctrl, mo=0))
        cmds.parent(midCtrl, mid_Ctrl)
        
        #adjust the relationship between the locators
        cmds.parent(mid_Ctrl, mid_Loc[2], r=True)
        cmds.parent(drv_Jnt[1], midCtrl)
        cmds.parent([top_Loc[2], mid_Loc[3], bttm_Loc[2]], w=True)
        cmds.makeIdentity(top_Loc[0], apply=True)
        cmds.makeIdentity(mid_Loc[0], apply=True)
        cmds.makeIdentity(bttm_Loc[0], apply=True)
        cmds.parent(top_Loc[2], top_Loc[0])
        cmds.parent(bttm_Loc[2], bttm_Loc[0])
        cmds.parent(mid_Loc[3], aux_Jnt[1]) 
        #create needed constraints in the locators in order to set the top always follow, to the base always aim the middle, to the middle always aim the top
        if firstLimb:
            cmds.aimConstraint(drv_Jnt[1], bttm_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=bttm_Loc[2], name=bttm_Loc[1]+"_AimConstraint")
            cmds.aimConstraint(top_Loc[0], mid_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=mid_Loc[3], name=mid_Loc[1]+"_AimConstraint")
            cmds.aimConstraint(drv_Jnt[1], top_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(-1, 0, 0), upVector=(0, 1, 0), worldUpType='object', worldUpObject=top_Loc[2], name=top_Loc[1]+"_AimConstraint")
        else:
            # bug fix to plane twist
            cmds.aimConstraint(drv_Jnt[1], bttm_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType='object', worldUpObject=bttm_Loc[2], name=bttm_Loc[1]+"_AimConstraint")
            cmds.aimConstraint(top_Loc[0], mid_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(-1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=mid_Loc[3], name=mid_Loc[1]+"_AimConstraint")
            cmds.aimConstraint(drv_Jnt[1], top_Loc[1], offset=(0, 0, 0), weight=1, aimVector=(-1, 0, 0), upVector=(0, 0, 1), worldUpType='object', worldUpObject=top_Loc[2], name=top_Loc[1]+"_AimConstraint")
        
        #create a point and orient constraint for the middle control
        cmds.pointConstraint(top_Loc[0], bttm_Loc[0], mid_Loc[0], offset=(0, 0, 0), weight=1, name=mid_Loc[0]+"_PointConstraint")
        ori = cmds.orientConstraint(top_Loc[0], bttm_Loc[0], aux_Jnt[0], offset=(0, 0, 0), weight=1, name=aux_Jnt[0]+"_OrientConstraint")
        
        #ribbon scale (volume variation)
        if numJoints == 3:
            proportionList = [0.5, 1, 0.5]
        elif numJoints == 5:
            proportionList = [0.4, 0.8, 1, 0.8, 0.4]
        elif numJoints == 7:
            proportionList = [0.25, 0.5, 0.75, 1, 0.75, 0.5, 0.25]

        curveInfoNode = cmds.arclen(ribbon+".v[0.5]", constructionHistory=True)
        curveInfoNode = cmds.rename(curveInfoNode, ribbon+"_CurveInfo")
        curveFromSurfaceIso = cmds.listConnections(curveInfoNode+".inputCurve", source=True, destination=False)
        cmds.rename(curveFromSurfaceIso, ribbon+"_CurveFromSurfaceIso")
        rbScaleMD = cmds.createNode("multiplyDivide", name=ribbon+"_ScaleCompensate_MD")
        rbNormalizeMD = cmds.createNode("multiplyDivide", name=ribbon+"_Normalize_MD")
        cmds.setAttr(rbNormalizeMD+".operation", 2)
        cmds.connectAttr(curveInfoNode+".arcLength", rbNormalizeMD+".input2X", force=True)
        cmds.connectAttr(rbScaleMD+".outputX", rbNormalizeMD+".input1X", force=True)

        if cmds.objExists(worldRef):
            if not cmds.objExists(worldRef+"."+limbManualVVAttr):
                cmds.addAttr(worldRef, longName=limbVVAttr, attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.addAttr(worldRef, longName=limbManualVVAttr, attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(worldRef, longName=limbMinVVAttr, attributeType="float", defaultValue=0.01, keyable=True)
            cmds.connectAttr(worldRef+".scaleX", rbScaleMD+".input1X", force=True)
        
        #fix group hierarchy
        extraCtrlGrp = cmds.group(empty=True, name=name+"_ExtraBendyCtrl_Grp")
        i = 0
        for jnt in rb_Jnt:
            cmds.makeIdentity(jnt, a=True)
            # create extra control
            extraCtrlName = jnt.replace("_Jnt", "_Ctrl")
            extraCtrl = self.ctrls.cvControl("id_040_RibbonExtra", ctrlName=extraCtrlName, r=self.ctrlRadius, d=self.curveDegree)
            extraCtrlList.append(extraCtrl)
            cmds.rotate(0, 90, 0, extraCtrl)
            cmds.makeIdentity(extraCtrl, a=True)
            extraCtrlZero = utils.zeroOut([extraCtrl])[0]
            cmds.parent(extraCtrlZero, extraCtrlGrp)
            cmds.parentConstraint(fols[i], extraCtrlZero, w=1, name=extraCtrlZero+"_ParentConstraint")
            cmds.parentConstraint(extraCtrl, jnt, w=1, name=jnt+"_ParentConstraint")
            cmds.scaleConstraint(extraCtrl, jnt, w=1, name=jnt+"_ScaleConstraint")
            
            # work with volume variation
            rbProportionMD = cmds.createNode("multiplyDivide", name=extraCtrlName.replace("_Ctrl", "_Proportion_MD"))
            rbIntensityMD = cmds.createNode("multiplyDivide", name=extraCtrlName.replace("_Ctrl", "_Intensity_MD"))
            rbAddScalePMA = cmds.createNode("plusMinusAverage", name=extraCtrlName.replace("_Ctrl", "_AddScale_PMA"))
            rbScaleClp = cmds.createNode("clamp", name=extraCtrlName.replace("_Ctrl", "_Scale_Clp"))
            rbBlendCB = cmds.createNode("blendColors", name=extraCtrlName.replace("_Ctrl", "_Blend_BC"))
            cmds.connectAttr(worldRef+"."+limbVVAttr, rbBlendCB+".blender", force=True)
            cmds.setAttr(rbBlendCB+".color2", 1, 1, 1, type="double3")
            cmds.connectAttr(rbNormalizeMD+".outputX", rbProportionMD+".input1X", force=True)
            cmds.setAttr(rbProportionMD+".input2X", proportionList[i])
            cmds.connectAttr(rbProportionMD+".outputX", rbIntensityMD+".input1X", force=True)
            cmds.connectAttr(worldRef+"."+limbManualVVAttr, rbIntensityMD+".input2X", force=True)
            cmds.connectAttr(rbIntensityMD+".outputX", rbAddScalePMA+".input1D[1]", force=True)
            cmds.connectAttr(rbAddScalePMA+".output1D", rbScaleClp+".inputR", force=True)
            cmds.connectAttr(worldRef+"."+limbMinVVAttr, rbScaleClp+".minR")
            cmds.setAttr(rbScaleClp+".maxR", 1000000)
            cmds.connectAttr(rbScaleClp+".outputR", rbBlendCB+".color1.color1R", force=True)
            cmds.connectAttr(rbBlendCB+".output.outputR", extraCtrlZero+".scaleY", force=True)
            cmds.connectAttr(rbBlendCB+".output.outputR", extraCtrlZero+".scaleZ", force=True)
            
            # update i
            i = i + 1
        
        locatorsGrp = cmds.group(bttm_Loc[0], top_Loc[0], mid_Loc[0], bttm_Loc[3], top_Loc[3], n=name+'_Loc_Grp')
        skinJntGrp = cmds.group(rb_Jnt, n=name+'_Jnt_Grp')
        finalSystemGrp = cmds.group(ribbon, locatorsGrp, skinJntGrp, n=name+'_RibbonSystem_Grp')
        
        #do the controller joints skin and the ribbon
        ribbonShape = cmds.listRelatives(ribbon, shapes=True)
        skinClusterNode = cmds.skinCluster(drv_Jnt[0:3], ribbonShape, tsb=True, mi=2, dr=1, n=name+"_SC")[0]
        bindPose = cmds.listConnections(skinClusterNode+".bindPose", destination=False, source=True)
        cmds.rename(bindPose, name+"_BindPose")
        
        #skin presets for the ribbon (that's amazing!)
        if not horizontal:
            if numJoints == 3:
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][5]', tv=(drv_Jnt[2], 1))
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][4]', tv=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][3]', tv=[(drv_Jnt[2], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][2]', tv=[(drv_Jnt[0], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][1]', tv=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][0]', tv=(drv_Jnt[0], 1))

            elif numJoints == 5:
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][7]', tv=(drv_Jnt[2], 1))
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][6]', tv=[(drv_Jnt[2], 0.80), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][5]', tv=[(drv_Jnt[2], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][4]', tv=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][3]', tv=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][2]', tv=[(drv_Jnt[0], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][1]', tv=[(drv_Jnt[0], 0.8), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][0]', tv=(drv_Jnt[0], 1))
            elif numJoints == 7:
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][9]', tv=(drv_Jnt[2], 1))
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][8]', tv=[(drv_Jnt[2], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][7]', tv=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][6]', tv=[(drv_Jnt[2], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][5]', tv=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][4]', tv=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][3]', tv=[(drv_Jnt[0], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][2]', tv=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][1]', tv=[(drv_Jnt[0], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0:1][0]', tv=(drv_Jnt[0], 1))
        else:
            if numJoints == 3:
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[5][0:1]', tv=(drv_Jnt[2], 1))
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[4][0:1]', tv=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[3][0:1]', tv=[(drv_Jnt[2], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[2][0:1]', tv=[(drv_Jnt[0], 0.2), (drv_Jnt[1], 0.8)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[1][0:1]', tv=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0][0:1]', tv=(drv_Jnt[0], 1))
            elif numJoints == 5:
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[7][0:1]', tv=(drv_Jnt[2], 1))
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[6][0:1]', tv=[(drv_Jnt[2], 0.80), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[5][0:1]', tv=[(drv_Jnt[2], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[4][0:1]', tv=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[3][0:1]', tv=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[2][0:1]', tv=[(drv_Jnt[0], 0.5), (drv_Jnt[1], 0.5)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[1][0:1]', tv=[(drv_Jnt[0], 0.8), (drv_Jnt[1], 0.2)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0][0:1]', tv=(drv_Jnt[0], 1))
            elif numJoints == 7:
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[9][0:1]', tv=(drv_Jnt[2], 1))
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[8][0:1]', tv=[(drv_Jnt[2], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[7][0:1]', tv=[(drv_Jnt[2], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[6][0:1]', tv=[(drv_Jnt[2], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[5][0:1]', tv=[(drv_Jnt[2], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[4][0:1]', tv=[(drv_Jnt[0], 0.25), (drv_Jnt[1], 0.75)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[3][0:1]', tv=[(drv_Jnt[0], 0.35), (drv_Jnt[1], 0.65)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[2][0:1]', tv=[(drv_Jnt[0], 0.6), (drv_Jnt[1], 0.4)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[1][0:1]', tv=[(drv_Jnt[0], 0.85), (drv_Jnt[1], 0.15)])
                cmds.skinPercent(skinClusterNode, ribbon + '.cv[0][0:1]', tv=(drv_Jnt[0], 1))
        constr = []
        if guides:
            top = guides[0]
            bottom = guides[1]
            constr.append(cmds.parentConstraint(top, bttm_Loc[0], mo=False, name=bttm_Loc[0]+"_ParentConstraint"))
            constr.append(cmds.parentConstraint(bottom, top_Loc[0], mo=False, name=top_Loc[0]+"_ParentConstraint"))
            cmds.delete(cmds.parentConstraint(top, bttm_Loc[3], mo=False))
            cmds.delete(cmds.parentConstraint(bottom, top_Loc[3], mo=False))
            constr.append(cmds.pointConstraint(top, bttm_Loc[3], mo=False, name=bttm_Loc[3]+"_PointConstraint"))
            constr.append(cmds.pointConstraint(bottom, top_Loc[3], mo=False, name=top_Loc[3]+"_PointConstraint"))
        
        #fix orientation issues
        cmds.delete(ori)
        # we'll recreate it again if we don't use twistBone case it don't load matrix plugin.
        
        #fix loc_Grp scale
        if guides:
            from math import sqrt, pow
            auxLoc1 = cmds.spaceLocator(name='auxLoc1')[0]
            auxLoc2 = cmds.spaceLocator(name='auxLoc2')[0]
            cmds.delete(cmds.parentConstraint(top, auxLoc1, mo=False, w=1))
            cmds.delete(cmds.parentConstraint(bottom, auxLoc2, mo=False, w=1))
            a = cmds.xform(auxLoc1, ws=True, translation=True, q=True)
            b = cmds.xform(auxLoc2, ws=True, translation=True, q=True)
            
            dist = sqrt(pow(a[0]-b[0], 2.0)+pow(a[1]-b[1], 2.0)+pow(a[2]-b[2], 2.0))
            scale = dist/float(numJoints)
            
            cmds.setAttr(locatorsGrp+'.s', scale, scale, scale)
        
            cmds.delete(auxLoc1, auxLoc2)
        
        # baseTwist:
        if not upCtrl == None:
            bttm_LocGrp = cmds.group(bttm_Loc[2], name=bttm_Loc[2]+"_Grp")
            bttm_LocTwistBoneGrp = cmds.group(bttm_LocGrp, name=bttm_Loc[2]+"_TwistBone_Grp")
            bttm_LocPos = cmds.xform(bttm_Loc[0], query=True, worldSpace=True, translation=True)
            cmds.move(bttm_LocPos[0], bttm_LocPos[1], bttm_LocPos[2], bttm_LocGrp+".scalePivot", bttm_LocGrp+".rotatePivot", absolute=True)
            cmds.move(bttm_LocPos[0], bttm_LocPos[1], bttm_LocPos[2], bttm_LocTwistBoneGrp+".scalePivot", bttm_LocTwistBoneGrp+".rotatePivot", absolute=True)
            twistBoneMD = cmds.createNode("multiplyDivide", name=upCtrl+"_TwistBone_MD")
            invertTwistBoneMD = cmds.createNode("multiplyDivide", name=upCtrl+"_InvertTwistBone_MD")
            cmds.setAttr(invertTwistBoneMD+".input2Z", -1)
            cmds.connectAttr(upCtrl+".autoTwistBone", twistBoneMD+".input1Z", force=True)
            cmds.connectAttr(twistBoneMD+".outputZ", invertTwistBoneMD+".input1Z", force=True)
            cmds.connectAttr(invertTwistBoneMD+".outputZ", bttm_LocTwistBoneGrp+".rotateZ", force=True)
            cmds.connectAttr(upCtrl+".baseTwist", bttm_LocGrp+".rotateZ", force=True)
            retDict['twistBoneMD'] = twistBoneMD
        
        # autoRotate:
        loadedQuatNode = utils.checkLoadedPlugin("quatNodes", self.langDic[self.langName]['e014_cantLoadQuatNode'])
        loadedMatrixPlugin = utils.checkLoadedPlugin("decomposeMatrix", "matrixNodes", self.langDic[self.langName]['e002_decomposeMatrixNotFound'])
        if loadedQuatNode and loadedMatrixPlugin:
            upTwistBoneMD = utils.twistBoneMatrix(top_Loc[0], top_Loc[3], name+"_Top_TwistBone")
            bottomTwistBoneMD = utils.twistBoneMatrix(bttm_Loc[0], bttm_Loc[3], name+"_Bttm_TwistBone")
            twistBonePMA = cmds.createNode("plusMinusAverage", name=name+"_TwistBone_PMA")
            twistBoneInvMD = cmds.createNode("multiplyDivide", name=name+"_TwistBone_Inv_MD")
            twistBoneCnd = cmds.createNode("condition", name=name+"_TwistBone_Cnd")
            cmds.setAttr(twistBoneCnd+".colorIfTrueR", -1)
            cmds.setAttr(twistBoneCnd+".secondTerm", 1)
            cmds.connectAttr(twistBonePMA+".output1D", twistBoneInvMD+".input1X", force=True)
            cmds.connectAttr(twistBoneCnd+".outColor.outColorR", twistBoneInvMD+".input2X", force=True)
            cmds.connectAttr(upTwistBoneMD+".outputZ", twistBonePMA+".input1D[0]", force=True)
            cmds.connectAttr(bottomTwistBoneMD+".outputZ", twistBonePMA+".input1D[1]", force=True)
            cmds.connectAttr(twistBoneInvMD+".outputX", mid_Loc[2]+".rotateX", force=True)
            retDict['upTwistBoneMD'] = upTwistBoneMD
            retDict['bottomTwistBoneMD'] = bottomTwistBoneMD
            retDict['twistBoneCnd'] = twistBoneCnd
            
            # WIP
            # temp solution to avoid arms flipping
            cmds.orientConstraint(bttm_Loc[0], aux_Jnt[0], offset=(0, 0, 0), weight=1, name=aux_Jnt[0]+"_OrientConstraint")
            
        else:
            cmds.orientConstraint(bttm_Loc[0], aux_Jnt[0], weight=0.5, mo=True, name=aux_Jnt[0]+"_OrientConstraint")
        
        #updating values
        cmds.setAttr(rbScaleMD+".input2X", cmds.getAttr(curveInfoNode+".arcLength"))
        for jnt in rb_Jnt:
            rbAddScalePMA = jnt.replace("_Jnt", "_AddScale_PMA")
            cmds.setAttr(rbAddScalePMA+".input1D[0]", 1-cmds.getAttr(rbAddScalePMA+".input1D[1]"))

        #change renderStats
        ribbonShape = cmds.listRelatives(ribbon, s=True, f=True)[0]
        
        cmds.setAttr(ribbonShape+'.castsShadows', 0)
        cmds.setAttr(ribbonShape+'.receiveShadows', 0)
        cmds.setAttr(ribbonShape+'.motionBlur', 0)
        cmds.setAttr(ribbonShape+'.primaryVisibility', 0)
        cmds.setAttr(ribbonShape+'.smoothShading', 0)
        cmds.setAttr(ribbonShape+'.visibleInReflections', 0)
        cmds.setAttr(ribbonShape+'.visibleInRefractions', 0)
        cmds.setAttr(ribbonShape+'.doubleSided', 1)
        
        retDict['name'] = name
        retDict['locsList'] = [top_Loc[0], mid_Loc[0], bttm_Loc[0], top_Loc[3], bttm_Loc[3]]
        retDict['skinJointsList'] =  rb_Jnt
        retDict['scaleGrp'] = locatorsGrp
        retDict['finalGrp'] = finalSystemGrp
        retDict['middleCtrl'] = mid_Ctrl
        retDict['constraints'] = constr
        retDict['bendGrpList'] = [top_Loc[0], bttm_Loc[0]]
        retDict['extraCtrlGrp'] = extraCtrlGrp
        retDict['extraCtrlList'] = extraCtrlList
        retDict['rbScaleMD'] = rbScaleMD
        retDict['rbNormalizeMD'] = rbNormalizeMD
        cmds.setAttr(finalSystemGrp+'.v', v)
        return retDict
    
    
    def createFollicles(self, rib, num, pad=0.5, name='xxxx', horizontal=False, side=0, jointLabelAdd=0, jointLabelName="RibbonName", *args): 
        """ Create follicles to be used by the Ribbon system.
            Returns a list with joints and follicles created.
        """
        #define variables
        jnts = []
        fols = []
        #create joints and follicles based in the choose options from user
        if horizontal:
            #calcule the position of the first follicle
            passo = (1/float(num))/2.0;
            for i in range(num):
                #create the follicle and do correct connections to link it to the 
                folShape = cmds.createNode('follicle', name=name+'_%02d_FolShape'%i)
                folTrans = cmds.rename(cmds.listRelatives(folShape, p=1)[0], name+'_%02d_Fol'%i)         
                fols.append(folTrans)
                cmds.connectAttr(rib+'.worldMatrix[0]', folShape+'.inputWorldMatrix')
                cmds.connectAttr(rib+'.local', folShape+'.inputSurface')
                cmds.connectAttr(folShape+'.outTranslate', folTrans+'.translate')
                cmds.connectAttr(folShape+'.outRotate', folTrans+'.rotate')
                cmds.setAttr(folShape+'.parameterU', passo)
                cmds.setAttr(folShape+'.parameterV', 0.5) 
                #create the joint in the follicle
                cmds.select(cl=True)
                jnts.append(cmds.joint(n=name+'_%02d_Jnt'%i))
                cmds.setAttr(jnts[i]+'.jointOrient', 0, 0, 0)
                utils.setJointLabel(name+'_%02d_Jnt'%i, side+jointLabelAdd, 18, jointLabelName+'_%02d'%i)
                cmds.select(cl=True)
                #calculate the position of the first follicle
                passo+=(1/float(num))
            results = [jnts, fols]
            #return the joints and follicles created
        else:
            #calculate the position of the first follicle
            passo = (1/float(num))/2.0;
            for i in range(num):
                #create the follicle and do correct connections in order to link it to the ribbon
                folShape = cmds.createNode('follicle', name=name+'_%02d_FolShape'%i)
                folTrans = cmds.rename(cmds.listRelatives(folShape, p=1)[0], name+'_%02d_Fol'%i)
                fols.append(folTrans)
                cmds.connectAttr(rib+'.worldMatrix[0]', folShape+'.inputWorldMatrix')
                cmds.connectAttr(rib+'.local', folShape+'.inputSurface')
                cmds.connectAttr(folShape+'.outTranslate', folTrans+'.translate')
                cmds.connectAttr(folShape+'.outRotate', folTrans+'.rotate')
                cmds.setAttr(folShape+'.parameterU', 0.5)   
                cmds.setAttr(folShape+'.parameterV', passo) 
                #create the joint in the follicle
                cmds.select(cl=True)
                jnts.append(cmds.joint(n=name+'_%02d_Jnt'%i))
                cmds.setAttr(jnts[i]+'.jointOrient', 0, 0, 0)
                utils.setJointLabel(name+'_%02d_Jnt'%i, side+jointLabelAdd, 18, jointLabelName+'_%02d'%i)
                cmds.select(cl=True)
                #calculate the first follicle position
                passo+=(1/float(num))
            results = [jnts, fols]
        #return the created joints and follicles
        cmds.parent(fols, rib)
        return results