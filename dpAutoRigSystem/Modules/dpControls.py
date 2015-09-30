# importing libraries:
import maya.cmds as cmds


# CONTROLS functions:
def colorShape(objList, color):
    """Create a color override for all shapes from a objList.
    """
    i = color
    # find the color index by names:
    if color   == 'yellow':   i = 17
    elif color == 'red':      i = 13
    elif color == 'blue':     i = 6
    elif color == 'cian':     i = 18
    elif color == 'green':    i = 7
    elif color == 'darkRed':  i = 4
    elif color == 'darkBlue': i = 15
    elif color == 'white':    i = 16
    elif color == 'black':    i = 1
    elif color == 'gray':     i = 3
    elif color == 'none':     i = 0
    # find shapes and apply the color override:
    shapeTypeList = ['nurbsCurve', 'nurbsSurface', 'mesh', 'subdiv']
    if objList:
        for objName in objList:
            objType = cmds.objectType(objName)
            # verify if the object is the shape type:
            if objType in shapeTypeList:
                # set override as enable:
                cmds.setAttr(objName+".overrideEnabled", 1)
                # set color override:
                cmds.setAttr(objName+".overrideColor", i)
            # verify if the object is a transform type:
            elif objType == "transform":
                # find all shapes children of the transform object:
                shapeList = cmds.listRelatives(objName, shapes=True, children=True)
                if shapeList:
                    for shape in shapeList:
                        # set override as enable:
                        cmds.setAttr(shape+".overrideEnabled", 1)
                        # set color override:
                        cmds.setAttr(shape+".overrideColor", i)


def renameShape(transformList):
    """Find shapes, rename they to Shapes and return the results.
    """
    resultList = []
    for transform in transformList:
        # list all children shapes:
        childShapeList = cmds.listRelatives(transform, shapes=True, children=True)
        if childShapeList:
            # verify if there is only one shape and return it renamed:
            if len(childShapeList) == 1:
                shape = cmds.rename(childShapeList[0], transform+"Shape")
                cmds.select(clear=True)
                resultList.append(shape)
            # else rename and return one list of renamed shapes:
            elif len(childShapeList) > 1:
                childShapeList = []
                for child in childShapeList:
                    shape = cmds.rename(child, transform+"Shape")
                    resultList.append(shape)
                cmds.select(clear=True)
        else:
            print "There are not children shape to rename inside of:", transform
    return resultList

    
def directConnect(fromObj, toObj, attrList=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], f=True):
    """Connect attributes from list directely between two objects given.
    """
    if cmds.objExists(fromObj) and cmds.objExists(toObj):
        for attr in attrList:
            try:
                # connect attributes:
                cmds.connectAttr(fromObj+"."+attr, toObj+"."+attr, force=f)
            except:
                print "Error: Cannot connect", toObj, ".", attr, "directely."
    
    
def setLockHide(objList, attrList, l=True, k=False):
    """Set lock or hide to attributes for object in lists.
    """
    if objList and attrList:
        for obj in objList:
            for attr in attrList:
                try:
                    # set lock and hide of given attributes:
                    cmds.setAttr(obj+"."+attr, lock=l, keyable=k)
                except:
                    print "Error: Cannot set", obj, ".", attr, "as lock=", l, "and keyable=", k


def setNotRenderable(objList):
    """Receive a list of objects, find its shapes if necessary and set all as not renderable.
    """
    # declare a list of attributes for render:
    renderAttrList = ["castsShadows", "receiveShadows", "motionBlur", "primaryVisibility", "smoothShading", "visibleInReflections", "visibleInRefractions", "doubleSided", "miTransparencyCast", "miTransparencyReceive", "miReflectionReceive", "miRefractionReceive", "miFinalGatherCast", "miFinalGatherReceive"]
    shapeTypeList = ['nurbsCurve', 'nurbsSurface', 'mesh', 'subdiv']
    # find all children shapes:
    if objList:
        for obj in objList:
            objType = cmds.objectType(obj)
            # verify if the object is the shape type:
            if objType in shapeTypeList:
                # set attributes as not renderable:
                for attr in renderAttrList:
                    try:
                        cmds.setAttr(obj+"."+attr, 0)
                    except:
                        #print "Error: Cannot set not renderable ", attr, "as zero for", obj
                        pass
            # verify if the object is a transform type:
            elif objType == "transform":
                # find all shapes children of the transform object:
                shapeList = cmds.listRelatives(obj, shapes=True, children=True)
                if shapeList:
                    for shape in shapeList:
                        # set attributes as not renderable:
                        for attr in renderAttrList:
                            try:
                                cmds.setAttr(shape+"."+attr, 0)
                            except:
                                #print "Error: Cannot set not renderable ", attr, "as zero for", shape
                                pass


