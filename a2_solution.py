"""
A model of a zombie survival game wherein the player has to reach
the hospital whilst evading zombies.
"""
from typing import Tuple, Optional, Dict, List
import random
from constants import *


## Support code

def random_directions() -> List[Tuple[int, int]]:
    """
    Return a randomly sorted list of directions.

    The list will always contain (0, 1), (0, -1), (1, 0), (-1, 0)
    but the order will be random.

    Each direction is represented by an offset that is the change
    in (x, y) coordinates that results from moving in the direction.
    """
    return random.sample(OFFSETS, k=4)


def first_in_direction(
    grid: 'Grid', start: 'Position', offset: 'Position'
) -> Optional[Tuple['Position', 'Entity']]:
    """
    Get the first entity in in the direction of a position
    Parameters:
        grid: Grid of the current game
        start: Point of reference
        offset: Position offset representing a direction to look at
    Returns: A tuple of a position and the first entity found in the
        given direction, None if no entity found
    """
    position = start.add(offset)

    while grid.in_bounds(position):
        entity = grid.get_entity(position)
        if entity is not None:
            return position, entity

        position = position.add(offset)

    return None


class Position:
    """
    The position class represents a location in a 2D grid.

    A position is made up of an x coordinate and a y coordinate.
    The x and y coordinates are assumed to be non-negative whole numbers which
    represent a square in a 2D grid.

    Examples:
        >>> position = Position(2, 4)
        >>> position
        Position(2, 4)
        >>> position.get_x()
        2
        >>> position.get_y()
        4
    """

    def __init__(self, x: int, y: int):
        """
        The position class is constructed from the x and y coordinate which the
        position represents.

        Parameters:
            x: The x coordinate of the position
            y: The y coordinate of the position
        """
        self._x = x
        self._y = y

    def get_x(self) -> int:
        """Returns the x coordinate of the position."""
        return self._x

    def get_y(self) -> int:
        """Returns the y coordinate of the position."""
        return self._y

    def distance(self, position: "Position") -> int:
        """
        Returns the manhattan distance between this point and another point.

        The manhattan distance for two points (x_1, y_1) and (x_2, y_2)
        is calculated with the formula

        |x_1 - x_2| + |y_1 - y_2|

        where |x| is the absolute value of x.

        Parameters:
            position: Another position to calculate the distance from
                      the current position.
        """
        dx = abs(self.get_x() - position.get_x())
        dy = abs(self.get_y() - position.get_y())
        return dx + dy

    def in_range(self, position: "Position", range: int) -> bool:
        """
        Returns true if the given position is in range of the current position.

        The distance between the two positions are calculated by the manhattan
        distance. See the Position.distance method for details.

        Parameters:
            position: Another position to check if it is within range
                      of this current position.
            range: The maximum distance for another position to be considered
                   within range of this position.

        Precondition:
            range >= 0
        """
        distance = self.distance(position)
        return distance < range

    def add(self, position: "Position") -> "Position":
        """
        Add a given position to this position and return a new instance of
        Position that represents the cumulative location.

        This method shouldn't modify the current position.

        Examples:
            >>> start = Position(1, 2)
            >>> offset = Position(2, 1)
            >>> end = start.add(offset)
            >>> end
            Position(3, 3)

        Parameters:
            position: Another position to add with this position.

        Returns:
            A new position representing the current position plus
            the given position.
        """
        return Position(self._x + position.get_x(), self._y + position.get_y())

    def __eq__(self, other: object) -> bool:
        """
        Return whether the given other object is equal to this position.

        If the other object is not a Position instance, returns False.
        If the other object is a Position instance and the
        x and y coordinates are equal, return True.

        Parameters:
            other: Another instance to compare with this position.
        """
        # an __eq__ method needs to support any object for example
        # so it can handle `Position(1, 2) == 2`
        # https://www.pythontutorial.net/python-oop/python-__eq__/
        if not isinstance(other, Position):
            return False
        return self.get_x() == other.get_x() and self.get_y() == other.get_y()

    def __hash__(self) -> int:
        """
        Calculate and return a hash code value for this position instance.

        This allows Position instances to be used as keys in dictionaries.

        A hash should be based on the unique data of a class, in the case
        of the position class, the unique data is the x and y values.
        Therefore, we can calculate an appropriate hash by hashing a tuple of
        the x and y values.
        
        Reference: https://stackoverflow.com/questions/17585730/what-does-hash-do-in-python
        """
        return hash((self.get_x(), self.get_y()))

    def __repr__(self) -> str:
        """
        Return the representation of a position instance.

        The format should be 'Position({x}, {y})' where {x} and {y} are replaced
        with the x and y value for the position.

        Examples:
            >>> repr(Position(12, 21))
            'Position(12, 21)'
            >>> Position(12, 21).__repr__()
            'Position(12, 21)'
        """
        return f"Position({self.get_x()}, {self.get_y()})"

    def __str__(self) -> str:
        """
        Return a string of this position instance.

        The format should be 'Position({x}, {y})' where {x} and {y} are replaced
        with the x and y value for the position.
        """
        return self.__repr__()


class GameInterface:
    """
    The GameInterface class is an abstract class that handles the communication
    between the interface used to play the game and the game itself.

    For this assignment, we will only have one interface to play the game,
    the text interface.
    """

    def draw(self, game) -> None:
        """
        Draw the state of a game to the respective interface.

        The abstract GameInterface class should raise a NotImplementedError for
        this method.

        Parameters:
            map (Game): An instance of the game class that is to be displayed
                        to the user by printing the grid.
        """
        raise NotImplementedError

    def play(self, game) -> None:
        """
        The play method takes a game instance and orchestrates the running of
        the game, including the interaction between the player and the game.

        The abstract GameInterface class should raise a NotImplementedError for
        this method.

        Parameters:
            game (Game): An instance of the Game class to play.
        """
        raise NotImplementedError


