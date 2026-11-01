import sys    # for clear exit layout
import random    # for random board generator
import heapq   # priority q for gbfs path finding
import pygame     #for gui


pygame.init()

import board


ROWS = 11
COLS = 15

PLAYER_MOVE_DELAY = 125
ENEMY_MOVE_DELAY = 650

WALL = "#"
PATH = "."

START_PLAYER = (1, 1)

screen = pygame.display.set_mode((board.WIDTH, board.HEIGHT))
pygame.display.set_caption("Escape the Enemy")

clock = pygame.time.Clock()



# dfs-> 1 main solvable, open wall alternative routes, maze create
def generate_maze():
    maze = [[WALL for _ in range(COLS)] for _ in range(ROWS)]

    start = (1, 1)
    maze[start[1]][start[0]] = PATH
    stack = [start]

    while stack:
        x, y = stack[-1]
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        found_next = False

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if (1 <= nx < COLS - 1 and
                    1 <= ny < ROWS - 1 and
                    maze[ny][nx] == WALL):

                maze[y + dy // 2][x + dx // 2] = PATH
                maze[ny][nx] = PATH
                stack.append((nx, ny))
                found_next = True
                break

        if not found_next:
            stack.pop()

    possible_walls = []  # to create dif ways to reach goal

    for y in range(1, ROWS - 1):
        for x in range(1, COLS - 1):
            if maze[y][x] != WALL:
                continue

            horizontal = (
                    maze[y][x - 1] == PATH and
                    maze[y][x + 1] == PATH
            )

            vertical = (
                    maze[y - 1][x] == PATH and
                    maze[y + 1][x] == PATH
            )

            if horizontal or vertical:
                possible_walls.append((x, y))    # candidate for removal.

    random.shuffle(possible_walls)

    extra_openings = min(12, len(possible_walls))

    for x, y in possible_walls[:extra_openings]:
        maze[y][x] = PATH

    return ["".join(row) for row in maze]

# adjacent choose , wall check , only the possible paths are returned
def get_neighbors(position):

    x, y = position
    neighbors = []

    directions = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0)
    ]

    for dx, dy in directions:
        nx = x + dx
        ny = y + dy

        if (
                0 <= nx < COLS
                and 0 <= ny < ROWS
                and MAZE[ny][nx] != WALL
        ):
            neighbors.append((nx, ny))

    return neighbors



#bfs -> start to all other cell , ending & enemy position fix help
def get_distances(start):

    distances = {start: 0}
    queue = [start]
    index = 0

    while index < len(queue):
        current = queue[index]
        index += 1

        for neighbor in get_neighbors(current):
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances



# GBFS -->
def greedy_best_first_search(start, goal):

    if start == goal:
        return [start]

    def heuristic(position):
        return (
                abs(position[0] - goal[0])
                + abs(position[1] - goal[1])
        )

    frontier = []    # priority q
    heapq.heappush(
        frontier,
        (heuristic(start), random.random(), start)
    )

    came_from = {start: None}    # path track

    while frontier:
        _, _, current = heapq.heappop(frontier)
        # lowest heuristic-> pop cell

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            if neighbor not in came_from:
                came_from[neighbor] = current

                heapq.heappush(
                    frontier,
                    (
                        heuristic(neighbor),
                        random.random(),
                        neighbor
                    )
                )

    if goal not in came_from:
        return []


    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path



MAZE = generate_maze()

player_pos = START_PLAYER
enemy_pos = (COLS - 2, ROWS - 2)
exit_pos = (COLS - 2, 1)

score = 100
game_state = "menu"

last_player_move = 0
last_enemy_move = 0

saved_result = False


