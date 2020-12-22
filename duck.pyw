import pygame
import os
import random

class Settings(object):
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
        return (Settings.width, Settings.height)


class Background(pygame.sprite.Sprite):
    def __init__(self, filepath):
        super().__init__()
        self.image = pygame.image.load(filepath).convert()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, Settings.get_dim())

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class MovingSprite(pygame.sprite.Sprite):
    def __init__(self, img_filepath, game):
        super().__init__()
        self.image = pygame.image.load(img_filepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = 1
        self.direction_x = 0
        self.direction_y = 0

        self.game = game

    def update(self):
        pass

    def move_in_screen(self):
        new_left = self.rect.left + self.direction_x * self.speed
        new_top = self.rect.top + self.direction_y * self.speed
        new_right = new_left + self.rect.width
        new_bottom = new_top + self.rect.height
        if 0 < new_left and new_right < Settings.width:
            self.rect.left = new_left
        if 0 < new_top and new_bottom < Settings.height:
            self.rect.top = new_top

    def move(self):
        self.rect.left = self.rect.left + self.direction_x * self.speed
        self.rect.top = self.rect.top + self.direction_y * self.speed

    def move_up(self):
        self.direction_y = -1

    def move_down(self):
        self.direction_y = 1

    def move_left(self):
        self.direction_x = -1
    
    def move_right(self):
        self.direction_x = 1

    def stop_horizontal(self):
        self.direction_x = 0

    def stop_vertical(self):
        self.direction_y = 0

    def change_image(self, img_filepath):
        old_left = self.rect.left
        old_top = self.rect.top
        self.image = pygame.image.load(img_filepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.move_ip(old_left,old_top)


class Duck(MovingSprite):
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
        new_left = random.randint(0, Settings.width)
        new_top = random.randint(0, Settings.height)
        new_right = new_left + self.rect.width
        new_bottom = new_top + self.rect.height
        if 0 < new_left and new_right < Settings.width and 0 < new_top and new_bottom < Settings.height:
            self.rect.left = new_left
            self.rect.top = new_top
        else:
            self.respawn_random()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Hazard(MovingSprite):
    def __init__(self, img_filepath, game):
        super().__init__(img_filepath, game)
        self.startpos()
        self.move_down()

    def update(self):
        self.move()
        if self.rect.top >= Settings.height:
            self.kill()

    def startpos(self):
        self.rect.left = random.randint(0,Settings.width - self.rect.width)
        self.rect.bottom = 0


class Barrel(Hazard):
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'hazards', 'barrel.png'), game)
        self.speed = 5


class Axe(Hazard):
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'hazards', 'axe.png'), game)
        self.speed = 6


class Hammer(Hazard):
    def __init__(self, game):
        super().__init__(os.path.join(Settings.images_path, 'hazards', 'hammer.png'), game)
        self.speed = 7


class Text(pygame.sprite.Sprite):
    def __init__(self, fontPath, fontSize, fontColor, top, left):
        super().__init__()
        self.font = pygame.font.Font(fontPath, fontSize)
        self.font_color = fontColor
        self.str = ""
        self.image = self.font.render(self.str, True, self.font_color)
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left

    def write(self, str):
        self.str = str
        self.image = self.font.render(self.str, True, self.font_color)
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()


class Game(object):
    def __init__(self):
        self.screen = pygame.display.set_mode(Settings.get_dim())
        self.clock = pygame.time.Clock()
        self.done = False
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
            "score" : Text(pygame.font.match_font("RockwellExtra"), 24, 0xFFFFFFFF, 5, 5),
            #"debug" : Text(pygame.font.match_font("RockwellExtra"), 24, 0xFFFFFFFF, 5, 50),
        }
        for t in self.texts_by_name:
            self.all_texts.add(self.texts_by_name[t])

    def run(self):
        while not self.done:
            self.clock.tick(Settings.fps)

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

            self.update()
            self.draw()
    
    def update(self):
            self.duck.update()
            self.all_hazards.update()

            #increase score, spawn new hazard
            if (len(self.all_hazards) < Settings.nof_hazards
            and pygame.time.get_ticks() >= self.timestamps["last_hazard"] + self.hazard_rate):
                self.increase_score()

                hazard_class = random.choice([Barrel, Hammer, Axe])
                h = hazard_class(self)
                h.speed *= self.hazard_speed_modifier
                self.all_hazards.add(h)
                self.timestamps["last_hazard"] = pygame.time.get_ticks()

                #Hazards won't overlap with each other
                tries = 100
                while pygame.sprite.spritecollide(h,self.all_hazards, False) and tries > 0:
                    h.startpos()
                    tries -= 1

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
        self.score += 1
        self.texts_by_name["score"].write(f"{self.score} points")



if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
  
    pygame.quit()