EntityLocations = Dict[Tuple[int, int], str]
"""
EntityLocations stores locations of entities in the game map.

The key is a tuple, as (x, y) coordinates,
which represents the location of the entity.
The value is a string representing the entity.
"""


def load_map(filename: str) -> Tuple[EntityLocations, int]:
    """
    Open and read a map file, converting it into a tuple.

    The first element of the returned tuple contains a dictionary which maps
    (x, y) coordinates to a string representing an entity in the map.

    The second element of the returned tuple is the size of the map.

    Parameters:
        filename: Path where the map file should be found.

    Returns:
        A tuple containing the serialized map and the size of the map.
    """
    with open(filename) as map_file:
        contents = map_file.readlines()

    result = {}
    for y, line in enumerate(contents):
        for x, char in enumerate(line.strip("\n")):
            if char != " ":
                result[(x, y)] = char

    return result, len(contents)


## Task 1
class Entity:
    """
    Entity is an abstract class that is used to represent anything that can
    appear on the game's grid.
    
    For example, the game grid will always have a player, so a player is
    considered a type of entity. A game grid may also have a zombie, so a
    zombie is considered a type of entity.
    """

    def step(self, position: Position, game: "Game") -> None:
        """
        The `step` method is called on every entity in the game grid after each
        move made by the player, it controls what actions an entity will perform
        during the _step_ event.
        
        The abstract Entity class will not perform any action during the
        _step_ event. Therefore, this method should do nothing.
        
        Parameters:
            position: The position of this entity when the _step_ event
                      is triggered.
            game: The current game being played.
        """
        pass

    def display(self) -> str:
        """
        Return the character used to represent this entity in a text-based grid.
        
        An instance of the abstract Entity class should never be placed in the
        grid, so this method should only be implemented by subclasses of Entity.
        
        To indicate that this method needs to be implemented by subclasses,
        this method should raise a NotImplementedError.
        
        Raises:
            NotImplementedError: Whenever this method is called.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Return a representation of this entity.
        
        By convention, the repr string of a class should look as close as
        possible to how the class is constructed. Since entities do not take
        constructor parameters, the repr string will be the class name followed
        by parentheses, ().
        
        For example, the representation of the Entity class will be Entity().
        
        Examples:
            >>> repr(Entity())
            'Entity()'
            >>> Entity().__repr__()
            'Entity()'
            >>> entity = Entity()
            >>> repr(entity)
            'Entity()'
        """
        return f"{self.__class__.__name__}()"


class Player(Entity):
    """
    A player is a subclass of the entity class that represents the player
    that the user controls on the game grid.
    
    Examples:
        >>> player = Player()
        >>> repr(player)
        'Player()'
        >>> player.display()
        'P'
    """

    def display(self) -> str:
        """
        Return the character used to represent the player entity in a
        text-based grid.
        
        A player should be represented by the 'P' character.
        """
        return PLAYER


class Hospital(Entity):
    """
    A hospital is a subclass of the entity class that represents the hospital
    in the grid.
    
    The hospital is the entity that the player has to reach in order to win
    the game.
    
    Examples:
        >>> hospital = Hospital()
        >>> repr(hospital)
        'Hospital()'
        >>> hospital.display()
        'H'
    """

    def display(self) -> str:
        """
        Return the character used to represent the hospital entity in a
        text-based grid.
        
        A hospital should be represented by the 'H' character.
        """
        return HOSPITAL