def distanceBet(a, b, name="temp_DistBet", keep=False):
    """ Creates a distance between node for 2 objects a and b.
        Keeps them in the scene or delete.
        Returns the distance value only in case of not keeping distBet node or
        a list of distance value, distanceNode and two nulls used to calculate.
    """
    if cmds.objExists(a) and cmds.objExists(b):
        if keep:
            # create nulls:
            nullA = cmds.group(empty=True, name=a+"_DistBetNull")
            nullB = cmds.group(empty=True, name=b+"_DistBetNull")
            nullC = cmds.group(empty=True, name=b+"_DistBetNull_OrigRef")
            cmds.pointConstraint(a, nullA, maintainOffset=False, name=nullA+"_ParentConstraint")
            cmds.pointConstraint(b, nullB, maintainOffset=False, name=nullB+"_ParentConstraint")
            tempToDel = cmds.pointConstraint(b, nullC, maintainOffset=False)
            cmds.delete(tempToDel)
            pointConst = cmds.pointConstraint(b, nullC, nullB, maintainOffset=False, name=nullB+"_ParentConstraint")[0]
            # create distanceBetween node:
            distBet = cmds.shadingNode("distanceBetween", n=name, asUtility=True)
            # connect aPos to the distance between point1:
            cmds.connectAttr(nullA+".tx", distBet+".point1X")
            cmds.connectAttr(nullA+".ty", distBet+".point1Y")
            cmds.connectAttr(nullA+".tz", distBet+".point1Z")
            # connect bPos to the distance between point2:
            cmds.connectAttr(nullB+".tx", distBet+".point2X")
            cmds.connectAttr(nullB+".ty", distBet+".point2Y")
            cmds.connectAttr(nullB+".tz", distBet+".point2Z")
            dist = cmds.getAttr(distBet+".distance")
            return [dist, distBet, nullA, nullB, nullC, pointConst]
        else:
            # get xform datas:
            aPos = cmds.xform(a, query=True, worldSpace=True, translation=True)
            bPos = cmds.xform(b, query=True, worldSpace=True, translation=True)
            # create distanceBetween node:
            distBet = cmds.shadingNode("distanceBetween", n=name, asUtility=True)
            # set aPos to the distance between point1:
            cmds.setAttr(distBet+".point1X", aPos[0])
            cmds.setAttr(distBet+".point1Y", aPos[1])
            cmds.setAttr(distBet+".point1Z", aPos[2])
            # set bPos to the distance between point2:
            cmds.setAttr(distBet+".point2X", bPos[0])
            cmds.setAttr(distBet+".point2Y", bPos[1])
            cmds.setAttr(distBet+".point2Z", bPos[2])
            dist = cmds.getAttr(distBet+".distance")
            cmds.delete(distBet)
            return [dist, None, None, None, None, None]


def middlePoint(a, b, createLocator=False):
    """ Find the point location in the middle of two items.
        Return the middle point position as a vector and a locator in it if want.
    """
    if cmds.objExists(a) and cmds.objExists(b):
        # get xform datas:
        aPos = cmds.xform(a, query=True, worldSpace=True, rotatePivot=True)
        bPos = cmds.xform(b, query=True, worldSpace=True, rotatePivot=True)
        # calculating the result position:
        resultPosX = ( aPos[0] + bPos[0] )/2
        resultPosY = ( aPos[1] + bPos[1] )/2
        resultPosZ = ( aPos[2] + bPos[2] )/2
        resultPos = [resultPosX, resultPosY, resultPosZ]
        if createLocator:
            middleLoc = cmds.spaceLocator(name=a+"_"+b+"_Middle_Loc", position=resultPos)[0]
            cmds.xform(middleLoc, centerPivots=True)
            return [resultPos, middleLoc]
        return[resultPos]


def createSimpleRibbon(name='noodle', totalJoints=6):
    """ Creates a Ribbon system.
        Receives the total number of joints to create.
        Returns the ribbon nurbs plane, the joints groups and joints created.
    """
    # create a ribbonNurbsPlane:
    ribbonNurbsPlane = cmds.nurbsPlane(name=name+"RibbonNurbsPlane", constructionHistory=False, object=True, polygon=0, axis=(0, 1, 0), width=1, lengthRatio=8, patchesV=totalJoints)[0]
    # get the ribbonNurbsPlane shape:
    ribbonNurbsPlaneShape = cmds.listRelatives(ribbonNurbsPlane, shapes=True, children=True)[0]
    # make this ribbonNurbsPlane as template, invisible and not renderable:
    cmds.setAttr(ribbonNurbsPlane+".template", 1)
    cmds.setAttr(ribbonNurbsPlane+".visibility", 0)
    setNotRenderable([ribbonNurbsPlaneShape])
    # make this ribbonNurbsPlane as not skinable from dpAR_UI:
    cmds.addAttr(ribbonNurbsPlane, longName="doNotSkinIt", attributeType="bool", keyable=True)
    cmds.setAttr(ribbonNurbsPlane+".doNotSkinIt", 1)
    # create groups to be used as a root of the ribbon system:
    ribbonGrp = cmds.group(ribbonNurbsPlane, n=name+"_RibbonJoint_Grp")
    # create joints:
    jointList, jointGrpList = [], []
    for j in range(totalJoints+1):
        # create pointOnSurfaceInfo:
        infoNode = cmds.createNode('pointOnSurfaceInfo', name=name+"_POSI"+str(j))
        # setting parameters worldSpace, U and V:
        cmds.connectAttr(ribbonNurbsPlaneShape + ".worldSpace[0]", infoNode + ".inputSurface")
        cmds.setAttr(infoNode + ".parameterV", ((1/float(totalJoints))*j) )
        cmds.setAttr(infoNode + ".parameterU", 0.5)
        # create and parent groups to calculate:
        posGrp = cmds.group(n=name+"Pos"+str(j)+"_Grp", empty=True)
        upGrp  = cmds.group(n=name+"Up"+str(j)+"_Grp", empty=True)
        aimGrp = cmds.group(n=name+"Aim"+str(j)+"_Grp", empty=True)
        cmds.parent(upGrp, aimGrp, posGrp, relative=True)
        # connect groups translations:
        cmds.connectAttr(infoNode + ".position", posGrp + ".translate", force=True)
        cmds.connectAttr(infoNode + ".tangentU", upGrp + ".translate", force=True)
        cmds.connectAttr(infoNode + ".tangentV", aimGrp + ".translate", force=True)
        # create joint:
        cmds.select(clear=True)
        joint = cmds.joint(name=name+str(j)+"_Jnt")
        jointList.append(joint)
        cmds.addAttr(joint, longName='dpAR_joint', attributeType='float', keyable=False)
        # parent the joint to the groups:
        cmds.parent(joint, posGrp, relative=True)
        jointGrp = cmds.group(joint, name=name+"Joint"+str(j)+"_Grp")
        jointGrpList.append(jointGrp)
        # create aimConstraint from aimGrp to jointGrp:
        cmds.aimConstraint(aimGrp, jointGrp, offset=(0, 0, 0), weight=1, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=upGrp, n=name+"Ribbon"+str(j)+"_AimConstraint" )
        # parent this ribbonPos to the ribbonGrp:
        cmds.parent(posGrp, ribbonGrp, absolute=True)
    return [ribbonNurbsPlane, ribbonNurbsPlaneShape, jointGrpList, jointList]


