import pygame
import os
import random


class Settings(object):
    """
    global game settings and information
    """
    width = 700
    height = 400
    fps = 60
    title = "Duck"
    file_path = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(file_path, "images")

    @staticmethod
    def get_dim():
        """
        returns the dimensions of the screen
        """
        return (Settings.width, Settings.height)


class Background(pygame.sprite.Sprite):
    """
    Bitmap class to manage the background of the game.
    """
    def __init__(self, filepath):
        """Constructor
        Args:
            img_filepath (string): filename with path of the background bitmap
        """
        super().__init__()
        self.image = pygame.image.load(filepath).convert()
        self.rect = self.image.get_rect()

    def draw(self, screen):
        """
        draw the background
        """
        screen.blit(self.image, self.rect)


class MovingSprite(pygame.sprite.Sprite):
    """
    Base class for moving sprites
    """
    def __init__(self, img_filepath, game):
        """Constructor
        Args:
            img_filepath (string): filename with path of the sprite bitmap
            game (Game): Game object
        """
        super().__init__()
        self.image = pygame.image.load(img_filepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = 1
        self.direction_x = 0
        self.direction_y = 0

        self.game = game

    def update(self):
        """
        Base update fuction
        has to be redefined for each sub-class
        """
        pass

    def move_in_screen(self):
        """
        Move the sprite using self.direction_x , self.direction_y and self.speed without leaving the borders of the screen
        """
        new_left = self.rect.left + self.direction_x * self.speed
        new_top = self.rect.top + self.direction_y * self.speed
        new_right = new_left + self.rect.width
        new_bottom = new_top + self.rect.height
        if 0 < new_left and new_right < self.game.settings.width:
            self.rect.left = new_left
        if 0 < new_top and new_bottom < self.game.settings.height:
            self.rect.top = new_top

    def move_up(self):
        """
        sets self.direction_y so that the sprite will move up
        """
        self.direction_y = -1

    def move_down(self):
        """
        sets self.direction_y so that the sprite will move down
        """
        self.direction_y = 1

    def move_left(self):
        """
        sets self.direction_x so that the sprite will move left
        """
        self.direction_x = -1
    
    def move_right(self):
        """
        sets self.direction_x so that the sprite will move right
        """
        self.direction_x = 1

    def stop_horizontal(self):
        """
        stops horizontal movement
        """
        self.direction_x = 0

    def stop_vertical(self):
        """
        stops vertical movement
        """
        self.direction_y = 0


class Duck(MovingSprite):
    """
    duck class
    """
    def __init__(self, game):
        """Constructor
        Args:
            game (Game): game object
        """
        super().__init__(os.path.join(settings.images_path, 'duck', 'd_06_01.png'), game)
        self.speed = 3
        self.rect.centerx = self.game.settings.width // 2
        self.rect.bottom = self.game.settings.height

    def update(self):
        """
        move without leaving the screen
        """
        self.move_in_screen()

    def respawn_random(self):
        """
        reposition at a random position inside the screen's borders
        """
        new_left = random.randint(0, self.game.settings.width)
        new_top = random.randint(0, self.game.settings.height)
        new_right = new_left + self.rect.width
        new_bottom = new_top + self.rect.height
        if not (0 < new_left and new_right < self.game.settings.width
        and 0 < new_top and new_bottom < self.game.settings.height):
            self.respawn_random()
        else:
            self.rect.left = new_left
            self.rect.top = new_top

    def draw(self, screen):
        """
        draw the sprite
        """
        screen.blit(self.image, self.rect)


class Game(object):
    """
    Game management

    start the game with Game.run()
    """
    def __init__(self, settings):
        """Constructor
        Args:
            settings (Settings): settings object 
        """
        self.settings = settings
        self.screen = pygame.display.set_mode(settings.get_dim())
        self.clock = pygame.time.Clock()
        self.done = False
        pygame.display.set_caption(self.settings.title)

        #sprites
        self.background = Background(os.path.join(self.settings.images_path, 'background.png'))
        self.duck = Duck(self)



    def run(self):
        """
        main program loop
        """
        while not self.done:
            self.clock.tick(self.settings.fps)
            #event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

                if event.type == pygame.KEYUP:
                    #QUIT
                    if event.key == pygame.K_ESCAPE:
                        self.done = True 

                    #Stop Moving
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.duck.stop_horizontal()
                    elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        self.duck.stop_vertical()

                    #Respawn
                    elif event.key == pygame.K_SPACE:
                        self.duck.respawn_random()

                elif event.type == pygame.KEYDOWN:
                    #Start Moving
                    if event.key == pygame.K_LEFT:
                        self.duck.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.duck.move_right()
                    elif event.key == pygame.K_UP:
                        self.duck.move_up()
                    elif event.key == pygame.K_DOWN:
                        self.duck.move_down()

            #updates
            self.duck.update()
            
            #drawing
            self.background.draw(self.screen)
            self.duck.draw(self.screen)
            pygame.display.flip()




if __name__ == '__main__':
    settings = Settings()

    pygame.init()
    game = Game(settings)
    game.run()
  
    pygame.quit()

