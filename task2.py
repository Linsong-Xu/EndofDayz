# -*- coding: utf-8 -*-

from model_class import ImageMap, InventoryView, StatusBar
from a2_solution import *
from typing import Tuple, Optional, Dict, List
import tkinter as tk
from tkinter import messagebox
from constants import *
from PIL import Image, ImageTk


class ImageGraphicalInterface:
    def __init__(self, root, size: int) -> None:
        '''
        Init the window
        five frame
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

                                |------------------------------------------------------|
                                |                  _status_bar_frame                  |
                                |______________________________________________________|

        '''
        self._root = root
        self._size = size
        self._window_width = size * CELL_SIZE + INVENTORY_WIDTH + 12
        self._window_height = (size + 1) * CELL_SIZE + BANNER_HEIGHT + 16
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
        self._title_label_height = BANNER_HEIGHT

        self._title_label_canvas = tk.Canvas(self._title_label_frame, height=self._title_label_height,
                                             width=self._window_width - 8, bd=0,
                                             highlightthickness=0)
        self._title_label_image = ImageTk.PhotoImage(
            Image.open('images/banner.png').resize((self._window_width - 8, self._title_label_height)))
        self._title_label_canvas.create_image(0, 0, image=self._title_label_image, anchor='nw')
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
        self._basic_map = ImageMap(self._map_frame, size)
        self._inventory_view = InventoryView(self._inventory_frame, size)

        '''
        Init StatusBar Frame
        '''
        self._status_bar_frame = tk.Frame(self._root, bd=2)
        self._status_bar_frame.pack(side=tk.TOP)
        self._status_bar = StatusBar(self._status_bar_frame, width=self._window_width - 8, height=CELL_SIZE)
        self._status_bar.get_quit_button().configure(command=self.quit)
        self._status_bar.get_restart_button().configure(command=self.restart)

        '''
        Init the file menu
        '''
        self._menubar = tk.Menu(self._root)
        self._filemenu = tk.Menu(self._menubar, tearoff=0)
        self._filemenu.add_command(label="Restart game", command=self.restart)
        self._filemenu.add_command(label="Save game", command=self.save)
        self._filemenu.add_command(label="Load game", command=self.quit)
        self._filemenu.add_command(label="High scores", command=self.display_high_scores)
        self._filemenu.add_separator()
        self._filemenu.add_command(label="Quit", command=self.quit)
        self._menubar.add_cascade(label="File", menu=self._filemenu)

        self._root.config(menu=self._menubar)

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

        self._basic_map._basic_map_canvas.delete("entity")
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

    def _move(self, game: Game, direction: str) -> None:
        '''
        move the player and redrawing
        '''
        new_position = game.direction_to_offset(direction)
        game.move_player(new_position)
        self._status_bar.change_move(game.get_moves())
        self.draw(game)
        self._basic_map._basic_map_canvas.update()
        if not game.has_lost() and game.has_won():
            self._basic_map._basic_map_canvas.after_cancel(self._solve)
            score = game.get_steps()
            score_minute = int(score // 60)
            score_second = int(score % 60)

            self._win_window = tk.Toplevel(self._root)
            self._win_window.title('You Win!')
            self._win_window.geometry('280x80' + '+' + str(
                (self._screen_width - 280) // 2) + '+' + str(
                (self._screen_height - 80) // 2))
            self._win_window.minsize(280, 80)
            self._win_window.maxsize(280, 80)
            self._message_frame = tk.Frame(self._win_window, bd=0)
            self._message_frame.pack(side=tk.TOP)
            if score_minute == 0:
                message_label_text = 'You won in ' + str(score_second) + 's! Enter your name:'
            else:
                message_label_text = 'You won in ' + str(score_minute) + 'm and ' + str(
                    score_second) + 's! Enter your name:'
            self._message_label = tk.Label(self._message_frame, text=message_label_text)
            self._message_label.pack(side=tk.TOP)

            self._name_value = tk.Entry(self._message_frame, bd=1)
            self._name_value.pack(side=tk.TOP)

            button_frame = tk.Frame(self._message_frame)
            button_frame.pack(side=tk.TOP)
            enter_button = tk.Button(button_frame, text='Enter', command=lambda: self.enter_button_clicked(score))
            enter_button.pack(side=tk.LEFT)
            play_again_button = tk.Button(button_frame, text='Enter and play again',
                                          command=lambda: self.play_again_button_clicked(score))
            play_again_button.pack(side=tk.LEFT)

    def _fire(self, game: Game, direction: str) -> None:
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

    def _step(self, game: Game) -> None:
        game.step()
        self._status_bar.change_timer(game.get_steps())
        self.draw(game)
        self._solve = self._basic_map._basic_map_canvas.after(1000, self._step, game)
        if not game.has_won() and game.has_lost():
            self._basic_map._basic_map_canvas.after_cancel(self._solve)
            score = game.get_steps()
            score_minute = int(score // 60)
            score_second = int(score % 60)
            if score_minute == 0:
                lose_text = 'You lose in ' + str(score_second) + 's! Play again?'
            else:
                lose_text = 'You lose in ' + str(score_minute) + 'm and ' + str(
                    score_second) + 's! Play again?'
            if not messagebox.askyesno(LOSE_MESSAGE, lose_text):
                self._root.quit()
            else:
                self._root.focus_force()
                self.play(advanced_game(MAP_FILE))

    def play(self, game: Game) -> None:
        self._game = game
        self._inventory_view._inventory_view_canvas.bind("<Button-1>",
                                                         self.handler_adaptor(self._inventory_click,
                                                                              inventory=game.get_player().get_inventory()))
        self._basic_map._basic_map_canvas.bind("<Key>", self.handler_adaptor(self._key_press, game=game))
        self._basic_map._basic_map_canvas.focus_set()
        self.draw(game)
        self._basic_map._basic_map_canvas.update()
        self._solve = self._basic_map._basic_map_canvas.after(1000, self._step, game)

    def quit(self) -> None:
        self._basic_map._basic_map_canvas.after_cancel(self._solve)
        self._root.quit()

    def restart(self) -> None:
        self._basic_map._basic_map_canvas.after_cancel(self._solve)
        self._status_bar.change_timer(0)
        self._status_bar.change_move(0)
        self.play(advanced_game(MAP_FILE))

    def save(self) -> None:
        print(self._game.__dict__)
        #self._root.quit()

    def display_high_scores(self) -> None:
        with open(HIGH_SCORES_FILE, mode='a+') as high_score_file:
            high_score_file.seek(0)
            contents = high_score_file.readlines()
        high_scores = []
        for y, line in enumerate(contents):
            name_score = line.strip().split(':')
            score = name_score[1]
            score_minute = int(score) // 60
            score_second = int(score) % 60
            if score_minute > 0:
                high_scores.append(name_score[0] + ': ' + str(score_minute) + 'm ' + str(score_second) + 's')
            else:
                high_scores.append(name_score[0] + ': ' + str(score_second) + 's')

        self._high_score = tk.Toplevel(self._root)

        self._high_score.geometry('200x' + str((len(high_scores) + 1) * 50 + 30) + '+' + str(
            (self._screen_width - 200) // 2) + '+' + str(
            (self._screen_height - (len(high_scores) + 1) * 50 + 30) // 2))
        self._high_score.minsize(200, (len(high_scores) + 1) * 50 + 30)
        self._high_score.maxsize(200, (len(high_scores) + 1) * 50 + 30)

        self._high_score_label_frame = tk.Frame(self._high_score, bd=0)
        self._high_score_label_frame.pack(side=tk.TOP)
        self._high_score_label_canvas = tk.Canvas(self._high_score_label_frame, width=200, height=50, bd=0,
                                                  highlightthickness=0, bg=DARK_PURPLE)
        self._high_score_label_canvas.create_text(100, 25, text='High Scores', fill='white', font=('Purisa', 30))
        self._high_score_label_canvas.pack(side=tk.TOP)

        for i in range(min(MAX_ALLOWED_HIGH_SCORES, len(high_scores))):
            name_frame = tk.Frame(self._high_score, bd=0)
            name_frame.pack(side=tk.TOP)
            name_canvas = tk.Canvas(name_frame, width=200, height=50, bd=0, highlightthickness=0)
            name_canvas.create_text(100, 25, text=high_scores[i], fill='black')
            name_canvas.pack(side=tk.TOP)
        button_frame = tk.Frame(self._high_score, width=200, height=20, bd=0)
        button_frame.pack(side=tk.TOP)
        button_frame.pack_propagate(False)
        button = tk.Button(button_frame, text="Done", command=self._high_score.destroy)
        button.pack()

    def enter_button_clicked(self, score: int) -> None:
        winner_name = self._name_value.get()
        if winner_name == '':
            winner_name = 'XXX XXX'
        winner_score = score
        self.change_high_score_file(winner_name, winner_score)

        self._inventory_view._inventory_view_canvas.unbind("<Button-1>")
        self._basic_map._basic_map_canvas.unbind("<Key>")
        self._win_window.destroy()

    def play_again_button_clicked(self, score: int) -> None:
        winner_name = self._name_value.get()
        if winner_name == '':
            winner_name = 'XXX XXX'
        winner_score = score
        self.change_high_score_file(winner_name, winner_score)

        self._win_window.destroy()
        self._root.focus_force()
        self.play(advanced_game(MAP_FILE))

    def change_high_score_file(self, winner_name: str, winner_score: int) -> None:
        with open(HIGH_SCORES_FILE, mode='a+') as high_score_file:
            high_score_file.seek(0)
            contents = high_score_file.readlines()
        name_scores = []
        for y, line in enumerate(contents):
            name_score = line.strip().split(':')
            name_scores.append((name_score[0], int(name_score[1])))
        if len(name_scores) < MAX_ALLOWED_HIGH_SCORES:
            name_scores.append((winner_name, winner_score))
            name_scores = sorted(name_scores, key=lambda x: x[1])
            with open(HIGH_SCORES_FILE, mode='w+') as high_score_file:
                for item in name_scores:
                    high_score_file.writelines(item[0] + ':' + str(item[1]) + '\n')
        elif len(name_scores) == MAX_ALLOWED_HIGH_SCORES and name_scores[-1][1] > winner_score:
            name_scores[-1] = (winner_name, winner_score)
            name_scores = sorted(name_scores, key=lambda x: x[1])
            with open(HIGH_SCORES_FILE, mode='w+') as high_score_file:
                for item in name_scores:
                    high_score_file.writelines(item[0] + ':' + str(item[1]) + '\n')
