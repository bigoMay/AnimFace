'''

Miguel Ramos Carretero
Bournemouth University 2018

Maya/Python script:
AnimFace is a program that allows for the retargeting of facial motion capture into a facial mesh, either realistic or stylized. This script provides the main UI that orchestrates the functionality of the program.

Plugin version for Maya.

'''

import sys
import maya.api.OpenMaya as om 
import maya.cmds as cmds
from functools import partial

'''
Load all the plugins needed to run this program.
'''
def loadPlugins():
    cmds.loadPlugin("createMarkers_plugin.py")
    cmds.loadPlugin("groupMarkers_plugin.py")
    cmds.loadPlugin("transferMoCap_plugin.py")
    cmds.loadPlugin("calculateDistanceMatrix_plugin.py")
    cmds.loadPlugin("animateMesh_plugin.py")

'''
Entry function to create markers. 
''' 
def createMarkers(self):
    #If markers don't exist in scene:
    if not (cmds.objExists("Markers")):
        cmds.pyCreateMarkers()
        cmds.pyGroupMarkers()
    else:
        print("Markers already exists in the scene")

'''
Entry function to transfer mocap. 
'''
def transferMoCap(firstFrame, lastFrame, *args):
    extrFirstFrame = cmds.intField(firstFrame, q=1, v=1)
    extrLastFrame = cmds.intField(lastFrame, q=1, v=1)
    cmds.pyTransferMoCap(ff=extrFirstFrame, lf=extrLastFrame)

'''
Entry function to choose the animation method
'''
def animateMesh(firstFrame, lastFrame, steps, meshName, radioButton, distMatrixFolder, stiffnessUIList, *args):

    stiffnessValuesString = str(cmds.intField(stiffnessUIList[0], q=1, v=1)) 
    for i in range(1, len(stiffnessUIList)):
        stiffnessValuesString += "," + str(cmds.intField(stiffnessUIList[i], q=1, v=1)) 

    selected = cmds.radioButtonGrp(radioButton, q=1, sl=1)

    if (selected == 1):
        euclideanRBF(firstFrame, lastFrame, steps, meshName, distMatrixFolder, stiffnessValuesString, *args)
    elif (selected == 2):
        geodesicsRBF(firstFrame, lastFrame, steps, meshName, distMatrixFolder,stiffnessValuesString, *args)
    else:
        hybridRBF(firstFrame, lastFrame, steps, meshName, distMatrixFolder,stiffnessValuesString, *args)

'''
Animate mesh with Euclidean RBF, called by animateMesh.
'''
def euclideanRBF(firstFrame, lastFrame, steps, meshName, distMatrixFolder, stiffnessValuesString, *args):
    
    extrFirstFrame = cmds.intField(firstFrame, q=1, v=1)
    extrLastFrame = cmds.intField(lastFrame, q=1, v=1)
    extrSteps = cmds.intField(steps, q=1, v=1)
    extrMeshName = cmds.textField(meshName, q=1, tx=1)
    extrdistMatrixFolder = cmds.textField(distMatrixFolder, q=1, tx=1)
    
    cmds.pyAnimMesh(ff=extrFirstFrame, lf=extrLastFrame, st=extrSteps, mn=extrMeshName, ss = stiffnessValuesString, of=extrdistMatrixFolder, mt="Euclidean")

'''
Animate mesh with Geodesics RBF, called by animateMesh.
'''
def geodesicsRBF(firstFrame, lastFrame, steps, meshName, distMatrixFolder, stiffnessValuesString, *args):
    
    extrFirstFrame = cmds.intField(firstFrame, q=1, v=1)
    extrLastFrame = cmds.intField(lastFrame, q=1, v=1)
    extrSteps = cmds.intField(steps, q=1, v=1)
    extrMeshName = cmds.textField(meshName, q=1, tx=1)
    extrdistMatrixFolder = cmds.textField(distMatrixFolder, q=1, tx=1)
    
    cmds.pyAnimMesh(ff=extrFirstFrame, lf=extrLastFrame, st=extrSteps, mn=extrMeshName, ss = stiffnessValuesString, of=extrdistMatrixFolder, mt="Geodesics")

