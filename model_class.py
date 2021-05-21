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


class InitError(Exception):
    """
    The InitError class is inherits Exception,
    when the grid width can't divisible column or height can't divisible row
    raise this IniError Exception
    """

    def __init__(self) -> None:
        super(InitError, self).__init__()

    def __str__(self) -> str:
        return f'Wrong parameter!!!(Please check cols | width, rows | height)'


class AbstractGrid(tk.Canvas):
    """
    The AbstractGrid class is used to represent the 2D grid of entities.

    The grid can vary in size but it is always a square.
    Each (x, y) position in the grid can only contain one entity at a time.
    """

    def __init__(self, master, rows: int, cols: int, width: int, height: int, **kwargs) -> None:
        """
        A abstractgrid is constructed with rows, cols, width and height that dictate the length and width
        of the grid.

        Initially a grid does not contain any entities.

        Parameters:
            master: The parent of tk.Canvas, default is None.
            rows: The rows of the grid.
            cols: The columns of the grid.
            width: The width of the grid.
            height: The height of the grid.
        """
        if (width % cols != 0) or (height % rows != 0):
            raise InitError
        self._rows_y = rows
        self._cols_x = cols
        self._width = width
        self._height = height
        self._rec_width = width // cols
        self._rec_height = height // rows
        self._tiles: Dict[Position, str] = {}

    def get_bbox(self, position: Position) -> Tuple[int, int, int, int]:
        """
        Get the bounding box pixel position (pixel_x, pixel_y)

        Parameters:
            position: An (col_x, row_y) position represent the col and row
        """
        x_min = position.get_x() * self._rec_width
        y_min = position.get_y() * self._rec_height
        x_max = x_min + self._rec_width - 1
        y_max = y_min + self._rec_height - 1
        return (x_min, y_min, x_max, y_max)

    def pixel_to_position(self, pixel: Position) -> Position:
        """
        Convert the pixel position(graphics unit) to (row, column) position

        Parameters:
            pixel: An (pixel_x, pixel_y) position (graphics unit)
        """
        row_y = pixel.get_y() // self._rec_height
        col_x = pixel.get_x() // self._rec_width
        return Position(col_x, row_y)

    def get_position_center(self, position: Position) -> Position:
        """
        Get the pixel position(pixel_x, pixel_y) which is the center of the given (col_x, row_y) position

        Parameters:
            position: An (col_x, row_y) position represent the col and row.
        """
        pixel_x = position.get_x() * self._rec_width + self._rec_width // 2
        pixel_y = position.get_y() * self._rec_height + self._rec_height // 2
        return Position(pixel_x, pixel_y)

    def annotate_position(self, position: Position, text: str) -> None:
        """
        Annotates the center of the cell at the given (row, column) position with the provided text.

        Parameters:
            position: An (col_x, row_y) position represent the col and row.
            text: The provided text.
        """
        if self.in_bounds(position):
            self._tiles[position] = text

    def in_bounds(self, position: Position) -> bool:
        """
        Return True if the given position is within the bounds of the grid.

        For a position to be within the bounds of the grid, both the x and y
        coordinates have to be greater than or equal to zero but less than
        the size of the grid.

        Parameters:
            position: An (col_x, row_y) position that we want to check is
                      within the bounds of the grid.
        """
        return (0 <= position.get_x() < self._cols_x
                and 0 <= position.get_y() < self._rows_y)


class BasicMap(AbstractGrid):
    """
    BasicMap is a view class which inherits from AbstractGrid.
    Entities are drawn on the map using coloured rectangles at different (col_x, row_y) positions.
    """

    def __init__(self, master, size: int, **kwargs) -> None:
        """
        A basicmap is constructed with size that dictates the length and width
        of the map.

        Parameters:
            master: The parent of BasicMap
            size: The rows and columns of BasicMap
        """
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
        """
        Draws the entity with tile type at the given position using a coloured rectangle
        with superimposed text identifying the entity.

        Parameters:
            position: An (col_x, row_y) position in the map to draw the entity.
            title_type: The title type of the Entity.
        """
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
    """
    InventoryView is a view class which inherits from AbstractGrid and
    displays the items the player has in their inventory.
    This class also provides a mechanism through which the user can
    activate an item held in the player’s inventory.
    """
    def __init__(self, master, rows, **kwargs) -> None:
        """
        The parameter rows should be set to the number of rows in the game map.
        The column is setted 2 with pickup text and pickup lifetime

        Parameters:
            master: The parent of the InventoryView.
            rows: The rows of the InventoryView.
        """
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
        """
        Draws the inventory label and current items with their remaining lifetimes.

        Parameters:
            inventory: The inventory that HoldingPlayer has.
        """
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

            """
            Create inventory item display text at Position(col_x=0, row_y)
            """
            self._inventory_view_canvas.create_rectangle(item_bbox[0], item_bbox[1], item_bbox[2], item_bbox[3],
                                                         fill=background_color, outline=background_color, tags='pickup')
            item_center_piexl_position = self.get_position_center(item_position)
            self._inventory_view_canvas.create_text(item_center_piexl_position.get_x(),
                                                    item_center_piexl_position.get_y(),
                                                    text=item.__class__.__name__, fill=text_color, tags='pickup')
            """
            Create inventory item lifetime at Position(col_x=1, row_y)
            """
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
        """
        Activates or deactivates the item (if one exists) in the row containing the pixel.

        Parameters:
            pixel: An (pixel_x, pixel_y) position which you want to toggle item activation.
            inventory: The inventory that HoldingPlayer has.
        """
        position = self.pixel_to_position(pixel)
        row_y = position.get_y()
        if row_y > 0:
            inventory.get_items()[row_y - 1].toggle_active()