class Grid:
    """
    The Grid class is used to represent the 2D grid of entities.
    
    The grid can vary in size but it is always a square.
    Each (x, y) position in the grid can only contain one entity at a time.
    
    Examples:
        >>> grid = Grid(5)
        >>> grid.get_size()
        5
        >>> grid.in_bounds(Position(2, 2))
        True
        >>> grid.in_bounds(Position(0, 6))
        False
        >>> grid.get_entities()
        []
        >>> grid.add_entity(Position(2, 2), Hospital())
        >>> grid.get_entity(Position(2, 2))
        Hospital()
        >>> grid.get_entities()
        [Hospital()]
        >>> grid.serialize()
        {(2, 2): 'H'}
    """

    def __init__(self, size: int):
        """
        A grid is constructed with a size that dictates the length and width
        of the grid.
        
        Initially a grid does not contain any entities.
        
        Parameters:
            size: The length and width of the grid.
        """
        self._size = size
        self._tiles: Dict[Position, Entity] = {}

    def get_size(self) -> int:
        """Returns the size of the grid."""
        return self._size

    def in_bounds(self, position: Position) -> bool:
        """
        Return True if the given position is within the bounds of the grid.
        
        For a position to be within the bounds of the grid, both the x and y
        coordinates have to be greater than or equal to zero but less than
        the size of the grid.
        
        Parameters:
            position: An (x, y) position that we want to check is
                      within the bounds of the grid.
                      
        Examples:
            >>> grid5 = Grid(5)
            >>> grid5.in_bounds(Position(0, 10))
            False
            >>> grid5.in_bounds(Position(0, 5))
            False
            >>> grid5.in_bounds(Position(0, 4))
            True
            >>> grid5.in_bounds(Position(-1, 4))
            False
            >>> grid10 = Grid(10)
            >>> grid10.in_bounds(Position(9, 8))
            True
            >>> grid10.in_bounds(Position(9, 10))
            False
        """
        return (0 <= position.get_x() < self._size
                and 0 <= position.get_y() < self._size)

    def add_entity(self, position: Position, entity: Entity) -> None:
        """
        Place a given entity at a given position of the grid.
        
        If there is already an entity at the given position, the given
        entity will replace the existing entity.
        
        If the given position is outside the bounds of the grid, the entity
        should not be added.
        
        \\textbf{Hint:} You may find it helpful to implement `get_entity` below
        at the same time as this method.
        
        Parameters:
            position: An (x, y) position in the grid to place the entity.
            entity: The entity to place on the grid.
            
        Examples:
            >>> grid = Grid(4)
            >>> grid.add_entity(Position(0, 0), Player())
            >>> grid.get_entity(Position(0, 0))
            Player()
            >>> grid.add_entity(Position(0, 0), Hospital())
            >>> grid.get_entity(Position(0, 0))
            Hospital()
            >>> grid.add_entity(Position(-1, 0), Player())
            >>> grid.get_entity(Position(-1, 0))
        """
        if self.in_bounds(position):
            self._tiles[position] = entity

    def remove_entity(self, position: Position) -> None:
        """
        Remove the entity, if any, at the given position.
        
        Parameters:
            position: An (x, y) position in the grid from which the entity
                      is removed.
                      
        Examples:
            >>> grid = Grid(4)
            >>> grid.add_entity(Position(0, 0), Player())
            >>> grid.get_entity(Position(0, 0))
            Player()
            >>> grid.remove_entity(Position(0, 0))
            >>> grid.get_entity(Position(0, 0))
        """
        self._tiles.pop(position, None)

    def get_entity(self, position: Position) -> Optional[Entity]:
        """
        Return the entity that is at the given position in the grid.
        
        If there is no entity at the given position, returns None.
        If the given position is out of bounds, returns None.
        
        See the above `add_entity` method for examples.
        
        Parameters:
            position: The (x, y) position in the grid to check for an entity.
        """
        return self._tiles.get(position)

    def get_mapping(self) -> Dict[Position, Entity]:
        """
        Return a dictionary with position instances as the keys and entity
        instances as the values.
        
        For every position in the grid that has an entity, the returned
        dictionary should contain an entry with the position instance
        mapped to the entity instance.
        
        Updating the returned dictionary should have no side-effects.
        It would not modify the grid.
        
        Examples:
            >>> grid = Grid(4)
            >>> grid.add_entity(Position(0, 0), Player())
            >>> grid.add_entity(Position(3, 3), Hospital())
            >>> grid.get_mapping()
            {Position(0, 0): Player(), Position(3, 3): Hospital()}
        """
        return self._tiles.copy()

    def get_entities(self) -> List[Entity]:
        """
        Return a list of all the entities in the grid.
        
        Updating the returned list should have no side-effects.
        It would not modify the grid.
        
        Examples:
            # The example below shows a grid with multiple hospitals this should
            # never occur in practice but isn't prohibited
            >>> grid = Grid(5)
            >>> grid.add_entity(Position(0, 0), Hospital())
            >>> grid.add_entity(Position(0, 1), Player())
            >>> grid.add_entity(Position(2, 2), Hospital())
            >>> grid.add_entity(Position(4, 4), Hospital())
            >>> grid.get_entities()
            [Hospital(), Player(), Hospital(), Hospital()]
        """
        return list(self._tiles.values())

    def move_entity(self, start: Position, end: Position) -> None:
        """
        Move an entity from the given start position to the given end position.
        
        * If the end position or start position is out of the grid bounds,
          do not attempt to move.
        * If there is no entity at the given start position,
          do not attempt to move.
        * If there is an entity at the given end position, replace that entity
          with the entity from the start position.
          
        The start position should not have an entity after moving.
        
        Parameters:
            start: The position the entity is in initially.
            end: The position to which the entity will be moved.
            
        Examples:
            >>> grid = Grid(10)
            >>> grid.add_entity(Position(1, 2), Player())
            >>> grid.move_entity(Position(1, 2), Position(3, 5))
            >>> grid.get_entity(Position(1, 2))
            >>> grid.get_entity(Position(3, 5))
            Player()
        """
        if start == end:
            return
        if self.in_bounds(start) and self.in_bounds(end):
            entity = self.get_entity(start)
            if entity is not None:
                self._tiles[end] = entity
                del self._tiles[start]

    def find_player(self) -> Optional[Position]:
        """
        Return the position of the player within the grid.
        
        Return None if there is no player in the grid.
        
        If the grid has multiple players (which it should not),
        returning any of the player positions is sufficient.
        
        Examples:
            >>> grid = Grid(10)
            >>> grid.add_entity(Position(4, 6), Player())
            >>> grid.find_player()
            Position(4, 6)
        """
        for position, entity in self._tiles.items():
            if entity.display() == PLAYER:
                return position
        return None

    def serialize(self) -> Dict[Tuple[int, int], str]:
        """
        Serialize the grid into a dictionary that maps tuples to characters.

        The tuples should have two values, the x and y coordinate representing
        a postion.
        The characters are the display representation of the entity at that
        position. i.e. 'P' for player, `H' for hospital.
        
        Only positions that have an entity should exist in the dictionary.

        Examples:
            >>> grid = Grid(50)
            >>> grid.add_entity(Position(3, 8), Player())
            >>> grid.add_entity(Position(3, 20), Hospital())
            >>> grid.serialize()
            {(3, 8): 'P', (3, 20): 'H'}
        """
        serialized = {}

        for position, entity in self._tiles.items():
            pair = (position.get_x(), position.get_y())
            serialized[pair] = entity.display()

        return serialized


