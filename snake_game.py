import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
RED = (255, 50, 50)
BLUE = (30, 144, 255)
DARK_GREEN = (0, 100, 0)
GRAY = (40, 40, 40)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        self.grow_pending = 2
        self.is_alive = True

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0]*-1, point[1]*-1) == self.direction:
            return
        self.direction = point

    def move(self):
        if not self.is_alive:
            return

        head = self.get_head_position()
        x, y = self.direction
        new_pos = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        if new_pos in self.positions[1:]:
            self.is_alive = False
            return

        self.positions.insert(0, new_pos)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            rect = pygame.Rect(p[0]*GRID_SIZE, p[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)

            if i == 0:
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)
            else:
                color = GREEN if i % 2 == 0 else DARK_GREEN
                pygame.draw.rect(surface, color, rect)

    def grow(self):
        self.grow_pending += 1
        self.score += 10
        self.length += 1



class Food:
    def __init__(self):
        self.position = (0, 0)

    def randomize_position(self, snake_positions, barrier_positions):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1),
                   random.randint(0, GRID_HEIGHT-1))
            if pos not in snake_positions and pos not in barrier_positions:
                self.position = pos
                break

    def draw(self, surface):
        rect = pygame.Rect(self.position[0]*GRID_SIZE,
                           self.position[1]*GRID_SIZE,
                           GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)



class Barrier:
    def __init__(self, count=12):
        self.count = count
        self.positions = []

    def generate(self, snake_positions, food_position):
        self.positions = []
        while len(self.positions) < self.count:
            pos = (random.randint(0, GRID_WIDTH-1),
                   random.randint(0, GRID_HEIGHT-1))
            if pos not in snake_positions and pos != food_position:
                if pos not in self.positions:
                    self.positions.append(pos)

    def draw(self, surface):
        for pos in self.positions:
            rect = pygame.Rect(pos[0]*GRID_SIZE, pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, BLUE, rect)



class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake with Barriers")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.snake = Snake()
        self.barrier = Barrier()
        self.food = Food()

        self.barrier.generate(self.snake.positions, (0, 0))
        self.food.randomize_position(self.snake.positions, self.barrier.positions)

        self.game_over = False
        self.speed = FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.restart_game()

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if not self.snake.is_alive:
                    return

                if event.key == pygame.K_w:
                    self.snake.turn(UP)
                elif event.key == pygame.K_s:
                    self.snake.turn(DOWN)
                elif event.key == pygame.K_a:
                    self.snake.turn(LEFT)
                elif event.key == pygame.K_d:
                    self.snake.turn(RIGHT)

    def update(self):
        if not self.snake.is_alive:
            self.game_over = True
            return

        self.snake.move()

        # barrier collision
        if self.snake.get_head_position() in self.barrier.positions:
            self.snake.is_alive = False
            self.game_over = True
            return

        # food collision
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.randomize_position(self.snake.positions, self.barrier.positions)

            if self.snake.score % 30 == 0:
                self.speed += 1

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        self.barrier.draw(self.screen)
        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        # score
        score_text = self.font.render(f"Score: {self.snake.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # instructions
        controls = [
            "Controls:",
            "W A S D : Move",
            "R : Restart",
            "ESC : Quit"
        ]

        for i, text in enumerate(controls):
            t = self.small_font.render(text, True, WHITE)
            self.screen.blit(t, (10, HEIGHT - 100 + i * 25))

        # game over
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text,
                (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))

            final_score = self.font.render(f"Score: {self.snake.score}", True, WHITE)
            self.screen.blit(final_score,
                (WIDTH//2 - final_score.get_width()//2, HEIGHT//2))

            restart_text = self.font.render("Press R to Restart", True, GREEN)
            self.screen.blit(restart_text,
                (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    def restart_game(self):
        self.snake.reset()
        self.barrier.generate(self.snake.positions, (0, 0))
        self.food.randomize_position(self.snake.positions, self.barrier.positions)
        self.game_over = False
        self.speed = FPS

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.speed)


if __name__ == "__main__":
    Game().run()