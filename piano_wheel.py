import cairo
import os
from math import pi as PI, sin, cos

# globals
SVG_WIDTH, SVG_HEIGHT = [650, 650]

RGB_BLACK = [0, 0, 0]
RGB_DARK_GRAY = [0.5, 0.5, 0.5]
RGB_WHITE = [1, 1, 1]
RGB_LIGHT_GRAY = [0.9, 0.9, 0.9]

R = 300
R_KEY_DEGREE = 0.975
R_NOTE_NAMES = 0.85
R_KEY_MODE = 0.725
SECTOR_ANGLE = PI/6

NOTE_NAME_DIVIDER_SIZE = 0.12
KEY_DEGREE_RING_SIZE = 0.06
KEY_MODE_RING_SIZE = 0.06

cr = None # the cairo context; it's easier to debug with overlay when this is global


# Draws text as an arc along the perimeter of a circle of radius r. Circle center is current
# location of the cairo "paintbrush" on the canvas
#
# cr - cairo context used to draw text
# text - the text to draw in an arc
# font_size - desired font size for text
# r - the radius of a circle on which to draw the text
# theta_center - angle on which to center the text
# d_theta - the desired angular distance between characters in the text (letter spacing)
def arc_text(cr, text, font_size, r, theta_center, d_theta):
    cr.set_font_size(font_size)
    num_chars = len(text)
    
    if num_chars % 2 == 1:
        theta = theta_center - (d_theta*num_chars/2) + d_theta/2
    else:
        theta = theta_center - (d_theta*num_chars/2)

    for char in text:
        (x, y, w, h, dx, dy) = cr.text_extents(char)
        cr.move_to(
            # this -0.025*r adjustment to the width is a quick fix for an issue I don't care enough to solve at the moment...
            r*cos(theta) + (w/2 - 0.02*r) * (1 if cos(theta) > 0 else -1),
            r*sin(theta) + h/2 * (1 if sin(theta) <= 0 else -1),
        )
        cr.rotate(theta + PI/2)

        cr.show_text(char)

        cr.rotate(-(theta + PI/2))
        theta += d_theta


