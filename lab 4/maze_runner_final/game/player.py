import pygame
from game.maze import CELL

SPEED = 3


class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c * CELL + CELL // 2
        y = r * CELL + CELL // 2
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        # Move one axis at a time so a blocked direction does not
        # prevent movement in the other direction.
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols, dx, 0):
            self.rect = new_rect

        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols, 0, dy):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols, dx=0, dy=0):
        """Return True when rect crosses a maze boundary or wall."""
        # The player is kept inside the outer boundary of the maze.
        if rect.left < 0 or rect.right > cols * CELL:
            return True
        if rect.top < 0 or rect.bottom > rows * CELL:
            return True

        # Determine the cell containing the player's centre before the move.
        center_x = self.rect.centerx
        center_y = self.rect.centery
        current_r = center_y // CELL
        current_c = center_x // CELL

        if dx > 0:
            # Moving right: the player's right edge may cross the east wall.
            boundary_x = (current_c + 1) * CELL
            if rect.right > boundary_x and walls[current_r][current_c][2]:
                return True

        elif dx < 0:
            # Moving left: the player's left edge may cross the west wall.
            boundary_x = current_c * CELL
            if rect.left < boundary_x and walls[current_r][current_c][3]:
                return True

        elif dy > 0:
            # Moving down: the player's bottom edge may cross the south wall.
            boundary_y = (current_r + 1) * CELL
            if rect.bottom > boundary_y and walls[current_r][current_c][1]:
                return True

        elif dy < 0:
            # Moving up: the player's top edge may cross the north wall.
            boundary_y = current_r * CELL
            if rect.top < boundary_y and walls[current_r][current_c][0]:
                return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
