

# ---------------------------------------------------------------------------------------
# NO LONGER USED
# ----------------------------------------------------------------------------------------

import layoutClass
from layoutClass import Layout
from defaults import Defaults

import libsbml
import random
from graphicsUtils import BoundingBox
from graphicsUtils import TPointF
from graphicsUtils import TLineSegment
from graphicsUtils import computeLineIntersection


# Create a SBML bounding box
def createBoundingBox (x, y, w, h):
        boundingBox = libsbml.BoundingBox()
        boundingBox.setX(x)
        boundingBox.setY(y)
        boundingBox.setWidth(w)
        boundingBox.setHeight(h)
        return boundingBox
    
    
def saveLayoutObjToSBML (layoutObj : Layout, document):
    """Uses the layoutObject to generate sbml

    Args:
        layoutObj (Layout): Reference to a layout object
        sbmllayout (see sbml docs): Reference to a layout object from sbml via the layut plugin
    """
    document.enablePackage(libsbml.LayoutExtension_getXmlnsL3V1V1(), "layout", True)
    document.setPkgRequired("layout", False) 
    model = document.getModel() 
    mplugin = model.getPlugin("layout")
    sbmllayout = mplugin.createLayout()
           
    sbmllayout.setId("SBML_layout")
    layoutns = libsbml.LayoutPkgNamespaces(3, 1, 1)
    dimensions = libsbml.Dimensions()
    dimensions.setBounds(500, 500)
    sbmllayout.setDimensions(dimensions)
    
    for i in range (len (layoutObj.listOfCompartments)):
       compartmentGlyph = sbmllayout.createCompartmentGlyph() 
       compartment_id = layoutObj.listOfCompartments[i].compartmentId
       compartmentGlyph.setCompartmentId(compartment_id)
       compartmentGlyph.setId(layoutObj.listOfCompartments[i].compartmentGlyphId)

       compartmentGlyph.setBoundingBox (createBoundingBox(0, 0, 499, 499))  
    
       textGlyph = sbmllayout.createTextGlyph()
       textG_id = "TextG_" + compartment_id
       textGlyph.setId(textG_id)
       textGlyph.setText(compartment_id)
       textGlyph.setGraphicalObjectId('go_' + compartment_id)
    
    nodesSpeciesGlyphId = {}   # Mapping of species id to glyph species id
    numSpecies = len (layoutObj.listOfSpecies)
    for i in range (numSpecies): 
        species = layoutObj.listOfSpecies[i]
        #speciesLayoutid = "go_"  + species.id
        #species.graphicalObject_id = speciesLayoutid
            
        speciesGlyph = sbmllayout.createSpeciesGlyph()

        # Create mapping between species id and spieces glyph id
        nodesSpeciesGlyphId[species.id] = species.speciesGlyphId
            
        speciesGlyph.setId( species.speciesGlyphId)
        speciesGlyph.setSpeciesId(species.id)
        speciesGlyph.setBoundingBox (createBoundingBox(species.boundingBox.x, species.boundingBox.y, 
                                                       species.boundingBox.w, species.boundingBox.h)) 
            
        textGlyph = sbmllayout.createTextGlyph()
        textG_id = "TextG_" +  species.speciesGlyphId
        textGlyph.setId(textG_id)
        textGlyph.setText(species.id)
        textGlyph.setGraphicalObjectId(species.speciesGlyphId)  
        
    nodeCenters = {}
    for i in range (numSpecies):
        sp = layoutObj.listOfSpecies[i]
        ct = sp.getNodeCenter()
        nodeCenters[layoutObj.listOfSpecies[i].id] = ct
         
    numReactions = len (layoutObj.listOfReactions)
    for i in range(numReactions):
            reaction = layoutObj.listOfReactions[i]
            reaction_id = reaction.id
            reactionGlyph = sbmllayout.createReactionGlyph()
            reactionLayout_id = "ReactionG_" + reaction_id
            reactionGlyph.setId(reactionLayout_id)
            reactionGlyph.setReactionId(reaction_id)
            
            numReactants =  len (reaction.reactants)
            numProducts = len (reaction.products)
            
            reactionCurve = reactionGlyph.getCurve()
            ls = reactionCurve.createLineSegment()
            
            p = libsbml.Point()
            p.setX(reaction.center_pt[0]); p.setY(reaction.center_pt[1])
            ls.setStart(p)
            ls.setEnd(p)
            
            for j in range(numReactants):
                modelSpecies_id = reaction.reactants[j]

                speciesReferenceGlyph = reactionGlyph.createSpeciesReferenceGlyph()
                specsRefG_id = "SpecRef_Id_" + reaction_id + '_' + str(j)

                speciesReferenceGlyph.setId(specsRefG_id)
                speciesReferenceGlyph.setSpeciesGlyphId(nodesSpeciesGlyphId[modelSpecies_id])
                speciesReferenceGlyph.setSpeciesReferenceId(modelSpecies_id)
                speciesReferenceGlyph.setRole(libsbml.SPECIES_ROLE_SUBSTRATE)
                speciesReferenceCurve = speciesReferenceGlyph.getCurve()
                cb = speciesReferenceCurve.createLineSegment()   
                ct = nodeCenters[modelSpecies_id]  
                # Compute the start point here from node to center reaction pt
                node = layoutObj.find (modelSpecies_id)
                lineSegment = TLineSegment (TPointF (ct[0], ct[1]), 
                                 TPointF (reaction.center_pt[0], reaction.center_pt[1]))
                found, pt = computeLineIntersection(node, lineSegment)
                p = libsbml.Point () 
                if not found: # because nodes are next to each other
                    p.setX(ct[0]); p.setY(ct[1])
                else:
                    p.setX (pt.x); p.setY (pt.y)   
                cb.setStart (p)
                p.setX(reaction.center_pt[0]); p.setY(reaction.center_pt[1])
                cb.setEnd(p)
                        
            for j in range(numProducts):
                modelSpecies_id = reaction.products[j]
                
                ref_id = "SpecRef_" + reaction_id
                speciesReferenceGlyph = reactionGlyph.createSpeciesReferenceGlyph()
                specsRefG_id = "SpecRef_Id_" + reaction_id + '_' + str(j + numReactants)
                speciesReferenceGlyph.setId(specsRefG_id)
                speciesReferenceGlyph.setSpeciesGlyphId(nodesSpeciesGlyphId[modelSpecies_id])                                
                speciesReferenceGlyph.setSpeciesReferenceId(modelSpecies_id)
                speciesReferenceGlyph.setRole(libsbml.SPECIES_ROLE_PRODUCT)
                speciesReferenceCurve = speciesReferenceGlyph.getCurve()
                cb = speciesReferenceCurve.createLineSegment() 
                
                ct = nodeCenters[modelSpecies_id]  
                node = layoutObj.find (modelSpecies_id) 
                lineSegment = TLineSegment (TPointF (reaction.center_pt[0], reaction.center_pt[1]),
                                        TPointF (ct[0], ct[1]))
                found, pt = computeLineIntersection(node, lineSegment)
                p = libsbml.Point () 
                p.setX(reaction.center_pt[0]); p.setY(reaction.center_pt[1])  
                cb.setStart (p)
                if found:
                   p.setX (pt.x); p.setY(pt.y) 
                else:
                   p.setX (ct[0]); p.setY(ct[1]) 
                    
                cb.setEnd(p)