def cvLocator(ctrlName, r=0.3):
    """Create and return a cvLocator curve to be usually used in the guideSystem and the clusterHandle to shapeSize.
    """
    # create curve:
    curve = cmds.curve(n=ctrlName, d=1, p=[(0, 0, r), (0, 0, -r), (0, 0, 0), (r, 0, 0), (-r, 0, 0), (0, 0, 0), (0, r, 0), (0, -r, 0)] )
    # create an attribute to be used as guide by module:
    cmds.addAttr(curve, longName="nJoint", attributeType='long')
    cmds.setAttr(curve+".nJoint", 1)
    # rename curveShape:
    renameShape([curve])
    # colorize curveShape:
    colorShape([curve], 'blue')
    # shapeSize setup:
    shapeSizeCluster = shapeSizeSetup(curve)
#    return curve
    return [curve, shapeSizeCluster]


def cvJointLoc(ctrlName, r=0.3, extraLocs=False):
    """Create and return a cvJointLocator curve to be usually used in the guideSystem and the clusterHandle to shapeSize.
    """
    # create locator curve:
    cvLoc = cmds.curve(n=ctrlName+"_CvLoc", d=1, p=[(0, 0, r), (0, 0, -r), (0, 0, 0), (r, 0, 0), (-r, 0, 0), (0, 0, 0), (0, r, 0), (0, -r, 0)] )
    # create arrow curves:
    cvArrow1 = cmds.curve(n=ctrlName+"_CvArrow1", d=3, p=[(-0.1*r, 0.9*r, 0.2*r), (-0.1*r, 0.9*r, 0.23*r), (-0.1*r, 0.9*r, 0.27*r), (-0.1*r, 0.9*r, 0.29*r), (-0.1*r, 0.9*r, 0.3*r), (-0.372*r, 0.9*r, 0.24*r), (-0.45*r, 0.9*r, -0.13*r), (-0.18*r, 0.9*r, -0.345*r), (-0.17*r, 0.9*r, -0.31*r), (-0.26*r, 0.9*r, -0.41*r), (-0.21*r, 0.9*r, -0.41*r), (-0.05*r, 0.9*r, -0.4*r), (0, 0.9*r, -0.4*r), (-0.029*r, 0.9*r, -0.33*r), (-0.048*r, 0.9*r, -0.22*r), (-0.055*r, 0.9*r, -0.16*r), (-0.15*r, 0.9*r, -0.272*r), (-0.12*r, 0.9*r, -0.27*r), (-0.35*r, 0.9*r, -0.1*r), (-0.29*r, 0.9*r, 0.15*r), (-0.16*r, 0.9*r, 0.21*r), (-0.1*r, 0.9*r, 0.2*r)] )
    cvArrow2 = cmds.curve(n=ctrlName+"_CvArrow2", d=3, p=[(0.1*r, 0.9*r, -0.2*r), (0.1*r, 0.9*r, -0.23*r), (0.1*r, 0.9*r, -0.27*r), (0.1*r, 0.9*r, -0.29*r), (0.1*r, 0.9*r, -0.3*r), (0.372*r, 0.9*r, -0.24*r), (0.45*r, 0.9*r, 0.13*r), (0.18*r, 0.9*r, 0.345*r), (0.17*r, 0.9*r, 0.31*r), (0.26*r, 0.9*r, 0.41*r), (0.21*r, 0.9*r, 0.41*r), (0.05*r, 0.9*r, 0.4*r), (0, 0.9*r, 0.4*r), (0.029*r, 0.9*r, 0.33*r), (0.048*r, 0.9*r, 0.22*r), (0.055*r, 0.9*r, 0.16*r), (0.15*r, 0.9*r, 0.272*r), (0.12*r, 0.9*r, 0.27*r), (0.35*r, 0.9*r, 0.1*r), (0.29*r, 0.9*r, -0.15*r), (0.16*r, 0.9*r, -0.21*r), (0.1*r, 0.9*r, -0.2*r)] )
    cvArrow3 = cmds.curve(n=ctrlName+"_CvArrow3", d=3, p=[(-0.1*r, -0.9*r, 0.2*r), (-0.1*r, -0.9*r, 0.23*r), (-0.1*r, -0.9*r, 0.27*r), (-0.1*r, -0.9*r, 0.29*r), (-0.1*r, -0.9*r, 0.3*r), (-0.372*r, -0.9*r, 0.24*r), (-0.45*r, -0.9*r, -0.13*r), (-0.18*r, -0.9*r, -0.345*r), (-0.17*r, -0.9*r, -0.31*r), (-0.26*r, -0.9*r, -0.41*r), (-0.21*r, -0.9*r, -0.41*r), (-0.05*r, -0.9*r, -0.4*r), (0, -0.9*r, -0.4*r), (-0.029*r, -0.9*r, -0.33*r), (-0.048*r, -0.9*r, -0.22*r), (-0.055*r, -0.9*r, -0.16*r), (-0.15*r, -0.9*r, -0.272*r), (-0.12*r, -0.9*r, -0.27*r), (-0.35*r, -0.9*r, -0.1*r), (-0.29*r, -0.9*r, 0.15*r), (-0.16*r, -0.9*r, 0.21*r), (-0.1*r, -0.9*r, 0.2*r)] )
    cvArrow4 = cmds.curve(n=ctrlName+"_CvArrow4", d=3, p=[(0.1*r, -0.9*r, -0.2*r), (0.1*r, -0.9*r, -0.23*r), (0.1*r, -0.9*r, -0.27*r), (0.1*r, -0.9*r, -0.29*r), (0.1*r, -0.9*r, -0.3*r), (0.372*r, -0.9*r, -0.24*r), (0.45*r, -0.9*r, 0.13*r), (0.18*r, -0.9*r, 0.345*r), (0.17*r, -0.9*r, 0.31*r), (0.26*r, -0.9*r, 0.41*r), (0.21*r, -0.9*r, 0.41*r), (0.05*r, -0.9*r, 0.4*r), (0, -0.9*r, 0.4*r), (0.029*r, -0.9*r, 0.33*r), (0.048*r, -0.9*r, 0.22*r), (0.055*r, -0.9*r, 0.16*r), (0.15*r, -0.9*r, 0.272*r), (0.12*r, -0.9*r, 0.27*r), (0.35*r, -0.9*r, 0.1*r), (0.29*r, -0.9*r, -0.15*r), (0.16*r, -0.9*r, -0.21*r), (0.1*r, -0.9*r, -0.2*r)] )
    cvArrow5 = cmds.curve(n=ctrlName+"_CvArrow5", d=1, p=[(0, 0, 1.2*r), (0.09*r, 0, 1*r), (-0.09*r, 0, 1*r), (0, 0, 1.2*r)] )
    cvArrow6 = cmds.curve(n=ctrlName+"_CvArrow6", d=1, p=[(0, 0, 1.2*r), (0, 0.09*r, 1*r), (0, -0.09*r, 1*r), (0, 0, 1.2*r)] )
    # rename curveShape:
    locArrowList = [cvLoc, cvArrow1, cvArrow2, cvArrow3, cvArrow4, cvArrow5, cvArrow6]
    renameShape(locArrowList)
    # create ball curve:
    cvTemplateBall = cvBall(ctrlName+"_CvBall", r=0.7*r)
    # parent shapes to transform:
    locCtrl = cmds.group(name=ctrlName, empty=True)
    ballChildrenList = cmds.listRelatives(cvTemplateBall, shapes=True, children=True)
    for ballChildren in ballChildrenList:
        cmds.setAttr(ballChildren+".template", 1)
        cmds.parent(ballChildren, locCtrl, relative=True, shape=True)
    cmds.delete(cvTemplateBall)
    for transform in locArrowList:
        cmds.parent( cmds.listRelatives(transform, shapes=True, children=True)[0], locCtrl, relative=True, shape=True )
        cmds.delete(transform)
    if extraLocs: # does not used yet.
        # create hided locators in order to them as upAimOrient and fromAimOrient to further joint:
        cvUpAim = cvLocator(ctrlName+"_CvUpAim", r=0.25)
        cmds.xform(cvUpAim, ws=True, a=True, t=(r, 0, 0))
        cmds.setAttr(cvUpAim+".visibility", 0)
        cvFrontAim = cvLocator(ctrlName+"_CvFrontAim", r=0.25)
        cmds.xform(cvFrontAim, ws=True, a=True, t=(0, 0, r))
        cmds.setAttr(cvFrontAim+".visibility", 0)
        cmds.parent(cvUpAim, cvFrontAim, locCtrl, relative=True)
    # create an attribute to be used as guide by module:
    cmds.addAttr(locCtrl, longName="nJoint", attributeType='long')
    cmds.setAttr(locCtrl+".nJoint", 1)
    # colorize curveShapes:
    colorShape([locCtrl], 'blue')
    # shapeSize setup:
    shapeSizeCluster = shapeSizeSetup(locCtrl)
    cmds.select(clear=True)
    return [locCtrl, shapeSizeCluster]