class MapLoader:
    """
    The MapLoader class is used to read a map file and create an appropriate
    Grid instance which stores all the map file entities.
    
    The MapLoader class is an abstract class to allow for extensible map
    definitions. The BasicMapLoader class described below is a very simple
    implementation of the MapLoader which only handles the player and hospital
    entities.
    """

    def load(self, filename: str) -> Grid:
        """
        Load a new Grid instance from a map file.
        
        Load will open the map file and read each line to find all the entities
        in the grid and add them to the new Grid instance.
        
        The `create_entity` method below is used to turn a character
        in the map file into an Entity instance.
        
        \\textbf{Hint:} The `load_map` function in the support code may be helpful.
        
        Parameters:
            filename: Path where the map file should be found.
        """
        mapping, size = load_map(filename)

        grid = Grid(size)
        for position, entity in mapping.items():
            grid.add_entity(Position(*position), self.create_entity(entity))

        return grid

    def create_entity(self, token: str) -> Entity:
        """
        Create and return a new instance of the Entity class based on the
        provided token.
        
        For example, if the given token is 'P' a Player instance will be
        returned.
        
        The abstract MapLoader class does not support any entities, when this
        method is called, it should raise a NotImplementedError.
        
        Parameters:
            token: Character representing the Entity subtype.
        """
        raise NotImplementedError(token)


class BasicMapLoader(MapLoader):
    """
    BasicMapLoader is a subclass of MapLoader which can handle loading map
    files which include the following entities:
    
    * Player
    * Hospital
    """

    def create_entity(self, token: str) -> Entity:
        """
        Create and return a new instance of the Entity class based on the
        provided token.
        
        For example, if the given token is 'P' a Player instance will be
        returned.
        
        The BasicMapLoader class only supports the Player and Hospital entities.
        When a token is provided that does not represent the Player or Hospital,
        this method should raise a ValueError.
        
        Parameters:
            token: Character representing the Entity subtype.
        """
        if token == PLAYER:
            return Player()
        elif token == HOSPITAL:
            return Hospital()

        raise ValueError(f"Unrecognised entity '{token}' in map file.")


class Game:
    """
    The Game handles some of the logic for controlling the actions of the player
    within the grid.
    
    The Game class stores an instance of the Grid and keeps track of the player
    within the grid so that the player can be controlled.
    """

    def __init__(self, grid: Grid):
        """
        The construction of a Game instance takes the grid upon which the game
        is being played.
        
        Preconditions:
            The grid has a player, i.e. `grid.find_player()` is not None.
            
        Parameters:
            grid (Grid): The game's grid.
        """
        self._grid = grid
        self._player_position = grid.find_player()
        self._steps = 0
        self._moves = 0

    def get_grid(self) -> Grid:
        """Return the grid on which this game is being played."""
        return self._grid

    def get_player(self) -> Optional[Player]:
        """
        Return the instance of the Player class in the grid.
        
        If there is no player in the grid, return None.
        
        If there are multiple players in the grid, returning any player is
        sufficient.
        """
        if self._player_position is None:
            return None

        player = self.get_grid().get_entity(self._player_position)

        return player  # type: ignore

    def step(self) -> None:
        """
        The _step_ method of the game will be called after every action
        performed by the player.
        
        This method triggers the _step_ event by calling the step method
        of every entity in the grid. When the entity's step method is called,
        it should pass the entity's current position and this game as parameters.

        Note: Do not call this method in the `move_player` method.
        """
        for position, entity in self._grid.get_mapping().items():
            entity.step(position, self)
        self._steps += 1


    def get_steps(self) -> int:
        """
        Return the amount of steps made in the game,
        i.e. how many times the `step` method has been called.
        """
        return self._steps

    def get_moves(self) -> int:
        """
        Return the amount of steps made in the game,
        """
        return self._moves

    def move_player(self, offset: Position) -> None:
        """
        Move the player entity in the grid by a given offset.
        
        Add the offset to the current position of the player, move the player
        entity within the grid to the new position.
        
        If the new position is outside the bounds of the grid, or there is no
        player in the grid, this method should not move the player.
        
        Parameters:
            offset: A position to add to the player's current position
                    to produce the player's new desired position.
        """
        if self._player_position is not None:
            destination = self._player_position.add(offset)
            if self._grid.in_bounds(destination):
                self._grid.move_entity(self._player_position, destination)
                self._player_position = destination
        self._moves += 1

    def direction_to_offset(self, direction: str) -> Optional[Position]:
        """
        Convert a direction, as a string, to a offset position.
        
        The offset position can be added to a position to move in the
        given direction.
        
        If the given direction is not valid, this method should return None.
        
        Parameters:
            direction: Character representing the direction in which the
                       player should be moved.
                       
        Examples:
            >>> game = Game(Grid(5))
            >>> game.direction_to_offset("W")
            Position(0, -1)
            >>> game.direction_to_offset("S")
            Position(0, 1)
            >>> game.direction_to_offset("A")
            Position(-1, 0)
            >>> game.direction_to_offset("D")
            Position(1, 0)
            >>> game.direction_to_offset("N")
            >>> game.direction_to_offset("that way!")
        """
        if direction == UP:
            return Position(0, -1)
        elif direction == DOWN:
            return Position(0, 1)
        elif direction == LEFT:
            return Position(-1, 0)
        elif direction == RIGHT:
            return Position(1, 0)
        else:
            return None

    def has_won(self) -> bool:
        """
        Return true if the player has won the game.
        
        The player wins the game by stepping onto the hospital. When the player
        steps on the hospital, there will be no hospital entity in the grid.
        """
        return HOSPITAL not in self._grid.serialize().values()

    def has_lost(self) -> bool:
        """
        Return true if the player has lost the game.
        
        Currently there is no way for the player to lose the game so this
        method should always return false.
        """
        return False


