import FreeCAD as App
import Part
import Sketcher

fret_count = 22
scale_short = 635
scale_long = 711

def calc_fret_position(scale, index):
    return scale * (1 - 2 ** (-1 * index / 12))

# Index is the index of the next element to be drawn
# (0 if nothing has been drawn yet)
def construct_frets(sketch, frets, index):
    start_index = index
    
    for i in range(len(frets) - 1):
        index = start_index + i
        sketch.addGeometry(Part.LineSegment(App.Vector(0, 0, 0), App.Vector(0, -1, 0)), False)
        
        sketch.addConstraint(Sketcher.Constraint(
            "Distance",
            start_index, 1, index, 2,
            App.Units.Quantity("{} mm".format(frets[i + 1]))))
        sketch.addConstraint(Sketcher.Constraint("Vertical", index, 1, index, 2))
        
        if i == 0:
            continue
            
        # Make current segment start on previous segment end
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 1, index-1, 2))
    
    # Constrain the start of the first line segment    
    sketch.addConstraint(Sketcher.Constraint("Coincident", -1, 1, start_index, 1))
    
    return index + 1
    
def main():
    frets_short = []
    frets_long = []

    for i in range(fret_count + 1):
        frets_short.append(calc_fret_position(scale_short, i))
        frets_long.append(calc_fret_position(scale_long, i))

    doc = App.activeDocument()
    sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
    
    index = 0
    index = construct_frets(sketch, frets_short, index)
    index = construct_frets(sketch, frets_long, index)
    doc.recompute()
    
main()