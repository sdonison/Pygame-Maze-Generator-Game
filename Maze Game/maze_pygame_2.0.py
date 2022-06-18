import pygame
import os
from random import choice, randint
import sys

pygame.font.init()

RES = WIDTH, HEIGHT = 1202, 902
TILE = 50
cols, rows = WIDTH // TILE, HEIGHT // TILE
PLAYER_VEL = 2
WINNER_FONT = pygame.font.SysFont("Calibri", 75)

#This initializes pygame, sets the display surface to the resolution, and starts the clock that manages framerate.
pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()
global_top_walls = pygame.sprite.Group()
global_right_walls = pygame.sprite.Group()
global_left_walls = pygame.sprite.Group()
global_bottom_walls = pygame.sprite.Group()

class Cell:
    """This class has everything to do with drawing the cells of the maze. It initially creates a grid of cells and
    begins drawing the maze in the upper left corner. It uses a stack to remember which cells have been visited and
    pops from the stack when all nearby cells have been visited. It removes walls from the cells in the direction
    that it entered the cell and programs collision for the remaining walls.
    """
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.sprite_list = pygame.sprite.Group()
        self.needs_top_sprite = True
        self.needs_bottom_sprite = True
        self.needs_left_sprite = True
        self.needs_right_sprite = True

    def draw_current_cell(self, finished_maze = False):
        """Draws the starting cell that generates the maze.
        """
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, pygame.Color('saddlebrown'), (x + 2, y + 2, TILE - 2, TILE - 2), finished_maze)

    def draw(self, finished_maze =False):
        """Draws the initial grid for the maze and changes the color of the cells when they've been visited.
        """
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(sc, pygame.Color('black'), (x, y, TILE, TILE))

        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y), (x + TILE, y), 2)
            if finished_maze and self.needs_top_sprite:
                wall_sprite = Wall(x, x+TILE, y-3, y+3)
                global_top_walls.add(wall_sprite)
                self.needs_top_sprite = False

        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y), (x + TILE, y + TILE), 2)
            if finished_maze and self.needs_right_sprite:
                wall_sprite = Wall(x+TILE-3, x+TILE+3, y, y+TILE)
                global_right_walls.add(wall_sprite)
                self.needs_right_sprite = False

        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x + TILE, y + TILE), (x, y + TILE), 2)
            if finished_maze and self.needs_bottom_sprite:
                wall_sprite = Wall(x, x+TILE, y+TILE-3, y+TILE+3)
                global_bottom_walls.add(wall_sprite)
                self.needs_bottom_sprite = False

        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('darkorange'), (x, y + TILE), (x, y), 2)
            if finished_maze and self.needs_left_sprite:
                wall_sprite = Wall(x-3, x+3, y, y+TILE)
                global_left_walls.add(wall_sprite)
                self.needs_left_sprite = False
    
    def check_cell(self, x, y, grid_cells):
        """Checks to make sure the cell the generator is entering is not outside of the screen.
        """
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self, grid_cells):
        """Checks if the cells nearby have not been visited. Those that have not been visited are appended to a list
        and a random cell is chosen and returned. If all cells have been visited, this returns False.
        """
        neighbors = []
        top = self.check_cell(self.x, self.y - 1, grid_cells)
        right = self.check_cell(self.x + 1, self.y, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, grid_cells)
        left = self.check_cell(self.x - 1, self.y, grid_cells)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False

    def remove_walls(current, next):
        """Removes the walls of the maze as the current cell passes through them.
        """
        dx = current.x - next.x
        if dx == 1:
            current.walls['left'] = False
            next.walls['right'] = False

        elif dx == -1:
            current.walls['right'] = False
            next.walls['left'] = False

        dy = current.y - next.y
        if dy == 1:
            current.walls['top'] = False
            next.walls['bottom'] = False
            
        if dy == -1:
            current.walls['bottom'] = False
            next.walls['top'] = False
            

