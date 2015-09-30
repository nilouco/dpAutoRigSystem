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

def addRibbonToLimb(prefix='',nome=None,oriLoc=None,iniJnt=None,skipAxis='y',num=5,mirror=True,ctrlRadius=1):
    if not oriLoc:
        oriLoc = cmds.ls(sl=True,l=True)[0]
    if not iniJnt:
        iniJnt = cmds.ls(sl=True)[1]
    
    if not prefix == '':
        if not prefix.endswith('_'):
            prefix+='_'
    skipa = ['x','y','z']
    skipa.remove(skipAxis)
    lista = []
    lista.append(iniJnt)
    lista.append(cmds.listRelatives(lista[0],c=True)[0])
    lista.append(cmds.listRelatives(lista[1],c=True)[0])
    lista.append(cmds.listRelatives(lista[2],c=True)[0])
    #lastJnt = cmds.listRelatives(lista[3]
    
    auxLoc = cmds.duplicate(oriLoc,rr=True)
    midLoc = cmds.duplicate(oriLoc,rr=True)
    
    
    cmds.delete(cmds.parentConstraint(lista[2],auxLoc,mo=False,w=1))
    cmds.delete(cmds.aimConstraint(lista[3],auxLoc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(0,1,0)))
    cmds.delete(cmds.orientConstraint(oriLoc,auxLoc,mo=False,skip=skipa,weight=1))

    
    cmds.delete(cmds.parentConstraint(lista[1],midLoc,mo=False,w=1))
    cmds.delete(cmds.pointConstraint(lista[1],lista[2],midLoc,mo=False,w=1))
    cmds.delete(cmds.aimConstraint(lista[2],midLoc,mo=False,weight=2,aimVector=(1,0,0),upVector=(0,1,0),worldUpType="vector",worldUpVector=(1,0,0)))
    
    cmds.delete(cmds.orientConstraint(oriLoc,midLoc,mo=False,skip=skipa,weight=1))

    upLimb = createRibbon(name=prefix+'up_'+nome,axis=(0,0,1),horizontal=True,numJoints=num,v=False,guias=[lista[0],lista[1]])
    downLimb = createRibbon(name=prefix+'down_'+nome,axis=(0,0,1),horizontal=True,numJoints=num,v=False,guias=[lista[2],lista[3]])
    upctrl = createBendCtrl(prefix+'up_'+nome+'_off_ctrl', r=ctrlRadius)
    downctrl = createBendCtrl(prefix+'down_'+nome+'_off_ctrl', r=ctrlRadius)
    elbowctrl = createElbowCtrl(prefix+nome.lower()+'_off_ctrl', r=ctrlRadius)
    
    cmds.delete(cmds.parentConstraint(oriLoc,upctrl,mo=False,w=1))
    cmds.delete(cmds.pointConstraint(upLimb['middleCtrl'],upctrl,mo=False,w=1))
    
    cmds.delete(cmds.parentConstraint(auxLoc,downctrl,mo=False,w=1))
    cmds.delete(cmds.pointConstraint(downLimb['middleCtrl'],downctrl,mo=False,w=1))
    
    cmds.delete(cmds.parentConstraint(midLoc,elbowctrl,mo=False,w=1))
    
    cmds.delete(upLimb['constraints'][1])
    cmds.parentConstraint(cmds.listRelatives(elbowctrl,c=True)[0],upLimb['locsList'][0],mo=True,w=1)
    
    cmds.delete(downLimb['constraints'][0])
    cmds.parentConstraint(cmds.listRelatives(elbowctrl,c=True)[0],downLimb['locsList'][2],mo=True,w=1)
    
    cmds.parentConstraint(cmds.listRelatives(upLimb['middleCtrl'],p=True)[0],upctrl,mo=True,w=1)
    cmds.parentConstraint(cmds.listRelatives(upctrl,c=True)[0],upLimb['middleCtrl'],mo=True,w=1)
    
    cmds.parentConstraint(cmds.listRelatives(downLimb['middleCtrl'],p=True)[0],downctrl,mo=True,w=1)
    cmds.parentConstraint(cmds.listRelatives(downctrl,c=True)[0],downLimb['middleCtrl'],mo=True,w=1)
    
    cmds.pointConstraint(lista[1],lista[2],elbowctrl,mo=False,w=1)
    cmds.orientConstraint(lista[1],elbowctrl,mo=True,w=1)
    
    upJntGrp = cmds.listRelatives(upLimb['skinJointsList'][0],p=True,f=True)
    downJntGrp = cmds.listRelatives(downLimb['skinJointsList'][0],p=True,f=True)
    
    limbJoints = list(upLimb['skinJointsList'])
    limbJoints.extend(downLimb['skinJointsList'])
    
    jntGrp = cmds.group(limbJoints,n=prefix+nome.lower()+'_jnts_grp')
    
    for i in range(len(limbJoints)):
        limbJoints[i] = cmds.rename(limbJoints[i],prefix+nome.lower()+'_'+`i+1`+'_jnt')
        cmds.addAttr(limbJoints[i], longName="dpAR_joint", attributeType='float', keyable=False)
    
    scaleGrp = cmds.group(upLimb['scaleGrp'],downLimb['scaleGrp'],jntGrp,n=prefix+nome.lower()+'_ribbon_scale_grp')
    cmds.setAttr(upLimb['scaleGrp']+'.v',cmds.getAttr(upLimb['finalGrp']+'.v'))
    cmds.setAttr(downLimb['scaleGrp']+'.v',cmds.getAttr(downLimb['finalGrp']+'.v'))
    
    cmds.delete(upJntGrp,downJntGrp)
    
    staticGrp = cmds.group(upLimb['finalGrp'],downLimb['finalGrp'],n=prefix+nome.lower()+'_ribbon_static_grp')
    
    ctrlsGrp = cmds.group(upctrl,downctrl,elbowctrl,n=prefix+nome.lower()+'_ctrls_grp')
    
    cmds.delete(midLoc,auxLoc)
    
    # organizing joint nomenclature ('_jnt', '_jxt') and skin attributes (".dpAR_joint")
    # in order to quickly skin using dpAR_UI
    for item in lista[:-1]:
        #fix joint name suffix
        if '_jnt' in item:
            # remove dpAR skin attribute
            try:
                cmds.deleteAttr(item+".dpAR_joint")
            except:
                pass
            # rename joint
            cmds.rename(item,item.replace('_jnt','_jxt'))
            
    
    # not used this mirror by dpAR system because each module guide will create each own mirror
    if mirror:
        jnt = None
        if cmds.objExists(iniJnt.replace('jxt','jnt').replace('L_','R_')):
            jnt = iniJnt.replace('jxt','jnt').replace('L_','R_')
        else:
            jnt = iniJnt.replace('L_','R_')
        newOri = cmds.duplicate(oriLoc,rr=True)
        auxgrp = cmds.group(em=True,name='mirroraux_grp')
        
        cmds.parent(newOri,auxgrp)
        
        cmds.setAttr(auxgrp+'.sx',-1)
        cmds.parent(newOri,w=True)
        cmds.delete(auxgrp)
        grp = cmds.group(em=True,n='mirrorauxGrp')
        cmds.delete(cmds.parentConstraint(newOri,grp,mo=False,w=1))
        cmds.parent(newOri,grp)
        cmds.makeIdentity(newOri,a=1,s=1)
        
        addRibbonToLimb(prefix=prefix.replace('L_','R_'),nome=nome,oriLoc=newOri,iniJnt=jnt,num=num,mirror=False)
        
        cmds.delete(grp)
    return {'scaleGrp':scaleGrp,'staticGrp':staticGrp,'ctrlsGrp':ctrlsGrp}
    