def draw_note_wheel(ink_saver=False):
    rgb_black_key = RGB_DARK_GRAY if ink_saver else RGB_BLACK

    notes = {
        '1' : {'names': ['B#', 'C'],  'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
        '2' : {'names': ['C#', 'Db'], 'background_rgb': rgb_black_key, 'text_rgb': RGB_WHITE},
        '3' : {'names': ['D'],        'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
        '4' : {'names': ['D#', 'Eb'], 'background_rgb': rgb_black_key, 'text_rgb': RGB_WHITE},
        '5' : {'names': ['E', 'Fb'],  'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
        '6' : {'names': ['E#', 'F'],  'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
        '7' : {'names': ['F#', 'Gb'], 'background_rgb': rgb_black_key, 'text_rgb': RGB_WHITE},
        '8' : {'names': ['G'],        'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
        '9' : {'names': ['G#', 'Ab'], 'background_rgb': rgb_black_key, 'text_rgb': RGB_WHITE},
        '10': {'names': ['A'],        'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
        '11': {'names': ['A#', 'Bb'], 'background_rgb': rgb_black_key, 'text_rgb': RGB_WHITE},
        '12': {'names': ['B', 'Cb'],  'background_rgb': RGB_WHITE,     'text_rgb': RGB_BLACK},
    }

    sector_start = 3*PI/2
    
    font_size = 20

    # note wheel
    ims = cairo.SVGSurface("printouts/note_wheel_ink_saver.svg" if ink_saver else "printouts/note_wheel.svg", SVG_WIDTH, SVG_HEIGHT)
    cr = cairo.Context(ims)
    
    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)    
    
    cr.set_line_width(2)
    cr.set_source_rgb(*RGB_BLACK)

    cr.translate(SVG_WIDTH/2, SVG_HEIGHT/2)
    cr.arc(0, 0, R, 0, 2*PI)
    cr.stroke_preserve()

    for note, data in notes.items():
        sector_mid = (sector_start + SECTOR_ANGLE/2)

        # colored circle sector
        cr.move_to(0, 0)
        cr.arc(0, 0, R, sector_start, sector_start + SECTOR_ANGLE)
        cr.close_path()
        cr.set_source_rgb(*data['background_rgb'])
        cr.fill()

        cr.set_font_size(font_size)
        cr.set_source_rgb(*data['text_rgb'])
        
        # note has 2 names
        if len(data['names']) == 2:
            # note name divider
            cr.move_to(
                R*cos(sector_mid)*(R_NOTE_NAMES-NOTE_NAME_DIVIDER_SIZE/2),
                R*sin(sector_mid)*(R_NOTE_NAMES-NOTE_NAME_DIVIDER_SIZE/2)
            )
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.line_to(
                R*cos(sector_mid)*(R_NOTE_NAMES+NOTE_NAME_DIVIDER_SIZE/2),
                R*sin(sector_mid)*(R_NOTE_NAMES+NOTE_NAME_DIVIDER_SIZE/2)
            )
            cr.stroke()
            
            # sharp relative name
            (x, y, w, h, dx, dy) = cr.text_extents(data['names'][0])
            theta = sector_mid - SECTOR_ANGLE/5
            cr.move_to(
                R_NOTE_NAMES*R*cos(theta) - w/2,
                R_NOTE_NAMES*R*sin(theta) + h/2)
            cr.show_text(data['names'][0])

            # flat relative name
            (x, y, w, h, dx, dy) = cr.text_extents(data['names'][1])
            theta = sector_mid + SECTOR_ANGLE/5
            cr.move_to(
                R_NOTE_NAMES*R*cos(theta) - w/2,
                R_NOTE_NAMES*R*sin(theta) + h/2)
            cr.show_text(data['names'][1])
        
        # note has 1 name
        else:
            (x, y, w, h, dx, dy) = cr.text_extents(data['names'][0])
            theta = sector_mid
            cr.move_to(
                R_NOTE_NAMES*R*cos(theta) - w/2,
                R_NOTE_NAMES*R*sin(theta) + h/2)
            cr.show_text(data['names'][0])

        sector_start += SECTOR_ANGLE

    # draw lines separating B/C, E/F
    cr.move_to(0, 0)
    cr.set_line_width(1)
    cr.set_source_rgb(*RGB_BLACK)
    cr.line_to(R*cos(sector_start), R*sin(sector_start))
    cr.move_to(0, 0)
    cr.line_to(R*cos(sector_start + 5*SECTOR_ANGLE), R*sin(sector_start + 5*SECTOR_ANGLE))
    cr.stroke()


def draw_window_wheel(overlay=False):
    sectors = {
        '1' : {'degree': 'I / iii',  'outer_window': True,  'mode': 'Ionian'},
        '2' : {'degree': None,       'outer_window': False, 'mode': None},
        '3' : {'degree': 'II / iv',  'outer_window': True,  'mode': 'Dorian'},
        '4' : {'degree': None,       'outer_window': False, 'mode': None},
        '5' : {'degree': 'III / v',  'outer_window': True,  'mode': 'Phrygian'},
        '6' : {'degree': 'IV / vi',  'outer_window': True,  'mode': 'Lydian'},
        '7' : {'degree': None,       'outer_window': False, 'mode': None},
        '8' : {'degree': 'V / vii',  'outer_window': True,  'mode': 'Mixolydian'},
        '9' : {'degree': None,       'outer_window': False, 'mode': None},
        '10': {'degree': 'VI / i',   'outer_window': True,  'mode': 'Aeolian'},
        '11': {'degree': None,       'outer_window': False, 'mode': None},
        '12': {'degree': 'VII / ii', 'outer_window': True,  'mode': 'Locrian'},
    }

    # window wheel  
    if not overlay:
        ims = cairo.SVGSurface("printouts/window_wheel.svg", SVG_WIDTH, SVG_HEIGHT)
        cr = cairo.Context(ims) 
        cr.translate(SVG_WIDTH/2, SVG_HEIGHT/2)

    font_size = 12
    sector_start = 3*PI/2
        
    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(font_size)

    # outer ring
    cr.set_line_width(2)
    
    cr.arc(0, 0, R, 0, 2*PI)
    cr.set_source_rgb(*RGB_BLACK)
    cr.stroke_preserve()
    
    if not overlay:
        cr.set_source_rgb(*RGB_LIGHT_GRAY)
        cr.fill()

    cr.set_source_rgb(*RGB_BLACK)
    cr.set_line_width(1)
    
    # degree inner ring
    r = R * (R_KEY_DEGREE - KEY_DEGREE_RING_SIZE/2)
    cr.arc(0, 0, r, 0, 2*PI)
    cr.stroke_preserve()

    # mode outer ring
    r = R * (R_KEY_MODE + KEY_MODE_RING_SIZE/2)
    cr.arc(0, 0, r, 0, 2*PI)
    cr.stroke_preserve()

    # mode inner ring
    r = R * (R_KEY_MODE - KEY_MODE_RING_SIZE/2)
    cr.arc(0, 0, r, 0, 2*PI)
    cr.stroke_preserve()

    sector_start = 3*PI/2
    outer_window_border_width = SECTOR_ANGLE/12

    for sector, data in sectors.items():
        # circle sectors
        cr.move_to(0, 0)
        theta = sector_start + SECTOR_ANGLE
        cr.line_to(R*cos(theta), R*sin(theta))
        cr.stroke()

        # degree
        if data['degree']:
            arc_text(cr, data['degree'], font_size, R*R_KEY_DEGREE, sector_start + SECTOR_ANGLE/2, SECTOR_ANGLE/18)

        # mode
        if data['mode']:
            arc_text(cr, data['mode'], font_size, R*R_KEY_MODE, sector_start + SECTOR_ANGLE/2, SECTOR_ANGLE/14)

        # outer note window
        if data['outer_window']:
            r_line_start = R * (R_KEY_MODE + KEY_MODE_RING_SIZE/2)
            r_line_end = R * (R_KEY_DEGREE - KEY_DEGREE_RING_SIZE/2)
            
            theta = sector_start + outer_window_border_width
            cr.move_to(r_line_start*cos(theta), r_line_start*sin(theta))
            cr.line_to(r_line_end*cos(theta), r_line_end*sin(theta))
            cr.stroke()

            theta = sector_start + SECTOR_ANGLE - outer_window_border_width
            cr.move_to(r_line_start*cos(theta), r_line_start*sin(theta))
            cr.line_to(r_line_end*cos(theta), r_line_end*sin(theta))
            cr.stroke()

            arc_text(cr, 'CUT', font_size*1.5, R * (R_KEY_MODE + (R_KEY_DEGREE - R_KEY_MODE)/2), sector_start + SECTOR_ANGLE/2, SECTOR_ANGLE/10)
            
        sector_start += SECTOR_ANGLE


def main():
    os.mkdir('./printouts')
    draw_note_wheel()
    draw_note_wheel(ink_saver=True)
    draw_window_wheel()


if __name__ == "__main__":    
    main()