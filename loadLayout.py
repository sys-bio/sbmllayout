# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 10:00:29 2023

@author: hsauro
"""

import tellurium as te
import teUtils as tu

import SBMLDiagrams 
from drawModel import drawScreen
from drawModel import drawPdf
import random

import libsbml
import simplesbml
from layoutClass import TextGlyph
from layoutClass import Compartment
from layoutClass import Species     
from layoutClass import Curve          
from layoutClass import Reaction        
from layoutClass import Layout  

    
def load (sbmlStr):
    global mplugin

    random.seed(12312)
    document = libsbml.readSBMLFromString(sbmlStr)

    if document.getNumErrors() != 0:
        errMsgRead = document.getErrorLog().toString()
        raise Exception("Errors in SBML Model: ", errMsgRead)
    model = document.getModel()
    
    try:
        mplugin = model.getPlugin("layout")
        if mplugin == None:
           # There is no layout
           layoutObj = Layout()
           layoutObj.createNewLayoutObject (document)
           #layoutObj.setSpeciesPosition ('C', 5, 5)
                      
           layoutObj.saveLayoutObjToSBML (document)
           libsbml.writeSBMLToFile(document, 'c:\\tmp\\savesbml.xml')
        else:    
           layoutObj = Layout()
           layoutObj.loadLayoutFromSBML (document, 0)  # Zero = zeroth layout to load
    except Exception as e:
        raise Exception ('Unknown error:' + str (e))          
                         
    return layoutObj
 
 # -------------------------------------------------------------------------------------------------

boolLoadFromSBML = True
if boolLoadFromSBML:
   astr = ''
   ##astr = te.readFromFile('"C:\\Users\\Herbert Sauro\\Documents\\Tellurium\\SBMLLayoutRender\\Jana_WolfGlycolysis.xml"')
   #astr = te.readFromFile('c:\\tmp\pd_1.xml')
   astr = te.readFromFile('C:\\Users\\Herbert Sauro\\Documents\\Tellurium\\SBMLLayoutRender\\Jana_WolfGlycolysis.xml')
   layoutObj = load (astr)    
   #layoutObj.updateReactionPositions()
else:
   #r = te.loada ('''species ABCDEDGHIJKL; ABCDEDGHIJKL + B -> C; k1*ABCDEDGHIJKL; C -> D; k1*C; ABCDEDGHIJKL = 1; k1 = 0.1''')
   #r = te.loada (tu.buildNetworks.getRandomNetwork(10, 10))
   r = te.loada ('''species A, B, C, D, E; J0: A -> B; k1*A; J1: B -> C; k1*B; J2: C -> D; k1*C; J3: D -> E; k1*D; A = 1; k1 = 0.1''')
   #te.saveToFile('c:\\tmp\\small.xml', r.getSBML())
   layoutObj = load (r.getSBML())
   alist = layoutObj.getListofAliases ('A')
   
   x = 5;    layoutObj.setSpeciesPosition ('speciesGlyph_A', x, 20)
   x += 130; layoutObj.setSpeciesPosition ('speciesGlyph_B', x, 20)
   x += 130; layoutObj.setSpeciesPosition ('speciesGlyph_C', x, 20)
   x += 130; layoutObj.setSpeciesPosition ('speciesGlyph_D', x, 20)
   x += 130; layoutObj.setSpeciesPosition ('speciesGlyph_E', x, 20)
   layoutObj.setReactionGapDistance (4)

drawDirectFromLayoutObj = True
if drawDirectFromLayoutObj:
   im = drawScreen (layoutObj)
   im.show()   
else: 
   astr = te.readFromFile('c:\\tmp\\savesbml.xml')

   document = libsbml.readSBMLFromString(astr)
   layoutObj = Layout()
   layoutObj.loadLayoutFromSBML (document, 0)  
 
   for cp in layoutObj.listOfCompartments:
      print (cp)
      
   for sp in layoutObj.listOfSpecies:
      print (sp)

   for rt in layoutObj.listOfReactions:
      print (rt)
      
   im = drawScreen (layoutObj)
   im.show()

print (layoutObj.getNumAliases ('ATP'))
print (layoutObj.getListofAliases('ATP'))
print (layoutObj.getListofSpeciesIds ())
#drawPdf (layout, 'c:\\tmp\\output.pdf')