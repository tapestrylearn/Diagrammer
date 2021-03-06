from PIL import Image, ImageDraw
import json
import os
import shutil
import utils
utils.setup_pythonpath_for_tests()

from diagrammer import python as py_diagrammer


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
BASE_DIR = f'{os.path.expanduser("~")}/Desktop/local_visualizer_output'

def remove_base_dir() -> None:
    if os.path.isdir(BASE_DIR):
        shutil.rmtree(BASE_DIR)

def generate_single_png(diagram_data: dict, dir_relative_path: str, filename: str, console_output = ''):
    max_x = max(shape['x'] + shape['width'] / 2 for shape in diagram_data if 'shape' in shape)
    max_y = max(shape['y'] + shape['height'] / 2 for shape in diagram_data if 'shape' in shape)
    image1 = Image.new('RGB', (int(max_x) + 50, int(max_y) + 50), TAPESTRY_BLUE)
    draw = ImageDraw.Draw(image1)

    # draw shapes
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

            content = shape['content']
            if content['text'] != '':
                draw.text((xy[0][0] + 20, content['y']), content['text'], fill = TAPESTRY_GOLD)

    # print console output
    draw.text((0, 0), console_output, fill = TAPESTRY_GOLD)

    # save file
    dir_full_path = f'{BASE_DIR}/{dir_relative_path}'

    if not os.path.exists(dir_full_path):
        os.makedirs(dir_full_path)

    full_path = f'{dir_full_path}/{filename}.png'
    image1.save(full_path)


CODE = '''
a = 5
aa = 7.5
aaa = True
aaaa = None
b = 'hello world'
c = [6, ['hello', 2]]
d = [1, 2, 'yello']
'''

if __name__ == '__main__':
    full_diagram_data = py_diagrammer.generate_diagrams_for_code(CODE, [], primitive_era = True)

    for flag_num, flag_data in enumerate(full_diagram_data):
        for scope, diagram_data in flag_data['scenes'].items():
            generate_single_png(diagram_data['contents'], str(flag_num), scope, f'{flag_data["output"]}\n{flag_data["error"]}')
