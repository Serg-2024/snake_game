import pygame as pg, random as rdm, sys
from pygame.math import Vector2 as Pos
pg.init()
MOVE_SNAKE = pg.USEREVENT + 1
BALL_INCR = pg.USEREVENT + 2
pg.time.set_timer(MOVE_SNAKE, 150)
pg.time.set_timer(BALL_INCR, 300)
pg.mouse.set_visible(False)

class Game:
    level = score = 0
    def __init__(self):
        self.screen = pg.display.set_mode((800,800))
        self.font_148, self.font_64 = pg.font.Font(None, 148), pg.font.Font(None, 64)
        self.rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.status = 'new' #: new, pause, is_over, playing, new_level
        self.running = True
        self.finish = False
        self.direction = Pos(-1,0)
        self.all = pg.sprite.Group()
        self.tail = pg.sprite.Group()
        self.snake = WholeSnake()
        self.head = Snake(self.rect.center, [self.snake])
        #self.head.image.fill('gold4')
        for i in [1,2]: Snake(self.head.rect.topleft + Pos(40*i, 0), [self.snake, self.tail, self.all])
        self.fruits = Fruits()
        for _ in range(3): Fruit([self.fruits, self.all])
        self.exit_pos = Pos()
        self.level_exit = None

    def check_collision(self):
        if not self.rect.contains(self.head): self.status = 'is over'
        collisions = pg.sprite.spritecollide(self.head, self.all, dokill=False)
        if collisions in self.fruits:
            for c in collisions:
                Game.score += 1
                Snake(c.rect.topleft, [self.snake, self.tail, self.all])
                new_pos = c.get_pos()
                while any(s.rect.collidepoint(new_pos) for s in self.all.sprites()): new_pos = c.get_pos()
                c.rect.topleft = new_pos
            if not (len(self.snake) - 3) % 5 and self.status != 'new level':
                self.status = 'new level'
                Game.score += 5
                self.draw_exit()
        elif collisions in self.tail: self.status = 'is over'
        if self.status == 'new level' and self.level_exit.rect.colliderect(self.head.rect):
            if self.level_exit.rect.contains(self.head.rect): self.finish = True
            for s in self.snake.sprites():
                if self.level_exit.rect.contains(s): s.kill()
                if not self.snake:
                    pg.time.set_timer(MOVE_SNAKE, 150 - Game.level * 20)
                    Game.level += 1
                    self.__init__()

    def check_status(self):
        keys = pg.key.get_pressed()
        if self.status == 'new':
            self.draw_text(f'LEVEL {Game.level + 1}', 'ESC-exit, ENTER-play')
            if keys[pg.K_ESCAPE]: self.running = False
            elif keys[pg.K_RETURN]: self.status = 'playing'
        elif self.status == 'pause':
            self.draw_text('PAUSE', 'press SPACE to resume')
        elif self.status == 'is over':
            self.draw_text(f'SCORE: {Game.score}', 'ESC for exit, ENTER to play again')
            if keys[pg.K_ESCAPE]: self.running = False
            elif keys[pg.K_RETURN]:
                self.__init__()
                self.status = 'playing'
                Game.level = Game.score = 0
                pg.time.set_timer(MOVE_SNAKE, 150)
        elif self.status == 'new level':
            self.level_exit.draw()

    def draw_text(self, text1, text2):
        text1 = self.font_148.render(text1, True, 'black')
        rect1 = text1.get_rect(midbottom=self.rect.center)
        text2 = self.font_64.render(text2, True, 'black')
        surf = pg.Surface((800, 800), pg.SRCALPHA)
        pg.draw.rect(surf, (120, 120, 120, 150), (0, 0, 800, 800))
        surf.blit(text1, rect1)
        surf.blit(text2, text2.get_rect(midtop=rect1.midbottom + Pos(0, 10)))
        self.screen.blit(surf, (0, 0))

    def draw_exit(self):
        if not self.exit_pos:
            new_pos = Pos(rdm.randint(0, 17), rdm.randint(0, 17)) * 40
            while any(pg.Rect(new_pos, (120, 120)).colliderect(r) for r in self.snake.sprites()):
                new_pos = Pos(rdm.randint(0, 17), rdm.randint(0, 17)) * 40
            self.exit_pos = new_pos
            self.level_exit = LevelExit(self.exit_pos, self.all)

    def draw_misc(self):
        bar_text = pg.font.Font(None, 32).render(f'LEVEL: {Game.level + 1} SCORE: {Game.score}', True, 'black')
        bar_rect = bar_text.get_rect(topleft=(10,10))
        self.screen.blit(bar_text, bar_rect)

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT: self.running = False
                if event.type == pg.KEYDOWN:
                    if not self.finish:
                        d = {pg.K_LEFT: Pos(-1, 0), pg.K_RIGHT: Pos(1, 0), pg.K_UP: Pos(0, -1), pg.K_DOWN: Pos(0, 1)
                             }.get(event.key, self.direction)
                        self.direction = d if d.x != -self.direction.x and d.y != -self.direction.y else self.direction
                    if event.key == pg.K_SPACE:
                        if self.status == 'playing': self.status = 'pause'
                        elif self.status == 'pause': self.status = 'playing'
                if event.type == MOVE_SNAKE and self.status in ['playing', 'new level']:
                    self.snake.update()
                    self.check_collision()
                if event.type == BALL_INCR:
                    if self.status == 'playing':
                        self.fruits.radius += self.fruits.radius_dt
                        self.fruits.radius_dt *= -1
                    elif self.status == 'new level':
                        self.level_exit.update()
            self.screen.fill('darkolivegreen1')
            for row in range(20):
                for col in range(20):
                    if (row + col) % 2: pg.draw.rect(self.screen, 'darkolivegreen2', (col*40, row*40, 40, 40))
            self.fruits.draw(self.screen)
            self.snake.draw(self.screen)
            self.check_status()
            pg.draw.rect(self.screen, 'gold4', self.head.rect)
            self.draw_misc()
            self.clock.tick(30)
            pg.display.flip()
        pg.quit()
        sys.exit()

