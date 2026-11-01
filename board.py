import os
import pygame



WIDTH = 1000
HEIGHT = 720

ROWS = 11
COLS = 15
CELL = 40

BOARD_X = (WIDTH - COLS * CELL) // 2
BOARD_Y = 190



BACKGROUND = (12, 18, 34)
PANEL = (22, 31, 52)
PANEL_LIGHT = (31, 43, 68)

WALL_COLOR = (43, 57, 83)
PATH_COLOR = (19, 28, 46)
GRID_COLOR = (30, 42, 64)

WHITE = (238, 244, 255)
MUTED = (150, 166, 192)

CYAN = (70, 220, 235)
CYAN_DARK = (28, 120, 145)

RED = (255, 91, 112)
RED_DARK = (145, 45, 67)

GREEN = (100, 235, 170)
YELLOW = (255, 207, 92)


title_font = pygame.font.SysFont("arial", 42, bold=True)
heading_font = pygame.font.SysFont("arial", 27, bold=True)
body_font = pygame.font.SysFont("arial", 19)
small_font = pygame.font.SysFont("arial", 15)
button_font = pygame.font.SysFont("arial", 20, bold=True)



SCORE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "leaderboard.txt"
)



def draw_text(surface, text, font, color, x, y, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(image, rect)
    return rect


def draw_background(surface):
    surface.fill(BACKGROUND)

    for y in range(0, HEIGHT, 48):
        pygame.draw.line(
            surface,
            (16, 25, 43),
            (0, y),
            (WIDTH, y),
            1
        )


def draw_panel(surface, rect, color=PANEL, radius=18):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )

    pygame.draw.rect(
        surface,
        (47, 65, 94),
        rect,
        width=1,
        border_radius=radius
    )


def draw_button(surface, rect, text, color=CYAN_DARK):
    mouse_pos = pygame.mouse.get_pos()
    button_color = color

    if rect.collidepoint(mouse_pos):
        button_color = (
            min(color[0] + 20, 255),
            min(color[1] + 20, 255),
            min(color[2] + 20, 255)
        )

    pygame.draw.rect(
        surface,
        button_color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        surface,
        (100, 220, 235),
        rect,
        width=1,
        border_radius=12
    )

    draw_text(
        surface,
        text,
        button_font,
        WHITE,
        rect.centerx,
        rect.centery,
        center=True
    )



def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []

    scores = []

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    scores.append(int(line.strip()))
                except ValueError:
                    continue
    except OSError:
        return []

    return sorted(scores, reverse=True)[:5]


def save_score(score):


    scores = load_scores()
    scores.append(int(score))
    scores.sort(reverse=True)
    scores = scores[:5]

    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as file:
            for saved_score in scores:
                file.write(f"{saved_score}\n")
    except OSError:
        print("Could not save the leaderboard.")


def draw_leaderboard(surface, x, y):
    draw_text(
        surface,
        "TOP SCORES",
        heading_font,
        WHITE,
        x,
        y
    )

    scores = load_scores()

    if not scores:
        draw_text(
            surface,
            "Win a game to record your first score.",
            small_font,
            MUTED,
            x,
            y + 42
        )
        return

    for index, saved_score in enumerate(scores):
        draw_text(
            surface,
            f"{index + 1}.",
            body_font,
            CYAN,
            x,
            y + 42 + index * 31
        )

        draw_text(
            surface,
            f"{saved_score} points",
            body_font,
            WHITE,
            x + 35,
            y + 42 + index * 31
        )



def draw_menu(surface):
    draw_background(surface)

    draw_text(
        surface,
        "ESCAPE THE ENEMY",
        title_font,
        WHITE,
        WIDTH // 2,
        100,
        center=True
    )

    draw_text(
        surface,
        "Think fast. Find the exit. Don't get caught.",
        body_font,
        MUTED,
        WIDTH // 2,
        145,
        center=True
    )

    left_panel = pygame.Rect(105, 210, 460, 370)
    right_panel = pygame.Rect(595, 210, 300, 370)

    draw_panel(surface, left_panel)
    draw_panel(surface, right_panel)

    draw_text(
        surface,
        "YOUR MISSION",
        heading_font,
        CYAN,
        140,
        245
    )

    instructions = [
        "1. Escape through the maze.",
        "2. Avoid the red enemy.",
        "3. Reach the green exit to win.",
        "",
        "CONTROLS",
        "Arrow keys or WASD: Move",
        "Hold a key: Keep moving",
        "R: Restart during a game",
        "ESC: Return to menu"
    ]

    for index, instruction in enumerate(instructions):
        color = YELLOW if instruction == "CONTROLS" else WHITE

        draw_text(
            surface,
            instruction,
            body_font,
            color,
            145,
            300 + index * 30
        )

    draw_leaderboard(surface, 625, 250)

    start_button = pygame.Rect(320, 615, 180, 52)
    quit_button = pygame.Rect(520, 615, 160, 52)

    draw_button(surface, start_button, "START GAME")
    draw_button(surface, quit_button, "QUIT", RED_DARK)

    draw_text(
        surface,
        "AI: Greedy Best-First Search",
        small_font,
        MUTED,
        WIDTH // 2,
        690,
        center=True
    )

    return {
        "start": start_button,
        "quit": quit_button
    }