'''
Animate mesh with Hybrid RBF, called by animateMesh.
'''
def hybridRBF(firstFrame, lastFrame, steps, meshName, distMatrixFolder, stiffnessValuesString, *args):
    
    extrFirstFrame = cmds.intField(firstFrame, q=1, v=1)
    extrLastFrame = cmds.intField(lastFrame, q=1, v=1)
    extrSteps = cmds.intField(steps, q=1, v=1)
    extrMeshName = cmds.textField(meshName, q=1, tx=1)
    extrdistMatrixFolder = cmds.textField(distMatrixFolder, q=1, tx=1)
    
    cmds.pyAnimMesh(ff=extrFirstFrame, lf=extrLastFrame, st=extrSteps, mn=extrMeshName, ss = stiffnessValuesString, of=extrdistMatrixFolder, mt="Hybrid")

'''
Entry function to calculate distance matrix.
'''
def calculateDistMatrix(meshName, distMatrixFolder, *args):
    extrMeshName = cmds.textField(meshName, q=1, tx=1)
    extrdistMatrixFolder = cmds.textField(distMatrixFolder, q=1, tx=1)
    cmds.pyCalculateDistMatrix(mn=extrMeshName, of=extrdistMatrixFolder)

'''
Main entry of the program 
''' 
def main():

    winID = "animFaceUI"
    
    #Avoid opening more that one instance of the window
    if (cmds.window(winID, exists=True)):
        cmds.deleteUI(winID)
    
    #Load the plugins needed to run the program
    loadPlugins()
    
    window = cmds.window(winID, title = "AnimFace - by Miguel R. C.")
    form = cmds.formLayout(numberOfDivisions=100)
    
    
    #=========================================
    # Creating Element First_Frame LABEL
    object = cmds.text( label="First frame:", w=68, h=25, al="left")
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 340), ( object, 'left', 34)] )
    #=========================================
    # Creating Element first_frame_anim INTFIELD
    firstFrame_Anim = cmds.intField( w=51, h=25, minValue=0, value=0)
    cmds.formLayout( form, edit=True, attachForm=[( firstFrame_Anim, 'top', 340), ( firstFrame_Anim, 'left', 119)] )
    #=========================================
    # Creating Element Last_Frame_anim LABEL
    object = cmds.text( label="Last frame:", w=68, h=25, al="left")
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 371), ( object, 'left', 34)] )
    #=========================================
    # Creating Element last_frame_anim INTFIELD
    lastFrame_Anim = cmds.intField(w=51, h=25, minValue=0, value=100)
    cmds.formLayout( form, edit=True, attachForm=[( lastFrame_Anim, 'top', 371), ( lastFrame_Anim, 'left', 119)] )
    #=========================================
    # Creating Element Label_Step LABEL
    object = cmds.text( label="Steps:", w=68, h=25, al="left")
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 402), ( object, 'left', 34)] )
    #=========================================
    # Creating Element steps INTFIELD
    steps_Anim = cmds.intField( w=51, h=25, minValue=0, value=5)
    cmds.formLayout( form, edit=True, attachForm=[( steps_Anim, 'top', 402), ( steps_Anim, 'left', 119)] )
    #=========================================
    # Creating Element Mesh_Name LABEL
    object = cmds.text( label="Mesh name:", w=275, h=25, al="left")
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 330), ( object, 'left', 203)] )
    #=========================================
    # Creating Element Mesh_Name TEXTFIELD
    meshName = cmds.textField(w=276, h=25, text="Head")
    cmds.formLayout( form, edit=True, attachForm=[( meshName, 'top', 351), ( meshName, 'left', 202)] )
    #=========================================
    # Creating Element Distance_Matrix_Path:transform1 LABEL
    object = cmds.text( label="Distance matrix folder:", w=274, h=25, al="left")
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 380), ( object, 'left', 204)] )
    #=========================================
    # Creating Element Distance_Matrix TEXTFIELD
    distMatrixFolder = cmds.textField(w=135, h=25, text="D:/Matrices/MatrixRealistic")
    cmds.formLayout(form, edit=True, attachForm=[( distMatrixFolder, 'top', 401), ( distMatrixFolder, 'left', 204)] )
    #=========================================
    # Creating Element Calculate_Dist_Matrix BUTTON
    object = cmds.button( backgroundColor=(1,0.690196,0.690196), label="Calculate Dist. Matrix", w=134, h=23, c=partial(calculateDistMatrix, meshName, distMatrixFolder))
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 401), ( object, 'left', 343)] )
    #=========================================
    # Creating Element Face_Image IMAGE
    ws = cmds.workspace(q=True, rd=True )
    iPath = str(ws) + "/sourceimages/FrontFaceImage.PNG"    
    object = cmds.image(image=iPath, w=272, h=272)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 30), ( object, 'left', 204)] )
    #=========================================
    # Creating Element Markers_stiffness LABEL
    object = cmds.text(label="Markers stiffness:", w=273, h=34, al="left")
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 20), ( object, 'left', 205)] )    
    
    
    stiffnessUIList = []
    
    #=========================================
    # Creating Element S1: Eyebrow_Center
    S1 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S1, 'top', 113), ( S1, 'left', 328)] )
    stiffnessUIList.append(S1)
    #=========================================
    # Creating Element S2: Forehead_L
    S2 = cmds.intField(backgroundColor=(0.262745,1,0.639216), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S2, 'top', 70), ( S2, 'left', 371)] )
    stiffnessUIList.append(S2)
    #=========================================
    # Creating Element S3: Forehead_M
    S3 = cmds.intField(backgroundColor=(0.262745,1,0.639216), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S3, 'top', 70), ( S3, 'left', 329)] )
    stiffnessUIList.append(S3)
    #=========================================
    # Creating Element S4: Forehead_R
    S4 = cmds.intField(backgroundColor=(0.262745,1,0.639216), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S4, 'top', 69), ( S4, 'left', 286)] )
    stiffnessUIList.append(S4)
    #=========================================
    # Creating Element S5: Leye_Up
    S5 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S5, 'top', 133), ( S5, 'left', 369)] )
    stiffnessUIList.append(S5)
    #=========================================
    # Creating Element S6: Leyebrow_Inside
    S6 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S6, 'top', 109), ( S6, 'left', 349)] )
    stiffnessUIList.append(S6)
    #=========================================
    # Creating Element S7: Leyebrow_M
    S7 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S7, 'top', 104), ( S7, 'left', 377)] )
    stiffnessUIList.append(S7)
    #=========================================
    # Creating Element S8: Leyebrow_Outside
    S8 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S8, 'top', 118), ( S8, 'left', 399)] )
    stiffnessUIList.append(S8)
    #=========================================
    # Creating Element S9: Reye_Up
    S9 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S9, 'top', 132), ( S9, 'left', 290)] )
    stiffnessUIList.append(S9)
    #=========================================
    # Creating Element S10: Reyebrow_Inside
    S10 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S10, 'top', 110), ( S10, 'left', 306)] )
    stiffnessUIList.append(S10)
    #=========================================
    # Creating Element S11: Reyebrow_M
    S11 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S11, 'top', 105), ( S11, 'left', 281)] )
    stiffnessUIList.append(S11)
    #=========================================
    # Creating Element S12: Reyebrow_Outside
    S12 = cmds.intField(backgroundColor=(0,1,0), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S12, 'top', 120), ( S12, 'left', 256)] )
    stiffnessUIList.append(S12)
    
    
    #=========================================
    # Creating Element S13: Leye_Inside
    S13 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S13, 'top', 148), ( S13, 'left', 348)] )
    stiffnessUIList.append(S13)
    #=========================================
    # Creating Element S14: Leye_Outside
    S14 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S14, 'top', 149), ( S14, 'left', 394)] )
    stiffnessUIList.append(S14)
    #=========================================
    # Creating Element S15: Reye_Inside
    S15 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S15, 'top', 147), ( S15, 'left', 311)] )
    stiffnessUIList.append(S15)
    #=========================================
    # Creating Element S16: Reye_Outside
    S16 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S16, 'top', 148), ( S16, 'left', 267)] )
    stiffnessUIList.append(S16)
    
    
    #=========================================
    # Creating Element S17: Lcheek_Up
    S17 = cmds.intField(backgroundColor=(0.472,0.39,0.20), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S17, 'top', 181), ( S17, 'left', 395)] )
    stiffnessUIList.append(S17)
    #=========================================
    # Creating Element S18: Leye_Down
    S18 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S18, 'top', 164), ( S18, 'left', 371)] )
    stiffnessUIList.append(S18)
    #=========================================
    # Creating Element S19: Mouth_Up
    S19 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S19, 'top', 216), ( S19, 'left', 331)] )
    stiffnessUIList.append(S19)
    #=========================================
    # Creating Element S20: Mouth_UpLone
    S20 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S20, 'top', 218), ( S20, 'left', 354)] )
    stiffnessUIList.append(S20)
    #=========================================
    # Creating Element S21: Mouth_UpRone
    S21 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S21, 'top', 218), ( S21, 'left', 309)] )
    stiffnessUIList.append(S21)
    #=========================================
    # Creating Element S22: NoseHead
    S22 = cmds.intField(backgroundColor=(1,0.690196,0.690196), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S22, 'top', 186), ( S22, 'left', 330)] )
    stiffnessUIList.append(S22)
    #=========================================
    # Creating Element S23: NoseHead_L
    S23 = cmds.intField(backgroundColor=(1,0.690196,0.690196), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S23, 'top', 194), ( S23, 'left', 356)] )
    stiffnessUIList.append(S23)
    #=========================================
    # Creating Element S24: NoseHead_R
    S24 = cmds.intField(backgroundColor=(1,0.690196,0.690196), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S24, 'top', 194), ( S24, 'left', 305)] )
    stiffnessUIList.append(S24)
    #=========================================
    # Creating Element S25: NoseTop
    S25 = cmds.intField(backgroundColor=(1,0.690196,0.690196), w=20, h=16, minValue=0, maxValue=9, value=4)
    cmds.formLayout( form, edit=True, attachForm=[( S25, 'top', 166), ( S25, 'left', 330)] )
    stiffnessUIList.append(S25)
    #=========================================
    # Creating Element S26: Rcheek_Up
    S26 = cmds.intField(backgroundColor=(0.472,0.39,0.20), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S26, 'top', 182), ( S26, 'left', 263)] )
    stiffnessUIList.append(S26)
    #=========================================
    # Creating Element S27: Reye_down
    S27 = cmds.intField(backgroundColor=(1,1,0.388235), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S27, 'top', 167), ( S27, 'left', 289)] )
    stiffnessUIList.append(S27)
    
    
    #=========================================
    # Creating Element S28: Lcheek_Down
    S28 = cmds.intField(backgroundColor=(0.472,0.39,0.20), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S28, 'top', 206), ( S28, 'left', 398)] )
    stiffnessUIList.append(S28)
    #=========================================
    # Creating Element S29: Lcheek_Outside
    S29 = cmds.intField(backgroundColor=(0.472,0.39,0.20), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S29, 'top', 195), ( S29, 'left', 419)] )
    stiffnessUIList.append(S29)
    #=========================================
    # Creating Element S30: Mouth_Lend
    S30 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S30, 'top', 226), ( S30, 'left', 376)] )
    stiffnessUIList.append(S30)
    #=========================================
    # Creating Element S31: Mouth_Rend
    S31 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S31, 'top', 226), ( S31, 'left', 287)] )
    stiffnessUIList.append(S31)
    #=========================================
    # Creating Element S32: Rcheek_Down
    S32 = cmds.intField(backgroundColor=(0.472,0.39,0.20), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S32, 'top', 209), ( S32, 'left', 261)] )
    stiffnessUIList.append(S32)
    #=========================================
    # Creating Element S33: Rcheek_Outside
    S33 = cmds.intField(backgroundColor=(0.472,0.39,0.20), w=20, h=16, minValue=0, maxValue=9, value=2)
    cmds.formLayout( form, edit=True, attachForm=[( S33, 'top', 196), ( S33, 'left', 240)] )
    stiffnessUIList.append(S33)
    
    #=========================================
    # Creating Element S34: Chin
    S34 = cmds.intField(backgroundColor=(0.4,0.6,0.4), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S34, 'top', 272), ( S34, 'left', 331)] )
    stiffnessUIList.append(S34)
    #=========================================
    # Creating Element S35: Chin_Lone
    S35 = cmds.intField(backgroundColor=(0.4,0.6,0.4), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S35, 'top', 261), ( S35, 'left', 366)] )
    stiffnessUIList.append(S35)
    #=========================================
    # Creating Element S36: Chin_Ltwo
    S36 = cmds.intField(backgroundColor=(0.4,0.6,0.4), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S36, 'top', 246), ( S36, 'left', 392)] )
    stiffnessUIList.append(S36)
    #=========================================
    # Creating Element S37: Chin_Rone
    S37 = cmds.intField(backgroundColor=(0.4,0.6,0.4), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S37, 'top', 263), ( S37, 'left', 294)] )
    stiffnessUIList.append(S37)
    #=========================================
    # Creating Element S38: Chin_Rtwo
    S38 = cmds.intField(backgroundColor=(0.4,0.6,0.4), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S38, 'top', 246), ( S38, 'left', 269)] )
    stiffnessUIList.append(S38)
    #=========================================
    # Creating Element S39: Mouth_Down
    S39 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S39, 'top', 246), ( S39, 'left', 330)] )
    stiffnessUIList.append(S39)
    #=========================================
    # Creating Element S40: Mouth_DownL
    S40 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S40, 'top', 240), ( S40, 'left', 353)] )
    stiffnessUIList.append(S40)
    #=========================================
    # Creating Element S41: Mouth_DownR
    S41 = cmds.intField(backgroundColor=(1,0.35,0.35), w=20, h=16, minValue=0, maxValue=9, value=3)
    cmds.formLayout( form, edit=True, attachForm=[( S41, 'top', 242), ( S41, 'left', 309)] )
    stiffnessUIList.append(S41)
    #=========================================

    
    #=========================================
    # Creating Element Create_Markers LABEL
    object = cmds.text( label="1. Create facial markers for the 3D model:", w=140, h=64, al="left", ww=True)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 06), ( object, 'left', 30)] )
    #=========================================
    # Creating Element Create_Markers BUTTON
    object = cmds.button( backgroundColor=(0,1,0), label="Create Markers", w=136, h=34, c=createMarkers)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 60), ( object, 'left', 33)] )
    
    #=========================================
    # Creating Element Sep_1
    object = cmds.separator( w=150, h=34)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 88), ( object, 'left', 23)] )
    
    #=========================================
    # Creating Element Transfer_MoCap LABEL
    object = cmds.text( label="2. Transfer the MoCap data to the facial markers:", w=137, h=34, al="left", ww=True)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 110), ( object, 'left', 30)] )
    #=========================================
    # Creating Element Transfer_MoCap BUTTON
    object = cmds.button( backgroundColor=(1,1,0.388235), label="Transfer MoCap", w=137, h=34, c=partial(transferMoCap, firstFrame_Anim, lastFrame_Anim))
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 148), ( object, 'left', 31)] )
    
    #=========================================
    # Creating Element Sep_2
    object = cmds.separator( w=150, h=36)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 176), ( object, 'left', 25)] )
    
    #=========================================
    # Creating Element Animate_Mesh LABEL
    object = cmds.text( label="3. Choose RBF method and calculate the animation:", w=170, h=34, al="left", ww=True)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 201), ( object, 'left', 30)] )
    #=========================================
    # Creating Element RBFMethod RADIO BUTTON
    radioButtonRBFMethod = cmds.radioButtonGrp(labelArray3=["Euc", "Geo", "Hyb"], numberOfRadioButtons = 3, columnWidth1 = (75), columnWidth2 = [75, 75], columnWidth3= [50, 50, 50], columnWidth4 = [75, 75, 75, 75], w=150, h=34, sl=1)
    cmds.formLayout( form, edit=True, attachForm=[( radioButtonRBFMethod, 'top', 230), ( radioButtonRBFMethod, 'left', 28)] )
    #=========================================
    # Creating Element Animate_Mesh BUTTON
    object = cmds.button( backgroundColor=(0.262745,1,0.639216), label="Animate Mesh", w=136, h=34, command=partial(animateMesh, firstFrame_Anim, lastFrame_Anim, steps_Anim, meshName, radioButtonRBFMethod, distMatrixFolder, stiffnessUIList))
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 269), ( object, 'left', 34)] )
    
    #=========================================
    # Creating Element Sep_3
    object = cmds.separator( w=460, h=34)
    cmds.formLayout( form, edit=True, attachForm=[( object, 'top', 306), ( object, 'left', 20)] )
    
    cmds.setParent( '..' )
    cmds.showWindow( window )
    cmds.window(winID, edit=True, widthHeight=(500.0, 450.0))

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
class PyAnimFaceUICmd(om.MPxCommand):
    kPluginCmdName = "animface"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return PyAnimFaceUICmd()
    
    def doIt(self, args):
        main()

# Initialize the plug-in
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(
            PyAnimFaceUICmd.kPluginCmdName, PyAnimFaceUICmd.cmdCreator
        )
    except:
        sys.stderr.write(
            "Failed to register command: %s\n" % PyAnimFaceUICmd.kPluginCmdName
        )
        raise

# Uninitialize the plug-in
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(PyAnimFaceUICmd.kPluginCmdName)
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % PyAnimFaceUICmd.kPluginCmdName
        )
        raise