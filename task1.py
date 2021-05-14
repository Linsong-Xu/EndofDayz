# -*- coding: utf-8 -*-
# @Time    : 2021/5/7 22:19
# @Author  : xls56i

from model_class import BasicMap, InventoryView
from a2_solution import Position, Game, Inventory, Garlic, Crossbow, HoldingPlayer, first_in_direction, advanced_game
import tkinter as tk
from tkinter import messagebox
from constants import *


class BasicGraphicalInterface:
    def __init__(self, root, size: int):
        '''
        Init the window
        four frame
                                |------------------------------------------------------|
                                |                  _title_label_frame                  |
                                |______________________________________________________|

                                |______________________________________________________|
                                |                _map_innventory_frame                 |
                                |  |------------------------|  |---------------------| |
                                |  |                        |  |                     | |
                                |  |       _map_frame       |  |  _inventory_frame   | |
                                |  |                        |  |                     | |
                                |  |                        |  |                     | |
                                |  |------------------------|  |---------------------| |
                                |______________________________________________________|

        '''
        self._root = root
        self._size = size
        self._window_width = size * CELL_SIZE + INVENTORY_WIDTH + 12
        self._window_height = (size + 1) * CELL_SIZE + 12
        self._screen_width = self._root.winfo_screenwidth()
        self._screen_height = self._root.winfo_screenheight()
        self._root.geometry(str(self._window_width) + 'x' + str(self._window_height) + '+' + str(
            (self._screen_width - self._window_width) // 2) + '+' + str(
            (self._screen_height - self._window_height) // 2))
        self._root.minsize(self._window_width, self._window_height)
        self._root.maxsize(self._window_width, self._window_height)

        '''
        Init the title label
        '''
        self._title_label_frame = tk.Frame(self._root, bd=2)
        self._title_label_frame.pack(side=tk.TOP)
        self._title_label_background_color = DARK_PURPLE
        self._title_label_height = CELL_SIZE

        self._title_label_canvas = tk.Canvas(self._title_label_frame, bg=self._title_label_background_color,
                                             height=self._title_label_height, width=self._window_width - 8, bd=0,
                                             highlightthickness=0)
        self._title_label_canvas.create_text(self._window_width // 2, self._title_label_height // 2, text='EndOfDayz',
                                             fill='white', font=('Purisa', 24))
        self._title_label_canvas.pack(side=tk.TOP)

        '''
        Init map and inventory frame
        '''
        self._map_innventory_frame = tk.Frame(self._root, bd=2)
        self._map_innventory_frame.pack(side=tk.TOP)
        self._map_frame = tk.Frame(self._map_innventory_frame, bd=2)
        self._map_frame.pack(side=tk.LEFT)
        self._inventory_frame = tk.Frame(self._map_innventory_frame, bd=2)
        self._inventory_frame.pack(side=tk.RIGHT)

        self._basic_map = BasicMap(self._map_frame, size)

        self._inventory_view = InventoryView(self._inventory_frame, size)


    def handler_adaptor(self, fun, **kwargs) -> None:
        return lambda event, fun=fun, kwargs=kwargs: fun(event, **kwargs)


    def _inventory_click(self, event, inventory: Inventory) -> None:
        pixel_x, pixel_y = event.x, event.y
        position = self._inventory_view.pixel_to_position(Position(pixel_x, pixel_y))
        row_index = position.get_y()
        if row_index > 0 and row_index <= len(inventory.get_items()):
            item = inventory.get_items()[row_index - 1]
            if not item.is_active():
                for active_item in inventory.get_items():
                    if active_item.is_active():
                        active_item.toggle_active()
                        break
            item.toggle_active()
        self._inventory_view.draw(inventory)


    def _key_press(self, event, game: Game) -> None:
        if event.char == 'w':
            self._move(game, UP)
        elif event.char == 'a':
            self._move(game, LEFT)
        elif event.char == 's':
            self._move(game, DOWN)
        elif event.char == 'd':
            self._move(game, RIGHT)
        elif event.keysym == 'Up':
            self._fire(game, UP)
        elif event.keysym == 'Down':
            self._fire(game, DOWN)
        elif event.keysym == 'Left':
            self._fire(game, LEFT)
        elif event.keysym == 'Right':
            self._fire(game, RIGHT)
        else:
            return

    def draw(self, game: Game) -> None:
        '''
        draw entity
        '''

        self._basic_map._basic_map_canvas.delete("all")
        mapping = game.get_grid().serialize()
        size = self._size

        for y in range(size):
            for x in range(size):
                tile = mapping.get((x, y), " ") or " "
                if tile is not " ":
                    self._basic_map.draw_entity(Position(x, y), tile)

        '''
        draw inventory
        '''
        self._inventory_view._inventory_view_canvas.delete("pickup")
        self._inventory_view.draw(game.get_player().get_inventory())


    def _move(self, game: Game, direction: str):
        '''
        move the player and redrawing
        '''
        new_position = game.direction_to_offset(direction)
        game.move_player(new_position)
        self.draw(game)
        self._basic_map._basic_map_canvas.update()
        if not game.has_lost() and game.has_won():
            self._basic_map._basic_map_canvas.after_cancel(self._solve)
            if not messagebox.askyesno(WIN_MESSAGE, 'Play again?'):
                self._root.quit()
            else:
                self._root.focus_force()
                self.play(advanced_game(MAP_FILE))


    def _fire(self, game: Game, direction: str):
        player = game.get_player()
        if player is None or not isinstance(player, HoldingPlayer):
            return  # Should never happen.

        # Ensure player has a weapon that they can fire.
        inventory = player.get_inventory()
        for item in inventory.get_items():
            if item.display() == CROSSBOW and item.is_active():
                # Fire the weapon in the indicated direction, if possible.
                start = game.get_grid().find_player()
                offset = game.direction_to_offset(direction)
                if start is None or offset is None:
                    return  # Should never happen.

                # Find the first entity in the direction player fired.
                first = first_in_direction(
                    game.get_grid(), start, offset
                )

                # If the entity is a zombie, kill it.
                if first is not None and first[1].display() in ZOMBIES:
                    position, entity = first
                    game.get_grid().remove_entity(position)
                break
        self.draw(game)


    def _step(self, game: Game):
        game.step()
        self.draw(game)
        self._solve = self._basic_map._basic_map_canvas.after(1000, self._step, game)
        if not game.has_won() and game.has_lost():
            self._basic_map._basic_map_canvas.after_cancel(self._solve)
            if not messagebox.askyesno(LOSE_MESSAGE, 'Play again?'):
                self._root.quit()
            else:
                self._root.focus_force()
                self.play(advanced_game(MAP_FILE))


    def play(self, game: Game):
        self._inventory_view._inventory_view_canvas.bind("<Button-1>",
                                                         self.handler_adaptor(self._inventory_click,
                                                                              inventory=game.get_player().get_inventory()))
        self._basic_map._basic_map_canvas.bind("<Key>", self.handler_adaptor(self._key_press, game=game))
        self._basic_map._basic_map_canvas.focus_set()
        self.draw(game)
        self._basic_map._basic_map_canvas.update()
        self._solve = self._basic_map._basic_map_canvas.after(1000, self._step, game)
