'''

Miguel Ramos Carretero
Bournemouth University 2018

Maya/Python script:
This script implements three different RBF techniques for the animation of the facial mesh: Euclidean, Geodesics and Hybrid. 

Plugin version for Maya.

'''

import sys
import maya.api.OpenMaya as om
import maya.mel as mel
import maya.cmds as cmds
import math

kPluginCmdName = "pyAnimMesh"

kShortFlag1Name = "-ff"
kLongFlag1Name = "-firstFrame"

kShortFlag2Name = "-lf"
kLongFlag2Name = "-lastFrame"

kShortFlag3Name = "-st"
kLongFlag3Name = "-steps"

kShortFlag4Name = "-mn"
kLongFlag4Name = "-meshname"

kShortFlag5Name = "-ss"
kLongFlag5Name = "-stiffnessstring"

kShortFlag6Name = "-of"
kLongFlag6Name = "-distMatrixFolderPath"

kShortFlag7Name = "-mt"
kLongFlag7Name = "-method"

'''
Python program to illustrate the intersection of two lists in most simple way
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
Get the absolute distance between two points
'''
def getEuclideanDistance(point1, point2):
    
    vect = (point2[0] - point1[0], point2[1] - point1[1], point2[2] - point1[2])
    dist = math.sqrt(vect[0]*vect[0] + vect[1]*vect[1] + vect[2]*vect[2])
    
    return dist 

'''
Get the mesh-based geodesic distance between two points (heuristic with recursive approach)
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
Get the aprox. of the mesh-based geodesic distance between two points (heuristic using edge path tool)
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
Calculates the RBF between two points according to the distance and the 
given parameter gamma. 
'''
def calculateGaussianRBF(dist, gamma):
    return math.exp(-(dist**2/gamma**2))

