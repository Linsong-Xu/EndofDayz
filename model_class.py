"""
A GUI-based zombie survival game wherein the player has to reach
the hospital whilst evading zombies.
"""

# Replace these <strings> with your name, student number and email address.
__author__ = "<Your Name>, <Your Student Number>"
__email__ = "<Your Student Email>"

import tkinter as tk
from a2_solution import *
from constants import *
from typing import Tuple, Optional, Dict, List
from PIL import Image


class InitErorr(Exception):
    def __init__(self) -> None:
        super(InitErorr, self).__init__()

    def __str__(self):
        return f'Wrong parameter!!!(Please check cols | width, rows | height)'


class AbstractGrid(tk.Canvas):
    def __init__(self, master, rows: int, cols: int, width: int, height: int, **kwargs) -> None:
        if (width % cols != 0) or (height % rows != 0):
            raise InitErorr
        self._rows_y = rows
        self._cols_x = cols
        self._width = width
        self._height = height
        self._rec_width = width // cols
        self._rec_height = height // rows
        self._tiles: Dict[Position, str] = {}

    def get_bbox(self, position: Position) -> Tuple[int, int, int, int]:
        '''
        Give position(col_x, row_y), return the bounding box pixel position
        '''
        x_min = position.get_x() * self._rec_width
        y_min = position.get_y() * self._rec_height
        x_max = x_min + self._rec_width - 1
        y_max = y_min + self._rec_height - 1
        return (x_min, y_min, x_max, y_max)

    def pixel_to_position(self, pixel: Position) -> Position:
        '''
        Convert the pixel position(graphics unit) to (row, column) position
        pixel position (x, y) --> Position (col_x, row_y)
        '''
        row_y = pixel.get_y() // self._rec_height
        col_x = pixel.get_x() // self._rec_width
        return Position(col_x, row_y)

    def get_position_center(self, position: Position) -> Position:
        '''
        Given Position(col_x, row_y)  --> The center of pixel position(x, y)
        向左上角近似
        '''
        pixel_x = position.get_x() * self._rec_width + self._rec_width // 2
        pixel_y = position.get_y() * self._rec_height + self._rec_height // 2
        return Position(pixel_x, pixel_y)

    def annotate_position(self, position: Position, text: str) -> None:
        '''
        Annotate position(col_x, row_y)
        '''
        if self.in_bounds(position):
            self._tiles[position] = text

    def in_bounds(self, position: Position) -> bool:
        '''
        if position(col_x, row_y) in bounds(AbstractGrid.col_x, AbstractGrid.row_y)
        '''
        return (0 <= position.get_x() < self._cols_x
                and 0 <= position.get_y() < self._rows_y)


class BasicMap(AbstractGrid):
    def __init__(self, master, size: int, **kwargs) -> None:
        self._rows = size
        self._cols = size
        self._rec_width = CELL_SIZE
        self._rec_height = CELL_SIZE
        self._width = self._rec_width * size
        self._height = self._rec_height * size
        self._background = MAP_BACKGROUND_COLOUR
        if kwargs is not None:
            for key, value in kwargs.items():
                if key == 'background':
                    self._background = value

        self._basic_map_canvas = tk.Canvas(master, bg=self._background, width=self._width,
                                           height=self._height, bd=0, highlightthickness=0)
        self._basic_map_canvas.pack(side=tk.TOP)

    def draw_entity(self, position: Position, title_type: str) -> None:
        entity_bgcolor_dict = {ZOMBIE: ENTITY_COLOURS[ZOMBIE],
                               TRACKING_ZOMBIE: ENTITY_COLOURS[TRACKING_ZOMBIE],
                               CROSSBOW: ENTITY_COLOURS[CROSSBOW],
                               GARLIC: ENTITY_COLOURS[GARLIC],
                               PLAYER: ENTITY_COLOURS[PLAYER],
                               HOSPITAL: ENTITY_COLOURS[HOSPITAL]}

        entity_textcolor_dict = {ZOMBIE: 'black',
                                 TRACKING_ZOMBIE: 'black',
                                 CROSSBOW: 'black',
                                 GARLIC: 'black',
                                 PLAYER: 'white',
                                 HOSPITAL: 'white'}
        bbox = self.get_bbox(position)
        self._basic_map_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], outline='black',
                                                fill=entity_bgcolor_dict[title_type], width=1)
        center_piexl_position = self.get_position_center(position)
        self._basic_map_canvas.create_text(center_piexl_position.get_x(), center_piexl_position.get_y(),
                                           text=title_type,
                                           fill=entity_textcolor_dict[title_type])
        self._basic_map_canvas.pack(side=tk.TOP)