def draw_maze(surface, maze, exit_pos, path=None):
    # Outer GAME frame
    board_rect = pygame.Rect(
        BOARD_X - 7,
        BOARD_Y - 7,
        COLS * CELL + 14,
        ROWS * CELL + 14
    )

    draw_panel(surface, board_rect, color=(10, 16, 30), radius=12)

    # maze cell
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(
                BOARD_X + x * CELL,
                BOARD_Y + y * CELL,
                CELL,
                CELL
            )

            if cell == "#":
                pygame.draw.rect(
                    surface,
                    WALL_COLOR,
                    rect,
                    border_radius=4
                )
            else:
                pygame.draw.rect(
                    surface,
                    PATH_COLOR,
                    rect
                )

                pygame.draw.rect(
                    surface,
                    GRID_COLOR,
                    rect,
                    width=1
                )

    # Mark exit
    ex, ey = exit_pos
    exit_rect = pygame.Rect(
        BOARD_X + ex * CELL + 5,
        BOARD_Y + ey * CELL + 5,
        CELL - 10,
        CELL - 10
    )

    pygame.draw.rect(
        surface,
        GREEN,
        exit_rect,
        border_radius=8
    )

    draw_text(
        surface,
        "E",
        heading_font,
        BACKGROUND,
        exit_rect.centerx,
        exit_rect.centery,
        center=True
    )



def draw_character(surface, position, color, label):
    x, y = position

    center_x = BOARD_X + x * CELL + CELL // 2
    center_y = BOARD_Y + y * CELL + CELL // 2

    # Soft outer ring.
    pygame.draw.circle(
        surface,
        color,
        (center_x, center_y),
        15
    )

    pygame.draw.circle(
        surface,
        WHITE,
        (center_x, center_y),
        15,
        width=2
    )

    draw_text(
        surface,
        label,
        small_font,
        BACKGROUND,
        center_x,
        center_y,
        center=True
    )



def draw_game(
        surface,
        maze,
        player_pos,
        enemy_pos,
        exit_pos,
        score,
        path=None
):
    draw_background(surface)

    draw_text(
        surface,
        "ESCAPE THE ENEMY",
        title_font,
        WHITE,
        WIDTH // 2,
        48,
        center=True
    )

    draw_text(
        surface,
        "Find the exit before the enemy reaches you.",
        small_font,
        MUTED,
        WIDTH // 2,
        88,
        center=True
    )

    # Score
    score_panel = pygame.Rect(175, 112, 190, 53)
    draw_panel(surface, score_panel)

    draw_text(
        surface,
        f"SCORE  {score}",
        heading_font,
        CYAN,
        score_panel.centerx,
        score_panel.centery,
        center=True
    )

    # AI status
    ai_panel = pygame.Rect(635, 112, 190, 53)
    draw_panel(surface, ai_panel)

    draw_text(
        surface,
        "GBFS ACTIVE",
        body_font,
        RED,
        ai_panel.centerx,
        ai_panel.centery,
        center=True
    )

    draw_maze(surface, maze, exit_pos)
    draw_character(surface, player_pos, CYAN, "P")
    draw_character(surface, enemy_pos, RED, "X")

    draw_text(
        surface,
        "P  YOU",
        small_font,
        CYAN,
        205,
        655
    )

    draw_text(
        surface,
        "X  ENEMY",
        small_font,
        RED,
        335,
        655
    )

    draw_text(
        surface,
        "E  EXIT",
        small_font,
        GREEN,
        490,
        655
    )

    draw_text(
        surface,
        "Hold WASD / arrow keys to move",
        small_font,
        MUTED,
        WIDTH // 2,
        690,
        center=True
    )



def draw_end(surface, won, score):
    draw_background(surface)

    panel = pygame.Rect(245, 155, 510, 400)
    draw_panel(surface, panel)

    if won:
        heading = "YOU ESCAPED!"
        heading_color = GREEN
        message = "Great job. You found the exit."
    else:
        heading = "GAME OVER"
        heading_color = RED
        message = "The enemy caught you. Try again!"

    draw_text(
        surface,
        heading,
        title_font,
        heading_color,
        WIDTH // 2,
        225,
        center=True
    )

    draw_text(
        surface,
        message,
        body_font,
        WHITE,
        WIDTH // 2,
        285,
        center=True
    )

    draw_text(
        surface,
        f"Final score: {score}",
        heading_font,
        CYAN,
        WIDTH // 2,
        340,
        center=True
    )

    if won:
        draw_text(
            surface,
            "Your score has been saved.",
            small_font,
            MUTED,
            WIDTH // 2,
            385,
            center=True
        )

    restart_button = pygame.Rect(310, 440, 175, 52)
    menu_button = pygame.Rect(515, 440, 175, 52)

    draw_button(surface, restart_button, "PLAY AGAIN")
    draw_button(surface, menu_button, "MAIN MENU")

    return {
        "restart": restart_button,
        "menu": menu_button
    }
