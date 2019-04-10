'''

Miguel Ramos Carretero
Bournemouth University 2018

Maya/Python script:
This script calculates the distance matrix of a given mesh using geodesics. 

'''

import sys
import os
import errno
import maya.api.OpenMaya as om
import maya.mel as mel
import maya.cmds as cmds
import math

kPluginCmdName = "pyCalculateDistMatrix"

kShortFlag1Name = "-mn"
kLongFlag1Name = "-meshname"

kShortFlag2Name = "-of"
kLongFlag2Name = "-outputfolder"

'''
Illustrate the intersection of two lists in most simple way
'''
def getIntersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
    
'''
Get the transform of a given object and returns it in a 3 element list
'''
def getObjectPoint(obj):
    
    x = cmds.getAttr(obj+".translateX")
    y = cmds.getAttr(obj+".translateY")
    z = cmds.getAttr(obj+".translateZ")
    
    point = [x,y,z]
    
    return point
    
'''
Calculates the RBF between two points according to the distance and the 
given parameter gamma. 
'''
def calculateGaussianRBF(dist, gamma):
    return math.exp(-(dist**2/gamma**2))
    
'''
Get the absolute distance between two points
'''
def getEuclideanDistance(point1, point2):
    
    vect = (point2[0] - point1[0], point2[1] - point1[1], point2[2] - point1[2])
    dist = math.sqrt(vect[0]*vect[0] + vect[1]*vect[1] + vect[2]*vect[2])
    
    return dist 

'''
Get the mesh-based geodesic distance between two points (heuristic based on recursivity)
Note: v1Name = mesh+".vtx["+str(v1)+"]"
      v2Name = mesh+".vtx["+str(v2)+"]"
'''
def getGeodesicDistance(v1Name, v2Name, iterations=5):
    
    distance = 0
    selectionV1 = []
    selectionV2 = []
    
    for i in range(iterations):
        
        #Grow the selection of v1
        cmds.select(v1Name, r=True)
        for j in range(i):
            mel.eval("select `ls -sl`;PolySelectTraverse 1;select `ls -sl`")
        selectionV1 = cmds.ls(selection=True, flatten=True)
        
        #Grow the selection of v2
        cmds.select(v2Name, r=True)
        for j in range(i):
            mel.eval("select `ls -sl`;PolySelectTraverse 1;select `ls -sl`")
        selectionV2 = cmds.ls(selection=True, flatten=True)
        
        #Check if there is intersection
        intersection = getIntersection(selectionV1, selectionV2)
        
        if (len(intersection) > 0):
            
            #If intersection contains each other vertex, stop and return distance
            if (v1Name in intersection) and (v2Name in intersection):
                return getEuclideanDistance(cmds.pointPosition(v1Name), cmds.pointPosition(v2Name))
                
            #Else find a middle point and apply recursivity
            chosenVert = ""
            tempDist = sys.float_info.max
            
            for v in range(len(intersection)):
            
                auxDist = getEuclideanDistance(cmds.pointPosition(intersection[v]), cmds.pointPosition(v1Name)) + getEuclideanDistance(cmds.pointPosition(intersection[v]), cmds.pointPosition(v2Name))
                
                if (auxDist < tempDist):
                    tempDist = auxDist
                    chosenVert = intersection[v]
                
            return distance + getGeodesicDistance(v1Name, chosenVert, iterations) + getGeodesicDistance(v2Name, chosenVert, iterations) 
        
    return getEuclideanDistance(cmds.pointPosition(v1Name), cmds.pointPosition(v2Name)) * 2 #Solution by default

'''
Get the aprox. of the mesh-based geodesic distance between two points (heuristic based on the edge path tool)
Note: v1Name = mesh+".vtx["+str(v1)+"]"
      v2Name = mesh+".vtx["+str(v2)+"]"
'''
def getGeodesicDistancev2(mesh, v1Index, v2Index):

    #Catch special case
    if (v1Index == v2Index):
        return 0
        
    #Get the shortest edge path
    sel = cmds.polySelect(mesh, shortestEdgePath=(v1Index, v2Index), ass=True )
    
    #Calculate the path length
    dist = 0

    for i in range(len(sel)):
        conv = cmds.polyListComponentConversion(sel[i], fe=True, tv=True)
        conv = cmds.filterExpand(conv, sm=31)
        dist += getEuclideanDistance(cmds.pointPosition(conv[0]), cmds.pointPosition(conv[1]))
        
    return dist

