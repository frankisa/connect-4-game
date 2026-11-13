
from drafter import *
from dataclasses import dataclass


set_website_title("Connect 4")
set_site_information(
    author="Frank Isabelle",
    description="Play games of connect 4",
    sources="",
    planning=[],
    links=["https://docs.google.com/document/d/1m3KmFro5lHx0qWsSqDqyfB4ZVYpI805I12iPoPxlDAk/edit?tab=t.0","https://docs.google.com/document/d/1mbkXXEIKM9iSzXRj1lvDCnTXg7NAKY_fk_uIw0lJH50/edit?tab=t.0#heading=h.1xxqmmg350hh", "https://docs.google.com/document/d/1sDU9ZAk0eYZbx8MRdWUlSwY70Nmq7zE7-k3vya9a85g/edit?tab=t.0#heading=h.1xxqmmg350hh"]
)
hide_debug_information()
set_website_framed(False)

# --------------------------------------------------
# DATA CLASSES
# --------------------------------------------------

@dataclass
class Tile:
    """
    Represents one space on the Connect 4 board.
    """
    x: int
    y: int
    appearance: str


@dataclass
class State:
    """
    Stores all game information.
    """
    player1: str
    player2: str
    board: list[Tile]
    turn: int
    wins: dict[str, int]
    losses: dict[str, int]
    current_player: int
    color_choice: str
    winner: str
    game_over: bool
    first_player: str


EMPTY = "⚪"
RED = "🔴"
YELLOW = "🟡"


# --------------------------------------------------
# BOARD FUNCTIONS
# --------------------------------------------------

def make_board() -> list[Tile]:
    """
    Creates an empty 6 by 7 board.
    """
    board = []

    for y in range(6):
        for x in range(7):
            board.append(Tile(x, y, EMPTY))

    return board


def get_tile(board: list[Tile], x: int, y: int) -> Tile:
    """
    Finds a tile using its coordinates.
    """
    for tile in board:
        if tile.x == x and tile.y == y:
            return tile


def drop_piece(board: list[Tile], column: int,
               appearance: str) -> bool:
    """
    Drops a piece into the lowest available space.
    """
    for y in range(5, -1, -1):
        tile = get_tile(board, column, y)

        if tile.appearance == EMPTY:
            tile.appearance = appearance
            return True

    return False


def check_direction(board: list[Tile], x: int, y: int,
                    dx: int, dy: int,
                    appearance: str) -> bool:
    """
    Checks for four connected pieces in one direction.
    """
    count = 1

    for step in range(1, 4):
        nx = x + dx * step
        ny = y + dy * step

        if 0 <= nx < 7 and 0 <= ny < 6:
            if get_tile(board, nx, ny).appearance == appearance:
                count += 1
            else:
                break
        else:
            break

    for step in range(1, 4):
        nx = x - dx * step
        ny = y - dy * step

        if 0 <= nx < 7 and 0 <= ny < 6:
            if get_tile(board, nx, ny).appearance == appearance:
                count += 1
            else:
                break
        else:
            break

    if count >= 4:
        return True

    return False


def check_winner(board: list[Tile],
                 appearance: str) -> bool:
    """
    Checks the entire board for four connected pieces.
    """
    directions = [
        (1, 0),
        (0, 1),
        (1, 1),
        (1, -1)
    ]

    for tile in board:
        if tile.appearance == appearance:
            for dx, dy in directions:
                if check_direction(
                    board,
                    tile.x,
                    tile.y,
                    dx,
                    dy,
                    appearance
                ):
                    return True

    return False


def board_full(board: list[Tile]) -> bool:
    """
    Checks whether the board is completely full.
    """
    for tile in board:
        if tile.appearance == EMPTY:
            return False

    return True


def draw_board(board: list[Tile]) -> list[list[PageContent]]:
    """
    Creates buttons for empty spaces and displays
    emojis for occupied spaces.
    """
    display = []

    for y in range(6):
        row = []

        for x in range(7):
            tile = get_tile(board, x, y)

            if tile.appearance == EMPTY:
                row.append(
                    Button(
                        EMPTY,
                        "make_move",
                        arguments=[
                            Argument("column", x)
                        ]
                    )
                )
            else:
                row.append(tile.appearance)

        display.append(row)

    return display


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@route
def index(state: State) -> Page:
    """
    Main home page.
    """
    return Page(state, [
        Header("🎮 Connect 4"),

        "Welcome to Connect 4!",

        "Challenge a friend and connect four pieces in a row!",

        Button("Start Game", "settings"),

        Button("Instructions", "instructions"),

        Button("Leaderboard", "leaderboard"),

        Button("About", "about")
    ])


# --------------------------------------------------
# SETTINGS PAGE
# --------------------------------------------------

