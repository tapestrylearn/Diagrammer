import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer
from PIL import Image, ImageDraw
import json



# MONKEY PATCHING ROUNDED RECTANGLE
def rounded_rectangle(self: ImageDraw, xy, corner_radius, outline = None):
    upper_left_point = xy[0]
    upper_right_point = (xy[1][0], xy[0][1])
    bottom_left_point = (xy[0][0], xy[1][1])
    bottom_right_point = xy[1]

    self.line(
        [
            (upper_left_point[0] + corner_radius, upper_left_point[1]),
            (upper_right_point[0] - corner_radius, upper_right_point[1])
        ],
        fill = outline
    )

    self.line(
        [
            (upper_right_point[0], upper_right_point[1] + corner_radius),
            (bottom_right_point[0], bottom_right_point[1] - corner_radius)
        ],
        fill = outline
    )

    self.line(
        [
            (bottom_left_point[0] + corner_radius, bottom_left_point[1]),
            (bottom_right_point[0] - corner_radius, bottom_right_point[1])
        ],
        fill = outline
    )

    self.line(
        [
            (upper_left_point[0], upper_left_point[1] + corner_radius),
            (bottom_left_point[0], bottom_left_point[1] - corner_radius)
        ],
        fill = outline
    )

    self.arc([upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
        180,
        270,
        fill = outline
    )

    self.arc([(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
        0,
        90,
        fill = outline
    )

    self.arc([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2), (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
        90,
        180,
        fill = outline
    )

    self.arc([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]), (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
        270,
        360,
        fill = outline
    )


ImageDraw.ImageDraw.rounded_rectangle = rounded_rectangle
# MONKEY PATCHING OVER



TAPESTRY_BLUE = (23, 25, 38)
TAPESTRY_GOLD = (175, 119, 13)

def generate_single_png(diagram_data: dict, filename: str):
    max_x = max(shape['x'] + shape['width'] / 2 for shape in diagram_data if 'shape' in shape)
    max_y = max(shape['y'] + shape['height'] / 2 for shape in diagram_data if 'shape' in shape)
    image1 = Image.new('RGB', (int(max_x) + 50, int(max_y) + 50), TAPESTRY_BLUE)
    draw = ImageDraw.Draw(image1)

    for shape in diagram_data:
        if 'shape' not in shape:
            draw.line(((shape['tail_x'], shape['tail_y']), (shape['head_x'], shape['head_y'])), fill = TAPESTRY_GOLD)
        else:
            xy = (
                (shape['x'] - shape['width'] / 2, shape['y'] - shape['height'] / 2),
                (shape['x'] + shape['width'] / 2, shape['y'] + shape['height'] / 2)
            )

            if shape['shape'] == 'square':
                draw.rectangle(xy, outline = TAPESTRY_GOLD)
            elif shape['shape'] == 'circle':
                draw.ellipse(xy, outline = TAPESTRY_GOLD)
            elif shape['shape'] == 'rounded_rect':
                draw.rounded_rectangle(xy, shape['corner_radius'], outline = TAPESTRY_GOLD)

    filename = f'{filename}.png'
    image1.save(filename)

def nsgaii_main():
    diagram_data = py_diagrammer.generate_diagrams_for_code('x = [1, 2, 3]\ny = x\nz = "abc"', [2])
    generate_single_png(diagram_data[0]['scenes']['locals'], 'hi')

if __name__ == '__main__':
    nsgaii_main()