'''
Animate the vertices of a given mesh according to a set of markers and 
following the Radial Basis Function method (RBF).
'''
def animateMesh(mesh, markersList, firstFrame, lastFrame, steps, stiffnessValues, RBFTechnique, matrixFileEuclidean, matrixFileGeodesics, matrixFileHybrid, geodesicVertices):
    
    #File flags
    eucMatrixExists = (matrixFileEuclidean != None)
    geoMatrixExists = (matrixFileGeodesics != None)
    hybMatrixExists = (matrixFileHybrid != None)
    
    #Start progress bar 
    progressAmount = 0;
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar(gMainProgressBar, edit=True, progress=progressAmount, status='Initializing calculations...', isInterruptable=True, bp=True )
    
    meshFullPath = cmds.ls(mesh, long=True)[0]
    nVert = cmds.polyEvaluate(mesh, v=True)
    
    RBFTime = 0
    
    #Set the default position of the vertices in all the frames
    
    print("Setting default position in all frames")
    
    for x in range (firstFrame, lastFrame+1, steps):
    
        cmds.currentTime(x)
        
        for i in range (nVert):
            cmds.select(mesh+".vtx["+str(i)+"]", r=True)
            cmds.setKeyframe(meshFullPath+"|"+mesh+"Shape.pnts["+str(i)+"]", breakdown=0)
            cmds.setKeyframe(mesh+".vtx["+str(i)+"]", breakdown=0,hierarchy="none", controlPoints=0, shape=0)
    
        #Progress control
        if cmds.progressBar(gMainProgressBar, q=True, ic=True):
            cmds.progressBar(gMainProgressBar, edit=1, ep=1)
            return
    
    #Calculate the vertices matching the markers at frame 0
    print("Calculating corresponding vertex for each marker...")
    
    #Pre-calculation timer starts
    cmds.timer(s=True, name="precalcTimer")
    
    cmds.currentTime(0)
    
    vertexMarkers = matchMarkersWithMesh(markersList, mesh)
    
    #Take the position reference from frame 0
    print("Calculating initial positions...")
    
    markersInitialPos = []
    
    for i in range (len(markersList)):
        markersInitialPos.append(getObjectPoint(markersList[i]))
        
    print("Filling distance matrix...")
    
    #Create and fill the distance matrix for Euclidean
    distMatrixEuc = []
    
    if (RBFTechnique == 0):
    
        for i in range (nVert):
            distMatrixEuc.append([])
            for j in range (nVert):
                distMatrixEuc[i].append(0)
        
        if (eucMatrixExists):
            for v in range (nVert):
                for c in range (len(markersList)):
                    cmds.timer(s=True, name="RBFTimer")
                    dist = float(matrixFileEuclidean.readline())
                    distMatrixEuc[v][vertexMarkers[c]] = dist
                    distMatrixEuc[vertexMarkers[c]][v] = dist
                    RBFTime += cmds.timer(e=True, name="RBFTimer")

        else:
        
            for v in range (nVert):
                for c in range (len(markersList)):
                    vPos1 = cmds.pointPosition(mesh + ".vtx[" + str(v) + "]")
                    vPos2 = cmds.pointPosition(mesh + ".vtx[" + str(vertexMarkers[c]) + "]")
                    cmds.timer(s=True, name="RBFTimer")
                    dist = getEuclideanDistance(vPos1, vPos2)
                    distMatrixEuc[v][vertexMarkers[c]] = dist
                    distMatrixEuc[vertexMarkers[c]][v] = dist
                    RBFTime += cmds.timer(e=True, name="RBFTimer")
                    
    #Create and fill the distance matrix for Geodesics
    distMatrixGeo = []
    
    if (RBFTechnique == 1):
        
        for i in range (nVert):
            distMatrixGeo.append([])
            for j in range (nVert):
                distMatrixGeo[i].append(0)
                    
        if (geoMatrixExists):
            
            for v in range (nVert):
                for c in range (len(vertexMarkers)):
                    cmds.timer(s=True, name="RBFTimer")
                    dist = float(matrixFileGeodesics.readline())
                    distMatrixGeo[v][vertexMarkers[c]] = dist
                    distMatrixGeo[vertexMarkers[c]][v] = dist
                    RBFTime += cmds.timer(e=True, name="RBFTimer")

        
        else:
        
            for v in range (nVert):
                for c in range (len(markersList)):
                    cmds.timer(s=True, name="RBFTimer")
                    dist = getGeodesicDistancev2(mesh, v, vertexMarkers[c]) 
                    distMatrixGeo[v][vertexMarkers[c]] = dist
                    distMatrixGeo[vertexMarkers[c]][v] = dist
                    RBFTime += cmds.timer(e=True, name="RBFTimer")

        
    print("Calculating weight matrix...")
    
    #Create and fill the distance matrix for Hybrid
    distMatrixHybrid = []
    
    if (RBFTechnique == 2):

        for i in range (nVert):
            distMatrixHybrid.append([])
            for j in range (nVert):
                distMatrixHybrid[i].append(0)
        
        if (hybMatrixExists):
            
            for v in range (nVert):
                for c in range (len(vertexMarkers)):
                    cmds.timer(s=True, name="RBFTimer")
                    dist = float(matrixFileHybrid.readline())
                    distMatrixHybrid[v][vertexMarkers[c]] = dist
                    distMatrixHybrid[vertexMarkers[c]][v] = dist
                    RBFTime += cmds.timer(e=True, name="RBFTimer")

        
        else: 
            for v in range(nVert):
            
                averWeight = 1
                    
                vName = mesh + ".vtx[" + str(v) + "]"
                vPoint = cmds.pointPosition(vName)
                if (not(vName in geodesicVertices)):
                    gdist = sys.float_info.max
                    for j in range (len(geodesicVertices)):
                        auxDist = getEuclideanDistance(vPoint, cmds.pointPosition(geodesicVertices[j]))
                        if (auxDist < gdist):
                            gdist = auxDist
                    averWeight = calculateGaussianRBF(gdist, 2)
                    
                for c in range (len(markersList)):
                    
                    cmds.timer(s=True, name="RBFTimer")
                    
                    dist = 0
                    if (averWeight < 0.6):
                        dist = getEuclideanDistance(vPoint, markersInitialPos[c])
                    else:
                        dist = getGeodesicDistancev2(mesh, v, vertexMarkers[c])*averWeight + getEuclideanDistance(vPoint, markersInitialPos[c])*(1-averWeight)  
                    
                    distMatrixHybrid[v][vertexMarkers[c]] = dist
                    distMatrixHybrid[vertexMarkers[c]][v] = dist
                    
                    RBFTime += cmds.timer(e=True, name="RBFTimer")

    #Print total RBF Time
    RBFPrecTime = RBFTime
    print("Total RBF Time in distance calculations: " + str(RBFPrecTime)  + " s")

    #Progress control
    progressStep = float(90) / (float(1+lastFrame-firstFrame) / float(steps))
    progressAmount += 5
    if cmds.progressBar(gMainProgressBar, q=True, ic=True):
        cmds.progressBar(gMainProgressBar, edit=1, ep=1)
        return
    
    #End pre-calculation timer
    precalcTime = cmds.timer(e=True, name="precalcTimer")
    
    #Initialize new timers
    frameTime = 0
    averageFrameTime = 0
    keyframingTime = 0
    averageKeyframingTime = 0
    iterations = 0
    
    for x in range (firstFrame, lastFrame+1, steps):
        
        iterations += 1
        
        #Frame timer starts
        cmds.timer(s=True, name="frameTimer")
        
        #Progress control
        cmds.progressBar(gMainProgressBar, edit=True, status="Calculating mesh deformation for frame " + str(x), progress=progressAmount)
        
        print("Calculating deformations for frame " + str(x))
        
        #Calculate the displacement of the control points
        
        cmds.currentTime(x)
        
        markersDispPos = []
        markersDisp = []
        
        for i in range (len(markersList)):
            
            markersDispPos.append(getObjectPoint(markersList[i]))
            
            markersDisp.append([markersDispPos[i][0] - markersInitialPos[i][0],
                               markersDispPos[i][1] - markersInitialPos[i][1],
                               markersDispPos[i][2] - markersInitialPos[i][2]])
        
        #Calculate the displacement of all the vertices by the RBF method
        
        #Initialize rbf matrix
        
        rbfMatrix = [] 
        for i in range (len(markersList)):
            rbfMatrix.append([])
            for j in range (len(markersList)):
                rbfMatrix[i].append(0)
            
        #Calculate the rbf matrix
        
        print ("   Calculating RBF matrix... ")

        for i in range (0, len(markersList)):
            for j in range (i, len(markersList)):
            
                dist = 0
                eucDist = 0
                geoDist = 0
                hybDist = 0
                
                #Euclidean calculations
                if (RBFTechnique == 0):
                    dist = distMatrixEuc[vertexMarkers[i]][vertexMarkers[j]]
                        
                #Geodesics calculations
                if (RBFTechnique == 1):
                    dist = distMatrixGeo[vertexMarkers[i]][vertexMarkers[j]]
                
                #Hybrid calculations
                if (RBFTechnique == 2):
                    dist = distMatrixHybrid[vertexMarkers[i]][vertexMarkers[j]]
                
                cmds.timer(s=True, name="RBFTimer")
                
                rbf = calculateGaussianRBF(dist, stiffnessValues[i])
                
                rbfMatrix[i][j] = rbf
                rbfMatrix[j][i] = rbf
                
                RBFTime += cmds.timer(e=True, name="RBFTimer")
        
        #Progress control
        if cmds.progressBar(gMainProgressBar, q=True, ic=True):
            cmds.progressBar(gMainProgressBar, edit=1, ep=1)
            return
            
        #Calculate the weight of each control point
        print("   Calculating weight of control points...")
        
        weights = []
        
        for i in range (len(markersList)):
                        
            weights.append([0,0,0])
            
            cmds.timer(s=True, name="RBFTimer")
            
            for j in range (len(markersList)):
                weights[i][0] += rbfMatrix[i][j]
                weights[i][1] += rbfMatrix[i][j]
                weights[i][2] += rbfMatrix[i][j]
            
            weights[i][0] = markersDisp[i][0] / weights[i][0]
            weights[i][1] = markersDisp[i][1] / weights[i][1]
            weights[i][2] = markersDisp[i][2] / weights[i][2]
            
            RBFTime += cmds.timer(e=True, name="RBFTimer")
        
        #Calculate the displacement of the vertices of the mesh
        print("   Calculating displacement of the vertices of the mesh...")

        vDisp = []
        
        for i in range (nVert):

            vDisp.append([0,0,0])
            
            vName = mesh + ".vtx[" + str(i) + "]"
            vPos = cmds.pointPosition(vName)
            
            for c in range (len(markersList)):
                
                dist = 0
                
                #Euclidean calculations
                if (RBFTechnique == 0):
                    dist = distMatrixEuc[i][vertexMarkers[c]]
                        
                #Geodesics calculations
                if (RBFTechnique == 1):
                    dist = distMatrixGeo[i][vertexMarkers[c]]

                #Hybrid calculations
                if (RBFTechnique == 2):
                    dist = distMatrixHybrid[i][vertexMarkers[c]]
                      
                cmds.timer(s=True, name="RBFTimer")

                rbf = calculateGaussianRBF(dist, stiffnessValues[c])
                
                vDisp[i][0] += weights[c][0]*rbf
                vDisp[i][1] += weights[c][1]*rbf
                vDisp[i][2] += weights[c][2]*rbf
                
                RBFTime += cmds.timer(e=True, name="RBFTimer")
        
        #Progress control
        if cmds.progressBar(gMainProgressBar, q=True, ic=True):
            cmds.progressBar(gMainProgressBar, edit=1, ep=1)
            return
            
        # Apply the calculated displacement to all the vertices 
        print("   Applying displacements...")
        
        for j in range (nVert):
        
            #Keyframing timer starts
            cmds.timer(s=True, name="keyframingTimer")
            
            #Displace the vertex
            cmds.select(mesh+".vtx["+str(j)+"]", r=True)
            cmds.move(vDisp[j][0], vDisp[j][1], vDisp[j][2], r=True, ls=True, wd=True)
            
            #Set a key for the vertex
            cmds.setKeyframe(meshFullPath+"|"+mesh+"Shape.pnts["+str(j)+"]", breakdown=0)
            cmds.setKeyframe(mesh+".vtx["+str(j)+"]", breakdown=0,hierarchy="none", controlPoints=0, shape=0)
        
            #Keyframing timer ends
            keyframingTime += cmds.timer(e=True, name="keyframingTimer")
            
        #Progress control
        progressAmount += progressStep
        if cmds.progressBar(gMainProgressBar, q=True, ic=True):
            cmds.progressBar(gMainProgressBar, edit=1, ep=1)
            return
        
        #Frame timer ends
        frameTime += cmds.timer(e=True, name="frameTimer")
        
    #Print times
    averageKeyframingTime = float(keyframingTime) / float(iterations)
    averageFrameTime = float(frameTime) / float(iterations)
    RBFTimePerFrame = float(RBFTime - RBFPrecTime) / float (iterations)
    
    print("")
    print("ALGORITHM: ----------------------------------")
    print("Pre-calculation time: " + str(precalcTime) + " s")
    print("Frames calculated: " + str(iterations) + " frames")
    print("Average frame time: " + str(averageFrameTime) + " s/frame")
    print("  Average keyframing time: " + str(averageKeyframingTime) + " s/frame")
    print("  Average algorithm time: " + str(averageFrameTime-averageKeyframingTime) + " s/frame")
    print("---------------------------------------------")
    print("")
    print("RBF CALCULATIONS: ---------------------------")
    print("RBF total calculation time: " + str(RBFTime) + " s")
    print("  RBF dist. calculation time: " + str(RBFPrecTime) + " s")
    print("  RBF calculation time per frame: " + str(RBFTimePerFrame) + " s/frame")
    print("---------------------------------------------")
    print("")

    #End progress bar
    cmds.progressBar(gMainProgressBar, edit=1, ep=1)
    return
    
