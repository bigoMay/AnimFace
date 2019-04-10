'''

Miguel Ramos Carretero
Bournemouth University 2018

Maya/Python script:
Create a set of markers for facial animation with MoCap.

Plugin version for Maya.

'''

import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds

'''
Create a floating joint (not parented)
'''
def createFloatingJoint(point, name, col):
    cmds.select(clear=True)
    cmds.joint(p=point, n=name+"_JNT", rad=1)
    cmds.setAttr("|"+name+"_JNT"+".overrideEnabled",1)
    cmds.setAttr("|"+name+"_JNT"+".overrideColor",col)
    cmds.parent(name+"_JNT","Markers")
    
'''
Create the forehead markers
'''
def createForeheadMarkers(col=18):
    createFloatingJoint((0,24,-1), "ForeHead_M", col)
    createFloatingJoint((4,23,-2), "ForeHead_L", col)
    createFloatingJoint((-4,23,-2), "ForeHead_R", col)

'''
Create the eyebrows markers
'''  
def createEyebrowsMarkers(col=14):
    createFloatingJoint((2,20,0), "Leyebrow_Inside", col)
    createFloatingJoint((4,21,-1), "Leyebrow_M", col)
    createFloatingJoint((6,19,-2), "Leyebrow_Outside", col)
    createFloatingJoint((0,19,0), "Eyebrow_Center", col)
    createFloatingJoint((-2,20,0), "Reyebrow_Inside", col)
    createFloatingJoint((-4,21,-1), "Reyebrow_M", col)
    createFloatingJoint((-6,19,-2), "Reyebrow_Outside", col)

'''
Create the eyes markers
'''
def createEyesMarkers(col=17):
    createFloatingJoint((4,18,-1), "Leye_Up", col)
    createFloatingJoint((4,14,-1), "Leye_Down", col)
    createFloatingJoint((2,16,0), "Leye_Inside", col)
    createFloatingJoint((6,16,-2), "Leye_Outside", col)
    createFloatingJoint((-4,18,-1), "Reye_Up", col)
    createFloatingJoint((-4,14,-1), "Reye_Down", col)
    createFloatingJoint((-2,16,0), "Reye_Inside", col)
    createFloatingJoint((-6,16,-2), "Reye_Outside", col)

'''
Create the nose markers
'''
def createNoseMarkers(col=20):
    createFloatingJoint((0,16,1), "NoseTop", col)
    createFloatingJoint((0,14,3), "NoseHead", col)
    createFloatingJoint((2,13,1), "NoseHead_L", col)
    createFloatingJoint((-2,13,1), "NoseHead_R", col)

'''
Create the mouth markers
'''
def createMouthMarkers(col=13):
    createFloatingJoint((0,11,2), "Mouth_Up", col)
    createFloatingJoint((0,8,1), "Mouth_Down", col)
    createFloatingJoint((2,11,1), "Mouth_UpL1", col)
    createFloatingJoint((3,10,0), "Mouth_Lend", col)
    createFloatingJoint((-2,11,1), "Mouth_UpR1", col)
    createFloatingJoint((-3,10,0), "Mouth_Rend", col)
    createFloatingJoint((2,8,0), "Mouth_DownL", col)
    createFloatingJoint((-2,8,0), "Mouth_DownR", col)

'''
Create the chin markers
'''
def createChinMarkers(col=26):
    createFloatingJoint((0,5,0), "Chin", col)
    createFloatingJoint((-3,6,-1), "Chin_R1", col)
    createFloatingJoint((-5,8,-4), "Chin_R2", col)
    createFloatingJoint((3,6,-1), "Chin_L1", col)
    createFloatingJoint((5,8,-4), "Chin_L2", col)

'''
Create the cheek markers
'''
def createCheekMarkers(col=21):
    createFloatingJoint((5,12,-2), "Lcheek_Up", col)
    createFloatingJoint((5,10,-3), "Lcheek_Down", col)
    createFloatingJoint((7,12,-7), "Lcheek_Outside", col)
    createFloatingJoint((-5,12,-2), "Rcheek_Up", col)
    createFloatingJoint((-5,10,-3), "Rcheek_Down", col)
    createFloatingJoint((-7,12,-7), "Rcheek_Outside", col)

'''
Entry point of the program
'''
def main():
    cmds.group(em=True, name="Markers")
    createForeheadMarkers()
    createEyebrowsMarkers()
    createEyesMarkers()
    createNoseMarkers()
    createMouthMarkers()
    createChinMarkers()
    createCheekMarkers()
    
'''
Plugin functionality
'''
def maya_useNewAPI():
    '''
    The presence of this function tells Maya that the plugin produces, and expects to be passed, objects created using the Maya Python API 2.0.
    '''
    pass
    
# command
class PyCreateMarkersCmd(om.MPxCommand):
    kPluginCmdName = "pyCreateMarkers"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return PyCreateMarkersCmd()

    def doIt(self, args):
        main()

# Initialize the plug-in
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(
            PyCreateMarkersCmd.kPluginCmdName, PyCreateMarkersCmd.cmdCreator
        )
    except:
        sys.stderr.write(
            "Failed to register command: %s\n" % PyCreateMarkersCmd.kPluginCmdName
        )
        raise

# Uninitialize the plug-in
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(PyCreateMarkersCmd.kPluginCmdName)
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % PyCreateMarkersCmd.kPluginCmdName
        )
        raise