class TextInterface(GameInterface):
    """
    A text-based interface between the user and the game instance.
    
    This class handles all input collection from the user and printing to the
    console.
    """

    def __init__(self, size: int):
        """
        The text-interface is constructed knowing the size of the game to be
        played, this allows the draw method to correctly print the right
        sized grid.
        
        Parameters:
            size (int): The size of the game to be displayed and played.
        """
        self._size = size

    def draw(self, game: Game) -> None:
        """
        The draw method should print out the given game surrounded
        by '#' characters representing the border of the game.
        
        Parameters:
            game: An instance of the game class that is to be displayed
                  to the user by printing the grid.
                  
        Examples:
            >>> grid = Grid(4)
            >>> grid.add_entity(Position(2, 2), Player())
            >>> game = Game(grid)
            >>> interface = TextInterface(4)
            >>> interface.draw(game)
            ######
            #    #
            #    #
            #  P #
            #    #
            ######
        """
        mapping = game.get_grid().serialize()
        size = self._size
        print(BORDER * (size + 2))
        for y in range(size):
            print(BORDER, end="")
            for x in range(size):
                tile = mapping.get((x, y), " ") or " "
                print(tile, end="")
            print(BORDER)
        print(BORDER * (size + 2))

    def play(self, game: Game) -> None:
        """
        The play method implements the game loop, constantly prompting the user
        for their action, performing the action and printing the game until the
        game is over.
        
        \\textbf{Hint:} Refer to the Gameplay section for a detailed
        explanation of the game loop.
        
        Parameters:
            game: The game to start playing.
        """
        won_game = False
        lost_game = False

        while not won_game and not lost_game:
            self.draw(game)

            action = input(ACTION_PROMPT)
            self.handle_action(game, action)

            if game.has_won():
                print(WIN_MESSAGE)
                won_game = True

            if not won_game and game.has_lost():
                print(LOSE_MESSAGE)
                lost_game = True

    def handle_action(self, game: Game, action: str) -> None:
        """
        The handle_action method is used to process the actions entered
        by the user during the game loop in the play method.
        
        The handle_action method should be able to handle all movement
        actions, i.e. 'W', 'A', 'S', 'D'.
        
        If the given action is not a direction, this method should
        only trigger the step event and do nothing else.

        \\textbf{Hint:} Refer to the Gameplay section for a detailed
        explanation of the game loop.
        
        Parameters:
            game: The game that is currently being played.
            action: An action entered by the player during the game loop.
        """
        if action in DIRECTIONS:
            offset = game.direction_to_offset(action)

            if offset is not None:
                game.move_player(offset)

        game.step()


## Task 2
class VulnerablePlayer(Player):
    """
    The VulnerablePlayer class is a subclass of the Player, this class extends
    the player by allowing them to become infected.
    
    Examples:
        >>> player = VulnerablePlayer()
        >>> player.is_infected()
        False
        >>> player.infect()
        >>> player.is_infected()
        True
        >>> player.infect()
        >>> player.is_infected()
        True
    """

    def __init__(self):
        """
        When an object of the VulnerablePlayer class is constructed,
        the player should not be infected
        """
        super().__init__()
        self._infected = False

    def infect(self) -> None:
        """
        When the infect method is called, the player becomes infected and
        subsequent calls to `is_infected` return true.
        """
        self._infected = True

    def is_infected(self) -> bool:
        """Return the current infected state of the player."""
        return self._infected


class Zombie(Entity):
    """
    The Zombie entity will wander the grid at random.
    
    The movement of a zombie is triggered by the player performing an action,
    i.e. the zombie moves during each _step_ event.
    """

    def _directions(
        self, position: Position, game: Game
    ) -> List[Tuple[int, int]]:
        """
        Returns the list of offsets sorted by the order of directions
        prioritised by this zombie
            
        Parameters:
            position: current position of this zombie
            game: current game being played
        """
        return random_directions()

    def step(self, position: Position, game: Game) -> None:
        """
        The `step` method for the zombie entity will move the zombie
        in a random direction.
        
        To implement this, generate a list of the possible directions to move
        in a random order by calling the `random_directions` function
        from the support code. Check each of the directions to see if the
        resultant position is available. The resultant position is the position
        you reach from moving in a direction.
        
        To be available, a position must be in the bounds of the grid and not
        already contain an entity.
        
        i.e. if `random_directions` returns [(1, 0), (0, 1), (-1, 0), (0, -1)]
        \\begin{enumerate}
        \\item check the current position + (1, 0),
        if that position is available, move there and stop looking.
        \\item check the current position + (0, 1),
        if that position is available, move there and stop looking.
        \\item check the current position + (-1, 0),
        if that position is available, move there and stop looking.
        \\item check the current position + (0, -1),
        if that position is available, move there and stop looking.
        \\end{enumerate}
        
        If none of the resultant positions are available, do not move the zombie.

        If the position the zombie is going to move to contains the player,
        the zombie should infect the player but not move to that position.
        
        Parameters:
            position: The position of this zombie when the _step_ event
                      is triggered.
            game: The current game being played.
        """
        for direction in self._directions(position, game):
            destination = position.add(
                Position(*direction)  # pylint: disable=(not-an-iterable)
            )

            destination_entity = game.get_grid().get_entity(destination)
            if destination_entity is not None:
                # The commented out line is how students are expected to
                # implement it, however, we gotta make the type checker happy.
                # if destination_entity.display() == PLAYER:
                if isinstance(destination_entity, VulnerablePlayer):
                    destination_entity.infect()
                    return

                continue

            if game.get_grid().in_bounds(destination):
                game.get_grid().move_entity(position, destination)
                break

    def display(self) -> str:
        """
        Return the character used to represent the zombie entity in a
        text-based grid.
        
        A zombie should be represented by the 'Z' character.
        """
        return ZOMBIE