class Player(pygame.sprite.Sprite):
    """A class that defines the player sprite. Collisions for the sprite and player movement are handled here.
    The function that determines victory condition is also here.
    """
    def __init__(self):
        """Pulls the sprite images from the files and places the sprite in the upper left corner of the maze.
        """
        pygame.sprite.Sprite.__init__(self)

        self.width = TILE / 2
        self.height = TILE / 2
        self.player_image_down = pygame.image.load(os.path.join("Maze Game", "sprites", "player_down.png"))
        self.player_down = pygame.transform.scale(self.player_image_down, (self.width, self.height))
        self.image = self.player_down
       
        # self.player_image_up = pygame.image.load(os.path.join("sprites", "player_up.png"))
        # self.player_image_left = pygame.image.load(os.path.join("sprites", "player_left.png"))
        # self.player_image_right = pygame.image.load(os.path.join("sprites", "player_right.png"))
        
        self.x = TILE / 2-12
        self.y = TILE / 2-12
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def player_movement(self, keys_pressed):
        """Handles player movement and checks for wall collision.
        """

        if keys_pressed[pygame.K_UP]:
            up_y, up_x = self.y - PLAYER_VEL, self.x
            if pygame.sprite.spritecollideany(self, global_top_walls):
                self.y += PLAYER_VEL*4
            elif up_y >= 0:
                self.y -= PLAYER_VEL
            else:
                self.y += PLAYER_VEL*4
        elif keys_pressed[pygame.K_DOWN]:
            down_y, down_x = self.y + PLAYER_VEL + TILE / 2, self.x
            if pygame.sprite.spritecollideany(self, global_bottom_walls):
                self.y -= PLAYER_VEL*4
            elif down_y <= HEIGHT:
                self.y += PLAYER_VEL
            else:
                self.y -= PLAYER_VEL*4
        elif keys_pressed[pygame.K_RIGHT]:
            right_y, right_x = self.y, self.x + PLAYER_VEL + TILE / 2
            if pygame.sprite.spritecollideany(self, global_right_walls):
                self.x -= PLAYER_VEL*4
            elif right_x <= WIDTH:
                self.x += PLAYER_VEL
            else:
                self.x -= PLAYER_VEL*4
        elif keys_pressed[pygame.K_LEFT]:
            left_y, left_x = self.y, self.x - PLAYER_VEL
            if pygame.sprite.spritecollideany(self, global_left_walls):
                self.x += PLAYER_VEL*4
            elif left_x >= 0:
                self.x -= PLAYER_VEL
            else:
                self.x += PLAYER_VEL*4

    def draw_victory(self,text):
        draw_text = WINNER_FONT.render(text, 1, "white")
        sc.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2,
                            HEIGHT//2 - draw_text.get_height()//2))
        pygame.display.update()
        pygame.time.delay(5000)

class Wall(pygame.sprite.Sprite):
    """Defines the dimensions of the walls for the purpose of collision.
    """
    def __init__(self, x1, x2, y1, y2):
        pygame.sprite.Sprite.__init__(self)

        self.rect = pygame.rect.Rect(x1, y1, x2-x1, y2-y1)
    
def main():
    pygame.mixer.music.load("Maze Game/music/music_jewels.ogg")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(loops=-1)
    """Initial values for generating the maze.
    """
    grid_cells = [Cell(col, row) for row in range(rows)for col in range(cols)]
    current_cell = grid_cells[0]
    stack = []
    colors, color = [], 40
    player = Player()

    player_spirte = pygame.sprite.Group()
    player_spirte.add(player)

    x_tiles = (WIDTH-2)/TILE - 1
    y_tiles = (HEIGHT-2)/TILE - 1
    min_x_tiles = x_tiles//2
    min_y_tiles = y_tiles//2
    finish_x = randint(min_x_tiles, x_tiles)
    finish_y = randint(min_y_tiles, y_tiles)

    run = True
    finished_maze = False
    while run:
        """While loop for running the game. If there are currently cells in the stack, it will continue to draw the maze
        until the stack is empty. Once the stack is empty, the player sprite will appear and can be controlled.
        """
        sc.fill(pygame.Color("darkslategray"))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        [cell.draw(finished_maze)for cell in grid_cells]
        
        current_cell.visited = True
        current_cell.draw_current_cell(finished_maze)
        [pygame.draw.rect(sc, colors[i], (cell.x * TILE + 5, cell.y * TILE +5,
                                            TILE - 10, TILE - 10), border_radius=12) for i, cell in enumerate(stack)]

        next_cell = current_cell.check_neighbors(grid_cells)
        if next_cell:
            next_cell.visited = True
            stack.append(current_cell)
            colors.append((0,min(color, 100), 50))
            color += 1
            Cell.remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()

        if len(stack) > 0:
            pygame.display.flip()
            clock.tick(60)
        else:
            finished_maze = True
            clock.tick(60)
            

            finish = pygame.Rect(finish_x*TILE+3, finish_y*TILE+3, TILE-3, TILE-3)
            pygame.draw.rect(sc, "green", finish)
            player.rect.x = player.x
            player.rect.y = player.y
            sc.blit(player.player_down, player.rect)
            pygame.display.update()

            keys_pressed = pygame.key.get_pressed()
            player.player_movement(keys_pressed)

            win = pygame.USEREVENT + 2

            if player.rect.colliderect(finish):
                pygame.event.post(pygame.event.Event(win))
                if event.type == win:
                    text = "Congratulations!"
                    player.draw_victory(text)
                    global_bottom_walls.empty()
                    global_left_walls.empty()
                    global_right_walls.empty()
                    global_top_walls.empty()
                    main()

main()