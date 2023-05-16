
from dataclasses import dataclass

NODE_EDGE_GAP_DISTANCE = 6  # Distance between node and start of bezier line

@dataclass
class TPointF:   # A 2D point
     x : float
     y : float
     
@dataclass    
class TLineSegment:  # A line segment
     p : TPointF
     q : TPointF
     
class BoundingBox:  
  def __init__(self, x, y, w, h):
      self.x = x
      self.y = y
      self.w = w
      self.h = h
   
  def __repr__(self):
      astr  = 'BoundingBox (x,y,w,h): ' + str (self.x) + ', ' + str (self.y) + ', ' + str (self.w) + ', ' + str (self.h)   
      return astr
   
# Array 1 to 4 of TLineSegment
# We don't use the first one, legacy form original code
squareSegments = [TLineSegment (TPointF (0, 0), TPointF (0, 0)),  
                  TLineSegment (TPointF (0, 0), TPointF (0, 0)),
                  TLineSegment (TPointF (0, 0), TPointF (0, 0)),
                  TLineSegment (TPointF (0, 0), TPointF (0, 0)),
                  TLineSegment (TPointF (0, 0), TPointF (0, 0))]
  
# Construct the outer rectangle segments which forms the 
# boundary where reaction arcs start and stop at nodes.
def computeOuterSegs (node):
  
  tx = node.boundingBox.x
  ty = node.boundingBox.y
  tw = node.boundingBox.w
  th = node.boundingBox.h

  gap = NODE_EDGE_GAP_DISTANCE

  squareSegments[1].p.x = tx - gap;
  squareSegments[1].p.y = ty - gap;
  squareSegments[1].q.x = tx + tw + gap;
  squareSegments[1].q.y = ty - gap;

  squareSegments[2].p.x = tx + tw + gap;
  squareSegments[2].p.y = ty - gap;
  squareSegments[2].q.x = tx + tw + gap;
  squareSegments[2].q.y = ty + th + gap;

  squareSegments[3].p.x = tx + tw + gap;
  squareSegments[3].p.y = ty + th + gap;
  squareSegments[3].q.x = tx - gap;
  squareSegments[3].q.y = ty + th + gap;

  squareSegments[4].p.x = tx - gap;
  squareSegments[4].p.y = ty + th + gap;
  squareSegments[4].q.x = tx - gap;
  squareSegments[4].q.y = ty - gap;
  
  return squareSegments

# Check if the target line (v2) intersects the SEGMENT line (v1). Returns
# true if lines intersect with intersection coordinate returned in v, else
# returns false
# Returns True/False and v
def segmentIntersects (v1 : TLineSegment, v2 : TLineSegment): # Returns TPointF, v1 and v2 : TLineSegment

  xlk = v2.q.x - v2.p.x;
  ylk = v2.q.y - v2.p.y;
  xnm = v1.p.x - v1.q.x;
  ynm = v1.p.y - v1.q.y;
  xmk = v1.q.x - v2.p.x;
  ymk = v1.q.y - v2.p.y;

  det = xnm*ylk - ynm*xlk;
  if abs (det) < 1e-6:
     return False, 0
  else:
     detinv = 1.0/det;
     s = (xnm*ymk - ynm*xmk)*detinv;
     t = (xlk*ymk - ylk*xmk)*detinv;
     if (s < 0.0) or (s > 1.0) or (t < 0.0) or (t > 1.0):
        return False, 0
     else:
        v = TPointF(0,0) 
        v.x = v2.p.x + xlk*s;
        v.y = v2.p.y + ylk*s;
        return True, v
    
# Returns True/False, and if True also the intersetion point
def computeLineIntersection(node, lineSegment):
  # Construct the outer rectangle for the node
  outerSegs = computeOuterSegs (node)

  for j in range (1, 4+1):
       isIntersects, pt = segmentIntersects (outerSegs[j], lineSegment)
       if isIntersects: 
          return True, pt
  return False, 0


def computeReactionCenterPt (layoutObj, reaction):
    reaction.center_pt = [0,0]
    numReactants =  len (reaction.speciesReferenceGlyphs_Reactants)
    numProducts = len (reaction.speciesReferenceGlyphs_Products)
    
    for j in range (numReactants):
        speciesGlyphId  = reaction.speciesReferenceGlyphs_Reactants[j].speciesGlyph
                
        node = layoutObj.findSpeciesGlyph (speciesGlyphId)
        ct = node.getNodeCenter()
                
        reaction.center_pt[0] += ct[0]
        reaction.center_pt[1] += ct[1]
                
    for j in range (numProducts):
        speciesGlyphId  = reaction.speciesReferenceGlyphs_Products[j].speciesGlyph
        
        node = layoutObj.findSpeciesGlyph (speciesGlyphId)       
        ct = node.getNodeCenter()
                
        reaction.center_pt[0] += ct[0]
        reaction.center_pt[1] += ct[1]
                
    reaction.center_pt[0] = reaction.center_pt[0]/(numReactants + numProducts) 
    reaction.center_pt[1] = reaction.center_pt[1]/(numReactants + numProducts) 