def reset_game():
    global MAZE, player_pos, enemy_pos, exit_pos
    global score, game_state
    global last_player_move, last_enemy_move, saved_result

    old_player_pos = player_pos
    old_exit_pos = exit_pos

    #  reset maze
    MAZE = generate_maze()

    open_cells = [
        (x, y)
        for y in range(ROWS)
        for x in range(COLS)
        if MAZE[y][x] == PATH
    ]


    start_options = [
        position for position in open_cells
        if position != old_player_pos
    ]

    player_pos = random.choice(start_options)

    # Find distances from the new player position
    distances = get_distances(player_pos)

    # Choose a reachable exit far away from the player
    exit_options = [
        position for position, distance in distances.items()
        if distance >= 10 and position != old_exit_pos
    ]

    if not exit_options:
        exit_options = [
            position for position in distances
            if position != player_pos
        ]

    exit_pos = random.choice(exit_options)

    # Prefer an enemy position away from both player and exit
    enemy_options = [
        position for position in open_cells
        if position != player_pos
           and position != exit_pos
           and distances.get(position, 0) >= 6
    ]

    if enemy_options:
        enemy_pos = random.choice(enemy_options)
    else:
        enemy_pos = random.choice([
            position for position in open_cells
            if position != player_pos and position != exit_pos
        ])

    # Reset game values
    score = 100
    game_state = "playing"

    now = pygame.time.get_ticks()
    last_player_move = now - PLAYER_MOVE_DELAY
    last_enemy_move = now
    saved_result = False


def finish_game(result):

    global game_state, saved_result

    game_state = result

    if not saved_result:
        if result == "won":
            board.save_score(score)

        saved_result = True



def move_player(dx, dy):

    global player_pos, score

    if game_state != "playing":
        return

    nx = player_pos[0] + dx
    ny = player_pos[1] + dy

    if not (0 <= nx < COLS and 0 <= ny < ROWS):
        return

    if MAZE[ny][nx] == WALL:
        return

    player_pos = (nx, ny)
    score = max(0, score - 1)

    # Check whether the enemy caught the player.
    if player_pos == enemy_pos:
        finish_game("lost")
        return

    # Check whether the player reached the exit.
    if player_pos == exit_pos:
        finish_game("won")



def move_enemy():
    """Move the enemy using Greedy Best-First Search."""

    global enemy_pos

    if game_state != "playing":
        return

    path = greedy_best_first_search(enemy_pos, player_pos)

    # Move one cell along the path toward the player.
    if len(path) > 1:
        enemy_pos = path[1]

    # Check whether the enemy caught the player.
    if enemy_pos == player_pos:
        finish_game("lost")



running = True

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()

    # Handle mouse and keyboard events.
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if game_state == "playing":
                    game_state = "menu"
                elif game_state in ("won", "lost"):
                    game_state = "menu"
                else:
                    running = False

            elif event.key == pygame.K_RETURN:
                if game_state == "menu":
                    reset_game()

            elif event.key == pygame.K_r:
                if game_state in ("playing", "won", "lost"):
                    reset_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                mouse_pos = event.pos

                if game_state == "menu":
                    buttons = board.draw_menu(screen)

                    if buttons["start"].collidepoint(mouse_pos):
                        reset_game()

                    elif buttons["quit"].collidepoint(mouse_pos):
                        running = False

                elif game_state in ("won", "lost"):
                    buttons = board.draw_end(
                        screen,
                        game_state == "won",
                        score
                    )

                    if buttons["restart"].collidepoint(mouse_pos):
                        reset_game()

                    elif buttons["menu"].collidepoint(mouse_pos):
                        game_state = "menu"

    # Continuous movement: holding a key repeats movement at a fixed rate.
    if game_state == "playing" and now - last_player_move >= PLAYER_MOVE_DELAY:
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1

        if dx != 0 or dy != 0:
            move_player(dx, dy)
            last_player_move = now

    # Move the enemy at a slower interval.
    if (
            game_state == "playing"
            and now - last_enemy_move >= ENEMY_MOVE_DELAY
    ):
        move_enemy()
        last_enemy_move = now

    # Draw the current screen.
    if game_state == "menu":
        board.draw_menu(screen)

    elif game_state == "playing":
        path = greedy_best_first_search(enemy_pos, player_pos)

        board.draw_game(
            screen,
            MAZE,
            player_pos,
            enemy_pos,
            exit_pos,
            score,
            path
        )

    elif game_state in ("won", "lost"):
        board.draw_end(
            screen,
            game_state == "won",
            score
        )

    pygame.display.flip()


pygame.quit()
sys.exit()
