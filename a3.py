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

# Uncomment the following imports to import the view classes that represent
# the GUI for each of the tasks that you implement in the assignment.
from task1 import BasicGraphicalInterface
from task2 import ImageGraphicalInterface
from csse7030 import MastersGraphicalInterface


def main() -> None:
    """Entry point to gameplay."""
    game = advanced_game(MAP_FILE)

    root = tk.Tk()
    root.title('EndOfDayz')
    if TASK == 1:
        gui = BasicGraphicalInterface
    elif TASK == 2:
        gui = ImageGraphicalInterface
    else:
        gui = MastersGraphicalInterface
    app = gui(root, game.get_grid().get_size())
    app.play(game)
    root.mainloop()


if __name__ == '__main__':
    main()