'''
Entry point of the program

    # RBF technique code:
    # 0 = Euclidean
    # 1 = Geodesics
    # 2 = Hybrid

'''
def main(firstFrame, lastFrame, steps, meshName, matrixFolderPath, stiffnessValues, RBFTechnique):
    
    #Check if the mesh exists in the DAG
    if not cmds.objExists(meshName):
        print("Mesh name does not match any object")
        return
        
    #Check that the RBF technique is valid 
    if (RBFTechnique < 0 or RBFTechnique > 2):
        print("The RBF Technique code is not valid")
        return
        
    #Try to open the distance matrix files 
    
    matrixFileEuclidean = None
    matrixFileGeodesics = None
    matrixFileHybrid = None

    if (RBFTechnique == 0):
        try:
            matrixFileEuclidean = open(matrixFolderPath+"/eucMatrix.mtx",'r')
        except IOError:
            confirm = cmds.confirmDialog( title='Matrix no found', message='Could not find the Euclidean matrix file (eucmatrix.mtx) in the given path, do you want to proceed with the calculations without matrix? (not recommended for dense meshes)', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if (confirm == "No"):
                return
    
    if (RBFTechnique == 1):
        try:
            matrixFileGeodesics = open(matrixFolderPath+"/geoMatrix.mtx",'r')
        except IOError:
            confirm = cmds.confirmDialog( title='Matrix no found', message='Could not find the Geodesics matrix file (geomatrix.mtx) in the given path, do you want to proceed with the calculations without matrix? (not recommended for dense meshes)', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if (confirm == "No"):
                return
    
    if (RBFTechnique == 2):
        try:
            matrixFileHybrid = open(matrixFolderPath+"/hybMatrix.mtx",'r')
        except IOError:
            confirm = cmds.confirmDialog( title='Matrix no found', message='Could not find the Hybrid matrix file (hybmatrix.mtx) in the given path, do you want to proceed with the calculations without matrix? (not recommended for dense meshes)', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if (confirm == "No"):
                return
    
    #Take the markers arranged in groups
    
    markersSelection = sorted(cmds.listRelatives("TopMarkers")) + sorted(cmds.listRelatives("TopMiddleMarkers")) + sorted(cmds.listRelatives("MiddleMarkers")) + sorted(cmds.listRelatives("MiddleBottomMarkers")) + sorted(cmds.listRelatives("BottomMarkers"))
    
    #Take the vertices of the geodesic areas (for hybrid)
    
    geodesicVertices = None
    if (RBFTechnique == 2):
        geodesicVertices = cmds.ls(cmds.sets("MouthArea", q=True), flatten=True) + cmds.ls(cmds.sets("REyeArea", q=True), flatten=True) + cmds.ls(cmds.sets("LEyeArea", q=True), flatten=True)
    
    #Calculate the animation of the mesh
    
    cmds.undoInfo(state=False)
    cmds.timer(s=True)
    mel.eval("paneLayout -e -manage false $gMainPane")

    animateMesh(meshName, markersSelection, firstFrame, lastFrame, steps,stiffnessValues, RBFTechnique, matrixFileEuclidean, matrixFileGeodesics,matrixFileHybrid, geodesicVertices)
    
    mel.eval("paneLayout -e -manage true $gMainPane")
    totalTime = cmds.timer(e=True)
    cmds.undoInfo(state=True)
    
    #Close the file descriptors
    if (matrixFileEuclidean != None):
        matrixFileEuclidean.close() 
    if (matrixFileGeodesics != None):
        matrixFileGeodesics.close() 
    if (matrixFileHybrid != None):
        matrixFileHybrid.close() 
    
    #Print total time
    print("TOTAL ---------------------------------------")
    print("Total running time: " + str(totalTime) + "s")
    print("---------------------------------------------")
    print("")
    
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
class PyAnimMeshGeodesicsMatrixCmd(om.MPxCommand):

    def __init__(self):
        om.MPxCommand.__init__(self)
    
    def doIt(self, args):
    
        firstFrame = 0
        lastFrame = 600
        steps = 5
        meshName = "Head"
        matrixFolderPath = "D:/Matrix.log"
        stiffnessString = "2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2"
        method = "Euclidean"
        RBFTechnique = 0

        parsedArgs = self.parseArguments( args )
        
        if (len(parsedArgs) == 7):
            firstFrame = parsedArgs[0]
            lastFrame = parsedArgs[1]
            steps = parsedArgs[2]
            meshName = parsedArgs[3]
            stiffnessString = parsedArgs[4]
            matrixFolderPath = parsedArgs[5]
            method = parsedArgs[6]
        
        #Parse the stiffness string
        stiffnessValues = [int(x) for x in stiffnessString.split(",")]

        #Parse the method string
        if (method == "Geodesics"):
            RBFTechnique = 1
        elif (method == "Hybrid"):
            RBFTechnique = 2
        
        main(firstFrame, lastFrame, steps, meshName, matrixFolderPath, stiffnessValues, RBFTechnique)
        
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
            
        if argData.isFlagSet( kShortFlag3Name ):
            flagValue = argData.flagArgumentInt( kShortFlag3Name, 0 )
            parsedArgs.append(flagValue)
        
        if argData.isFlagSet( kShortFlag4Name ):
            flagValue = argData.flagArgumentString( kShortFlag4Name, 0 )
            parsedArgs.append(flagValue)
            
        if argData.isFlagSet( kShortFlag5Name ):
            flagValue = argData.flagArgumentString( kShortFlag5Name, 0 )
            parsedArgs.append(flagValue)
            
        if argData.isFlagSet( kShortFlag6Name ):
            flagValue = argData.flagArgumentString( kShortFlag6Name, 0 )
            parsedArgs.append(flagValue)
        
        if argData.isFlagSet( kShortFlag7Name ):
            flagValue = argData.flagArgumentString( kShortFlag7Name, 0 )
            parsedArgs.append(flagValue)
            
        return parsedArgs
        
def cmdCreator():
    return PyAnimMeshGeodesicsMatrixCmd()

def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    syntax = om.MSyntax()
    
    syntax.addFlag( kShortFlag1Name, kLongFlag1Name, om.MSyntax.kDouble )
    syntax.addFlag( kShortFlag2Name, kLongFlag2Name, om.MSyntax.kDouble )
    syntax.addFlag( kShortFlag3Name, kLongFlag3Name, om.MSyntax.kDouble )
    syntax.addFlag( kShortFlag4Name, kLongFlag4Name, om.MSyntax.kString )
    syntax.addFlag( kShortFlag5Name, kLongFlag5Name, om.MSyntax.kString )
    syntax.addFlag( kShortFlag6Name, kLongFlag6Name, om.MSyntax.kString )
    syntax.addFlag( kShortFlag7Name, kLongFlag7Name, om.MSyntax.kString )

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