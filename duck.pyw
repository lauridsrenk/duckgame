import pygame
import os
import random

class Settings(object):
    """
    Settings for the game
    the entire class is static
    """
    width = 700
    height = 600
    fps = 60
    title = "Duck"
    file_path = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(file_path, "images")
    nof_hazards = 10
    max_hazard_speed_modifier = 2
    hazard_speed_increase_value = 0.1
    #time values in ms
    base_hazard_rate = 1000
    max_hazard_rate = 200
    hazard_rate_increase_value = -50
    hazard_speed_increase_rate = 3000
    hazard_rate_increase_rate = 1500


    @staticmethod
    def get_dim():
        """
        returns a tuple of the window width and height
        """
        return (Settings.width, Settings.height)


class Background(pygame.sprite.Sprite):
    """
    Background for the game
    """
    def __init__(self, filepath):
        super().__init__()
        self.image = pygame.image.load(filepath).convert()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, Settings.get_dim())

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class MovingSprite(pygame.sprite.Sprite):
    """
    Base Class for a sprite with movement
    """
    def __init__(self, img_filepath, game):
        super().__init__()
        self.image = pygame.image.load(img_filepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = 1
        self.direction_x = 0
        self.direction_y = 0

        self.game = game

    def update(self):
        """
        update needs to be defined for each subclass
        """
        pass

    def move_in_screen(self):
        """
        move the sprite according to self.speed, self.direction_x and self.direction_y
        without leaving the screen
        """
        new_left = self.rect.left + self.direction_x * self.speed
        new_top = self.rect.top + self.direction_y * self.speed
        new_right = new_left + self.rect.width
        new_bottom = new_top + self.rect.height
        if 0 < new_left and new_right < Settings.width:
            self.rect.left = new_left
        if 0 < new_top and new_bottom < Settings.height:
            self.rect.top = new_top

    def move(self):
        """
        move the sprite according to self.speed, self.direction_x and self.direction_y.
        sprite can leave the screen
        """
        self.rect.move_ip(self.direction_x * self.speed, self.direction_y * self.speed)

    def move_up(self):
        """
        sets the direction attributes to make the sprite move up
        """
        self.direction_y = -1

    def move_down(self):
        """
        sets the direction attributes to make the sprite move down
        """
        self.direction_y = 1

    def move_left(self):
        """
        sets the direction attributes to make the sprite move left
        """
        self.direction_x = -1
    
    def move_right(self):
        """
        sets the direction attributes to make the sprite move right
        """
        self.direction_x = 1

    def stop_horizontal(self):
        """
        sets the direction attributes to stop horizontal movement
        """
        self.direction_x = 0

    def stop_vertical(self):
        """
        sets the direction attributes to stop vertical movement
        """
        self.direction_y = 0

    def change_image(self, img_filepath):
        """
        changes the image of the sprite
        """
        old_left = self.rect.left
        old_top = self.rect.top
        self.image = pygame.image.load(img_filepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.move_ip(old_left,old_top)


class Duck(MovingSprite):
    """
    Player Object
    """
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'duck', 'd_06_01.png'), game)
        self.speed = 5
        self.rect.centerx = Settings.width // 2
        self.rect.bottom = Settings.height

    def update(self):
        self.move_in_screen()
        if self.direction_x == -1:
            self.change_image(os.path.join(Settings.images_path, 'duck', 'd_04_01.png'))
        if self.direction_x == 1:
            self.change_image(os.path.join(Settings.images_path, 'duck', 'd_06_01.png'))

    def respawn_random(self):
        """
        respawns the duck at a random position without leaving the screen
        duck may collide with other sprites
        """
        new_left = random.randint(0, Settings.width - self.rect.width)
        new_top = random.randint(0, Settings.height - self.rect.height)
        self.rect.move_ip(new_left, new_top)

    def draw(self, screen):
        #self.draw is needed because this object will not be stored in a spritegroup
        screen.blit(self.image, self.rect)


class Hazard(MovingSprite):
    """
    Base class for hazards
    """
    def __init__(self, img_filepath, game):
        super().__init__(img_filepath, game)
        self.startpos()
        self.move_down()

    def update(self):
        self.move()
        if self.rect.top >= Settings.height:
            self.kill()
            self.game.increase_score()

    def startpos(self):
        self.rect.left = random.randint(0,Settings.width - self.rect.width)
        self.rect.bottom = 0


class Barrel(Hazard):
    """
    A hazard with a base speed of 5
    """
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'hazards', 'barrel.png'), game)
        self.speed = 5


