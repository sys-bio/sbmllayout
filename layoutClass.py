
import libsbml
import simplesbml
import random
import sbmlUtils
import graphicsUtils
from graphicsUtils import BoundingBox
from graphicsUtils import TLineSegment
from graphicsUtils import TPointF
from graphicsUtils import computeLineIntersection
from graphicsUtils import computeReactionCenterPt

from defaults import Defaults

from simplesbml import SbmlModel
  
# CurveSegment currently not used
class CurveSegment:
    
    # curveType can be “CubicBezier” or "LineSegment"
    def __init__ (self):
        self.curveType = Defaults.LINE_SEGMENT     # or Defaults.CUBIC_BEZIER
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        # optional bezier handles here b1 (x, y), b2 (x, y)
        self.basepoint1 = []
        self.basepoint2 = []
        
class Curve:
    
    def __init__ (self, speciesId):
        # Contains objects of type CurveSegment, multiple curves are not currenlty supported
        #self.listOfCurves = []  

        self.curveType = Defaults.LINE_SEGMENT     # or Defaults.CUBIC_BEZIER
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        # optional bezier handles here b1 (x, y), b2 (x, y)
        self.basepoint1 = []
        self.basepoint2 = []

        
    
# Layout classes

class SpeciesReferenceGlyph:
    
    def __init__ (self):
        self.id="SpeciesReferenceGlyph_J0_rct1"
        self.speciesReference="SpeciesReference_J0_rct1"
        self.speciesGlyph="SpeciesGlyph_B_idx_1"
        self.role="substrate"
        self.curve = Curve('')



# In Layout a TextGlyph has o font information
class TextGlyph:
    
    def __init__ (self, id, text):
        self.id = id
        self.graphicalObject_id = ''
        self.text = text
        self.boundingBox = BoundingBox(0, 0, 0, 0)  # x, y, w, h
        
        
class Compartment:
    
    # Id is the model compartment id, glyphId is the layout compartment id
    def __init__ (self, id, text):
        self.compartmentId = id
        self.boundingBox = BoundingBox (0, 0, Defaults.MAX_COMPARMENT_SIZE-1, Defaults.MAX_COMPARMENT_SIZE-1)  
        self.order = 0.0
        self.compartmentGlyphId = 'compartmentGlpyh_' + id           
        self.textGlyphs = []
        
        self.textGlyphs.append (TextGlyph(id, text))
              

    def __repr__(self):
        astr = 'Compartment = ' + self.compartmentId + '\n'
        astr += 'Glyph id = ' + self.compartmentGlyphId + '\n'
        astr += '-------------------------------------------' + '\n'
        return astr        
      
        
class Species:
    
    def __init__ (self, id, displayName):
        self.speciesGlyphId = "speciesGlyph_"  + id
        self.modelId = id
        self.displayNaame = displayName
        self.boundingBox = BoundingBox(0, 0, 0, 0)
        self.textGlyphs = []  # List of test glyphs
        self.textGlyphs.append (TextGlyph(id, id)) 
        
    def __repr__(self):
        astr = 'Species: ' + self.modelId + '\n' 
        astr += 'Glyph id = ' + self.speciesGlyphId + '\n'
        astr +=  str (self.boundingBox) + '\n'
        astr += 'Number of text glyphs = ' + str (len (self.textGlyphs)) + '\n'
        for t in self.textGlyphs:
           astr += 'Text (GraphicalObj) = ' + t.graphicalObject_id + '\n'
           astr += 'text = "' + t.text + '"\n'
           astr += str (self.boundingBox) + '\n'
        astr += '-------------------------------------------' + '\n'
        return astr   
    
    def getNodeCenter(self):
        return [self.boundingBox.x + self.boundingBox.w/2, 
                self.boundingBox.y + self.boundingBox.h/2]
  
# layout:id="reactionGlyph_J1" layout:reaction="J1">  
class Reaction:
    
    def __init__ (self):
        self.reaction_modelId = ''  # This is the sbml model id
        self.reactionGlyph_id = '' # "reactionGlyph_" + reaction_id
        self.textGlyphs = []  # List of test glyphs
        self.center_pt = [] 
        
        # Convenience place to put the model ids for the reactants and products
        self.model_reactantIds = []
        self.model_productsIds = []
        #speciesReferenceGlyph, id="SpecRefG__J0_rct1", speciesReference="SpecRef__J0_rct1", speciesGlyph="SpecG_B_idx_1", role="substrate"

        self.reactionGlyph_curve = Curve('')  # Central curve(s) 
        self.speciesReferenceGlyphs_Reactants = []
        self.speciesReferenceGlyphs_Products = []
                
    def __repr__(self):
       astr = 'Reaction: ' + self.id + '\n'
       astr += 'Center pt = ' + str (self.center_pt) + '\n'
       astr += 'Bounding Box = ' + str (self.boundingBox) + '\n'
       return astr    
   
       