def createBendCtrl(nome='bend_ctrl', r=1, zero=True):
    curve = cmds.curve(n=nome,d=1,p=[(-1.5*r,0,0),(-1.06066*r,0,-1.06066*r),(0,0,-1.5*r),(1.06066*r,0,-1.06066*r),(1.5*r,0,0),(1.06066*r,0,1.06066*r),(0,0,1.5*r),(-1.06066*r,0,1.06066*r),(-1.5*r,0,0),(-1.06066*r,0,-1.06066*r)])
    cmds.setAttr(curve+'.rz',90)
    cmds.makeIdentity(curve,a=1)
    if zero:
        curve = cmds.group(curve, n=nome+'_grp')
    return curve
    
def createElbowCtrl(nome='limb_ctrl', r=1,zero=True):
    curve = cmds.curve(n=nome,d=1,p=[(-2*r,0,-1*r),(-1*r,0,-1*r),(-1*r,0,-2*r),(1*r,0,-2*r),(1*r,0,-1*r),(2*r,0,-1*r),(2*r,0,1*r),(1*r,0,1*r),(1*r,0,2*r),(-1*r,0,2*r),(-1*r,0,1*r),(-2*r,0,1*r),(-2*r,0,-1*r),(-1*r,0,-1*r)])
    cmds.setAttr(curve+'.rz',90)
    cmds.makeIdentity(curve,a=1)
    if zero:
        curve = cmds.group(curve, n=nome+'_grp')
    return curve
    
