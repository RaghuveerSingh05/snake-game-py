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

# Directions
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
        # Prevent turning directly back on itself
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        self.direction = point
    
    def move(self):
        if not self.is_alive:
            return
            
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        # Check collision with self
        if new_position in self.positions[1:]:
            self.is_alive = False
            return
            
        self.positions.insert(0, new_position)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
    
    def draw(self, surface):
        for i, p in enumerate(self.positions):
            # snake body
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            
            # Head is different color
            if i == 0:
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)
                
                
                eye_size = GRID_SIZE // 5
                if self.direction == RIGHT:
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + GRID_SIZE - eye_size, p[1] * GRID_SIZE + eye_size*2), eye_size)
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + GRID_SIZE - eye_size, p[1] * GRID_SIZE + GRID_SIZE - eye_size*2), eye_size)
                elif self.direction == LEFT:
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + eye_size, p[1] * GRID_SIZE + eye_size*2), eye_size)
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + eye_size, p[1] * GRID_SIZE + GRID_SIZE - eye_size*2), eye_size)
                elif self.direction == UP:
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + eye_size*2, p[1] * GRID_SIZE + eye_size), eye_size)
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + GRID_SIZE - eye_size*2, p[1] * GRID_SIZE + eye_size), eye_size)
                elif self.direction == DOWN:
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + eye_size*2, p[1] * GRID_SIZE + GRID_SIZE - eye_size), eye_size)
                    pygame.draw.circle(surface, RED, (p[0] * GRID_SIZE + GRID_SIZE - eye_size*2, p[1] * GRID_SIZE + GRID_SIZE - eye_size), eye_size)
            else:
                # Body segments
                color = GREEN if i % 2 == 0 else DARK_GREEN
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 1)
    
    def grow(self):
        self.grow_pending += 1
        self.score += 10
        self.length += 1

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                         random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), 
                          (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)
        
        #apple-like shape
        stem_rect = pygame.Rect((self.position[0] * GRID_SIZE + GRID_SIZE//2 - 1, 
                                self.position[1] * GRID_SIZE - 3), 
                               (2, 5))
        pygame.draw.rect(surface, DARK_GREEN, stem_rect)
        
        leaf_rect = pygame.Rect((self.position[0] * GRID_SIZE + GRID_SIZE//2 + 2, 
                                self.position[1] * GRID_SIZE - 2), 
                               (4, 3))
        pygame.draw.ellipse(surface, GREEN, leaf_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game - Python")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.snake = Snake()
        self.food = Food()
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
                    
                if event.key == pygame.K_UP:
                    self.snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.turn(RIGHT)
    
    def update(self):
        if not self.snake.is_alive:
            self.game_over = True
            return
            
        self.snake.move()
        
        # Check if snake ate food
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.randomize_position()
            
            # Ensure food doesn't spawn on snake
            while self.food.position in self.snake.positions:
                self.food.randomize_position()
            
            # Increase speed every 5 foods
            if self.snake.score % 50 == 0 and self.snake.score > 0:
                self.speed += 1
    
    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y), 1)
    
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # score
        score_text = self.font.render(f"Score: {self.snake.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # length
        length_text = self.font.render(f"Length: {self.snake.length}", True, BLUE)
        self.screen.blit(length_text, (WIDTH - length_text.get_width() - 10, 10))
        
        # controls
        controls = [
            "Controls:",
            "↑ ↓ ← → : Move",
            "R : Restart",
            "ESC : Quit"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(control_text, (10, HEIGHT - 100 + i * 25))
        
        # game over screen
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, 
                           (WIDTH // 2 - game_over_text.get_width() // 2, 
                            HEIGHT // 2 - 50))
            
            final_score = self.font.render(f"Final Score: {self.snake.score}", True, WHITE)
            self.screen.blit(final_score, 
                           (WIDTH // 2 - final_score.get_width() // 2, 
                            HEIGHT // 2))
            
            restart_text = self.font.render("Press R to Restart", True, GREEN)
            self.screen.blit(restart_text, 
                           (WIDTH // 2 - restart_text.get_width() // 2, 
                            HEIGHT // 2 + 50))
    
    def restart_game(self):
        self.snake.reset()
        self.food.randomize_position()
        self.game_over = False
        self.speed = FPS
        
        # Check food doesn't spawn on snake
        while self.food.position in self.snake.positions:
            self.food.randomize_position()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(self.speed)

if __name__ == "__main__":
    game = Game()
    game.run()
    