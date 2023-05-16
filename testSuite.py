
import SBMLLayout
import os
import tempfile
import cv2
import numpy as np

# Test
testList = []
for file in os.listdir(".\\tests"):
    if file.endswith(".xml"):
       p = os.path.splitext(file)
       testList.append (p[0])
           
 
for root in testList:
    model = root + '.xml'
    expectedImg = root + '.png'    
 
    sbmllayout = SBMLLayout.SBMLLayout ('.\\tests\\' + model)
    #sbmllayout.drawToScreen ()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, expectedImg)
        sbmllayout.drawToPng (path)
    
        # read image 1
        img1 = cv2.imread('.\\tests\\' + expectedImg)

        # read image 2
        img2 = cv2.imread(path)
    
        if len (img1) == len (img2):
           # do absdiff
           diff = cv2.absdiff(img1, img2)

           # get mean of absdiff
           mean_diff = np.mean(diff)

           # print result
           if mean_diff < 0.1:
              print('Pass: ' + str (mean_diff) + ', ' + root)
           else:
              print('Fail: ' + str (mean_diff) + ', ' + root)
        else:
           print ('Fail on model : ' + root) 
    