'''
Get the hybrid distance between two points, given the Euclidean and the geodesic distance.
'''
def getHybridDistance(geodesicVertices, vName, eucDist, geoDist):
    
    averWeight = 1
    
    vPoint = cmds.pointPosition(vName)
    if (not(vName in geodesicVertices)):
        gdist = sys.float_info.max
        for j in range (len(geodesicVertices)):
            auxDist = getEuclideanDistance(vPoint, cmds.pointPosition(geodesicVertices[j]))
            if (auxDist < gdist):
                gdist = auxDist
        averWeight = calculateGaussianRBF(gdist, 2)

    if (averWeight < 0.6):
        dist = eucDist
    else:
        dist = geoDist*averWeight + eucDist*(1-averWeight)  

    return dist
    
'''
Get a match between the markers and the vertices of a given mesh
'''
def matchMarkersWithMesh(markersList, mesh):
    
    nVert = cmds.polyEvaluate(mesh, v=True)
    
    indexList = []
    distances = []
    
    for i in range (len(markersList)):
        
        indexList.append(0)
        distances.append(sys.float_info.max)
    
    print("Calculating matches for markers and vertices...")
    
    for i in range (nVert):
        
        vertexPoint = cmds.pointPosition(mesh + ".vtx[" + str(i) + "]")
        
        for j in range (len(markersList)):
            
            markerPoint = getObjectPoint(markersList[j])
     
            dist = getEuclideanDistance(vertexPoint, markerPoint)
            
            if (dist < distances[j]):
                distances[j] = dist
                indexList[j] = i
    
    return indexList

'''
Calculate the distance matrix of a given mesh and writes it into a file
'''
def calculateDistanceMatrixToFile(meshName, outputFolder, markersList, geodesicVertices, calculateEuclideanMatrix=True, calculateGeodesicMatrix=True):
    
    #Start progress bar 
    progressAmount = 0;
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar(gMainProgressBar, edit=True, progress=progressAmount, status='Calculating...', isInterruptable=True, bp=True )
    
    nVert = cmds.polyEvaluate(meshName, v=True)
    
    outFileEuclidean = None
    outFileGeodesics = None
    outFileHybrid = None
    
    #Open the output files
    if (calculateEuclideanMatrix):
        if not os.path.exists(outputFolder):
            try:
                os.makedirs(outputFolder)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        path = outputFolder+"/eucMatrix.mtx"
        outFileEuclidean = open(path, 'w')
        
    if (calculateGeodesicMatrix):
        if not os.path.exists(outputFolder):
            try:
                os.makedirs(outputFolder)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        path = outputFolder+"/geoMatrix.mtx"
        outFileGeodesics = open(path, 'w')
    
    if (calculateEuclideanMatrix and calculateGeodesicMatrix):
        if not os.path.exists(outputFolder):
            try:
                os.makedirs(outputFolder)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        path = outputFolder+"/hybMatrix.mtx"
        outFileHybrid = open(path, 'w')
    
    #Go to frame 0 (reference frame)
    cmds.currentTime(0)
    
    #Create a list with the closest vertices to the markers
    vertexMarkers = matchMarkersWithMesh(markersList, meshName)
    
    #Progress control
    progressStep = float(100) / float(nVert)
    euclideanTime = 0
    geodesicTime = 0
    hybridTime = 0
    
    #Calculate distance matrix values for every vertex
    if (calculateEuclideanMatrix or calculateGeodesicMatrix):
        for i in range (0, nVert):
        
            progressAmount += progressStep
            cmds.progressBar(gMainProgressBar, edit=True, status="Calculating distance matrices for row " + str(i) + " of " + str(nVert), progress=progressAmount)

            for j in range (0, len(vertexMarkers)):
                v1Name = meshName + ".vtx[" + str(i) + "]"
                v2Name = meshName + ".vtx[" + str(vertexMarkers[j]) + "]"
                
                eucDist = 0
                geoDist = 0
                
                if (calculateEuclideanMatrix):
                    cmds.timer(s=True, name="euclideanTimer")
                    v1 = cmds.pointPosition(v1Name)
                    v2 = cmds.pointPosition(v2Name)
                    eucDist = getEuclideanDistance(v1, v2)
                    outFileEuclidean.write(str(eucDist)+"\n")
                    euclideanTime += cmds.timer(e=True, name="euclideanTimer")
                    
                if (calculateGeodesicMatrix):
                    cmds.timer(s=True, name="geodesicTimer")
                    geoDist = getGeodesicDistancev2(meshName, i, vertexMarkers[j])
                    outFileGeodesics.write(str(geoDist)+"\n")
                    geodesicTime += cmds.timer(e=True, name="geodesicTimer")
                
                if (calculateEuclideanMatrix and calculateGeodesicMatrix):
                    cmds.timer(s=True, name="hybridTimer")
                    hybDist = getHybridDistance(geodesicVertices, v1Name, eucDist, geoDist)
                    outFileHybrid.write(str(hybDist)+"\n")
                    hybridTime += cmds.timer(e=True, name="hybridTimer")
                
                #Progress control
                if cmds.progressBar(gMainProgressBar, q=True, ic=True):
                    cmds.progressBar(gMainProgressBar, edit=1, ep=1)
                    if (outFileEuclidean != None):
                        outFileEuclidean.close()
                    if (outFileGeodesics != None):
                        outFileGeodesics.close()
                    if (outFileHybrid != None):
                        outFileHybrid.close()
                    return
    
    #Close the file descriptors
    if (outFileEuclidean != None):
        outFileEuclidean.close()
    if (outFileGeodesics != None):
        outFileGeodesics.close()
    if (outFileHybrid != None):
        outFileHybrid.close()
    
    #Close the progress bar
    cmds.progressBar(gMainProgressBar, edit=1, ep=1)
    
    #Print the time results
    print("Time for calculating Euclidean dist. matrix: " + str(euclideanTime))
    print("Time for calculating Geodesic dist. matrix: " + str(geodesicTime))
    print("Time for calculating Hybrid dist. matrix: " + str(hybridTime))

