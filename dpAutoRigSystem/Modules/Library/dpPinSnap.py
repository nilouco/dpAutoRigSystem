# importing libraries:
from maya import cmds
from ...Extras import dpCustomAttr

DP_PINSNAP_VERSION = 1.0



class PinSnapClass(object):
    def __init__(self, dpUIinst, netName, worldRef, pinOffsetCtrl, dpDev=False, *args):
        # defining variables:
        self.netName = netName
        self.worldRef = worldRef
        self.pinOffsetCtrl = pinOffsetCtrl
        
        # store data
        self.pinState = round(cmds.getAttr(self.pinOffsetCtrl+".pin"), 0)
        self.pinSnapNet = cmds.createNode("network", name=self.netName+"_PinSnap_Net")
        self.customAttr = dpCustomAttr.CustomAttr(dpUIinst, ui=False, verbose=False)
        self.customAttr.addAttr(0, [self.pinSnapNet]) #dpID

        self.dpID = cmds.getAttr(self.pinSnapNet+".dpID")
        self.storePinSnapData()
        if dpDev:
            cmds.scriptJob(attributeChange=(self.pinOffsetCtrl+".pin", self.jobChangedPin), killWithScene=True, compressUndo=True)
        else:
            self.generateScriptNode()
    

    ###
    # ---------------------------------
    # Code to development or creating a new module instance
    ###

    def storePinSnapData(self, *args):
        """ Store all the needed attributes data to pin snap into the network node.
        """
        # add
        cmds.addAttr(self.pinSnapNet, longName="dpNetwork", attributeType="bool")
        cmds.addAttr(self.pinSnapNet, longName="dpPinSnapNet", attributeType="bool")
        cmds.addAttr(self.pinSnapNet, longName="dpPinNetName", dataType="string")
        cmds.addAttr(self.pinSnapNet, longName="pinState", attributeType="short")
        cmds.addAttr(self.pinSnapNet, longName="worldRef", attributeType="message")
        cmds.addAttr(self.pinSnapNet, longName="pinOffsetCtrl", attributeType="message")
        cmds.addAttr(self.worldRef, longName="pinSnapNet", attributeType="message")
        # set
        cmds.setAttr(self.pinSnapNet+".dpNetwork", 1)
        cmds.setAttr(self.pinSnapNet+".dpPinSnapNet", 1)
        cmds.setAttr(self.pinSnapNet+".dpPinNetName", self.netName, type="string")
        cmds.setAttr(self.pinSnapNet+".pinState", self.pinState)
        # connect
        cmds.connectAttr(self.pinSnapNet+".message", self.worldRef+".pinSnapNet", force=True)
        cmds.connectAttr(self.worldRef+".message", self.pinSnapNet+".worldRef", force=True)
        cmds.connectAttr(self.pinOffsetCtrl+".message", self.pinSnapNet+".pinOffsetCtrl", force=True)


    ###
    # ---------------------------------
    # Code to use by the scriptJob included in the scriptNode
    ###

    def jobChangedPin(self, *args):
        """ Just call pinSnap function to set as well.
        """
        self.worldRef = cmds.listConnections(self.pinSnapNet+".worldRef")[0]
        self.pinSnapState = cmds.getAttr(self.pinSnapNet+".pinState")
        currentValue = cmds.getAttr(self.pinOffsetCtrl+".pin")
        self.pinOffsetCtrl = cmds.listConnections(self.pinSnapNet+".pinOffsetCtrl")[0]
        ctrlPos = self.getPosition(self.pinOffsetCtrl)[0]
        ctrlRot = self.getPosition(self.pinOffsetCtrl)[1]
        if self.pinSnapState == 0: #pinOn
            if currentValue == 1:
                pinConnections = cmds.listConnections(self.pinOffsetCtrl+".pin", source=False, destination=True, plugs=True)
                self.changePinSnapAttr(0, False)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, False)
                self.changePinSnapAttr(1, True)
                self.snapPin(self.pinOffsetCtrl, ctrlPos, ctrlRot)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, True)
        else: #pinOff
            if currentValue == 0:
                pinConnections = cmds.listConnections(self.pinOffsetCtrl+".pin", source=False, destination=True, plugs=True)
                self.changePinSnapAttr(1, False)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, False)
                self.changePinSnapAttr(0, True)
                self.snapPin(self.pinOffsetCtrl, ctrlPos, ctrlRot)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, True)


    def reconnectingAttr(self, pinOffsetCtrl, connections, connect, *args):
        if connections:
            for connection in connections:
                if connect == True:
                    cmds.connectAttr(pinOffsetCtrl+".pin", connection)
                else:
                    cmds.disconnectAttr(pinOffsetCtrl+".pin", connection)

    def getPosition(self, pinOffsetCtrl, *args):
        self.pinOffsetCtrl = pinOffsetCtrl
        ctrlPos = cmds.xform(self.pinOffsetCtrl, query=True, worldSpace=True, translation=True)
        ctrlRot = cmds.xform(self.pinOffsetCtrl, query=True, worldSpace=True, rotation=True)
        return [ctrlPos, ctrlRot]

    def changePinSnapAttr(self, pinSnapValue, setState, *args):
        """ 0 = unpin offset ctrl
            1 = pin offset ctrl
        """
        cmds.setAttr(self.pinOffsetCtrl+".pin", pinSnapValue)
        if setState:
            self.pinSnapState = pinSnapValue
            cmds.setAttr(self.pinSnapNet+".pinState", pinSnapValue)

    def snapPin(self, pinOffsetCtrl, ctrlPos, ctrlRot, *args):
        """ Function to get offsetCtrl position, change attribute's connections and set offsetCtrl position
        """
        selection = cmds.ls(sl=True)
        self.pinOffsetCtrl = pinOffsetCtrl
        cmds.xform(self.pinOffsetCtrl, worldSpace=True, translation=ctrlPos)
        cmds.xform(self.pinOffsetCtrl, worldSpace=True, rotation=ctrlRot)
        cmds.select(selection)


    ###
    # ---------------------------------
    # Code to scriptNode
    ###

    def generateScriptNode(self, *args):
        """ Create a scriptNode to store the ikFkSnap code into it.
        """
        pinSnapCode = '''
from maya import cmds

DP_PINSNAP_VERSION = '''+str(DP_PINSNAP_VERSION)+'''

class PinSnap(object):
    def __init__(self, pinSnapNet, *args):
        self.pinSnapNet = pinSnapNet
        self.reloadNetData()
        cmds.scriptJob(attributeChange=(self.pinOffsetCtrl+".pin", self.jobChangedPin), killWithScene=True, compressUndo=True)
        
    def reloadNetData(self):
        self.worldRef = cmds.listConnections(self.pinSnapNet+".worldRef")[0]
        self.pinSnapState = cmds.getAttr(self.pinSnapNet+".pinState")
        self.pinOffsetCtrl = cmds.listConnections(self.pinSnapNet+".pinOffsetCtrl")[0]
        
    def jobChangedPin(self, *args):
        """ Just call pinSnap function to set as well.
        """
        self.worldRef = cmds.listConnections(self.pinSnapNet+".worldRef")[0]
        self.pinSnapState = cmds.getAttr(self.pinSnapNet+".pinState")
        currentValue = cmds.getAttr(self.pinOffsetCtrl+".pin")
        self.pinOffsetCtrl = cmds.listConnections(self.pinSnapNet+".pinOffsetCtrl")[0]
        ctrlPos = self.getPosition(self.pinOffsetCtrl)[0]
        ctrlRot = self.getPosition(self.pinOffsetCtrl)[1]
        if self.pinSnapState == 0: #pinOn
            if currentValue == 1:
                pinConnections = cmds.listConnections(self.pinOffsetCtrl+".pin", source=False, destination=True, plugs=True)
                self.changePinSnapAttr(0, False)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, False)
                self.changePinSnapAttr(1, True)
                self.snapPin(self.pinOffsetCtrl, ctrlPos, ctrlRot)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, True)
        else: #pinOff
            if currentValue == 0:
                pinConnections = cmds.listConnections(self.pinOffsetCtrl+".pin", source=False, destination=True, plugs=True)
                self.changePinSnapAttr(1, False)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, False)
                self.changePinSnapAttr(0, True)
                self.snapPin(self.pinOffsetCtrl, ctrlPos, ctrlRot)
                self.reconnectingAttr(self.pinOffsetCtrl, pinConnections, True)


    def reconnectingAttr(self, pinOffsetCtrl, connections, connect, *args):
        if connections:
            for connection in connections:
                if connect == True:
                    cmds.connectAttr(pinOffsetCtrl+".pin", connection)
                else:
                    cmds.disconnectAttr(pinOffsetCtrl+".pin", connection)

    def getPosition(self, pinOffsetCtrl, *args):
        self.pinOffsetCtrl = pinOffsetCtrl
        ctrlPos = cmds.xform(self.pinOffsetCtrl, query=True, worldSpace=True, translation=True)
        ctrlRot = cmds.xform(self.pinOffsetCtrl, query=True, worldSpace=True, rotation=True)
        return [ctrlPos, ctrlRot]

    def changePinSnapAttr(self, pinSnapValue, setState, *args):
        """ 0 = unpin offset ctrl
            1 = pin offset ctrl
        """
        cmds.setAttr(self.pinOffsetCtrl+".pin", pinSnapValue)
        if setState:
            self.pinSnapState = pinSnapValue
            cmds.setAttr(self.pinSnapNet+".pinState", pinSnapValue)

    def snapPin(self, pinOffsetCtrl, ctrlPos, ctrlRot, *args):
        """ Function to get offsetCtrl position, change attribute's connections and set offsetCtrl position
        """
        selection = cmds.ls(sl=True)
        self.pinOffsetCtrl = pinOffsetCtrl
        cmds.xform(self.pinOffsetCtrl, worldSpace=True, translation=ctrlPos)
        cmds.xform(self.pinOffsetCtrl, worldSpace=True, rotation=ctrlRot)
        cmds.select(selection)

# fire scriptNode
for net in cmds.ls(type="network"):
    if cmds.objExists(net+".dpNetwork") and cmds.getAttr(net+".dpNetwork") == 1:
        if cmds.objExists(net+".dpPinSnapNet") and cmds.getAttr(net+".dpPinSnapNet") == 1:
            if cmds.objExists(net+".dpID") and cmds.getAttr(net+".dpID") == "'''+self.dpID+'''":
                PinSnap(net)
'''
        sn = cmds.scriptNode(name=self.netName+'_PinSnap_SN', sourceType='python', scriptType=2, beforeScript=pinSnapCode)
        cmds.addAttr(self.pinSnapNet, longName="pinSnapScriptNode", attributeType="message")
        cmds.addAttr(sn, longName="pinSnapNet", attributeType="message")
        cmds.connectAttr(sn+".message", self.pinSnapNet+".pinSnapScriptNode", force=True)
        cmds.connectAttr(self.pinSnapNet+".message", sn+".pinSnapNet", force=True)
        cmds.scriptNode(sn, executeBefore=True)