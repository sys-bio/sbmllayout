
import os
import libsbml
from layoutClass import Layout 
from drawModel import drawScreen
from drawModel import drawPdf
from drawModel import drawPng
from drawModel import drawSVG

class SBMLLayout:
    
    def __init__ (self, sbml):
        """ Load an sbml modl into SBMLLayout

        Args:
            sbml (string): This can either be an sbml string or a file name to an sbml file
        """
        if os.path.isfile(sbml):
            with open(sbml) as f:
                self.sbmlstr = f.read()
        else:  
            self.sbmlstr = sbml
            
        self.document = libsbml.readSBMLFromString(self.sbmlstr)

        if self.document.getNumErrors() != 0:
           errMsgRead = self.document.getErrorLog().toString()
           raise Exception("Errors in SBML Model: ", errMsgRead)
      
        model = self.document.getModel()
        mplugin = model.getPlugin("layout")
        self.layoutObj = Layout()
        if mplugin == None:
           self.layoutObj.createNewLayoutObject (self.document)
        else:
           self.layoutObj.loadLayoutFromSBML (self.document, 0)  # Zero = zeroth layout to load

    def saveToSBML (self, fileName):
        
        self.layoutObj.saveLayoutObjToSBML (self.document)
        libsbml.writeSBMLToFile(self.document, fileName)
        
        
    def drawToScreen (self):
        im = drawScreen (self.layoutObj)
        im.show()
        
    def drawToPdf (self, fileName):
        drawPdf (self.layoutObj, fileName)
           
    def drawToPng (self, fileName):
        drawPng (self.layoutObj, fileName)
        
    def drawToSvg (self, fileName):
        drawSVG (self.layoutObj, fileName) 
        
    #  Access methods
    
    def setLayoutDims (self, w, h):
        self.layoutObj.setLayoutDims (w, h)
        
    def computeLayoutExtent(self):
        return self.layoutObj.computeLayoutExtent()
        
    def getNumSpeciesGlyphs (self, modelSpeciesId):
        return self.layoutObj.getNumSpeciesGlyphs (modelSpeciesId)

    def getListOfSpeciesGlyphs (self, modelSpeciesId):
        return self.layoutObj.getListofSpeciesGlyphs (modelSpeciesId)
    
    def getNumCompartmentAliases (self, modelCompartmentId):
        return self.layoutObj.getNumCompartmentGlyphs (modelCompartmentId)
        
    def getListOfCompartmentGlyphs (self, modelCompartmentId):
        return self.layoutObj.getListofCompartmentGlyphs (modelCompartmentId)
    
    def getListOfModelSpeciesIds (self, modelId):
        return self.layoutObj.getListofModelSpeciesIds (modelId) 
    
    
    def getNodeCenter (self, modelId):
        if self.layoutObj.getNumSpeciesGlyphs (modelId) == 1:
            node = self.layoutObj.findSpeciesId (modelId)
            if node == None:
                raise Exception ('No such species glyph could ne locatred: ' + modelId)
            return node.getNodeCenter()
        else:
            node = self.layoutObj.findSpeciesGlyph (modelId)
            if node == None:
                raise Exception ('No such species glyph could ne locatred: ' + modelId)
            return node.getNodeCenter()
    
    
    def setSpeciesPosition (self, speciesGlyphId, x, y):
        self.layoutObj.setSpeciesPosition (speciesGlyphId, x, y)
          
          
    def setCompartmentDimension (self, compartmentGlyphId, w, h):
        compartment = self.layoutObj.findCompartmentGlyph (compartmentGlyphId)
        if compartment != None: 
           compartment.boundingBox.w = w
           compartment.boundingBox.h = h       
        else:
            raise Exception('Unable to locate compartment: ' + compartmentGlyphId)
        
    
if __name__ == "__main__":
    import tellurium as te
    import random
    
    random.seed(12312)
    
    #r = te.loada ('''species A, B, C, D, E; J0: A -> B; k1*A; J1: B -> C; k1*B; J2: C -> D; k1*C; J3: D -> E; k1*D; A = 1; k1 = 0.1''')
    r = te.loada ('''species A, B, C''')
 
    sbmllayout = SBMLLayout (r.getSBML())
    
    speciesA = sbmllayout.getListOfSpeciesGlyphs('A')
    speciesB = sbmllayout.getListOfSpeciesGlyphs('B')
    speciesC = sbmllayout.getListOfSpeciesGlyphs('C')
    compartments = sbmllayout.getListOfCompartmentGlyphs('default_compartment')
    print (compartments)
    #sbmllayout.setLayoutDims (120, 120)
    sbmllayout.setSpeciesPosition (speciesA[0], 20, 20)
    sbmllayout.setSpeciesPosition (speciesB[0], 100, 20)
    sbmllayout.setSpeciesPosition (speciesC[0], 180, 20)
    sbmllayout.setCompartmentDimension (compartments[0], 100, 80)
    #sbmllayout.setSpeciesPosition ()
    p = sbmllayout.computeLayoutExtent()
    sbmllayout.setLayoutDims (p[0], p[1])
    sbmllayout.drawToScreen ()
    sbmllayout.saveToSBML ('.\\tests\\threenodes.xml')
    s = 'C:\\Users\\Herbert Sauro\\Documents\\Tellurium\\SBMLLayoutRender\\Tests\\threenodes.png'
    sbmllayout.drawToPng (s)
    
    # Test
    testList = []
    for file in os.listdir(".\\tests"):
        if file.endswith(".xml"):
           p = os.path.splitext(file)
           testList.append (p[0])
           
          
    import tempfile
    import cv2
    import numpy as np
 
    for root in testList:
        model = root + '.xml'
        expectedImg = root + '.png'    
 
        sbmllayout = SBMLLayout ('.\\tests\\' + model)
        #sbmllayout.drawToScreen ()
        with tempfile.TemporaryDirectory() as tmp:
             path = os.path.join(tmp, expectedImg)
             sbmllayout.drawToPng (path)
             #sbmllayout.drawToPng ('c:\\tmp\\onenodegen.png')
    
             # read image 1
             img1 = cv2.imread('.\\tests\\' + expectedImg)

             # read image 2
             img2 = cv2.imread(path)
    
             # do absdiff
             diff = cv2.absdiff(img1,img2)

             # get mean of absdiff
             mean_diff = np.mean(diff)

             # print result
             print(mean_diff)
    