#function to create the ribbon
def createRibbon(axis=(0,0,1),name='xxxx',horizontal=False, numJoints=3,guias=None, v=True):
        retDict = {}
        
        #define variables
        top_loc = []
        mid_loc = []
        bttm_loc = []
        rb_jnt = []
        drv_jnt =[]
        fols = []
        aux_jnt = []
        ribbon = ''
        #create a nurbsPlane based in the choose orientation option
        if horizontal:
            ribbon =cmds.nurbsPlane(ax=axis,w=numJoints,lr=(1/float(numJoints)),d=3,u=numJoints,v=1,ch=0,name=name+'_plane')[0]
            cmds.rebuildSurface(ribbon,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=0,kc=0,sv=1,du=3,dv=1,tol=0.01,fr=0,dir=1) 
        else:
            ribbon =cmds.nurbsPlane(ax=axis,w=1,lr=numJoints,d=3,u=1,v=numJoints,ch=0,name=name+'_plane')[0]
            cmds.rebuildSurface(ribbon,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=0,kc=0,su=1,du=1,dv=3,tol=0.01,fr=0,dir=0) 
        # make this ribbonNurbsPlane as not skinable from dpAR_UI:
        cmds.addAttr(ribbon, longName="doNotSkinIt", attributeType="bool", keyable=True)
        cmds.setAttr(ribbon+".doNotSkinIt", 1)
        #call the function to create follicles and joint in the nurbsPlane
        results = createFollicles(rib=ribbon,num=numJoints,name=name,horizontal=horizontal)
        rb_jnt = results[0]
        fols = results[1]
        #create locator controls for the middle of the ribbon
        mid_loc.append(cmds.spaceLocator(name=name+'_mid_pos_loc')[0])
        mid_loc.append(cmds.spaceLocator(name=name+'_mid_aim_loc')[0])
        mid_loc.append(cmds.spaceLocator(name=name+'_mid_off_loc')[0])
        mid_loc.append(cmds.spaceLocator(name=name+'_mid_up_loc')[0])
        #parent correctly the middle locators
        cmds.parent(mid_loc[2],mid_loc[1],relative=True)
        cmds.parent(mid_loc[1],mid_loc[0],relative=True)
        cmds.parent(mid_loc[3],mid_loc[0],relative=True)
        #create the locators controls for the top of the ribbon
        top_loc.append(cmds.spaceLocator(name=name+'_top_pos_loc')[0])
        top_loc.append(cmds.spaceLocator(name=name+'_top_aim_loc')[0])
        top_loc.append(cmds.spaceLocator(name=name+'_top_up_loc')[0])
        #parent correctly the top locators
        cmds.parent(top_loc[1],top_loc[0],relative=True)
        cmds.parent(top_loc[2],top_loc[0],relative=True)
        #create the locators for the end of the ribbon
        bttm_loc.append(cmds.spaceLocator(name=name+'_bttm_pos_loc')[0])
        bttm_loc.append(cmds.spaceLocator(name=name+'_bttm_aim_loc')[0])
        bttm_loc.append(cmds.spaceLocator(name=name+'_bttm_up_loc')[0])
        #parent correctly the bottom locators
        cmds.parent(bttm_loc[1],bttm_loc[0],relative=True)
        cmds.parent(bttm_loc[2],bttm_loc[0],relative=True)
        
        #put the top locators in the same place of the top joint
        cmds.parent(top_loc[0],fols[len(fols)-1],relative=True)
        cmds.parent(top_loc[0],w=True)
        
        #put the bottom locators in the same place of the bottom joint
        cmds.parent(bttm_loc[0],fols[0],relative=True)
        cmds.parent(bttm_loc[0],w=True)
        cmds.select(clear=True)
        
        #create the joints that will be used to control the ribbon
        drv_jnt = cmds.duplicate([rb_jnt[0],rb_jnt[(len(rb_jnt)-1)/2],rb_jnt[len(rb_jnt)-1]])
        dup = cmds.duplicate([drv_jnt[0],drv_jnt[2]])
        drv_jnt.append(dup[0])
        drv_jnt.append(dup[1])
        #cmds.parent(drv_jnt,w=True)
        for jnt in drv_jnt:
            cmds.joint(jnt,e=True,oj='none',ch=True,zso=True);
            cmds.setAttr(jnt+'.radius',cmds.getAttr(jnt+'.radius')+0.5)
        #rename created joints
        drv_jnt[0] = cmds.rename(drv_jnt[0],name+'_drv_bttm_jxt')
        drv_jnt[1] = cmds.rename(drv_jnt[1],name+'_drv_mid_jxt')
        drv_jnt[2] = cmds.rename(drv_jnt[2],name+'_drv_top_jxt')
        drv_jnt[3] = cmds.rename(drv_jnt[3],name+'_drv_bttm_end')
        drv_jnt[4] = cmds.rename(drv_jnt[4],name+'_drv_top_end')
        
        #place joints correctly accordaly with the user options choose
        if (horizontal and axis==(1,0,0)) or (horizontal and axis==(0,0,1)):
            cmds.setAttr(bttm_loc[2]+'.translateY',2)
            cmds.setAttr(top_loc[2]+'.translateY',2)
            cmds.setAttr(mid_loc[3]+'.translateY',2)
        elif (horizontal and axis==(0,1,0)) or (not horizontal and axis==(1,0,0)):
            cmds.setAttr(bttm_loc[2]+'.translateZ',2)
            cmds.setAttr(top_loc[2]+'.translateZ',2)
            cmds.setAttr(mid_loc[3]+'.translateZ',2)
        elif not horizontal and axis==(0,1,0) or (not horizontal and axis==(0,0,1)):
            cmds.setAttr(bttm_loc[2]+'.translateX',2)
            cmds.setAttr(top_loc[2]+'.translateX',2)
            cmds.setAttr(mid_loc[3]+'.translateX',2)
        #create auxiliary joints that will be used to control the ribbon
        aux_jnt.append(cmds.duplicate(drv_jnt[1],name=name+'_jxt_rot')[0])
        cmds.setAttr(aux_jnt[0]+'.jointOrient', 0,0,0)
        aux_jnt.append(cmds.duplicate(aux_jnt[0],name=name+'_jxt_rot_end')[0])
        
        cmds.parent(aux_jnt[1],mid_loc[3])
        cmds.setAttr(aux_jnt[1]+'.translate',0,0,0)
        cmds.parent(aux_jnt[1],aux_jnt[0])
        cmds.parent(mid_loc[3],aux_jnt[1])
        #calculate the adjust for the new chain position
        dist=float(numJoints)/2.0
        end_dist = (1/float(numJoints))
        cmds.parent(drv_jnt[3],drv_jnt[0])
        cmds.parent(drv_jnt[4],drv_jnt[2])
        
        #adjust the joints orientation and position based in the options choose from user
        if horizontal and axis==(1,0,0):
            cmds.setAttr(drv_jnt[0]+'.jointOrient', 0,90,0)
            cmds.setAttr(drv_jnt[2]+'.jointOrient', 0,90,0)
        
            cmds.setAttr(drv_jnt[0]+'.tz',-dist)
            cmds.setAttr(drv_jnt[3]+'.tz',end_dist*dist)
            cmds.setAttr(drv_jnt[2]+'.tz',dist)
            cmds.setAttr(drv_jnt[4]+'.tz',-end_dist*dist)
            
        elif horizontal and axis==(0,1,0):
            cmds.setAttr(drv_jnt[0]+'.jointOrient', 0,0,0)
            cmds.setAttr(drv_jnt[2]+'.jointOrient', 0,0,0)
            
            cmds.setAttr(drv_jnt[0]+'.tx',-dist)
            cmds.setAttr(drv_jnt[3]+'.tx',end_dist*dist)
            cmds.setAttr(drv_jnt[2]+'.tx',dist)
            cmds.setAttr(drv_jnt[4]+'.tx',-end_dist*dist)
        
        elif horizontal and axis==(0,0,1):
            cmds.setAttr(drv_jnt[0]+'.jointOrient', 0,0,0)
            cmds.setAttr(drv_jnt[2]+'.jointOrient', 0,0,0)
            
            cmds.setAttr(drv_jnt[0]+'.tx',-dist)
            cmds.setAttr(drv_jnt[3]+'.tx',end_dist*dist)
            cmds.setAttr(drv_jnt[2]+'.tx',dist)
            cmds.setAttr(drv_jnt[4]+'.tx',-end_dist*dist)
        
        elif not horizontal and axis==(1,0,0):
            cmds.setAttr(drv_jnt[0]+'.jointOrient', 0,0,-90)
            cmds.setAttr(drv_jnt[2]+'.jointOrient', 0,0,-90)
        
            cmds.setAttr(drv_jnt[0]+'.ty',-dist)
            cmds.setAttr(drv_jnt[3]+'.ty',end_dist*dist)
            cmds.setAttr(drv_jnt[2]+'.ty',dist)
            cmds.setAttr(drv_jnt[4]+'.ty',-end_dist*dist)
            
        elif not horizontal and axis==(0,1,0):
            cmds.setAttr(drv_jnt[0]+'.jointOrient', 0,90,0)
            cmds.setAttr(drv_jnt[2]+'.jointOrient', 0,90,0)
        
            cmds.setAttr(drv_jnt[0]+'.tz',-dist)
            cmds.setAttr(drv_jnt[3]+'.tz',end_dist*dist)
            cmds.setAttr(drv_jnt[2]+'.tz',dist)
            cmds.setAttr(drv_jnt[4]+'.tz',-end_dist*dist)
            
        elif not horizontal and axis==(0,0,1):
            cmds.setAttr(drv_jnt[0]+'.jointOrient', 0,0,-90)
            cmds.setAttr(drv_jnt[2]+'.jointOrient', 0,0,-90)
        
            cmds.setAttr(drv_jnt[0]+'.ty',-dist)
            cmds.setAttr(drv_jnt[3]+'.ty',end_dist*dist)
            cmds.setAttr(drv_jnt[2]+'.ty',dist)
            cmds.setAttr(drv_jnt[4]+'.ty',-end_dist*dist)
        
        #fix the control locators position and orientation
        cmds.parent(top_loc[0],drv_jnt[2])
        cmds.setAttr(top_loc[0]+'.translate',0,0,0)
        cmds.parent(top_loc[0],w=True)
        cmds.setAttr(top_loc[0]+'.rotate',0,0,0)
        
        cmds.parent(bttm_loc[0],drv_jnt[0])
        cmds.setAttr(bttm_loc[0]+'.translate',0,0,0)
        cmds.parent(bttm_loc[0],w=True)
        cmds.setAttr(bttm_loc[0]+'.rotate',0,0,0)    
        
        cmds.parent(drv_jnt[2],top_loc[1])
        cmds.parent(drv_jnt[1],mid_loc[2])
        cmds.parent(drv_jnt[0],bttm_loc[1])
         
        cmds.parent(aux_jnt[0],mid_loc[0])
        #create a nurbs control in order to be used in the ribbon offset
        mid_ctrl = cmds.circle (c=(0,0,0),nr=(1,0,0),name=name+'_mid_ctrl')[0]
        midCtrl = mid_ctrl
        mid_ctrl = cmds.group(n=mid_ctrl+'_grp',em=True)
        cmds.delete(cmds.parentConstraint(midCtrl,mid_ctrl,mo=0))
        cmds.parent(midCtrl,mid_ctrl)
        
        #adjust the realtionship between the locators
        cmds.parent(mid_ctrl,mid_loc[2],r=True)
        cmds.parent(drv_jnt[1],midCtrl)
        cmds.parent([top_loc[2],mid_loc[3],bttm_loc[2]],w=True)
        cmds.makeIdentity(top_loc[0], apply=True)
        cmds.makeIdentity(mid_loc[0], apply=True)
        cmds.makeIdentity(bttm_loc[0], apply=True)
        cmds.parent(top_loc[2],top_loc[0])
        cmds.parent(bttm_loc[2],bttm_loc[0])
        cmds.parent(mid_loc[3],aux_jnt[1]) 
        #create needed constraints in the locators in order to set the top always follow, to the base always aim the middle, to the middle always aim the top
        cmds.aimConstraint(drv_jnt[1],bttm_loc[1],offset=(0,0,0),weight=1,aimVector=(1,0,0),upVector=(0,0,1),worldUpType='object',worldUpObject=bttm_loc[2])
        cmds.aimConstraint(top_loc[0],mid_loc[1],offset=(0,0,0),weight=1,aimVector=(1,0,0),upVector=(0,0,1),worldUpType='object',worldUpObject=mid_loc[3])
        cmds.aimConstraint(drv_jnt[1],top_loc[1],offset=(0,0,0),weight=1,aimVector=(-1,0,0),upVector=(0,0,1),worldUpType='object',worldUpObject=top_loc[2])
        
        #create a point and orient constraint for the middel control
        cmds.pointConstraint(top_loc[0],bttm_loc[0],mid_loc[0],offset=(0,0,0),weight=1)
        ori = cmds.orientConstraint(top_loc[0],bttm_loc[0],aux_jnt[0],offset=(0,0,0),weight=1)
        
        #fix group hierarchy
        i = 0
        for jnt in rb_jnt:
            cmds.makeIdentity(jnt,a=True)
            cmds.parentConstraint(fols[i],jnt,w=1)
            i = i + 1
        
        locatorsGrp = cmds.group(bttm_loc[0],top_loc[0],mid_loc[0],n=name+'_loc_grp')
        skinJntGrp = cmds.group(rb_jnt,n=name+'_jnt_grp')
        finalSystemGrp = cmds.group(ribbon,locatorsGrp,skinJntGrp,n=name+'_ribbonSystem_grp')
        
        #do the controller joints skin and the ribbon
        ribbonShape = cmds.listRelatives(ribbon, shapes=True)
        skin = cmds.skinCluster(drv_jnt[0:3], ribbonShape, tsb=True,mi=2, dr=1)
        
        #skin presets for the ribbon (that's amazing!)
        if not horizontal:
            if numJoints == 3:
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][5]',tv=(drv_jnt[2],1))
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][4]',tv=[(drv_jnt[2],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][3]',tv=[(drv_jnt[2],0.2),(drv_jnt[1],0.8)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][2]',tv=[(drv_jnt[0],0.2),(drv_jnt[1],0.8)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][1]',tv=[(drv_jnt[0],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][0]',tv=(drv_jnt[0],1))

            elif numJoints == 5:
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][7]',tv=(drv_jnt[2],1))
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][6]',tv=[(drv_jnt[2],0.80),(drv_jnt[1],0.2)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][5]',tv=[(drv_jnt[2],0.5),(drv_jnt[1],0.5)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][4]',tv=[(drv_jnt[2],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][3]',tv=[(drv_jnt[0],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][2]',tv=[(drv_jnt[0],0.5),(drv_jnt[1],0.5)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][1]',tv=[(drv_jnt[0],0.8),(drv_jnt[1],0.2)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][0]',tv=(drv_jnt[0],1))
            elif numJoints == 7:
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][9]',tv=(drv_jnt[2],1))
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][8]',tv=[(drv_jnt[2],0.85),(drv_jnt[1],0.15)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][7]',tv=[(drv_jnt[2],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][6]',tv=[(drv_jnt[2],0.35),(drv_jnt[1],0.65)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][5]',tv=[(drv_jnt[2],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][4]',tv=[(drv_jnt[0],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][3]',tv=[(drv_jnt[0],0.35),(drv_jnt[1],0.65)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][2]',tv=[(drv_jnt[0],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][1]',tv=[(drv_jnt[0],0.85),(drv_jnt[1],0.15)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0:1][0]',tv=(drv_jnt[0],1))
        else:
            if numJoints == 3:
                cmds.skinPercent(skin[0],ribbon + '.cv[5][0:1]',tv=(drv_jnt[2],1))
                cmds.skinPercent(skin[0],ribbon + '.cv[4][0:1]',tv=[(drv_jnt[2],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[3][0:1]',tv=[(drv_jnt[2],0.2),(drv_jnt[1],0.8)])
                cmds.skinPercent(skin[0],ribbon + '.cv[2][0:1]',tv=[(drv_jnt[0],0.2),(drv_jnt[1],0.8)])
                cmds.skinPercent(skin[0],ribbon + '.cv[1][0:1]',tv=[(drv_jnt[0],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0][0:1]',tv=(drv_jnt[0],1))
            elif numJoints == 5:
                cmds.skinPercent(skin[0],ribbon + '.cv[7][0:1]',tv=(drv_jnt[2],1))
                cmds.skinPercent(skin[0],ribbon + '.cv[6][0:1]',tv=[(drv_jnt[2],0.80),(drv_jnt[1],0.2)])
                cmds.skinPercent(skin[0],ribbon + '.cv[5][0:1]',tv=[(drv_jnt[2],0.5),(drv_jnt[1],0.5)])
                cmds.skinPercent(skin[0],ribbon + '.cv[4][0:1]',tv=[(drv_jnt[2],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[3][0:1]',tv=[(drv_jnt[0],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[2][0:1]',tv=[(drv_jnt[0],0.5),(drv_jnt[1],0.5)])
                cmds.skinPercent(skin[0],ribbon + '.cv[1][0:1]',tv=[(drv_jnt[0],0.8),(drv_jnt[1],0.2)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0][0:1]',tv=(drv_jnt[0],1))
            elif numJoints == 7:
                cmds.skinPercent(skin[0],ribbon + '.cv[9][0:1]',tv=(drv_jnt[2],1))
                cmds.skinPercent(skin[0],ribbon + '.cv[8][0:1]',tv=[(drv_jnt[2],0.85),(drv_jnt[1],0.15)])
                cmds.skinPercent(skin[0],ribbon + '.cv[7][0:1]',tv=[(drv_jnt[2],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[6][0:1]',tv=[(drv_jnt[2],0.35),(drv_jnt[1],0.65)])
                cmds.skinPercent(skin[0],ribbon + '.cv[5][0:1]',tv=[(drv_jnt[2],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[4][0:1]',tv=[(drv_jnt[0],0.25),(drv_jnt[1],0.75)])
                cmds.skinPercent(skin[0],ribbon + '.cv[3][0:1]',tv=[(drv_jnt[0],0.35),(drv_jnt[1],0.65)])
                cmds.skinPercent(skin[0],ribbon + '.cv[2][0:1]',tv=[(drv_jnt[0],0.6),(drv_jnt[1],0.4)])
                cmds.skinPercent(skin[0],ribbon + '.cv[1][0:1]',tv=[(drv_jnt[0],0.85),(drv_jnt[1],0.15)])
                cmds.skinPercent(skin[0],ribbon + '.cv[0][0:1]',tv=(drv_jnt[0],1))
        constr = []
        if guias:
            top = guias[0]
            bottom = guias[1]
            constr.append(cmds.parentConstraint(top,bttm_loc[0],mo=False))
            constr.append(cmds.parentConstraint(bottom,top_loc[0],mo=False))
        
        #fix orientation issues
        cmds.delete(ori)
        cmds.orientConstraint(bttm_loc[0],aux_jnt[0],weight=0.5, mo=True)
        
        #fix loc_grp scale
        if guias:
            from math import sqrt,pow
            auxLoc1 = cmds.spaceLocator(name='auxLoc1')[0]
            auxLoc2 = cmds.spaceLocator(name='auxLoc2')[0]
            cmds.delete(cmds.parentConstraint(top,auxLoc1,mo=False,w=1))
            cmds.delete(cmds.parentConstraint(bottom,auxLoc2,mo=False,w=1))
            a = cmds.xform(auxLoc1,ws=True,translation=True,q=True)
            b = cmds.xform(auxLoc2,ws=True,translation=True,q=True)
            
            dist = sqrt(pow(a[0]-b[0],2.0)+pow(a[1]-b[1],2.0)+pow(a[2]-b[2],2.0))
            scale = dist/float(numJoints)
            
            cmds.setAttr(locatorsGrp+'.s',scale,scale,scale)
        
            cmds.delete(auxLoc1,auxLoc2)
        
        ribbonShape = cmds.listRelatives(ribbon,s=True,f=True)[0]
        
        cmds.setAttr(ribbonShape+'.castsShadows', 0)
        cmds.setAttr(ribbonShape+'.receiveShadows', 0)
        cmds.setAttr(ribbonShape+'.motionBlur', 0)
        cmds.setAttr(ribbonShape+'.primaryVisibility', 0)
        cmds.setAttr(ribbonShape+'.smoothShading', 0)
        cmds.setAttr(ribbonShape+'.visibleInReflections', 0)
        cmds.setAttr(ribbonShape+'.visibleInRefractions', 0)
        cmds.setAttr(ribbonShape+'.doubleSided', 0)
        
        retDict['name'] = name
        retDict['locsList'] = [top_loc[0],mid_loc[0],bttm_loc[0]]
        retDict['skinJointsList'] =  rb_jnt
        retDict['scaleGrp'] = locatorsGrp
        retDict['finalGrp'] = finalSystemGrp
        retDict['middleCtrl'] = mid_ctrl
        retDict['constraints'] = constr
        cmds.setAttr(finalSystemGrp+'.v',v)
        return retDict
            
#function to create follicles and joints
def createFollicles(rib, num, pad = 0.5, name='xxxx', horizontal=False): 
    #define variables
    jnts = []
    fols = []
    #create joints and follicles based in the choose options from user
    if horizontal:
        #calcule the position of the first follicle
        passo = (1/float(num))/2.0;
        for i in range(num):
            #create the follicle and do correct connections to link it to the 
            folShape = cmds.createNode('follicle',name=name+'_%d_folShape'%i)
            folTrans = cmds.rename(cmds.listRelatives(folShape, p=1)[0],name+'_%d_fol'%i)         
            fols.append(folTrans)
            cmds.connectAttr(rib+'.worldMatrix[0]', folShape+'.inputWorldMatrix')
            cmds.connectAttr(rib+'.local', folShape+'.inputSurface')
            cmds.connectAttr(folShape+'.outTranslate', folTrans+'.translate')
            cmds.connectAttr(folShape+'.outRotate', folTrans+'.rotate')
            cmds.setAttr(folShape+'.parameterU', passo)
            cmds.setAttr(folShape+'.parameterV', 0.5) 
            #create the joint in the follicle
            cmds.select(cl=True)
            jnts.append(cmds.joint(n=name+'_%d_jnt'%i))
            cmds.setAttr(jnts[i]+'.jointOrient',0,0,0)
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
            folShape = cmds.createNode('follicle',name=name+'_%d_folShape'%i)
            folTrans = cmds.rename(cmds.listRelatives(folShape, p=1)[0],name+'_%d_fol'%i)
            fols.append(folTrans)
            cmds.connectAttr(rib+'.worldMatrix[0]', folShape+'.inputWorldMatrix')
            cmds.connectAttr(rib+'.local', folShape+'.inputSurface')
            cmds.connectAttr(folShape+'.outTranslate', folTrans+'.translate')
            cmds.connectAttr(folShape+'.outRotate', folTrans+'.rotate')
            cmds.setAttr(folShape+'.parameterU', 0.5)   
            cmds.setAttr(folShape+'.parameterV', passo) 
            #create the joint in the follicle
            cmds.select(cl=True)
            jnts.append(cmds.joint(n=name+'_%d_jnt'%i))
            cmds.setAttr(jnts[i]+'.jointOrient',0,0,0)
            cmds.select(cl=True)
            #calculate the first follicle position
            passo+=(1/float(num))
        results = [jnts, fols]
    #return the created joints and follicles
    cmds.parent(fols,rib)
    return results