class Fruit(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pg.Surface((40, 40))
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect(topleft=self.get_pos())

    def get_pos(self):
        return Pos(rdm.randint(0, 19), rdm.randint(0, 19)) * 40  # new apple position

class Fruits(pg.sprite.Group):
    def __init__(self):
        super().__init__(self)
        self.radius = 20
        self.radius_dt = -3

    def draw(self, screen, special_flags=0, **kwargs):
        for fruit in self.sprites():
            fruit.image.fill('black')
            pg.draw.circle(fruit.image, 'dark red', (20, 20), self.radius + self.radius_dt)
            screen.blit(fruit.image, fruit.rect)

class WholeSnake(pg.sprite.Group):
    def __init__(self):
        super().__init__(self)

    def update(self):
        sprites = self.sprites()
        sprites[-1].rect.topleft = sprites[0].rect.topleft
        sprites.insert(1,sprites.pop())
        self.empty()
        self.add(sprites)
        self.sprites()[0].rect.move_ip(game.direction * 40)

class Snake(pg.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pg.Surface((40, 40))
        self.image.fill('dark green')
        self.rect = self.image.get_rect(topleft=pos)

class LevelExit(pg.sprite.Sprite):
    def __init__(self, exit_pos, group):
        super().__init__(group)
        self.rect = pg.Rect(exit_pos + Pos(40,40), (40,40))

    def update(self):
        if self.rect.width < 128: self.rect.inflate_ip(8,8)
        else: self.rect.inflate_ip(-8,-8)

    def draw(self):
        pg.draw.rect(pg.display.get_surface(), 'black', self.rect)

if __name__ == '__main__':
    game = Game()
    game.run()