def cvBall(ctrlName, r=1):
    """Create and return a cvBall curve to be usually used in the ribbonSystem and the clusterHandle to shapeSize..
    """
    # create circles to get the shapes:
    ballX = cmds.circle(n=ctrlName+"_x", ch=False, o=True, nr=(1, 0, 0), d=3, s=8, radius=r)
    ballY = cmds.circle(n=ctrlName+"_y", ch=False, o=True, nr=(0, 1, 0), d=3, s=8, radius=r)
    ballZ = cmds.circle(n=ctrlName+"_z", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=r)
    # parent shapes to transform:
    ballCtrl = cmds.group(name=ctrlName, empty=True)
    cmds.parent( cmds.listRelatives(ballX, shapes=True, children=True)[0], ballCtrl, relative=True, shape=True)
    cmds.parent( cmds.listRelatives(ballY, shapes=True, children=True)[0], ballCtrl, relative=True, shape=True)
    cmds.parent( cmds.listRelatives(ballZ, shapes=True, children=True)[0], ballCtrl, relative=True, shape=True)
    # delete old x, y and z transforms:
    cmds.delete(ballX, ballY, ballZ)
    cmds.select(clear=True)
    return ballCtrl


def cvBox(ctrlName, r=1, h=-1):
    """Create and return a simple curve as a box control and the clusterHandle to shapeSize..
    """
    # verify height:
    if (h == -1):
        h = r
    # create curve:
    curve = cmds.curve(n=ctrlName, d=1, p=[(-r, -h, r), (-r, h, r), (r, h, r), (r, -h, r), (-r, -h, r), (-r, -h, -r), (-r, h, -r), (-r, h, r), (r, h, r), (r, h, -r), (r, -h, -r), (r, -h, r), (r, -h, -r), (-r, -h, -r), (-r, h, -r), (r, h, -r)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvHead(ctrlName, r=1):
    """Create a control to be used as a headControl.
    """
    # create a simple circle curve:
    curve = cmds.curve(n=ctrlName, d=3, p=[(0, -r, 0), (-0.5*r, -0.9*r, 0), (-1.3*r, -0.7*r, 0), (-2.5*r, 1.5*r, 0), (-1.7*r, 3.3*r, 0), (0, 3.3*r, 0), (1.7*r, 3.3*r, 0), (2.5*r, 1.5*r, 0), (1.3*r, -0.7*r, 0), (0.5*r, -0.9*r, 0), (0, -r, 0)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvClavicle(ctrlName, r=1):
    """Create a control to be used as a clavicle or hip control.
    """
    # create a simple circle curve:
    curve = cmds.curve(n=ctrlName, d=3, p=[(0, 0, 0), (0, 0.2*r, 0.1*r), (0, 1*r, 0.1*r), (0, 1.7*r, 0.7*r), (0, 2.1*r, 0), (0, 1.7*r, -0.7*r), (0, 1*r, -0.1*r), (0, 0.2*r, -0.1*r), (0, 0, 0)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvKnee(ctrlName, r=1):
    """Create a control to be used as a poleVector for Knee control.
    """
    # create a simple circle curve:
    curve = cmds.curve(n=ctrlName, d=3, p=[(0, -0.6*r, 0), (-0.2*r, -0.6*r, 0), (-0.5*r, -0.6*r, 0), (-0.2*r, 0, 0), (-0.5*r, 0.6*r, 0), (0, 0.8*r, 0), (0.5*r, 0.6*r, 0), (0.2*r, 0, 0), (0.5*r, -0.6*r, 0), (0.2*r, -0.6*r, 0), (0, -0.6*r, 0)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvElbow(ctrlName, r=1):
    """Create a control to be used as a poleVector for Elbow control.
    """
    # create a simple circle curve:
    curve = cmds.curve(n=ctrlName, d=3, p=[(0, -0.75*r, 0), (-0.1*r, -0.75*r, 0), (-0.25*r, -0.25*r, 0), (-r, 0, 0), (-0.25*r, 0.25*r, 0), (0, r, 0), (0.25*r, 0.25*r, 0), (r, 0, 0), (0.25*r, -0.25*r, 0), (0.1*r, -0.75*r, 0), (0, -0.75*r, 0)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvJaw(ctrlName, r=1):
    """Create a control to be used as a Jaw control.
    """
    # create a simple circle curve:
    curve = cmds.curve(n=ctrlName, d=3, p=[(0, -0.5*r, 1.5*r), (-0.1*r, -0.5*r, 1.5*r), (-0.5*r, -0.5*r, 1.4*r), (-0.9*r ,-0.5*r, 0.75*r), (-1.3*r, 0, -r), (0, 0, -0.5*r), (1.3*r, 0, -r), (0.9*r, -0.5*r, 0.75*r), (0.5*r, -0.5*r, 1.4*r), (0.1*r, -0.5*r, 1.5*r), (0, -0.5*r, 1.5*r)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvChin(ctrlName, r=1):
    """Create a control to be used as a Chin control.
    """
    # create a simple circle curve:
    curve = cmds.curve(n=ctrlName, d=3, p=[(0, 0.8*r, -0.5*r), (0, 0.9*r, -0.7*r), (0, 0, -0.5*r), (0, -0.8*r, -0.7*r), (0, -0.8*r, 1.4*r), (0, -0.3*r, 1.3*r), (0, 0, 1.2*r), (0, 0, 0), (0, 0.8*r, -0.3*r), (0, 0.8*r, -0.5*r)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvEyes(ctrlName, r=1, Le="L", Ri="R", eye="eye", pupil="pupil"):
    """Create a control to be used as a Chin control.
    """
    # create a simple circle curve:
    eyes = cmds.curve(n=ctrlName+eye+"_Ctrl", d=3, p=[(0, -0.4*r, 0), (-0.2*r, -0.5*r, 0), (-0.8*r, -0.6*r, 0), (-1.3*r, -0.1*r, 0), (-0.7*r, 0.7*r, 0), (0, 0.3*r, 0), (0.7*r, 0.7*r, 0), (1.3*r, -0.1*r, 0), (0.8*r, -0.6*r, 0), (0.2*r, -0.5*r, 0), (0, -0.4*r, 0)] )
    L_eye = cmds.curve(n=ctrlName+Le+"_"+eye+"_Ctrl", d=3, p=[(0.15*r, -0.1*r, 0), (0.1*r, 0.3*r, 0), (0.7*r, 0.5*r, 0), (r, 0, 0), (1.1*r, -0.2*r, 0), (0.5*r, -0.5*r, 0), (0.2*r, -0.2*r, 0), (0.15*r, -0.1*r, 0)] )
    R_eye = cmds.curve(n=ctrlName+Ri+"_"+eye+"_Ctrl", d=3, p=[(-0.15*r, -0.1*r, 0), (-0.1*r, 0.3*r, 0), (-0.7*r, 0.5*r, 0), (-r, 0, 0), (-1.1*r, -0.2*r, 0), (-0.5*r, -0.5*r, 0), (-0.2*r, -0.2*r, 0), (-0.15*r, -0.1*r, 0)] )
    L_pupil = cmds.curve(n=ctrlName+Le+"_"+pupil+"_Ctrl", d=3, p=[(0.5*r, -0.14*r, 0), (0.43*r, -0.13*r, 0), (0.36*r, -0.06*r, 0), (0.35*r, 0, 0), (0.38*r, 0.1*r, 0), (0.5*r, 0.15*r, 0), (0.65*r, 0.06*r, 0), (0.65*r, -0.1*r, 0), (0.53*r, -0.14*r, 0), (0.5*r, -0.14*r, 0)] )
    R_pupil = cmds.curve(n=ctrlName+Ri+"_"+pupil+"_Ctrl", d=3, p=[(-0.5*r, -0.14*r, 0), (-0.43*r, -0.13*r, 0), (-0.36*r, -0.06*r, 0), (-0.35*r, 0, 0), (-0.38*r, 0.1*r, 0), (-0.5*r, 0.15*r, 0), (-0.65*r, 0.06*r, 0), (-0.65*r, -0.1*r, 0), (-0.53*r, -0.14*r, 0), (-0.5*r, -0.14*r, 0)] )
    # center pivots and rename shapes:
    curveList = [eyes, L_eye, R_eye, L_pupil, R_pupil]
    for curve in curveList:
        cmds.xform(curve, preserve=True, centerPivots=True)
    renameShape(curveList)
    # parent correctly:
    cmds.parent(L_pupil, L_eye, r=True)
    cmds.parent(R_pupil, R_eye, r=True)
    cmds.parent(L_eye, R_eye, eyes, r=True)
    cmds.select(clear=True)
    return curveList
    

def cvNeck(ctrlName, r=1):
    """Create a control to be used as a Neck control.
    """
    # create a neck curve:
    curve = cmds.curve(n=ctrlName, d=1, p=[(0, 0, 0), (0, 0, -0.44*r), (0, 0, -0.9*r), (0, 0, -1.23*r), (-0.21*r, 0, -1.37*r), (-0.44*r, 0, -2*r), (0, 0, -2.2*r), (0.44*r, 0, -2*r), (0.21*r, 0, -1.37*r), (0, 0, -1.23*r), (0, 0.21*r, -1.37*r), (0, 0.44*r, -2*r), (0, 0, -2.2*r), (0, -0.44*r, -2*r), (0, -0.21*r, -1.37*r), (0, 0, -1.23*r)] )
    # rename curveShape:
    renameShape([curve])
    return curve
    

def cvFinger(ctrlName, r=1):
    """Create a control to be used as a Neck control.
    """
    # create a finger curve:
    curve = cmds.curve(n=ctrlName, d=1, p=[(0, 0, 0), (0.44*r, 0, 0), (0.9*r, 0, 0), (1.1*r, 0, 0), (1.37*r, -0.44*r, 0), (2*r, -0.44*r, 0), (2.2*r, 0, 0), (2*r, 0.44*r, 0), (1.37*r, 0.44*r, 0), (1.1*r, 0, 0), (1.37*r,0, 0.44*r), (2*r, 0, 0.44*r), (2.2*r, 0, 0), (2*r, 0, -0.44*r), (1.37*r, 0, -0.44*r), (1.1*r, 0, 0)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvSmile(ctrlName, r=1):
    """Create and return a cvSmile curve to be usually used in the face_Ctrl.
    """
    # create circles to get the shapes:
    face = cmds.circle(n=ctrlName+"_Face", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=r)
    lEye = cmds.circle(n=ctrlName+"_L_Eye", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=r*0.3)
    rEye = cmds.circle(n=ctrlName+"_R_Eye", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=r*0.3)
    mouth = cmds.circle(n=ctrlName+"_Mouth", ch=False, o=True, nr=(0, 0, 1), d=3, s=8, radius=r*0.5)
    # change circle shapes:
    cmds.setAttr(lEye[0]+".translateX", 0.4)
    cmds.setAttr(lEye[0]+".translateY", 0.3)
    cmds.setAttr(rEye[0]+".translateX", -0.4)
    cmds.setAttr(rEye[0]+".translateY", 0.3)
    cmds.setAttr(mouth[0]+".translateY", -0.3)
    cmds.makeIdentity(lEye[0], apply=True)
    cmds.makeIdentity(rEye[0], apply=True)
    cmds.makeIdentity(mouth[0], apply=True)
    cmds.move(-0.6, -0.4, 0, mouth[0]+"Shape.cv[3]")
    cmds.move(0.6, -0.4, 0, mouth[0]+"Shape.cv[7]")
    cmds.move(0.325, -0.225, 0, mouth[0]+"Shape.cv[0]")
    cmds.move(-0.325, -0.225, 0, mouth[0]+"Shape.cv[2]")
    cmds.move(0, -0.55, 0, mouth[0]+"Shape.cv[1]")
    # parent shapes to transform:
    smileCtrl = cmds.group(name=ctrlName, empty=True)
    cmds.parent( cmds.listRelatives(face, shapes=True, children=True)[0], smileCtrl, relative=True, shape=True)
    cmds.parent( cmds.listRelatives(lEye, shapes=True, children=True)[0], smileCtrl, relative=True, shape=True)
    cmds.parent( cmds.listRelatives(rEye, shapes=True, children=True)[0], smileCtrl, relative=True, shape=True)
    cmds.parent( cmds.listRelatives(mouth, shapes=True, children=True)[0], smileCtrl, relative=True, shape=True)
    # delete old x, y and z transforms:
    cmds.delete(face, lEye, rEye, mouth)
    cmds.select(clear=True)
    return smileCtrl


def cvCharacter(ctrlName, r=1):
    """Create a control like a mini character (minimim) to be used as an option_Ctrl.
    """
    # get radius by checking linear unit
    r = dpCheckLinearUnit(r)
    # create a minime curve:
    curve = cmds.curve(n=ctrlName, d=1, p=[(0, 9*r, 0), (1*r, 9*r, 0), (1.9*r, 8.2*r, 0), (1*r, 7*r, 0), (0.4*r, 6.6*r, 0), (0.4*r, 5.7*r, 0), (2.4*r, 5.45*r, 0), (3.8*r, 5.5*r, 0), (4.6*r, 6*r, 0), (5.8*r, 5.5*r, 0), (5.25*r, 4.6*r, 0), (4*r, 5*r, 0), (2.4*r, 4.9*r, 0), (1.6*r, 4.5*r, 0), (1.1*r, 3*r, 0), (1.5*r, 1.7*r, 0), (1.7*r, 0.5*r, 0), (3*r, 0.37*r, 0), (3.15*r, 0, 0), (1*r, 0, 0), (0.73*r, 1.5*r, 0), (0, 2.25*r, 0), (-0.73*r, 1.5*r, 0), (-1*r, 0, 0), (-3.15*r, 0, 0), (-3*r, 0.37*r, 0), (-1.7*r, 0.5*r, 0), (-1.5*r, 1.7*r, 0), (-1.1*r, 3*r, 0), (-1.6*r, 4.5*r, 0), (-2.4*r, 4.9*r, 0), (-4*r, 5*r, 0), (-5.25*r, 4.6*r, 0), (-5.8*r, 5.5*r, 0), (-4.6*r, 6*r, 0), (-3.8*r, 5.5*r, 0), (-2.4*r, 5.45*r, 0), (-0.4*r, 5.7*r, 0), (-0.4*r, 6.6*r, 0), (-1*r, 7*r, 0), (-1.9*r, 8.2*r, 0), (-1*r, 9*r, 0), (0, 9*r, 0)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def cvSquare(ctrlName, r=1):
    """Create and return a simple curve as a square control.
    """
    # create curve:
    curve = cmds.curve(n=ctrlName, d=1, p=[(-r, 0, r), (r, 0, r), (r, 0, -r), (-r, 0, -r), (-r, 0, r)] )
    # rename curveShape:
    renameShape([curve])
    return curve


def findHistory(objList, historyName):
    """Search and return the especific history of the listed objects.
    """
    if objList:
        foundHistoryList = []
        for objName in objList:
            # find historyName in the object's history:
            histList = cmds.listHistory(objName)
            for hist in histList:
                histType = cmds.objectType(hist)
                if histType == historyName:
                    foundHistoryList.append(hist)
        return foundHistoryList
    
    
def cvBaseGuide(ctrlName, r=1):
    """Create a control to be used as a Base Guide control.
        Returns the main control (circle) and the radius control in a list.
    """
    # get radius by checking linear unit
    r = dpCheckLinearUnit(r)
    # create a simple circle curve:
    circle = cmds.circle(n=ctrlName, ch=True, o=True, nr=(0, 0, 1), d=3, s=8, radius=r)[0]
    radiusCtrl = cmds.circle(n=ctrlName+"_RadiusCtrl", ch=True, o=True, nr=(0, 1, 0), d=3, s=8, radius=(r/4.0))[0]
    # rename curveShape:
    renameShape([circle, radiusCtrl])
    # configure system of limits and radius:
    cmds.setAttr(radiusCtrl+".translateX", r)
    cmds.parent(radiusCtrl, circle, relative=True)
    cmds.transformLimits(radiusCtrl, tx=(0.01, 1), etx=(True, False))
    setLockHide([radiusCtrl], ['ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
    # find makeNurbCircle history of the circles:
    historyList = findHistory([circle, radiusCtrl], 'makeNurbCircle')
    circleHistory     = historyList[0]
    radiusCtrlHistory = historyList[1]
    # rename and make a connection for circle:
    circleHistory = cmds.rename(circleHistory, circle+"_makeNurbCircle")
    cmds.connectAttr(radiusCtrl+".tx", circleHistory+".radius", force=True)
    radiusCtrlHistory = cmds.rename(radiusCtrlHistory, radiusCtrl+"_makeNurbCircle")
    # create a mutiplyDivide in order to automatisation the radius of the radiusCtrl:
    radiusCtrlMD = cmds.createNode('multiplyDivide', name=radiusCtrl+'_MD')
    cmds.connectAttr(radiusCtrl+'.translateX', radiusCtrlMD+'.input1X', force=True)
    cmds.setAttr(radiusCtrlMD+'.input2X', 0.15)
    cmds.connectAttr(radiusCtrlMD+".outputX", radiusCtrlHistory+".radius", force=True)
    # colorize curveShapes:
    colorShape([circle, radiusCtrl], 'yellow')
    cmds.select(clear=True)
    return [circle, radiusCtrl]


def setAndFreeze(nodeName="", tx=None, ty=None, tz=None, rx=None, ry=None, rz=None, sx=None, sy=None, sz=None, freeze=True):
    """This function set attribute values and do a freezeTransfomation.
    """
    if nodeName != "":
        attrNameList  = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        attrValueList = [tx, ty, tz, rx, ry, rz, sx, sy, sz]
        # setting attribute values:
        for v, attrValue in enumerate(attrValueList):
            if attrValue:
                try:
                    cmds.setAttr(nodeName+'.'+attrNameList[v], attrValue)
                except:
                    pass
        # looking the need of freeze:
        if freeze:
            freezeT = False
            freezeR = False
            freezeS = False
            if tx != None or ty != None or tz != None:
                freezeT = True
            if rx != None or ry != None or rz != None:
                freezeR = True
            if sx != None or sy != None or sz != None:
                freezeS = True
            try:
                cmds.makeIdentity(nodeName, apply=freeze, translate=freezeT, rotate=freezeR, scale=freezeS)
            except:
                pass


def dpCheckLinearUnit(origRadius, defaultUnit="centimeter"):
    """ Verify if the Maya linear unit is in Centimeter.
        Return the radius to the new unit size.

        WIP!
        Changing to shapeSize cluster setup
    """
    newRadius = origRadius
#    newRadius = 1
#    linearUnit = cmds.currentUnit(query=True, linear=True, fullName=True)
#    # centimeter
#    if linearUnit == defaultUnit:
#        newRadius = origRadius
#    elif linearUnit == "meter":
#        newRadius = origRadius*0.01
#    elif linearUnit == "millimeter":
#        newRadius = origRadius*10
#    elif linearUnit == "inch":
#        newRadius = origRadius*0.393701
#    elif linearUnit == "foot":
#        newRadius = origRadius*0.032808
#    elif linearUnit == "yard":
#        newRadius = origRadius*0.010936
    return newRadius


def shapeSizeSetup(transformNode):
    """ Find shapes, create a cluster deformer to all and set the pivot to transform pivot.
        Returns the created cluster.
    """
    clusterHandle = None
    childShapeList = cmds.listRelatives(transformNode, shapes=True, children=True)
    if childShapeList:
        thisNamespace = childShapeList[0].split(":")[0]
        cmds.namespace(set=thisNamespace, force=True)
        clusterName = transformNode.split(":")[1]+"_ShapeSizeCH"
        clusterHandle = cmds.cluster(childShapeList, name=clusterName)[1]
        cmds.setAttr(clusterHandle+".visibility", 0)
        cmds.xform(clusterHandle, scalePivot=(0, 0, 0), worldSpace=True)
        cmds.namespace(set=":")
    else:
        print "There are not children shape to create shapeSize setup of:", transformNode
    return clusterHandle