class IntermediateGame(Game):
    """
    An intermediate game extends some of the functionality of the basic game.

    Specifically, the intermediate game includes the ability for the player
    to lose the game when they become infected.
    """

    def has_lost(self) -> bool:
        """
        Return true if the player has lost the game.
        
        The player loses the game if they become infected by a zombie.
        """
        player = self.get_player()
        if player is None:
            return True

        # This is to ensure that the type checker is happy.
        # Students are not required to implement this.
        if not isinstance(player, VulnerablePlayer):
            return False

        return player.is_infected()


class IntermediateMapLoader(BasicMapLoader):
    """
    The IntermediateMapLoader class extends BasicMapLoader to add support for
    new entities that are added in task 2 of the assignment.
    
    When a player token, 'P', is found, a VulnerablePlayer instance should
    be created instead of a Player.
    
    In addition to the entities handled by the BasicMapLoader, the
    IntermediateMapLoader should be able to load the following entities:
    
    * Zombie
    """

    def create_entity(self, token: str) -> Entity:
        if token == ZOMBIE:
            return Zombie()
        elif token == PLAYER:
            return VulnerablePlayer()
        return super().create_entity(token)


## Task 3
class TrackingZombie(Zombie):
    """
    The TrackingZombie is a more intelligent type of zombie which is able
    to see the player and move towards them.
    """

    def _directions(
        self, position: Position, game: Game
    ) -> List[Tuple[int, int]]:
        target = game.get_grid().find_player()
        if target is None:
            return []  # Should never happen.

        def distance(direction):
            new_position = position.add(Position(*direction))
            return new_position.distance(target), direction

        best_directions = sorted(OFFSETS, key=distance)
        return best_directions

    def step(self, position: Position, game: Game) -> None:
        """
        The `step` method for the tracking zombie will move the tracking zombie
        in the best possible direction to move closer to the player.
        
        To implement this, sort a list of possible directions to minimize
        the distance between the resultant position and the player's position.
        The resultant position is the position resulting from moving the
        tracking zombie in a direction.
        
        If there are multiple directions that result in being the same
        distance from the player, the direction should be picked in preference
        order picking 'W' first followed by 'S', 'N', and finally 'E'.
        
        i.e. if the zombie is at (1, 1) and the player is at (2, 4)
        * Moving 'N' will give a resultant position of (1, 2), which is a
          distance of 3 from the player
        * Moving 'E' will give a resultant position of (2, 1) which is a
          distance of 3 from the player
        * Moving 'W' will give a resultant position of (0, 1) which is a
          distance of 5 from the player
        * Moving 'S' will give a resultant position of (1, 0) which is a
          distance of 5 from the player
          
        In this situation 'N' and 'E' compete for best direction so 'N' is
        picked, 'W' and 'S' are also equidistant so 'W' is picked, causing an
        order of 'N', 'E', 'W', 'S' to be chosen.
        
        Similar to the zombie's `step` method, this method should check each of
        the possible directions in order, and move the zombie to the first
        available position.
        
        To be available, a position must be in the bounds of the grid and not
        already contain an entity.
        
        If none of the resultant positions are available, do not move the zombie.

        If the position the zombie is going to move to contains the player,
        the zombie should infect the player but not move to that position.
        
        Parameters:
            position: The position of this zombie when the _step_ event
                      is triggered.
            game: The current game being played.
        """
        super().step(position, game)

    def display(self) -> str:
        """
        Return the character used to represent the tracking zombie entity in
        a text-based grid.
        
        A tracking zombie should be represented by the 'T' character.
        """
        return TRACKING_ZOMBIE


class Pickup(Entity):
    """
    A Pickup is a special type of entity that the player is able to pickup and
    hold in their inventory.

    The Pickup class is an abstract class.
    """

    def __init__(self):
        """
        When a Pickup entity is created, the lifetime of the entity should
        be equal to its maximum lifetime (durability).
        """
        self._lifetime = self.get_durability()
        self._using = False     # Entities are not selected to be actively
                                # used, when they are first picked up.

    def get_durability(self) -> int:
        """
        Return the maximum amount of steps the player is able to take while
        holding this item. After the player takes this many steps,
        the item disappears.

        The abstract Pickup class should never be placed in the grid, so
        this method should be implemented by the subclasses of Pickup only.

        To indicate that this method needs to be implemented by subclasses,
        this method should raise a NotImplementedError.
        """
        raise NotImplementedError()

    def get_lifetime(self) -> int:
        """
        Return the remaining steps a player can take with this instance
        of the item before the item disappears from the player's inventory.
        """
        return self._lifetime

    def hold(self) -> None:
        """
        The `hold` method is called on every pickup entity that the player
        is holding each time the player takes a step.

        This will result in the remaining lifetime of the pickup entity
        decreasing by one, if it is selected as being active.
        """
        if self._using:
            self._lifetime -= 1

    def is_active(self) -> bool:
        """
        Returns whether this entity is selected as being active.
        """
        return self._using

    def toggle_active(self) -> None:
        """
        Toggle whether this entity is selected as being active or not.
        """
        self._using = not self._using

    def __repr__(self) -> str:
        """
        Return a string that represents the entity, the representation
        contains the type of the pickup entity and the amount of
        remaining steps.
        """
        return f"{self.__class__.__name__}({self.get_lifetime()})"



