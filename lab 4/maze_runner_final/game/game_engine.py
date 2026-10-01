import json
import os
import time

import pygame

from game.maze import CELL, generate_maze, shortest_path
from game.player import Player

FPS = 60
BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
HINT_COLOR = (255, 215, 70)
FOG_COLOR = (0, 0, 0, 220)
FOG_RADIUS_CELLS = 3

DIFFICULTIES = {
    "Easy": (10, 8),
    "Medium": (15, 13),
    "Hard": (20, 18),
}

LEADERBOARD_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "leaderboard.json"
)


class GameEngine:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)

        # Use the medium size for the initial menu window. The window is
        # resized to the selected maze dimensions when the game starts.
        self.cols, self.rows = DIFFICULTIES["Medium"]
        self.screen = pygame.display.set_mode(
            (self.cols * CELL, self.rows * CELL + 60)
        )
        pygame.display.set_caption("Maze Runner")

        self.leaderboard = self.load_leaderboard()
        self.walls = None
        self.player = None
        self.exit_rect = None
        self.start_time = 0.0
        self.elapsed = 0.0
        self.won = False
        self.show_hint = False

    def load_leaderboard(self):
        """Load and return the five fastest valid completion times."""
        if not os.path.exists(LEADERBOARD_FILE):
            return []

        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                return []

            times = []
            for value in data:
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    value = float(value)
                    if value >= 0:
                        times.append(value)

            return sorted(times)[:5]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def save_leaderboard(self):
        """Save the current top five completion times to leaderboard.json."""
        try:
            with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
                json.dump(self.leaderboard, file, indent=2)
        except OSError:
            # A read-only directory should not crash the game.
            pass

    def record_completion_time(self):
        """Add the completed run and retain only the five fastest times."""
        self.leaderboard.append(round(self.elapsed, 1))
        self.leaderboard.sort()
        self.leaderboard = self.leaderboard[:5]
        self.save_leaderboard()

    def reset(self):
        """Generate a fresh maze using the currently selected difficulty."""
        self.walls = generate_maze(self.cols, self.rows)
        self.player = Player(0, 0)
        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 5,
            (self.rows - 1) * CELL + 5,
            CELL - 10,
            CELL - 10,
        )
        self.start_time = time.time()
        self.elapsed = 0.0
        self.won = False
        self.show_hint = False

    def start_difficulty(self, cols, rows):
        """Apply a difficulty size, resize the window, and start a maze."""
        self.cols, self.rows = cols, rows
        self.screen = pygame.display.set_mode(
            (self.cols * CELL, self.rows * CELL + 60)
        )
        self.reset()

    def select_difficulty(self):
        """Show the required Easy/Medium/Hard difficulty selection screen."""
        menu_width, menu_height = 520, 500
        self.screen = pygame.display.set_mode((menu_width, menu_height))
        pygame.display.set_caption("Maze Runner - Select Difficulty")

        title_font = pygame.font.SysFont("monospace", 32, bold=True)
        button_font = pygame.font.SysFont("monospace", 24, bold=True)
        detail_font = pygame.font.SysFont("monospace", 18)

        options = [
            ("Easy", DIFFICULTIES["Easy"]),
            ("Medium", DIFFICULTIES["Medium"]),
            ("Hard", DIFFICULTIES["Hard"]),
        ]

        while True:
            self.screen.fill((25, 25, 25))
            title = title_font.render("Select Difficulty", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(menu_width // 2, 70)))

            buttons = []
            button_width, button_height = 300, 85
            start_y = 120
            gap = 20

            for index, (name, (cols, rows)) in enumerate(options):
                rect = pygame.Rect(
                    (menu_width - button_width) // 2,
                    start_y + index * (button_height + gap),
                    button_width,
                    button_height,
                )
                buttons.append((cols, rows, rect))

                pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=8)
                pygame.draw.rect(
                    self.screen, (180, 180, 180), rect, 2, border_radius=8
                )

                label = button_font.render(name, True, (255, 255, 255))
                detail = detail_font.render(
                    f"{cols} x {rows}", True, (210, 210, 210)
                )
                self.screen.blit(
                    label, label.get_rect(center=(rect.centerx, rect.centery - 14))
                )
                self.screen.blit(
                    detail, detail.get_rect(center=(rect.centerx, rect.centery + 20))
                )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for cols, rows, rect in buttons:
                        if rect.collidepoint(event.pos):
                            return cols, rows

            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_h and not self.won:
                    self.show_hint = not self.show_hint

        return True

    def update(self):
        if self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, self.rows, self.cols)
        self.elapsed = time.time() - self.start_time

        if self.player.rect.colliderect(self.exit_rect):
            self.elapsed = time.time() - self.start_time
            self.won = True
            self.record_completion_time()

    def get_hint_path(self):
        """Find the shortest BFS path from the player's current cell to exit."""
        player_row = self.player.rect.centery // CELL
        player_col = self.player.rect.centerx // CELL
        goal = (self.rows - 1, self.cols - 1)
        return shortest_path(self.walls, (player_row, player_col), goal)

    def draw_hint(self):
        """Draw the BFS path as a translucent cell highlight."""
        path = self.get_hint_path()
        if not path:
            return

        hint_surface = pygame.Surface(
            (self.cols * CELL, self.rows * CELL), pygame.SRCALPHA
        )
        for row, col in path:
            rect = pygame.Rect(
                col * CELL + 7,
                row * CELL + 7,
                CELL - 14,
                CELL - 14,
            )
            pygame.draw.rect(
                hint_surface, (*HINT_COLOR, 110), rect, border_radius=6
            )
        self.screen.blit(hint_surface, (0, 0))

    def draw_fog(self):
        """Hide everything outside a radius of exactly three cells."""
        maze_width = self.cols * CELL
        maze_height = self.rows * CELL
        fog = pygame.Surface((maze_width, maze_height), pygame.SRCALPHA)
        fog.fill(FOG_COLOR)

        radius = FOG_RADIUS_CELLS * CELL
        reveal_mask = pygame.Surface((maze_width, maze_height), pygame.SRCALPHA)
        pygame.draw.circle(
            reveal_mask,
            (0, 0, 0, 255),
            self.player.rect.center,
            radius,
        )
        fog.blit(
            reveal_mask,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_SUB,
        )
        self.screen.blit(fog, (0, 0))

    def draw_maze(self):
        wall_width = 3
        for row in range(self.rows):
            for col in range(self.cols):
                x, y = col * CELL, row * CELL
                walls = self.walls[row][col]

                if walls[0]:
                    pygame.draw.line(
                        self.screen, WALL_COLOR, (x, y), (x + CELL, y), wall_width
                    )
                if walls[1]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_width,
                    )
                if walls[2]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_width,
                    )
                if walls[3]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_width,
                    )

    def draw_leaderboard(self):
        title = self.font.render("TOP 5 TIMES", True, HINT_COLOR)
        self.screen.blit(
            title,
            (self.screen.get_width() // 2 - title.get_width() // 2, 205),
        )

        if not self.leaderboard:
            empty = self.font.render("No completed runs yet", True, (220, 220, 220))
            self.screen.blit(
                empty,
                (self.screen.get_width() // 2 - empty.get_width() // 2, 245),
            )
            return

        for index, completion_time in enumerate(self.leaderboard, start=1):
            entry = self.font.render(
                f"{index}. {completion_time:.1f}s", True, (230, 230, 230)
            )
            self.screen.blit(
                entry,
                (self.screen.get_width() // 2 - entry.get_width() // 2, 240 + index * 30),
            )

    def draw(self):
        self.screen.fill(BG)
        self.draw_maze()

        if self.show_hint:
            self.draw_hint()

        pygame.draw.rect(self.screen, EXIT_COLOR, self.exit_rect, border_radius=4)
        exit_label = self.font.render("EXIT", True, (20, 80, 20))
        self.screen.blit(
            exit_label,
            (self.exit_rect.x + 2, self.exit_rect.y + 4),
        )

        # Hide the maze, hint, and goal outside the player's visible radius.
        self.draw_fog()
        self.player.draw(self.screen)

        hud_y = self.rows * CELL
        hud = pygame.Rect(0, hud_y, self.cols * CELL, 60)
        pygame.draw.rect(self.screen, (30, 30, 50), hud)
        time_surface = self.font.render(
            f"Time: {self.elapsed:.1f}s   H = Hint   R = New Maze",
            True,
            (200, 200, 200),
        )
        self.screen.blit(time_surface, (10, hud_y + 18))

        if self.won:
            overlay = pygame.Surface(
                (self.cols * CELL, self.rows * CELL), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!", True, (80, 240, 80)
            )
            sub = self.font.render(
                "Press R for a new maze", True, (200, 200, 200)
            )
            self.screen.blit(
                msg,
                (self.screen.get_width() // 2 - msg.get_width() // 2, 90),
            )
            self.screen.blit(
                sub,
                (self.screen.get_width() // 2 - sub.get_width() // 2, 140),
            )
            self.draw_leaderboard()

        pygame.display.flip()

    def run(self):
        selected = self.select_difficulty()
        if selected is None:
            pygame.quit()
            return

        self.start_difficulty(*selected)

        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