class InventoryView(AbstractGrid):
    def __init__(self, master, rows, **kwargs) -> None:
        '''
        The parameter rows should be set to the number of rows in the game map
        '''
        self._rows_y = rows
        self._cols_x = 2
        self._rec_height = CELL_SIZE
        self._rec_width = INVENTORY_WIDTH // self._cols_x
        self._width = INVENTORY_WIDTH
        self._height = self._rec_height * self._rows_y
        self._background = LIGHT_PURPLE

        self._inventory_view_canvas = tk.Canvas(master, bg=self._background, width=self._width,
                                                height=self._height, bd=0, highlightthickness=0)
        self._inventory_view_canvas.create_text(self._width // 2, self._rec_height // 2,
                                                text='Inventory', fill=DARK_PURPLE, font=('Purisa', 24),
                                                tags='inventory_label')
        self._inventory_view_canvas.pack(side=tk.RIGHT)

    def draw(self, inventory: Inventory) -> None:

        items = inventory.get_items()
        if len(items) == 0:
            return
        start_row = 1
        for item in items:
            item_position = Position(0, start_row)
            item_bbox = self.get_bbox(item_position)
            lifetime_position = Position(1, start_row)
            lifetime_bbox = self.get_bbox(lifetime_position)

            text_color = 'white' if item.is_active() else 'black'
            background_color = DARK_PURPLE if item.is_active() else LIGHT_PURPLE

            self._inventory_view_canvas.create_rectangle(item_bbox[0], item_bbox[1], item_bbox[2], item_bbox[3],
                                                         fill=background_color, outline=background_color, tags='pickup')
            item_center_piexl_position = self.get_position_center(item_position)
            self._inventory_view_canvas.create_text(item_center_piexl_position.get_x(),
                                                    item_center_piexl_position.get_y(),
                                                    text=item.__class__.__name__, fill=text_color, tags='pickup')

            self._inventory_view_canvas.create_rectangle(lifetime_bbox[0], lifetime_bbox[1], lifetime_bbox[2],
                                                         lifetime_bbox[3],
                                                         fill=background_color, outline=background_color, tags='pickup')
            lifetime_center_piexl_position = self.get_position_center(lifetime_position)
            self._inventory_view_canvas.create_text(lifetime_center_piexl_position.get_x(),
                                                    lifetime_center_piexl_position.get_y(),
                                                    text=item.get_lifetime(), fill=text_color, tags='pickup')
            start_row += 1
        self._inventory_view_canvas.pack(side=tk.TOP)

    def toggle_item_activation(self, pixel: Position, inventory: Inventory) -> None:
        '''
        pixel Position (x, y)
        '''
        position = self.pixel_to_position(pixel)
        row_y = position.get_y()
        if row_y > 0:
            inventory.get_items()[row_y - 1].toggle_active()


class ImageMap(AbstractGrid):
    def __init__(self, master, size: int, **kwargs) -> None:
        self._rows = size
        self._cols = size
        self._rec_width = CELL_SIZE
        self._rec_height = CELL_SIZE
        self._width = self._rec_width * size
        self._height = self._rec_height * size
        self._images: Dict[Position, tk.PhotoImage] = {}

        self._basic_map_canvas = tk.Canvas(master, width=self._width, height=self._height, bd=0, highlightthickness=0)

        self._back_ground = tk.PhotoImage(file=IMAGES[BACK_GROUND])
        for row in range(self._rows):
            for col in range(self._cols):
                bbox = self.get_bbox(Position(col, row))
                self._basic_map_canvas.create_image(bbox[0], bbox[1], image=self._back_ground, anchor='nw', tags='bg')
        self._basic_map_canvas.pack(side=tk.TOP)

    def draw_entity(self, position: Position, title_type: str) -> None:
        entity_image_dict = {ZOMBIE: IMAGES[ZOMBIE],
                             TRACKING_ZOMBIE: IMAGES[TRACKING_ZOMBIE],
                             CROSSBOW: IMAGES[CROSSBOW],
                             GARLIC: IMAGES[GARLIC],
                             PLAYER: IMAGES[PLAYER],
                             HOSPITAL: IMAGES[HOSPITAL],
                             TIME_MACHINE: 'images/time_machine.png'}

        self._images[position] = tk.PhotoImage(file=entity_image_dict[title_type])
        bbox = self.get_bbox(position)
        self._basic_map_canvas.create_image(bbox[0], bbox[1], image=self._images[position], anchor='nw', tags='entity')
        self._basic_map_canvas.pack(side=tk.TOP)


