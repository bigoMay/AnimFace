'''

Miguel Ramos Carretero
Bournemouth University 2018

Maya/Python script:
Group the markers created in five groups.

Plugin version for Maya. 

'''

import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds

'''
Create a floating joint (not parented)
'''
def parentMarker(name, groupname):
    cmds.parent(name+"_JNT",groupname)
    
'''
Create the forehead markers
'''
def parentTopMarkers():
    cmds.group(em=True, name="TopMarkers", parent="Markers")
    parentMarker("Eyebrow_Center", "TopMarkers")
    parentMarker("ForeHead_L", "TopMarkers")
    parentMarker("ForeHead_M", "TopMarkers")
    parentMarker("ForeHead_R", "TopMarkers")
    parentMarker("Leye_Up", "TopMarkers")
    parentMarker("Leyebrow_Inside", "TopMarkers")
    parentMarker("Leyebrow_M", "TopMarkers")
    parentMarker("Leyebrow_Outside", "TopMarkers")
    parentMarker("Reye_Up", "TopMarkers")
    parentMarker("Reyebrow_Inside", "TopMarkers")
    parentMarker("Reyebrow_M", "TopMarkers")
    parentMarker("Reyebrow_Outside", "TopMarkers")

'''
Create the eyebrows markers
'''  
def parentTopMiddleMarkers():
    cmds.group(em=True, name="TopMiddleMarkers", parent="Markers")
    parentMarker("Leye_Inside","TopMiddleMarkers")
    parentMarker("Leye_Outside","TopMiddleMarkers")
    parentMarker("Reye_Inside","TopMiddleMarkers")
    parentMarker("Reye_Outside","TopMiddleMarkers")

'''
Create the eyes markers
'''
def parentMiddleMarkers():
    cmds.group(em=True, name="MiddleMarkers", parent="Markers")
    parentMarker("Lcheek_Up","MiddleMarkers")
    parentMarker("Leye_Down","MiddleMarkers")
    parentMarker("Mouth_Up","MiddleMarkers")
    parentMarker("Mouth_UpL1","MiddleMarkers")
    parentMarker("Mouth_UpR1","MiddleMarkers")
    parentMarker("NoseHead","MiddleMarkers")
    parentMarker("NoseHead_L","MiddleMarkers")
    parentMarker("NoseHead_R","MiddleMarkers")
    parentMarker("NoseTop","MiddleMarkers")
    parentMarker("Rcheek_Up","MiddleMarkers")
    parentMarker("Reye_Down","MiddleMarkers")

'''
Create the nose markers
'''
def parentMiddleBottomMarkers():
    
    cmds.group(em=True, name="MiddleBottomMarkers", parent="Markers")
    parentMarker("Lcheek_Down","MiddleBottomMarkers")
    parentMarker("Lcheek_Outside","MiddleBottomMarkers")
    parentMarker("Mouth_Lend","MiddleBottomMarkers")
    parentMarker("Mouth_Rend","MiddleBottomMarkers")
    parentMarker("Rcheek_Down","MiddleBottomMarkers")
    parentMarker("Rcheek_Outside","MiddleBottomMarkers")

'''
Create the mouth markers
'''
def parentBottomMarkers():
    cmds.group(em=True, name="BottomMarkers", parent="Markers")
    parentMarker("Chin","BottomMarkers")
    parentMarker("Chin_L1","BottomMarkers")
    parentMarker("Chin_L2","BottomMarkers")
    parentMarker("Chin_R1","BottomMarkers")
    parentMarker("Chin_R2","BottomMarkers")
    parentMarker("Mouth_Down","BottomMarkers")
    parentMarker("Mouth_DownL","BottomMarkers")
    parentMarker("Mouth_DownR","BottomMarkers")

'''
Entry point of the program
'''
def main():
    parentTopMarkers()
    parentTopMiddleMarkers()
    parentMiddleMarkers()
    parentMiddleBottomMarkers()
    parentBottomMarkers()

'''
Plugin functionality
'''
def maya_useNewAPI():
    '''
    The presence of this function tells Maya that the plugin produces, and expects to be passed, objects created using the Maya Python API 2.0.
    '''
    pass
    
# command
class PyGroupMarkersCmd(om.MPxCommand):
    kPluginCmdName = "pyGroupMarkers"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return PyGroupMarkersCmd()

    def doIt(self, args):
        main()

# Initialize the plug-in
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(
            PyGroupMarkersCmd.kPluginCmdName, PyGroupMarkersCmd.cmdCreator
        )
    except:
        sys.stderr.write(
            "Failed to register command: %s\n" % PyGroupMarkersCmd.kPluginCmdName
        )
        raise

# Uninitialize the plug-in
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(PyGroupMarkersCmd.kPluginCmdName)
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % PyGroupMarkersCmd.kPluginCmdName
        )
        raise