'''
Entry of the program
'''
def main(meshName, outputFolder):

    cmds.timer(s=True)
    cmds.undoInfo( state=False)
    mel.eval("paneLayout -e -manage false $gMainPane")
    
    #Take the markers arranged in groups
    markersSelection = sorted(cmds.listRelatives("TopMarkers")) + sorted(cmds.listRelatives("TopMiddleMarkers")) + sorted(cmds.listRelatives("MiddleMarkers")) + sorted(cmds.listRelatives("MiddleBottomMarkers")) + sorted(cmds.listRelatives("BottomMarkers"))
    
    #Take the geodesic vertices
    geodesicVertices = cmds.ls(cmds.sets("MouthArea", q=True), flatten=True) + cmds.ls(cmds.sets("REyeArea", q=True), flatten=True) + cmds.ls(cmds.sets("LEyeArea", q=True), flatten=True)
    
    matrix = calculateDistanceMatrixToFile(meshName, outputFolder, markersSelection, geodesicVertices, calculateEuclideanMatrix = True, calculateGeodesicMatrix=True)
    
    mel.eval("paneLayout -e -manage true $gMainPane")
    cmds.undoInfo( state=True)
    time = cmds.timer(e=True)

    print("Matrix calculations completed. Files created at: " + outputFolder)
    print("Running time: " + str(time) + "s")

###

'''
Plugin functionality
'''
def maya_useNewAPI():
    '''
    The presence of this function tells Maya that the plugin produces, and expects to be passed, objects created using the Maya Python API 2.0.
    '''
    pass
    
# command
class PyCalculateDistMatrixCmd(om.MPxCommand):

    def __init__(self):
        om.MPxCommand.__init__(self)
    
    def doIt(self, args):
        
        meshName = "Head"
        outputFolder = "D:/Matrix"

        parsedArgs = self.parseArguments( args )
        
        if (len(parsedArgs) == 2):
            meshName = parsedArgs[0]
            outputFolder = parsedArgs[1]
            
        main(meshName, outputFolder)
        
        pass
        
    def parseArguments(self, args):

        parsedArgs = []
        
        argData = om.MArgParser( self.syntax(), args )
        
        if argData.isFlagSet( kShortFlag1Name ):
            flagValue = argData.flagArgumentString( kShortFlag1Name, 0 )
            parsedArgs.append(flagValue)
            
        if argData.isFlagSet( kShortFlag2Name ):
            flagValue = argData.flagArgumentString( kShortFlag2Name, 0 )
            parsedArgs.append(flagValue)
            
        return parsedArgs
        
def cmdCreator():
    return PyCalculateDistMatrixCmd()

def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    syntax = om.MSyntax()

    syntax.addFlag( kShortFlag1Name, kLongFlag1Name, om.MSyntax.kString )
    syntax.addFlag( kShortFlag2Name, kLongFlag2Name, om.MSyntax.kString )

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