class StatusBar(tk.Frame):

    def __init__(self, master, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._button_width = self._width - 2 * CELL_SIZE

        '''
            Init chaser frame
        '''
        self._chaser_frame = tk.Frame(master, bd=0, bg='white', height=CELL_SIZE, width=CELL_SIZE)
        self._chaser_frame.pack(side=tk.LEFT)
        self._chaser_canvas = tk.Canvas(self._chaser_frame, width=CELL_SIZE, height=CELL_SIZE, bd=0,
                                        highlightthickness=0)
        self._chaser_image = tk.PhotoImage(file='images/chaser.png')
        self._chaser_canvas.create_image(0, 0, image=self._chaser_image, anchor='nw')
        self._chaser_canvas.pack(side=tk.TOP)

        '''
            Init timer frame
        '''
        self._timer_frame = tk.Frame(master, bd=0, height=CELL_SIZE,
                                     width=self._button_width // 3)
        self._timer_frame.pack(side=tk.LEFT)
        self._timer_label_frame = tk.Frame(self._timer_frame, bd=0, height=CELL_SIZE // 2,
                                           width=self._button_width // 3)
        self._timer_label_frame.pack(side=tk.TOP)
        self._timer_label_canvas = tk.Canvas(self._timer_label_frame, height=CELL_SIZE // 2,
                                             width=self._button_width // 3, bd=0, highlightthickness=0)
        self._timer_label_canvas.create_text(self._button_width // 6, CELL_SIZE // 4, text='Timer')
        self._timer_label_canvas.pack(side=tk.TOP)

        self._timer_num_frame = tk.Frame(self._timer_frame, bd=0, height=CELL_SIZE // 2,
                                         width=self._button_width // 3)
        self._timer_num_frame.pack(side=tk.TOP)
        self._timer_num_canvas = tk.Canvas(self._timer_num_frame, height=CELL_SIZE // 2,
                                           width=self._button_width // 3, bd=0, highlightthickness=0)
        self._timer_num_canvas.create_text(self._button_width // 6, CELL_SIZE // 4, text='0 mins 0 seconds')
        self._timer_num_canvas.pack(side=tk.TOP)

        '''
            Init moves frame
        '''
        self._moves_frame = tk.Frame(master, bd=0, height=CELL_SIZE,
                                     width=self._button_width // 3)
        self._moves_frame.pack(side=tk.LEFT)
        self._moves_label_frame = tk.Frame(self._moves_frame, bd=0, height=CELL_SIZE // 2,
                                           width=self._button_width // 3)
        self._moves_label_frame.pack(side=tk.TOP)
        self._moves_label_canvas = tk.Canvas(self._moves_label_frame, height=CELL_SIZE // 2,
                                             width=self._button_width // 3, bd=0, highlightthickness=0)
        self._moves_label_canvas.create_text(self._button_width // 6, CELL_SIZE // 4, text='Moves made')
        self._moves_label_canvas.pack(side=tk.TOP)

        self._moves_num_frame = tk.Frame(self._moves_frame, bd=0, height=CELL_SIZE // 2,
                                         width=self._button_width // 3)
        self._moves_num_frame.pack(side=tk.TOP)
        self._moves_num_canvas = tk.Canvas(self._moves_num_frame, height=CELL_SIZE // 2,
                                           width=self._button_width // 3, bd=0, highlightthickness=0)
        self._moves_num_canvas.create_text(self._button_width // 6, CELL_SIZE // 4, text='0 moves')
        self._moves_num_canvas.pack(side=tk.TOP)

        '''
            Init button frame
        '''
        self._button_frame = tk.Frame(master, bd=0, height=CELL_SIZE,
                                      width=self._button_width - 2 * (self._button_width // 3))
        self._button_frame.pack(side=tk.LEFT)
        self._button_frame.pack_propagate(False)
        self._restart_button_frame = tk.Frame(self._button_frame, bd=0, height=CELL_SIZE // 2,
                                              width=self._button_width - 2 * (self._button_width // 3))
        self._restart_button_frame.pack(side=tk.TOP)
        self._restart_button_frame.pack_propagate(False)
        self._restart_button = tk.Button(self._restart_button_frame, text="Restart Game")
        self._restart_button.pack(side=tk.TOP)
        self._quit_button_frame = tk.Frame(self._button_frame, bd=0, height=CELL_SIZE // 2,
                                           width=self._button_width - 2 * (self._button_width // 3))
        self._quit_button_frame.pack(side=tk.TOP)
        self._quit_button_frame.pack_propagate(False)
        self._quit_button = tk.Button(self._quit_button_frame, text="Quit Game")
        self._quit_button.pack(side=tk.TOP)

        '''
            Init chasee frame
        '''
        self._chasee_frame = tk.Frame(master, bd=0, bg='white', height=CELL_SIZE, width=CELL_SIZE)
        self._chasee_frame.pack(side=tk.LEFT)
        self._chasee_canvas = tk.Canvas(self._chasee_frame, width=CELL_SIZE, height=CELL_SIZE, bd=0,
                                        highlightthickness=0)
        self._chasee_image = tk.PhotoImage(file='images/chasee.png')
        self._chasee_canvas.create_image(0, 0, image=self._chasee_image, anchor='nw')
        self._chasee_canvas.pack(side=tk.TOP)

    def change_timer(self, time: int) -> None:
        self._timer_num_canvas.delete("all")
        minutes = str(time // 60)
        seconds = str(time % 60)
        self._timer_num_canvas.create_text(self._button_width // 6, CELL_SIZE // 4,
                                           text=minutes + ' mins ' + seconds + ' seconds')

    def change_move(self, moves: int) -> None:
        self._moves_num_canvas.delete("all")
        self._moves_num_canvas.create_text(self._button_width // 6, CELL_SIZE // 4, text=str(moves) + ' moves')

    def get_quit_button(self) -> tk.Button:
        return self._quit_button

    def get_restart_button(self) -> tk.Button:
        return self._restart_button
