import FreeCAD as App
import Part
import Sketcher

fret_count = 22
scale_short = 635
scale_long = 711
center_fret = 10 # fret that is straight i.e. the center of the fan
nut_spacing = 8 # center to center (mm)
bridge_spacing = 10.414 # center to center
string_count = 6

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
        
        if i == 0:
            continue
            
        # Make current segment start on previous segment end and be collinear
        sketch.addConstraint(Sketcher.Constraint("Tangent", index, 1, index-1, 2))
    
    return index + 1
    
def calc_width_nth_fret(nut_width, bridge_width, scale, fret_distance):
    # Take weighted average of nut and bridge spacing
    proportion = fret_distance / scale
    diff = bridge_width - nut_width
    return nut_width + (diff * proportion)

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

    # Calculate explicitly where the center fret should be
    nut_width = nut_spacing * (string_count - 1)
    bridge_width = bridge_spacing * (string_count - 1)
    center_fret_index_short = center_fret - 1
    center_fret_index_long = center_fret - 1 + fret_count
    center_fret_width = calc_width_nth_fret(nut_width, bridge_width, scale_short, frets_short[center_fret_index_short])
    center_fret_line = sketch.addGeometry(
        Part.LineSegment(App.Vector(-0.5 * center_fret_width, 0, 0), App.Vector(0.5 * center_fret_width, 0, 0)),
        False)
    sketch.addConstraint(Sketcher.Constraint('Block', center_fret_line))

    # Fix the center fret
    sketch.addConstraint(Sketcher.Constraint("Coincident", center_fret_line, 1, center_fret_index_long, 2))
    sketch.addConstraint(Sketcher.Constraint("Coincident", center_fret_line, 2, center_fret_index_short, 2))

    # Constrain the nut spacing
    sketch.addConstraint(Sketcher.Constraint(
        "Distance",
        0, 1, fret_count, 1,
        App.Units.Quantity("{} mm".format(nut_width))))

    # Constrain last fret spacing
    """
    last_fret_width = calc_width_nth_fret(nut_width, bridge_width, scale_short, frets_short[fret_count])
    sketch.addConstraint(Sketcher.Constraint(
        "Distance",
        fret_count - 1, 2, fret_count * 2 - 1, 2,
        App.Units.Quantity("{} mm".format(last_fret_width))))
    """


    doc.recompute()
    
main()