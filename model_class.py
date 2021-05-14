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


class InitErorr(Exception):
    def __init__(self):
        super(InitErorr, self).__init__()

    def __str__(self):
        return f'Wrong parameter!!!(Please check cols | width, rows | height)'


class AbstractGrid(tk.Canvas):
    def __init__(self, master, rows: int, cols: int, width: int, height: int, **kwargs):
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
    def __init__(self, master, size: int, **kwargs):
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
        entity_bgcolor_dict = {'Z': '#B8D58E', 'T': '#B8D58E', 'C': '#E5E1EF', 'G': '#E5E1EF', 'P': '#371D33',
                               'H': '#371D33'}
        entity_textcolor_dict = {'Z': 'black', 'T': 'black', 'C': 'black', 'G': 'black', 'P': 'white',
                                 'H': 'white'}
        bbox = self.get_bbox(position)
        self._basic_map_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], outline='black',
                                                fill=entity_bgcolor_dict[title_type], width=1)
        center_piexl_position = self.get_position_center(position)
        self._basic_map_canvas.create_text(center_piexl_position.get_x(), center_piexl_position.get_y(),
                                           text=title_type,
                                           fill=entity_textcolor_dict[title_type])
        self._basic_map_canvas.pack(side=tk.TOP)


class InventoryView(AbstractGrid):
    def __init__(self, master, rows, **kwargs):
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