class Axe(Hazard):
    """
    A hazard with a base speed of 6
    """
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'hazards', 'axe.png'), game)
        self.speed = 6


class Hammer(Hazard):
    """
    A hazard with a base speed of 7
    """
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'hazards', 'hammer.png'), game)
        self.speed = 7


class Text(pygame.sprite.Sprite):
    """
    A pygame.sprite.Sprite child class used to display text
    """
    def __init__(self, fontPath, fontSize, fontColor, top, left):
        super().__init__()
        self.font = pygame.font.Font(fontPath, fontSize)
        self.font_color = fontColor
        self.str = ""
        self.image = self.font.render(self.str, True, self.font_color)
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left

    def write(self, text):
        """
        sets the string that this object shall display
        """
        self.str = text
        self.image = self.font.render(self.str, True, self.font_color)
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()


class Game(object):
    """
    Main game object
    """
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.get_dim())
        self.clock = pygame.time.Clock()
        self.done = False
        self.font = pygame.font.match_font("RockwellExtra")
        pygame.display.set_caption(Settings.title)

        #game variables
        self.hazard_rate = Settings.base_hazard_rate
        self.hazard_speed_modifier = 1
        self.timestamps = {
            "last_hazard" : 0,
            "last_rate_increase" : pygame.time.get_ticks(),
            "last_speed_increase" : pygame.time.get_ticks(),
        }
        self.score = 0

        #sprites
        self.background = Background(os.path.join(Settings.images_path, 'background.png'))
        self.duck = Duck(self)
        self.all_hazards = pygame.sprite.Group()

        #texts
        self.all_texts = pygame.sprite.Group()
        self.texts_by_name = {
            "score" : Text(self.font, 24, 0xFFFFFFFF, 5, 5),
            #"debug" : Text(self.font, 24, 0xFFFFFFFF, 5, 50),
        }
        for t in self.texts_by_name:
            self.all_texts.add(self.texts_by_name[t])

    def run(self):
        """
        Main game loop
        """
        while not self.done:
            self.clock.tick(Settings.fps)
            self.handle_events()
            self.update()
            self.draw()
    
    def handle_events(self):
        for event in pygame.event.get():
            #Quit on window closed
            if event.type == pygame.QUIT:
                self.done = True

            if event.type == pygame.KEYUP:
                #"Quit on ESC
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
                    tries = 100
                    while pygame.sprite.spritecollide(self.duck, self.all_hazards, False) and tries > 0:
                        tries -= 1
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

    def update(self):
            self.duck.update()
            self.all_hazards.update()

            #spawn new hazard
            if (len(self.all_hazards) < Settings.nof_hazards
            and pygame.time.get_ticks() >= self.timestamps["last_hazard"] + self.hazard_rate):

                Hazard_class = random.choice([Barrel, Hammer, Axe])
                h = Hazard_class(self)
                h.speed *= self.hazard_speed_modifier
                self.timestamps["last_hazard"] = pygame.time.get_ticks()

                #Hazards won't overlap with each other
                tries = 100
                while pygame.sprite.spritecollide(h, self.all_hazards, False) and tries > 0:
                    h.startpos()
                    tries -= 1
                self.all_hazards.add(h)

            #collisions with duck
            if pygame.sprite.spritecollide(self.duck,self.all_hazards, False):
                self.done = True

            #Hazard Rate and Speed increases
            if pygame.time.get_ticks() >= self.timestamps["last_speed_increase"] + Settings.hazard_speed_increase_rate:
                if self.hazard_speed_modifier <= Settings.max_hazard_speed_modifier:
                    self.hazard_speed_modifier += Settings.hazard_speed_increase_value
                    self.timestamps["last_speed_increase"] = pygame.time.get_ticks()

            if pygame.time.get_ticks() >= self.timestamps["last_rate_increase"] + Settings.hazard_rate_increase_rate:
                if self.hazard_rate >= Settings.max_hazard_rate:
                    self.hazard_rate += Settings.hazard_rate_increase_value
                    self.timestamps["last_rate_increase"] = pygame.time.get_ticks()

    def draw(self):
            self.background.draw(self.screen)
            self.duck.draw(self.screen)
            self.all_hazards.draw(self.screen)
            self.all_texts.draw(self.screen)
            pygame.display.flip()

    def increase_score(self):
        """
        Increases the score
        """
        self.score += 1
        self.texts_by_name["score"].write(f"{self.score} points")



if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
  
    pygame.quit()