def lookForTextGlyphs(layout, srcGlyph):
     
     textGlyphs = []
     numTextGlyphs = layout.getNumTextGlyphs()
     for k in range(numTextGlyphs):
         textGlyphSBML = layout.getTextGlyph(k)
         if textGlyphSBML != None:
             if textGlyphSBML.isSetGraphicalObjectId():
                 graphicalObject_id = textGlyphSBML.getGraphicalObjectId()
             else:
                 graphicalObject_id = ''  
                 
         if graphicalObject_id == srcGlyph:
            textGlyph = TextGlyph('',textGlyphSBML.getText())    
            textGlyph.graphicalObject_id = graphicalObject_id
            temp_id = textGlyphSBML.getId()
            textGlyphs.append (textGlyph)
                   
            text_boundingbox = textGlyphSBML.getBoundingBox()
            text_x = text_boundingbox.getX()
            text_y = text_boundingbox.getY()   
            text_width = text_boundingbox.getWidth()
            text_height = text_boundingbox.getHeight()
            textGlyph.boundingBox = BoundingBox(text_x, text_y, text_width, text_height)
            
     return textGlyphs
    
class Layout: 
 
    def __init__ (self):
       self.width = Defaults.MAX_COMPARMENT_SIZE; self.height = Defaults.MAX_COMPARMENT_SIZE 
       self.id = '' 
       self.listOfCompartments = []
       self.listOfSpecies = []
       self.listOfTexts = []
       self.listOfReactions = []   
       
    def setLayoutDims (self, w, h):
        self.width = w
        self.height = h
        
    def computeLayoutExtent (self):
        
        x = 0; y = 0
        for compartment in self.listOfCompartments:
            if x < compartment.boundingBox.x + compartment.boundingBox.w:
                x = compartment.boundingBox.x + compartment.boundingBox.w
            if y < compartment.boundingBox.y  + compartment.boundingBox.h:
                y = compartment.boundingBox.y  + compartment.boundingBox.h
                
        for species in self.listOfSpecies:
            if x < species.boundingBox.x + species.boundingBox.w:
                x = species.boundingBox.x + species.boundingBox.w
            if y < species.boundingBox.y + species.boundingBox.h:
                y = species.boundingBox.y + species.boundingBox.h
                
        # Add 10% to the extent
        return (x + 0.1*x, y + 0.1*y)
            
    def findCompartmentGlyph (self, compartmentGlyphId):
        for node in self.listOfCompartments:
            if node.compartmentGlyphId == compartmentGlyphId:
                return node
        return None
    
    def findSpeciesGlyph (self, id):
        """ Find a species id in the layoutobj list of species. If found it returns a reference to that species object

        Args:
            id (string): The id for a species we want to find

        Raises:
            Exception: If a given speies cannpt be found it raises an exception. This should never happen
            in normal circumcstances

        Returns:
            Species_: A reference to a a species object
        """
        for node in self.listOfSpecies:
            if node.speciesGlyphId == id:
                return node
        #raise Exception('findSpeciesGlyph node: Unable to locate node: ' + id)
        return None
        
        
    def findSpeciesId (self, id):
        """ Find a species id in the layoutobj list of species. If found it returns a reference to that species object

        Args:
            id (string): The id for a species we want to find

        Raises:
            Exception: If a given speies cannpt be found it raises an exception. This should never happen
            in normal circumcstances

        Returns:
            Species_: A reference to a a species object
        """
        for node in self.listOfSpecies:
            if node.modelId == id:
                return node
        #raise Exception('findSpeciesId node: Unable to locate node: ' + id)
        return None
    
    
    def isSpecies_a_Reactant (self, reaction, id):
        for rt in reaction.speciesReferenceGlyphs_Reactants:
            if rt == id:
                return True
        return False
        
    def isSpecies_a_Product (self, reaction, id):
        for rt in reaction.speciesReferenceGlyphs_Products:
            if rt == id:
                return True
        return False
    
    
    
    def getNumCompartmentGlyphs (self, modelCompartmentId):
        count = 0
        for sp in self.listOfCompartments:  
            if sp.compartmentGlyphId == modelCompartmentId:
                count += 1
        return count
    
    
    def getListofCompartmentGlyphs (self, modelCompartmentId):
        alist = []
        for sp in self.listOfCompartments:
            if sp.compartmentId == modelCompartmentId:
                alist.append (sp.compartmentGlyphId)
        return alist
    
    
    def getNumSpeciesGlyphs (self, modelSpeciesId):
        count = 0
        for sp in self.listOfSpecies:  
            if sp.modelId == modelSpeciesId:
                count += 1
        return count


    def getListofSpeciesGlyphs (self, modelSpeciesId):
        alist = []
        for sp in self.listOfSpecies:
            if sp.modelId == modelSpeciesId:
                alist.append (sp.speciesGlyphId)
        return alist
         
         
    def getListofModelSpeciesIds (self):
        alist = []
        for sp in self.listOfSpecies:
            alist.append (sp.modelId)
        return alist       
      
      
    def setReactionGapDistance (self, gap):
        graphicsUtils.NODE_EDGE_GAP_DISTANCE = gap
        for reaction in self.listOfReactions:
            self.recomputeReactionPoints (reaction)
      
        
    def recomputeReactionPoints (self, reaction):
        #computeReactionCenterPt (self, reaction)               
        numReactants =  len (reaction.speciesReferenceGlyphs_Reactants)
        numProducts =  len (reaction.speciesReferenceGlyphs_Products)
                    
        for j in range (numReactants):
        
            speciesGlyphId  = reaction.speciesReferenceGlyphs_Reactants[j].speciesGlyph
                
            speciesReferenceGlyph = reaction.speciesReferenceGlyphs_Reactants[j]
                
            node = self.findSpeciesGlyph (speciesGlyphId) 
            # Compute the start point from node to center reaction pt
            ct = node.getNodeCenter() 
            found, pt = self.getReactantIntersectionPoint (node, reaction)
            if found: 
               speciesReferenceGlyph.curve.start_x = pt.x
               speciesReferenceGlyph.curve.start_y =  pt.y
            else:
               # because nodes are next to each other
               speciesReferenceGlyph.curve.start_x = ct[0]
               speciesReferenceGlyph.curve.start_y = ct[1]
                       
            speciesReferenceGlyph.curve.end_x = reaction.center_pt[0]
            speciesReferenceGlyph.curve.end_y = reaction.center_pt[1]  
            
        for j in range (numProducts):

            speciesGlyphId  = reaction.speciesReferenceGlyphs_Products[j].speciesGlyph
            speciesReferenceGlyph = reaction.speciesReferenceGlyphs_Products[j]
                
            node = self.findSpeciesGlyph (speciesGlyphId)
            ct = node.getNodeCenter() 

            found, pt  = self.getProductIntersectionPoint (node, reaction)
                
            speciesReferenceGlyph.curve.start_x = reaction.center_pt[0]
            speciesReferenceGlyph.curve.start_y = reaction.center_pt[1]
                
            if found:
                speciesReferenceGlyph.curve.end_x = pt.x
                speciesReferenceGlyph.curve.end_y = pt.y 
            else:
                speciesReferenceGlyph.curve.end_x = ct[0]
                speciesReferenceGlyph.curve.end_y = ct[1]  

    
    def setCompartmentDims (self, compartmentGlyphId, w, h):
        compartment = self.findCompartmentGlyph (compartmentGlyphId)    
        if compartment == None:
            raise Exception ('Unknown comparment glyph id')
        compartment.boundingBox.w = w
        compartment.boundingBox.h = h      
          
        
    # If we change a species position we have to recompute the reaction centers and intersection points
    def setSpeciesPosition (self, speciesGlyphId, x, y):
        species = self.findSpeciesGlyph (speciesGlyphId)
        if species == None:
            raise Exception ('Unknown species glyph id')
        species.boundingBox.x = x
        species.boundingBox.y = y
        
        # Recompute all intersection points since we don't know 
        # which reaction the species is associated with 
        for reaction in self.listOfReactions:
            computeReactionCenterPt (self, reaction)                                   
            self.recomputeReactionPoints (reaction)
                            
       
    # If we change a species position we have to recompute the reaction centers and intersection points
    def setSpeciesPosition_old (self, id, x, y, alias=0):
        species = self.findSpeciesGlyph (id)
        if species == None:
            raise Exception ('Unknown species id')
        species.boundingBox.x = x
        species.boundingBox.y = y
        
        # Recompute all intersection points since we don't know 
        # which reaction the species is associated with 
        for reaction in self.listOfReactions:
            computeReactionCenterPt (self, reaction)                                   
            self.recomputeReactionPoints (reaction)
        
        
    def loadLayoutFromSBML (self, document, n):
        """Load layout information from an SBML instance into the layoutobj

        Args:
            document (_type_): Reference to a libsbml document
            n (int): nth layout to load
        """
        model = document.getModel()
        mplugin = model.getPlugin("layout")
        if mplugin == None:
           raise Exception ('There is no layout information in this SBML model')

        numLayouts = mplugin.getNumLayouts()
        if n >= numLayouts:
          raise Exception ('The sbml model only has ' + str (numLayouts) + ' You selected layout does not exist')

        sbmllayout = mplugin.getLayout(n)
        if sbmllayout == None: 
           raise Exception ('Can"t fnd a layout to read')
             
        self.id = sbmllayout.getId() 
        dims = sbmllayout.getDimensions()
        self.width = dims.getWidth()
        self.height = dims.getHeight()
       
        numCompGlyphs = sbmllayout.getNumCompartmentGlyphs()
        numSpecGlyphs = sbmllayout.getNumSpeciesGlyphs()
        numReactionGlyphs = sbmllayout.getNumReactionGlyphs()
        numTextGlyphs = sbmllayout.getNumTextGlyphs()
       
        for i in range (numCompGlyphs):
           compGlyph = sbmllayout.getCompartmentGlyph(i)
           compartment = Compartment(compGlyph.getCompartmentId(), compGlyph.getCompartmentId())
           compartment.compartmentId = compGlyph.getCompartmentId()

           compartment.textGlyphs = lookForTextGlyphs (sbmllayout, compartment.compartmentId)
           self.listOfCompartments.append (compartment)
           
        for i in range (numSpecGlyphs):
          specGlyph = sbmllayout.getSpeciesGlyph(i)
          species = Species(specGlyph.getSpeciesId(), 'displayname')  # implement getDisplayName in simpleSBML 
          species.speciesGlyphId = specGlyph.getId() 
          boundingbox = specGlyph.getBoundingBox()
          
          height = boundingbox.getHeight()
          width = boundingbox.getWidth()
          pos_x = boundingbox.getX()
          pos_y = boundingbox.getY()

          species.boundingBox = BoundingBox (pos_x, pos_y, width, height)
          self.listOfSpecies.append(species)         
       
          species.textGlyphs = lookForTextGlyphs (sbmllayout, species.speciesGlyphId) 
                
        for i in range (numReactionGlyphs):
            reaction = Reaction()
            reactionGlyph = sbmllayout.getReactionGlyph(i)
            reaction.id = reactionGlyph.getId()         
            reaction.reaction_modelId = reactionGlyph.getReactionId()
           
            reaction.textGlyphs = lookForTextGlyphs (sbmllayout, reaction.id)           
           
            # This is the center curve. We normally treat it as a point
            curve = reactionGlyph.getCurve()   

            reaction.center_pt = []
            center_sz = []
            for segment in curve.getListOfCurveSegments():
                short_line_start_x = segment.getStart().getXOffset()
                short_line_start_y = segment.getStart().getYOffset()
                short_line_end_x   = segment.getEnd().getXOffset()
                short_line_end_y   = segment.getEnd().getYOffset() 
                short_line_start = [short_line_start_x, short_line_start_y]
                short_line_end   = [short_line_end_x, short_line_end_y]
                if short_line_start == short_line_end: #the centroid is a dot
                   reaction.center_pt = short_line_start
                else: # the centroid is a short line
                   reaction.center_pt = [0.5*(short_line_start_x+short_line_end_x),
                                             0.5*(short_line_start_y+short_line_end_y)]          

            boundingBox = reactionGlyph.getBoundingBox()
            width = boundingbox.getWidth()
            height = boundingbox.getHeight()
            pos_x = boundingbox.getX()
            pos_y = boundingBox.getY()
                
            reaction.boundingBox = BoundingBox (pos_x, pos_y, width, height)
            if reaction.center_pt == []:
               if pos_x == 0 and pos_y == 0 and width == 0 and height == 0: #LinearChain.xml
                   reaction.center_pt = []
               else:
                   reaction.center_pt = [pos_x+.5*width, pos_y+.5*height]
            center_sz = [width, height]
           
            #if curveType == Defaults.CUBIC_BEZIER:
            #   raise Exception('Cubic Bezier in middle segment of reaction is not supported')
            
           # Here we start reading the substrate and product curves
           
            numSpecRefGlyphs = reactionGlyph.getNumSpeciesReferenceGlyphs()
            for j in range(numSpecRefGlyphs):
               speciesReferenceGlyph = SpeciesReferenceGlyph()
               
               specRefGlyph = reactionGlyph.getSpeciesReferenceGlyph(j)
               speciesGlyphId = specRefGlyph.getSpeciesGlyphId()
               y = specRefGlyph.getSpeciesReferenceId()
               speiescReferenceGlyph_id = specRefGlyph.getId()    
      
               speciesReferenceGlyph.id = speiescReferenceGlyph_id   # ok
               speciesReferenceGlyph.speciesGlyph = speciesGlyphId  # ok
               speciesReferenceGlyph.speciesReference = speiescReferenceGlyph_id  
               speciesReferenceGlyph.role = specRefGlyph.getRoleString()
               