class Garlic(Pickup):
    """
    Garlic is an entity which the player can pickup.
    
    While the player is holding a garlic entity they cannot
    be infected by a zombie.
    """

    def get_durability(self) -> int:
        """
        Return the durability of a garlic.
        
        A player can only hold a garlic entity for 10 _steps_.
        """
        return LIFETIMES[GARLIC]

    def display(self) -> str:
        """
        Return the character used to represent the garlic entity in
        a text-based grid.
        
        A garlic should be represented by the 'G' character.
        """
        return GARLIC


class Crossbow(Pickup):
    """
    Crossbow is an entity which the player can pickup.
    
    While the player is holding a crossbow entity they are
    able to use the fire action to launch a protectile in a
    given direction, removing the first zombie in that direction.
    """

    def get_durability(self) -> int:
        """
        Return the durability of a crossbow.
        
        A player can only hold a crossbow entity for 5 _steps_.
        """
        return LIFETIMES[CROSSBOW]

    def display(self) -> str:
        """
        Return the character used to represent the crossbow entity in
        a text-based grid.
        A crossbow should be represented by the 'C' character.
        """
        return CROSSBOW


class TimeMachine(Pickup):
    """
    Crossbow is an entity which the player can pickup.

    While the player is holding a crossbow entity they are
    able to use the fire action to launch a protectile in a
    given direction, removing the first zombie in that direction.
    """

    def get_durability(self) -> int:
        """
        Return the durability of a crossbow.

        A player can only hold a crossbow entity for 5 _steps_.
        """
        return 1

    def display(self) -> str:
        """
        Return the character used to represent the crossbow entity in
        a text-based grid.
        A crossbow should be represented by the 'C' character.
        """
        return TIME_MACHINE

    # def hold(self) -> None:
    #     pass


class Inventory:
    """
    An inventory holds a collection of entities which the player can pickup,
    i.e. Pickup subclasses.
    
    The player is only able to hold any given item for a limited duration, this
    is the lifetime of the item. Once the lifetime is exceeded the item will
    be destroyed by being removed from the inventory.
    
    Examples:
        >>> crossbow = Crossbow()
        >>> garlic = Garlic()
        >>> inventory = Inventory()
        >>> inventory.get_items()
        []
        >>> inventory.add_item(crossbow)
        >>> inventory.add_item(garlic)
        >>> inventory.get_items()
        [Crossbow(5), Garlic(10)]
        >>> inventory.step()
        >>> inventory.step()
        >>> inventory.step()
        >>> inventory.get_items()
        [Crossbow(2), Garlic(7)]
        >>> inventory.step()
        >>> inventory.get_items()
        [Crossbow(1), Garlic(6)]
        >>> inventory.step()
        >>> inventory.get_items()
        [Garlic(5)]
        >>> for _ in range(30): inventory.step()
        >>> inventory.get_items()
        []
    """

    def __init__(self):
        """
        When an inventory is constructed, it should not contain any items.
        """
        self._items = []

    def step(self) -> None:
        """
        The step method should be called every time the player steps as a part
        of the player's `step` method.
        
        When this method is called, the lifetime of every active item stored 
        within the inventory should decrease. Any items in the inventory that 
        have exceeded their lifetime should be removed.
        """
        new_items = []
        for item in self._items:
            item.hold()
            if item.get_lifetime() > 0:
                new_items.append(item)
        self._items = new_items

    def add_item(self, item: Pickup) -> None:
        """
        This method should take a pickup entity and add it to the inventory.

        Parameters:
            item: The pickup entity to add to the inventory.
        """
        self._items.append(item)

    def get_items(self) -> List[Pickup]:
        """
        Return the pickup entity instances currently stored in the inventory.

        Updating the returned list should have no side-effects. It is not
        possible to add items to the inventory by adding to the returned list.
        """
        return self._items[:]

    def contains(self, pickup_id: str) -> bool:
        """
        Return true if the inventory contains any entities which return the
        given pickup_id from the entity's `display` method.
        
        Examples:
            >>> inventory = Inventory()
            >>> inventory.add_item(Garlic())
            >>> inventory.contains("C")
            False
            >>> inventory.contains("G")
            True
        """
        for item in self._items:
            if item.display() == pickup_id:
                return True
        return False

    def has_active(self, pickup_id: str) -> bool:
        """
        Returns whether the inventory contains any active entities of the
        corresponding pickup_id type.
        """
        for item in self._items:
            if item.display() == pickup_id and item.is_active():
                return True
        return False

    def any_active(self) -> bool:
        """
        Returns whether the inventory contains any active entities.
        """
        for item in self._items:
            if item.is_active():
                return True
        return False


class HoldingPlayer(VulnerablePlayer):
    """
    The HoldingPlayer is a subclass of VulnerablePlayer that extends the
    existing functionality of the player.
    
    In particular, a holding player will now keep an inventory.
    """

    def __init__(self):
        super().__init__()
        self._inventory = Inventory()

    def get_inventory(self) -> Inventory:
        """
        Return the instance of the Inventory class that represents the player's
        inventory.
        """
        return self._inventory

    def infect(self) -> None:
        """
        Extend the existing infect method so that the player is
        immune to becoming infected if they are actively holding garlic.
        """
        if not self.get_inventory().has_active(GARLIC):
            super().infect()

    def step(self, position: Position, game: Game) -> None:
        """
        The `step` method for a holding player will notify its inventory
        that a _step_ event has occurred.
        
        Parameters:
            position: The position of this entity when the _step_ event
                      is triggered.
            game: The current game being played.
        """
        self._inventory.step()


