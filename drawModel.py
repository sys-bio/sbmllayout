
import skia
import tempfile
from PIL import Image  # to load images
from IPython.core.display import display

from layoutClass import Layout
from defaults import Defaults

# Not used
def addSimpleText(canvas, text, position, text_line_color, text_line_width=1, fontSize = Defaults.FONT_SIZE):
    fontColor = skia.Color(text_line_color[0], text_line_color[1], text_line_color[2], text_line_color[3])
    #fontColor = skia.Color(255, 255, 255, 255)
    font = skia.Font(skia.Typeface('Arial', skia.FontStyle.Normal()), fontSize)
    paintText = skia.Paint(Color=fontColor, StrokeWidth=text_line_width)
    canvas.drawSimpleText(text, position[0], position[1], font, paintText)  
   
    
def drawScreen (layout):
    surface = skia.Surface(int (layout.width), int (layout.height))
    canvas = surface.getCanvas()  
    _draw (layout, canvas)  

    image = surface.makeImageSnapshot()
    _, tmpfile = tempfile.mkstemp()
    image.save(tmpfile, skia.kPNG)
                
    pil_im = Image.open(tmpfile)
    #new_image = pil_im.resize((500, 500))
    #display(new_image)   
    display (pil_im)
    return pil_im #new_image   
    
    
def drawPdf (layout, fileName):   
    stream = skia.FILEWStream(fileName)
    with skia.PDF.MakeDocument(stream) as document:
       with document.page(layout.width, layout.height) as canvas:
            _draw (layout, canvas)
            
def drawSVG (layout, fileName):
    
    stream = skia.FILEWStream(fileName)
    canvas = skia.SVGCanvas.Make((layout.width, layout.height), stream)
    _draw(layout, canvas)
    del canvas
    stream.flush()


def drawPng (layout, fileName):
    surface = skia.Surface(int (layout.width), int (layout.height))
    canvas = surface.getCanvas()  
    _draw (layout, canvas)  

    image = surface.makeImageSnapshot()
    image.save(fileName, skia.kPNG)

# draw to any canvas
def _draw(layout : Layout, canvas):
    
    # Clear the canvas first
    paintFill = skia.Paint(
                Color=Defaults.WHITE,
                Style=skia.Paint.kFill_Style)
    rect = skia.Rect(0, 0, layout.width, layout.height)     
    canvas.drawRect(rect, paintFill)     
        
    paintStroke = skia.Paint(
          AntiAlias=True,
          StrokeWidth=3,
          Style = skia.Paint.kStroke_Style,
          Color =  Defaults.DARK_ORANGE)
    
    for cp in layout.listOfCompartments:
        # Only draw non-default compartments
        if cp.compartmentId != Defaults.DEFAULT_COMPARMTENT_ID:
           rect = skia.Rect(cp.boundingBox.x, cp.boundingBox.y,
                            cp.boundingBox.x + cp.boundingBox.w, 
                            cp.boundingBox.y + cp.boundingBox.h)  
           canvas.drawRoundRect(rect, 6, 6, paintStroke);
  
    for rt in layout.listOfReactions:
        for rc in rt.speciesReferenceGlyphs_Reactants: 
            if rc.curve.curveType == Defaults.LINE_SEGMENT:
               canvas.drawLine (rc.curve.start_x, rc.curve.start_y, rc.curve.end_x, rc.curve.end_y, paintStroke)
            else:
               path = skia.Path()
               path.moveTo(rc.curve.start_x, rc.curve.start_y)
               path.cubicTo(rc.curve.basepoint1[0] , rc.curve.basepoint1[1], 
                            rc.curve.basepoint2[0], rc.curve.basepoint2[1], rc.curve.end_x, rc.curve.end_y)
               canvas.drawPath(path, paintStroke)
               oldWidth = paintStroke.getStrokeWidth()
               paintStroke.setStrokeWidth (2)
               canvas.drawLine (rc.curve.start_x, rc.curve.start_y,
                                rc.curve.basepoint1[0] , rc.curve.basepoint1[1], paintStroke)
               paintStroke.setStrokeWidth (oldWidth)            
    
        for rc in rt.speciesReferenceGlyphs_Products:
            if rc.curve.curveType == Defaults.LINE_SEGMENT:
               canvas.drawLine (rc.curve.start_x, rc.curve.start_y, rc.curve.end_x, rc.curve.end_y, paintStroke)
            else:
               path = skia.Path()
               path.moveTo(rc.curve.start_x, rc.curve.start_y)
               path.cubicTo(rc.curve.basepoint1[0] , rc.curve.basepoint1[1], 
                            rc.curve.basepoint2[0], rc.curve.basepoint2[1], rc.curve.end_x, rc.curve.end_y)
               canvas.drawPath(path, paintStroke)
               oldWidth = paintStroke.getStrokeWidth()
               paintStroke.setStrokeWidth (2)
               canvas.drawLine (rc.curve.basepoint2[0] , rc.curve.basepoint2[1], 
                                rc.curve.end_x, rc.curve.end_y, paintStroke)
               paintStroke.setStrokeWidth (oldWidth)               
                

    for sp in layout.listOfSpecies:
        
        # First thing to do is find out the width of the text
        x = sp.textGlyphs[0].boundingBox.x + sp.boundingBox.w/2
        y = sp.textGlyphs[0].boundingBox.y + sp.boundingBox.h/2
        #addSimpleText(canvas, sp.textGlyphs[0].text, [x,  y], [255,255,255,255])
        
        node_x = sp.boundingBox.x
        node_y = sp.boundingBox.y
        widthNode = sp.boundingBox.w
        heightNode = sp.boundingBox.h
        
        font = skia.Font(skia.Typeface(Defaults.FONT_NAME, skia.FontStyle.Normal()), Defaults.FONT_SIZE)
        textblob = skia.TextBlob.MakeFromString(sp.textGlyphs[0].text, font)
        twidth = font.measureText(sp.textGlyphs[0].text)
        
        m = font.getMetrics()
        theight = abs (m.fTop) - m.fBottom
        txt_x = node_x + (widthNode/2) - twidth/2
        txt_y = node_y + (heightNode/2) + theight/2
         
        paint = skia.Paint(
                Color=Defaults.ORANGE,
                Style=skia.Paint.kFill_Style)
        
        paintStroke = skia.Paint(
          AntiAlias=True,
          StrokeWidth=3,
          Style = skia.Paint.kStroke_Style,
          Color =  Defaults.DARK_ORANGE)
        
        # Adjust the node width to the size of text
        if twidth > sp.boundingBox.w:
           rect = skia.Rect(sp.boundingBox.x, sp.boundingBox.y,
                           sp.boundingBox.x + twidth,
                           sp.boundingBox.y + sp.boundingBox.h) 
           sp.boundingBox.w = twidth
           txt_x = node_x
           # Recompute reaction start and end points
           
        else:
           rect = skia.Rect(sp.boundingBox.x, sp.boundingBox.y,
                           sp.boundingBox.x + sp.boundingBox.w, 
                           sp.boundingBox.y + sp.boundingBox.h) 
            
        canvas.drawRoundRect(rect, 6, 6, paint)    
        canvas.drawRoundRect(rect, 6, 6, paintStroke);   
        
        paintText = skia.Paint(Color = Defaults.BLACK, StrokeWidth=2)
        
        canvas.drawTextBlob(textblob, txt_x, txt_y, paintText)
    
 
    
    