@route
def settings(state: State) -> Page:
    """
    Allows players to customize their game.
    """
    return Page(state, [
        Header("Game Settings"),

        "Enter Player 1's name:",

        TextBox("player1", state.player1),

        "Enter Player 2's name:",

        TextBox("player2", state.player2),

        "Choose Player 1's color:",

        SelectBox(
            "color_choice",
            ["🔴", "🟡"],
            state.color_choice
        ),

        "Who would you like to go first?",

        SelectBox(
            "first_player",
            [state.player1, state.player2],
            state.first_player
        ),

        Button("Begin Game", "new_game"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# START NEW GAME
# --------------------------------------------------

@route
def new_game(state: State) -> Page:
    """
    Resets the board and starts a new game.
    """

    if state.player1 == "":
        state.player1 = "Player 1"

    if state.player2 == "":
        state.player2 = "Player 2"

    state.board = make_board()

    state.turn = 0

    state.winner = ""

    state.game_over = False

    # Add players to the records if necessary.
    if state.player1 not in state.wins:
        state.wins[state.player1] = 0
        state.losses[state.player1] = 0

    if state.player2 not in state.wins:
        state.wins[state.player2] = 0
        state.losses[state.player2] = 0

    # Decide who goes first.
    if state.first_player == state.player1:
        state.current_player = 1
    else:
        state.current_player = 2

    return play_game(state)


# --------------------------------------------------
# MAIN GAME PAGE
# --------------------------------------------------

@route
def play_game(state: State) -> Page:
    """
    Displays the board and current player's turn.
    """

    if state.current_player == 1:
        player = state.player1
    else:
        player = state.player2

    if state.color_choice == RED:
        player1_color = RED
        player2_color = YELLOW
    else:
        player1_color = YELLOW
        player2_color = RED

    display = draw_board(state.board)

    return Page(state, [
        Header("Connect 4"),

        "🔴 Player 1: " + state.player1
        if player1_color == RED
        else "🟡 Player 1: " + state.player1,

        "🔴 Player 2: " + state.player2
        if player2_color == RED
        else "🟡 Player 2: " + state.player2,

        Header("Current Turn: " + player),

        "Choose a column to drop your piece!",

        Table(display),

        "Total Turns: " + str(state.turn),

        Button("Instructions", "instructions"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# MAKE A MOVE
# --------------------------------------------------

@route
def make_move(state: State, column: int) -> Page:
    """
    Handles a player's move.
    """

    if state.game_over:
        return final_record(state)

    # Determine the current player's color.
    if state.current_player == 1:

        if state.color_choice == RED:
            piece = RED
        else:
            piece = YELLOW

    else:

        if state.color_choice == RED:
            piece = YELLOW
        else:
            piece = RED

    # Attempt to place the piece.
    successful_move = drop_piece(
        state.board,
        column,
        piece
    )

    if not successful_move:
        return play_game(state)

    state.turn += 1

    # Check whether the player won.
    if check_winner(state.board, piece):

        if state.current_player == 1:
            state.winner = state.player1

            state.wins[state.player1] += 1

            state.losses[state.player2] += 1

        else:
            state.winner = state.player2

            state.wins[state.player2] += 1

            state.losses[state.player1] += 1

        state.game_over = True

        return final_record(state)

    # Check whether the board is full.
    if board_full(state.board):

        state.winner = "Draw"

        state.game_over = True

        return final_record(state)

    # Switch to the next player.
    if state.current_player == 1:
        state.current_player = 2
    else:
        state.current_player = 1

    return play_game(state)


# --------------------------------------------------
# INSTRUCTIONS PAGE
# --------------------------------------------------

@route
def instructions(state: State) -> Page:
    """
    Explains how to play Connect 4.
    """
    return Page(state, [
        Header("How to Play"),

        "1. Two players take turns.",

        "2. Choose a column by pressing a button.",

        "3. Your piece falls to the lowest empty space.",

        "4. Connect four pieces horizontally, vertically, or diagonally.",

        "5. The first player to connect four wins!",

        "If the board fills without a winner, the game is a draw.",

        Button("Start Playing", "settings"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# FINAL RECORD PAGE
# --------------------------------------------------

@route
def final_record(state: State) -> Page:
    """
    Displays the winner and final board.
    """

    return Page(state, [
        Header("🏆 Game Over!"),

        "Winner: " + state.winner,

        "Total Turns: " + str(state.turn),

        "Final Board:",

        Table(draw_board(state.board)),

        Button("Play Again", "play_again"),

        Button("Final Records", "records"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# PLAY AGAIN PAGE
# --------------------------------------------------

@route
def play_again(state: State) -> Page:
    """
    Allows players to start another game.
    """
    return Page(state, [
        Header("Play Again?"),

        "Would you like another round?",

        Button("Yes! Play Again", "settings"),

        Button("No, Show Records", "records"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# RECORDS PAGE
# --------------------------------------------------

@route
def records(state: State) -> Page:
    """
    Displays player wins and losses.
    """
    return Page(state, [
        Header("Final Records"),

        state.player1 + " Wins: "
        + str(state.wins[state.player1]),

        state.player1 + " Losses: "
        + str(state.losses[state.player1]),

        state.player2 + " Wins: "
        + str(state.wins[state.player2]),

        state.player2 + " Losses: "
        + str(state.losses[state.player2]),

        Button("Play Again", "play_again"),

        Button("Leaderboard", "leaderboard"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# LEADERBOARD PAGE
# --------------------------------------------------

@route
def leaderboard(state: State) -> Page:
    """
    Displays the current leaderboard.
    """
    return Page(state, [
        Header("🏆 Leaderboard"),

        state.player1 + ": "
        + str(state.wins[state.player1]) + " wins",

        state.player2 + ": "
        + str(state.wins[state.player2]) + " wins",

        Button("Play Game", "settings"),

        Button("Home", "index")
    ])


# --------------------------------------------------
# ABOUT PAGE
# --------------------------------------------------

@route
def about(state: State) -> Page:
    """
    Information about Connect 4.
    """
    return Page(state, [
        Header("About Connect 4"),

        "Connect 4 is a two-player strategy game.",

        "Players take turns dropping colored pieces into a grid.",

        "The goal is to connect four pieces in a row.",

        "You can win horizontally, vertically, or diagonally.",

        "Good luck and have fun!",

        Button("Home", "index")
    ])


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

start_server(
    State(
        "Player 1",
        "Player 2",
        make_board(),
        0,
        {
            "Player 1": 0,
            "Player 2": 0
        },
        {
            "Player 1": 0,
            "Player 2": 0
        },
        1,
        RED,
        "",
        False,
        "Player 1"
    )
)