class AdvancedGame(IntermediateGame):
    """
    The AdvancedGame class extends IntermediateGame to add support for the
    player picking up a Pickup item when they come into contact with it.
    """

    def move_player(self, offset: Position) -> None:
        """
        Move the player entity in the grid by a given offset.
        
        If the player moves onto a Pickup item, it should be added to the
        player's inventory and removed from the grid.
        
        Parameters:
            offset: A position to add to the player's current position
                    to produce the player's new desired position.
        """
        if self._player_position is not None:
            destination = self._player_position.add(offset)
            if self._grid.in_bounds(destination):
                entity = self._grid.get_entity(destination)
                if entity is not None and isinstance(entity, Pickup):
                    player = self.get_player()
                    if isinstance(player, HoldingPlayer):
                        player.get_inventory().add_item(entity)
                        self.get_grid().remove_entity(destination)
                elif entity is not None and isinstance(entity, Zombie):
                    return
        super().move_player(offset)


class AdvancedMapLoader(IntermediateMapLoader):
    """
    The AdvancedMapLoader class extends IntermediateMapLoader to add support for
    new entities that are added in task 3 of the assignment.
    
    When a player token, 'P', is found, a HoldingPlayer instance should be
    created instead of a Player or VulnerablePlayer.
    
    In addition to the entities handled by the IntermediateMapLoader, the
    AdvancedMapLoader should be able to load the following entities:
    
    * TrackingZombie
    * Garlic
    * Crossbow
    """

    def create_entity(self, token: str) -> Entity:
        if token == PLAYER:
            return HoldingPlayer()
        elif token == TRACKING_ZOMBIE:
            return TrackingZombie()
        elif token == GARLIC:
            return Garlic()
        elif token == CROSSBOW:
            return Crossbow()
        elif token == TIME_MACHINE:
            return TimeMachine()
        return super().create_entity(token)


class AdvancedTextInterface(TextInterface):
    """
    A text-based interface between the user and the game instance.
    
    This class extends the existing functionality of TextInterface to include
    displaying the state of the player's inventory and a firing action.
    """

    def draw(self, game: Game) -> None:
        """
        The draw method should print out the given game surrounded
        by '#' characters representing the border of the game.
        
        This method should behave in the same way as the super class except
        if a player is currently holding items in their inventory.
        
        If the player is holding items in their inventory,
        'The player is currently holding:' should be printed after the grid,
        followed by the representation of each item in the inventory on
        separate lines.
        See the examples for more details.
        
        Parameters:
            game: An instance of the game class that is to be displayed
                  to the user by printing the grid.
                  
        Examples:
            >>> grid = Grid(4)
            >>> grid.add_entity(Position(2, 2), HoldingPlayer())
            >>> game = Game(grid)
            >>> interface = AdvancedTextInterface(4)
            >>> interface.draw(game)
            ######
            #    #
            #    #
            #  P #
            #    #
            ######
            >>> game.get_player().get_inventory().c
            >>> game.get_player().get_inventory().add_item(Crossbow())
            >>> interface.draw(game)
            ######
            #    #
            #    #
            #  P #
            #    #
            ######
            The player is currently holding:
            Garlic(10)
            Crossbow(5)
        """
        super().draw(game)

        player = game.get_player()
        if isinstance(player, HoldingPlayer):
            inventory = player.get_inventory().get_items()
            if len(inventory) > 0:
                print(HOLDING_MESSAGE)
                for item in inventory:
                    print(item)

    def handle_action(self, game: Game, action: str) -> None:
        """
        The handle_action method for AdvancedTextInterface should extend
        the interface to be able to handle the fire action for a crossbow.
        
        If the user enters, 'F' for fire take the following actions:`
        \\begin{enumerate}
        \\item Check that the user has something to fire, i.e. a crossbow,
               if they do not hold a crossbow,
               print `You are not holding anything to fire!'
        \\item Prompt the user to enter a direction in which to fire, with
               `Direction to fire:{\\textvisiblespace}'
        \\item If the direction is not one of `W', `A', `S' or `D',
               print `Invalid firing direction entered!'
        \\item Find the first entity, starting from the player's position
               in the direction specified.
        \\item If there are no entities in that direction, or if the
               first entity is not a zombie, (zombies include tracking zombies),
               then print `No zombie in that direction!'
        \\item If the first entity in that direction is a zombie, remove the
               zombie.
        \\item Trigger the _step_ event.
        \\end{enumerate}`
        
        If the action is not fire, this method should behave the same as
        `TextInterface.handle_action`.
        
        Parameters:
            game: The game that is currently being played.
            action: An action entered by the player during the game loop.
        """
        if action == FIRE:
            player = game.get_player()
            if player is None or not isinstance(player, HoldingPlayer):
                return  # Should never happen.

            # Ensure player has a weapon that they can fire.
            if player.get_inventory().contains(CROSSBOW):
                direction = input(FIRE_PROMPT)

                # Fire the weapon in the indicated direction, if possible.
                if direction in DIRECTIONS:
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
                    else:
                        print(NO_ZOMBIE_MESSAGE)

                else:
                    print(INVALID_FIRING_MESSAGE)
            else:
                print(NO_WEAPON_MESSAGE)
            game.step()
        else:
            super().handle_action(game, action)


def advanced_game(filename: str) -> AdvancedGame:
    """
    Return an initialised advanced game corresponding to task 3
    in assignment two.
    """
    loader = AdvancedMapLoader()
    grid = loader.load(filename)
    return AdvancedGame(grid)


def main() -> None:
    """Entry point to gameplay."""
    map_file = input("Map: ")
    game = advanced_game(map_file)

    app = AdvancedTextInterface(game.get_grid().get_size())
    app.play(game)


if __name__ == "__main__":
    main()