#<layout:speciesReferenceGlyph layout:id="SpecRefG_J0_rct0" layout:speciesReference="SpecRef_J0_rct0" layout:speciesGlyph="SpecG_External_glucose_idx_0" layout:role="substrate">
 
#<layout:speciesReferenceGlyph layout:id="speciesReference_J0_0" layout:speciesReference="A" layout:speciesGlyph="speciesGlyph_A" layout:role="substrate">
     
               curve = specRefGlyph.getCurve()
               if curve.getListOfCurveSegments().__len__() > 1:
                  raise Exception ('More than one curve segment not supported')
                        
               for segment in curve.getListOfCurveSegments():  
                            curveType = segment.getTypeCode()   
                            speciesReferenceGlyph.curve.curveType = Defaults.LINE_SEGMENT               
                            line_start_x = segment.getStart().getXOffset()
                            line_start_y = segment.getStart().getYOffset()
                            line_end_x = segment.getEnd().getXOffset()
                            line_end_y = segment.getEnd().getYOffset() 
                            if curveType == Defaults.CUBIC_BEZIER:
                               speciesReferenceGlyph.curve.curveType = Defaults.CUBIC_BEZIER
                               speciesReferenceGlyph.curve.basepoint1 = [segment.getBasePoint1().getXOffset(), segment.getBasePoint1().getYOffset()] 
                               speciesReferenceGlyph.curve.basepoint2 = [segment.getBasePoint2().getXOffset(), segment.getBasePoint2().getYOffset()] 
                                        
               speciesReferenceGlyph.curve.start_x = line_start_x
               speciesReferenceGlyph.curve.start_y = line_start_y
               speciesReferenceGlyph.curve.end_x = line_end_x
               speciesReferenceGlyph.curve.end_y = line_end_y

               if speciesReferenceGlyph.role == 'substrate':
                   reaction.speciesReferenceGlyphs_Reactants.append (speciesReferenceGlyph) 

               if speciesReferenceGlyph.role == 'product':
                   reaction.speciesReferenceGlyphs_Products.append (speciesReferenceGlyph) 
                                                     
            self.listOfReactions.append(reaction)  
    
    
    def createBoundingBox (self, x, y, w, h):
        boundingBox = libsbml.BoundingBox()
        boundingBox.setX(x)
        boundingBox.setY(y)
        boundingBox.setWidth(w)
        boundingBox.setHeight(h)
        return boundingBox



    # Create a SBML bounding box
    def createBoundingBox (self, x, y, w, h):
            boundingBox = libsbml.BoundingBox()
            boundingBox.setX(x)
            boundingBox.setY(y)
            boundingBox.setWidth(w)
            boundingBox.setHeight(h)
            return boundingBox
    
    
    def getReactantIntersectionPoint (self, node, reaction):
        ct = node.getNodeCenter()
        lineSegment = TLineSegment (TPointF (ct[0], ct[1]), 
                                    TPointF (reaction.center_pt[0], reaction.center_pt[1]))
        return computeLineIntersection(node, lineSegment)
    
    
    def getProductIntersectionPoint (self, node, reaction):
        ct = node.getNodeCenter()
        lineSegment = TLineSegment (TPointF (reaction.center_pt[0], reaction.center_pt[1]),
                                    TPointF (ct[0], ct[1]))
        return computeLineIntersection(node, lineSegment)
        
        
    def saveLayoutObjToSBML (self, document):
        """Uses the layoutObject to generate to update the libsbml document argument

        Args:
            document: Refernce to libsbml document
        """
        document.enablePackage(libsbml.LayoutExtension_getXmlnsL3V1V1(), "layout", True)
        document.setPkgRequired("layout", False) 
        model = document.getModel() 
        mplugin = model.getPlugin("layout")
        sbmllayout = mplugin.createLayout()
            
        sbmllayout.setId("SBML_layout")
        layoutns = libsbml.LayoutPkgNamespaces(3, 1, 1)
        dimensions = libsbml.Dimensions()
        dimensions.setBounds(self.width, self.height)
        sbmllayout.setDimensions(dimensions)
        
        for i in range (len (self.listOfCompartments)):
           compartmentGlyph = sbmllayout.createCompartmentGlyph() 
           compartment_id = self.listOfCompartments[i].compartmentId
           compartmentGlyph.setCompartmentId(compartment_id)
           compartmentGlyph.setId(self.listOfCompartments[i].compartmentGlyphId)

           compartmentGlyph.setBoundingBox (self.createBoundingBox(0, 0, 499, 499))  
        
           textGlyph = sbmllayout.createTextGlyph()
           textG_id = "TextG_" + compartment_id
           textGlyph.setId(textG_id)
           textGlyph.setText(compartment_id)
           textGlyph.setGraphicalObjectId('compartmentGlyph_' + compartment_id)
        
        nodesSpeciesGlyphId = {}   # Mapping of species id to glyph species id
        numSpecies = len (self.listOfSpecies)
        for i in range (numSpecies): 
            species = self.listOfSpecies[i]
                
            speciesGlyph = sbmllayout.createSpeciesGlyph()

            # Create mapping between species id and spieces glyph id
            nodesSpeciesGlyphId[species.modelId] = species.speciesGlyphId
                
            speciesGlyph.setId( species.speciesGlyphId)
            speciesGlyph.setSpeciesId(species.modelId)
            speciesGlyph.setBoundingBox (self.createBoundingBox(species.boundingBox.x, species.boundingBox.y, 
                                                        species.boundingBox.w, species.boundingBox.h)) 
                
            textGlyph = sbmllayout.createTextGlyph()
            textG_id = "TextG_" +  species.speciesGlyphId
            textGlyph.setId(textG_id)
            textGlyph.setText(species.modelId)
            textGlyph.setGraphicalObjectId(species.speciesGlyphId)  
            
        nodeCenters = {}  # a map between species ids and node centers
        for i in range (numSpecies):
            sp = self.listOfSpecies[i]
            ct = sp.getNodeCenter()
            nodeCenters[self.listOfSpecies[i].modelId] = ct
            
        numReactions = len (self.listOfReactions)
        for i in range(numReactions):
                reaction = self.listOfReactions[i]
                reaction_modelId = reaction.reaction_modelId
                reactionGlyph = sbmllayout.createReactionGlyph()
                reactionGlyph.setId(reaction.reactionGlyph_layout_id)
                reactionGlyph.setReactionId(reaction_modelId)
                
                numReactants =  len (reaction.speciesReferenceGlyphs_Reactants)
                numProducts = len (reaction.speciesReferenceGlyphs_Products)
                
                reactionCurve = reactionGlyph.getCurve()
                ls = reactionCurve.createLineSegment()
                
                p = libsbml.Point()
                p.setOffsets (reaction.center_pt[0], reaction.center_pt[1])
                ls.setStart(p)
                ls.setEnd(p)
                
                for j in range(numReactants):
                    modelSpecies_id = reaction.model_reactantIds[j]

                    speciesReferenceGlyph = reactionGlyph.createSpeciesReferenceGlyph()
                    speciesReferencefGlyph_id = "speciesReference_" + reaction_modelId + '_' + str(j)

                    speciesReferenceGlyph.setId(speciesReferencefGlyph_id)
                    # this line won't work when creating alias nodes
                    speciesReferenceGlyph.setSpeciesGlyphId(nodesSpeciesGlyphId[modelSpecies_id]) # not ok
                    speciesReferenceGlyph.setSpeciesReferenceId(modelSpecies_id)  # ok
                    speciesReferenceGlyph.setRole(libsbml.SPECIES_ROLE_SUBSTRATE)
                    
        #self.id="SpeciesReferenceGlyph_J0_rct1"
        #self.speciesReference="SpeciesReference_J0_rct1"
        #self.speciesGlyph="SpeciesGlyph_B_idx_1"
        
        
                    speciesReferenceCurve = speciesReferenceGlyph.getCurve()
                    cb = speciesReferenceCurve.createLineSegment()   
                                      
                    ct = nodeCenters[modelSpecies_id]  
                    # Compute the start point here from node to center reaction pt
                    #node = self.find (modelSpecies_id)
                    #found, pt = self.getReactantIntersectionPoint (node, reaction)

                    pt = TPointF(reaction.speciesReferenceGlyphs_Reactants[j].curve.start_x,
                                 reaction.speciesReferenceGlyphs_Reactants[j].curve.start_y)
                    
                    p = libsbml.Point () 
                    p.setOffsets (pt.x, pt.y)   
                    cb.setStart (p)
                    p.setOffsets (reaction.center_pt[0], reaction.center_pt[1])
                    cb.setEnd(p)
                            
                for j in range(numProducts):
                    modelSpecies_id = reaction.model_productIds[j]
                    
                    speciesReferenceGlyph = reactionGlyph.createSpeciesReferenceGlyph()
                    specsRefG_id = "speciesReference_" + reaction_modelId + '_' + str(j + numReactants)
                    speciesReferenceGlyph.setId(specsRefG_id)
                    speciesReferenceGlyph.setSpeciesGlyphId(nodesSpeciesGlyphId[modelSpecies_id])                                
                    speciesReferenceGlyph.setSpeciesReferenceId(modelSpecies_id)
                    speciesReferenceGlyph.setRole(libsbml.SPECIES_ROLE_PRODUCT)
                    speciesReferenceCurve = speciesReferenceGlyph.getCurve()
                    cb = speciesReferenceCurve.createLineSegment() 
                
                    pt = TPointF(0,0)
                    pt.x =  reaction.speciesReferenceGlyphs_Products[j].curve.end_x
                    pt.y =  reaction.speciesReferenceGlyphs_Products[j].curve.end_y
                    
                    p = libsbml.Point () 
                    p.setOffsets (reaction.center_pt[0], reaction.center_pt[1])  
                    cb.setStart (p)
                    p.setOffsets (pt.x, pt.y)                         
                    cb.setEnd(p)

        
    def computeStartEndPointForReactant(reactantId, nodeCenter):
        pass
        
        
    def updateReactionPositions (self):
        for rt in self.listOfReactions:
            computeReactionCenterPt(self, rt)  
            self.computeIntersectionPts (rt)
 
    
    # Needs to be fixed
    def computeIntersectionPts (self, reaction):
        for subCurve in reaction.reactantCurves: 
            # Compute the start point here from node to center reaction pt
            node = self.findSpeciesGlyph (subCurve.speciesId)
            ct = node.getNodeCenter ()
            found, pt = self.getReactantIntersectionPoint (node, reaction)
            if not found: # because nodes are next to each other, therefore no intersection
                subCurve.start_x = ct[0]
                subCurve.start_y = ct[1]
            else:
                subCurve.start_x = pt.x
                subCurve.start_y = pt.y
                       
            subCurve.end_x = reaction.center_pt[0]
            subCurve.end_y = reaction.center_pt[1]
    
        for subCurve in reaction.productCurves:

            node = self.findSpeciesGlyph (subCurve.speciesId)
            ct = node.getNodeCenter ()
 
            found, pt  = self.getProductIntersectionPoint (node, reaction)
                
            subCurve.start_x = reaction.center_pt[0]
            subCurve.start_y = reaction.center_pt[1]
                
            if found:
               subCurve.end_x = pt.x
               subCurve.end_y = pt.y 
            else:
               subCurve.end_x = ct[0]
               subCurve.end.y = ct[1] 
               
                 
    # Call this if we don't have a layout in the SBML model  
    def createNewLayoutObject (self, document):
        """Given a reference to a sbml document fill in the layoutobj with layout information
          that could be used at a later time to generate SBML layout output

        Args:
            document (Sbml document): Referece to a libsbml document
        """    
        model = document.getModel()
        
        numCompartments = model.getNumCompartments()
        for i in range (numCompartments):
            sbmlCompartment = model.getCompartment(i)
            # '' means method will create a glyph id for the compartment
            compartment = Compartment(sbmlCompartment.getId(), sbmlCompartment.getId())
            self.listOfCompartments.append (compartment)
            
        numSpecies = model.getNumSpecies()
        speciesList = sbmlUtils.getListOfAllSpecies(model)
        nodeCenters = {}
        nodesSpeciesGlyphId = {}
        for i in range (numSpecies):
            species = Species(speciesList[i], 'displayName')
            self.listOfSpecies.append(species)    
            species.speciesGlyphId = "speciesGlyph_"  + species.modelId

            nodesSpeciesGlyphId[species.modelId] = species.speciesGlyphId
            
            x = random.randint(0, 300)
            y = random.randint(0, 300)
            species.boundingBox = BoundingBox(x, y, Defaults.NODE_WIDTH, Defaults.NODE_HEIGHT)
            nodeCenters[species.modelId] = species.getNodeCenter()
            
        numReactions = model.getNumReactions()
        for i in range(numReactions):
            reaction = Reaction()
            reaction.model_reactantIds = []
            reaction.model_productIds = []
            
            reaction.id = sbmlUtils.getNthReactionId(model, i) # model reaction id
            reaction.reactionGlyph_layout_id = 'reactionGlyph_' + reaction.id # local id to this reactionGlyph

            self.listOfReactions.append (reaction)
            # Compute the centroid between the reactants and products
            reaction.center_pt = [0,0]
            numReactants = sbmlUtils.getNumReactants(model, i)
            numProducts = sbmlUtils.getNumProducts(model, i)
            
            for j in range (numReactants):
                reactantId = sbmlUtils.getReactant(model, i, j)
                reaction.model_reactantIds.append (reactantId)
            for j in range (numProducts):
                productId = sbmlUtils.getProduct(model, i, j)
                reaction.model_productIds.append (productId)
                
            #  Set up the species glyph so that we can then compute the center pt
            for j in range (numReactants):
                reactantId = sbmlUtils.getReactant(model, i, j)
                
                speciesReferenceGlyph = SpeciesReferenceGlyph() 
                speciesReferenceGlyph.speciesGlyph = nodesSpeciesGlyphId[reactantId] 
                
                reaction.speciesReferenceGlyphs_Reactants.append (speciesReferenceGlyph)           

            for j in range (numProducts):
                productId = sbmlUtils.getProduct(model, i, j)
                
                speciesReferenceGlyph = SpeciesReferenceGlyph() 
                speciesReferenceGlyph.speciesGlyph = nodesSpeciesGlyphId[productId] 
                
                reaction.speciesReferenceGlyphs_Products.append (speciesReferenceGlyph) 
                   
            computeReactionCenterPt(self, reaction)    
                
        #self.id="SpeciesReferenceGlyph_J0_rct1"
        #self.speciesReference="SpeciesReference_J0_rct1"
        #self.speciesGlyph="SpeciesGlyph_B_idx_1"
        
            # Next we compte the coordinates for the reaction curves
            for j in range (numReactants):
        
                speciesGlyphId  = reaction.speciesReferenceGlyphs_Reactants[j].speciesGlyph
                
                speciesReferenceGlyph = reaction.speciesReferenceGlyphs_Reactants[j]
                speciesReferenceGlyph.curve.curveType = Defaults.LINE_SEGMENT
                
                node = self.findSpeciesGlyph (speciesGlyphId) 
                # Compute the start point from node to center reaction pt
                ct = node.getNodeCenter() 
                found, pt = self.getReactantIntersectionPoint (node, reaction)
                if not found: # because nodes are next to each other
                    speciesReferenceGlyph.curve.start_x = ct[0]
                    speciesReferenceGlyph.curve.start_y = ct[1]
                else:
                    speciesReferenceGlyph.curve.start_x = pt.x
                    speciesReferenceGlyph.curve.start_y =  pt.y
                       
                speciesReferenceGlyph.curve.end_x = reaction.center_pt[0]
                speciesReferenceGlyph.curve.end_y = reaction.center_pt[1]

            for j in range (numProducts):

                speciesGlyphId  = reaction.speciesReferenceGlyphs_Products[j].speciesGlyph
                speciesReferenceGlyph = reaction.speciesReferenceGlyphs_Products[j]
                speciesReferenceGlyph.curve.curveType = Defaults.LINE_SEGMENT
                
                node = self.findSpeciesGlyph (speciesGlyphId)
                ct = node.getNodeCenter() 

                found, pt  = self.getProductIntersectionPoint (node, reaction)
                
                speciesReferenceGlyph.curve.start_x = reaction.center_pt[0]
                speciesReferenceGlyph.curve.start_y = reaction.center_pt[1]
                
                if found:
                   speciesReferenceGlyph.curve.end_x = pt.x
                   speciesReferenceGlyph.curve.end_y = pt.y 
                else:
                   speciesReferenceGlyph.curve.end_x = ct[0]
                   speciesReferenceGlyph.curve.end_y = ct[1]   

  
