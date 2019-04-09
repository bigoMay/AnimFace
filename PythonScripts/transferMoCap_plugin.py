'''

Miguel Ramos Carretero
Bournemouth University 2018

Maya/Python script:
Transfer the MoCap animation to the facial markers.

Plugin version for Maya.

'''

import sys
import maya.api.OpenMaya as om 
import maya.cmds as cmds

kPluginCmdName = "pyTransferMoCap"

kShortFlag1Name = "-ff"
kLongFlag1Name = "-firstFrame"

kShortFlag2Name = "-lf"
kLongFlag2Name = "-lastFrame"

'''
Get the transform of a given object and returns it in a 3 element list
TODO: Find a way to import it from animateMesh.py directly.
'''
def getObjectPoint(obj):
    
    x = cmds.getAttr(obj+".translateX")
    y = cmds.getAttr(obj+".translateY")
    z = cmds.getAttr(obj+".translateZ")
    
    point = [x,y,z]
    
    return point

'''
Calculates the offset vector for each marker according to the mocap points
'''
def calibrateMarkers(markers, mocap, areDividedMarkers):
    
    markerGroupOffset = getObjectPoint(markers)
    mocapGroupOffset = getObjectPoint(mocap)
    
    markersList = []
    if (areDividedMarkers == True):
        markersParents = cmds.listRelatives(markers)
        for i in range (len(markersParents)):
            markersList += cmds.listRelatives(markersParents[i])
        markersList = sorted(markersList)
    else:
        markersList = cmds.listRelatives(markers)
    
    print(markersList)
    offsets = []
    
    for i in range (len(markersList)):
        
        markerPoint = getObjectPoint(markersList[i])
        mocapPoint = getObjectPoint(markersList[i][:-4])
        offset = [markerGroupOffset[0]+markerPoint[0]-
                        (mocapGroupOffset[0]+mocapPoint[0]),
                  markerGroupOffset[1]+markerPoint[1]-
                        (mocapGroupOffset[1]+mocapPoint[1]),
                  markerGroupOffset[2]+markerPoint[2]-
                        (mocapGroupOffset[2]+mocapPoint[2])]

        offsets.append(offset)
    
    return offsets

'''
Transfers the mocap animation into the markers for the given frame number
'''
def transferAnimation(markers, mocap, offsets, frameNumber, areDividedMarkers):
    
    cmds.autoKeyframe( state=True )

    markerGroupOffset = getObjectPoint(markers)
    mocapGroupOffset = getObjectPoint(mocap)
    
    markersList = []
    if (areDividedMarkers):
        markersParents = cmds.listRelatives(markers)
        for i in range (len(markersParents)):
            markersList += cmds.listRelatives(markersParents[i])
        markersList = sorted(markersList)
    else:
        markersList = cmds.listRelatives(markers)
    
    cmds.currentTime(frameNumber)
    
    for i in range (len(markersList)):
        
        mocapPoint = getObjectPoint(markersList[i][:-4])
                
        newMarkerPoint = [mocapPoint[0]+mocapGroupOffset[0]+offsets[i][0],
                          mocapPoint[1]+mocapGroupOffset[1]+offsets[i][1],
                          mocapPoint[2]+mocapGroupOffset[2]+offsets[i][2]]
        
        cmds.setAttr(markersList[i]+".translateX",
                        newMarkerPoint[0]-markerGroupOffset[0]);
        cmds.setAttr(markersList[i]+".translateY",
                        newMarkerPoint[1]-markerGroupOffset[1]);
        cmds.setAttr(markersList[i]+".translateZ",
                        newMarkerPoint[2]-markerGroupOffset[2]);
        
        cmds.setKeyframe(markersList[i])

'''
Entry point of the program
'''
def main(range1, range2):

    markersGroup = "Markers"
    mocapGroup = "MoCapData"

    offsets = calibrateMarkers(markersGroup, mocapGroup, True)
    print str(offsets)
    
    for i in range(range1,range2+1):
        transferAnimation(markersGroup, mocapGroup, offsets, i, True)

'''
Plugin functionality
'''
def maya_useNewAPI():
    '''
    The presence of this function tells Maya that the plugin produces, and expects to be passed, objects created using the Maya Python API 2.0.
    '''
    pass
    
# command
class PyTransferMoCapCmd(om.MPxCommand):

    def __init__(self):
        om.MPxCommand.__init__(self)
    
    def doIt(self, args):
    
        firstFrame = 0
        lastFrame = 600
        
        parsedArgs = self.parseArguments( args )
        
        if (len(parsedArgs) == 2):
            firstFrame = parsedArgs[0]
            lastFrame = parsedArgs[1]
            
        main(firstFrame, lastFrame)
        
        pass

    def parseArguments(self, args):

        parsedArgs = []
        
        argData = om.MArgParser( self.syntax(), args )
        
        if argData.isFlagSet( kShortFlag1Name ):
            flagValue = argData.flagArgumentInt( kShortFlag1Name, 0 )
            parsedArgs.append(flagValue)

        if argData.isFlagSet( kShortFlag2Name ):
            flagValue = argData.flagArgumentInt( kShortFlag2Name, 0 )
            parsedArgs.append(flagValue)
            
        return parsedArgs

            
def cmdCreator():
    return PyTransferMoCapCmd()

def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    syntax = om.MSyntax()
    
    syntax.addFlag( kShortFlag1Name, kLongFlag1Name, om.MSyntax.kDouble )
    syntax.addFlag( kShortFlag2Name, kLongFlag2Name, om.MSyntax.kDouble )

    # ... Add more flags here ...
        
    return syntax

# Initialize the plug-in
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(
            kPluginCmdName, cmdCreator, syntaxCreator
        )
    except:
        sys.stderr.write(
            "Failed to register command: %s\n" % kPluginCmdName
        )
        raise

# Uninitialize the plug-in
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % kPluginCmdName
        )
        raise