class ImageMap(AbstractGrid):
    """

    """
    def __init__(self, master, size: int, **kwargs) -> None:
        """

        """
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
        """

        """
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
    """
    The StatusBar that inherits from tk.Frame which include:
    • The chaser and chasee images (see images folder).
    • A game timer displaying the number of minutes and seconds the user has been playing the current game.
    • A moves counter, displaying how many moves the player has made in the current game.
    • A ‘Quit Game’ button, which ends the program.
    • A ‘Restart Game’ button, which allows the user to start the game again.
      This must reset the information on the status bar, as well as setting the map
      back to how it appeared at the start of the game. Clicking the ‘Restart Game’
      button after game play is finished should start a new game.

      *************************************************************
      * ************** ************* ************* ************** *
      * *chaser frame* *timer frame* *moves frame* *button frame* *
      * *            * *           * *           * *            * *
      * ************** ************* ************* ************** *
      *************************************************************
    """
    def __init__(self, master, width: int, height: int) -> None:
        """
        A StatusBar is constructed with width and height that dictates the length and width of the statusbar.

        Parameters:
            master: The parent of StatusBar
            width: The width of StatusBar
            height: The height of StatusBar
        """
        self._width = width
        self._height = height
        self._button_width = self._width - 2 * CELL_SIZE

        """
        Init chaser frame
        """
        self._chaser_frame = tk.Frame(master, bd=0, bg='white', height=CELL_SIZE, width=CELL_SIZE)
        self._chaser_frame.pack(side=tk.LEFT)
        self._chaser_canvas = tk.Canvas(self._chaser_frame, width=CELL_SIZE, height=CELL_SIZE, bd=0,
                                        highlightthickness=0)
        self._chaser_image = tk.PhotoImage(file='images/chaser.png')
        self._chaser_canvas.create_image(0, 0, image=self._chaser_image, anchor='nw')
        self._chaser_canvas.pack(side=tk.TOP)

        """
        Init timer frame
        """
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

        """
        Init moves frame
        """
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

        """
        Init button frame
        """
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

        """
        Init chasee frame
        """
        self._chasee_frame = tk.Frame(master, bd=0, bg='white', height=CELL_SIZE, width=CELL_SIZE)
        self._chasee_frame.pack(side=tk.LEFT)
        self._chasee_canvas = tk.Canvas(self._chasee_frame, width=CELL_SIZE, height=CELL_SIZE, bd=0,
                                        highlightthickness=0)
        self._chasee_image = tk.PhotoImage(file='images/chasee.png')
        self._chasee_canvas.create_image(0, 0, image=self._chasee_image, anchor='nw')
        self._chasee_canvas.pack(side=tk.TOP)

    def change_timer(self, time: int) -> None:
        """
        Change the timer number of StatusBar.

        Parameters:
            time: The timer number now.
        """
        self._timer_num_canvas.delete("all")
        minutes = str(time // 60)
        seconds = str(time % 60)
        self._timer_num_canvas.create_text(self._button_width // 6, CELL_SIZE // 4,
                                           text=minutes + ' mins ' + seconds + ' seconds')

    def change_move(self, moves: int) -> None:
        """
        Change the moves made number of StatusBar.

        Parameters:
            moves: The moves made now.
        """
        self._moves_num_canvas.delete("all")
        self._moves_num_canvas.create_text(self._button_width // 6, CELL_SIZE // 4, text=str(moves) + ' moves')

    def get_quit_button(self) -> tk.Button:
        """
        Return the quit button
        """
        return self._quit_button

    def get_restart_button(self) -> tk.Button:
        """
        Return the restart button.
        """
        return self._restart_button
