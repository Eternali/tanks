import pygame, random

player_turn = True
background_music = 'backgroundRainbow.mp3'

colors = {
    'WHITE': (255,255,255),
    'BLACK': (0,0,0),
    'GREY': (150,150,150),
    'RED': (255,0,0),
    'GREEN': (0,155,0),
    'FORESTGREEN': (34,139,34),
    'LAWNGREEN': (124,252,0),
    'BLUE': (0,0,255),
    'SEABLUE': (0,154,205),
    'YELLOW': (255,255,0),
    'ORANGE': (255,125,0),
    'PURPLE': (200,0,255),
    'BROWN': (139,69,19)
    }

power_colors = {
    'GREEN': (0,175,0),
    'MEDGREEN': (124,252,0),
    'YELLOWGREEN': (173,255,47),
    'YELLOW': (255,255,0),
    'YELLOWORANGE': (255,204,0),
    'ORANGE': (255,125,0),
    'ORANGERED': (255,60,0),
    'RED': (255,0,0),
    'DARKRED': (139,0,0)
}

explosion_colors = [power_colors['YELLOW'], power_colors['YELLOWORANGE'], power_colors['ORANGE'],
                    power_colors['ORANGERED'], power_colors['RED']]

delta = {
    'left': -5,
    'right': 5,
    'shell_x': -5,
    'shell_y': 5,
    'turret_l': -1,
    'turret_r': 1
}

class Text_render(object):
    def __init__(self):
        self.SMALLFONT = pygame.font.SysFont('comicsansms', 25)
        self.MEDFONT = pygame.font.SysFont('comicsansms', 35)
        self.LARGEFONT = pygame.font.SysFont('comicsansms', 50)
    def text_obj(self, msg, color, size):
        if size == 'small':
            self.text_surface = self.SMALLFONT.render(msg, True, color)
        elif size == 'medium':
            self.text_surface = self.MEDFONT.render(msg, True, color)
        else:
            self.text_surface = self.LARGEFONT.render(msg, True, color)
        return self.text_surface, self.text_surface.get_rect()
    def to_screen(self, msg, color, surface, posX, posY, size='small'):
        self.text_surf, self.text_rect = self.text_obj(msg, color, size)
        self.text_rect.center = posX, posY
        surface.blit(self.text_surf, self.text_rect)

class Tank(pygame.sprite.Sprite):
    def __init__(self, ground, surface, clock, fps, startX, start_pbarX, start_pbarY, pbar_width, pbar_height, pbar_displace):
        pygame.sprite.Sprite.__init__(self)
        self.sounds = {
            'explosion': pygame.mixer.Sound('fire.wav'),
            'fire': pygame.mixer.Sound('explosion.wav')
            }
        self.display = surface
        self.clock = clock
        self.fps = fps
        self.ground_height = ground
        self.start_pbarX = start_pbarX
        self.start_pbarY = start_pbarY
        self.pbar_width = pbar_width
        self.pbar_height = pbar_height
        self.pbar_displace = pbar_displace
        self.tank_width = 40
        self.tank_height = 20
        self.turret_width = 5
        self.wheel_width = 5
        self.start_x = startX - self.tank_width
        self.start_y = int(ground) - self.tank_height - self.wheel_width + 2
        self.num_wheels = 9
        self.speed = [0, 0]    #19 turret positions
        self.possible_t_pos = [(-25, 0), (-25, -1), (-24, -7), (-22, -12), (-20, -15), (-15, -20), (-12, -22), (-7, -24), (-1, -25),
                               (0, -25), (1, -25), (7, -24), (12, -22), (15, -20), (20, -15), (22, -12), (24, -7), (25, -1), (25, 0)]
        self.tur_pos = 9
        self.tur_change = 0
        self.shell_radius = 3
        self.original_power = 0.05
        self.max_power = 1.9
        self.power = self.original_power
        self.magnitude = 2
        self.health = 200
        self.is_fire = False
        self.can_fire = True
        self.shell_land = False
        self.width, self.height = pygame.display.get_surface().get_rect().width, pygame.display.get_surface().get_rect().height
    def draw(self, color, posX, posY, width, height, t_width, w_num, w_width):
        posX = int(posX)
        posY = int(posY)
        pygame.draw.circle(self.display, color, (posX, posY), int(height/2))
        pygame.draw.rect(self.display, color, (posX-height, posY, width, height))
        pygame.draw.line(self.display, color, (posX, posY),
                         (posX+self.possible_t_pos[self.tur_pos][0], posY+self.possible_t_pos[self.tur_pos][1]), t_width)
        w_start = posX-int(width/2)
        for n in range(w_num):
            pygame.draw.circle(self.display, color, (w_start, posY+height), w_width)
            w_start += w_width
    def display_power(self):
        if self.power < 0.1:
            self.magnitude = 6
        if self.power >= 0.1:
            self.magnitude = 6
            pygame.draw.rect(self.display, power_colors['GREEN'], (self.start_pbarX, self.start_pbarY, self.pbar_width, self.pbar_height))
            if self.power > 0.25:
                self.magnitude = 8
                pygame.draw.rect(self.display, power_colors['MEDGREEN'], (self.start_pbarX, self.start_pbarY - self.pbar_height - 1, self.pbar_width, self.pbar_height))
                if self.power > 0.45:
                    self.magnitude = 10
                    pygame.draw.rect(self.display, power_colors['YELLOWGREEN'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 2), self.pbar_width, self.pbar_height))
                    if self.power > 0.65:
                        self.magnitude = 12
                        pygame.draw.rect(self.display, power_colors['YELLOW'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 3), self.pbar_width, self.pbar_height))
                        if self.power > 0.85:
                            self.magnitude = 14
                            pygame.draw.rect(self.display, power_colors['YELLOWORANGE'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 4), self.pbar_width, self.pbar_height))
                            if self.power > 1.05:
                                self.magnitude = 16
                                pygame.draw.rect(self.display, power_colors['ORANGE'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 5), self.pbar_width, self.pbar_height))
                                if self.power > 1.25:
                                    self.magnitude = 18
                                    pygame.draw.rect(self.display, power_colors['ORANGERED'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 6), self.pbar_width, self.pbar_height))
                                    if self.power > 1.45:
                                        self.magnitude = 20
                                        pygame.draw.rect(self.display, power_colors['RED'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 7), self.pbar_width, self.pbar_height))
                                        if self.power > 1.65:
                                            self.magnitude = 22
                                            pygame.draw.rect(self.display, power_colors['DARKRED'], (self.start_pbarX, self.start_pbarY - (self.pbar_displace * 8), self.pbar_width, self.pbar_height))
    def fire_shell(self, gunX, gunY, turX, turY):
        startingPos = [int(gunX), int(gunY)]
        pygame.draw.circle(self.display, colors['BLACK'], (startingPos[0], startingPos[1]), self.shell_radius)
    def got_hit(self, enemy):
        pass
    def explosion(self, x, y, enemy, name):
        magnitude_particles = self.magnitude * 2
        pygame.mixer.Sound.play(self.sounds['explosion'])
        while magnitude_particles > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()
            bit_x = x + random.randint(-self.magnitude, self.magnitude)
            bit_y = y + random.randint(-self.magnitude, self.magnitude)
            pygame.draw.circle(self.display, explosion_colors[random.randrange(0, 5)], (bit_x, bit_y), int(random.randrange(0, self.magnitude//2)))
            magnitude_particles -= 1
            if enemy.start_x - enemy.tank_width < bit_x < enemy.start_x + enemy.tank_width and bit_y > enemy.ground_height - enemy.tank_height:
                enemy.health -= 2
            elif self.start_x - self.tank_width < bit_x < self.start_x + self.tank_width and bit_y > self.ground_height - self.tank_height:
                self.health -= 2
            if 'enemy' in name:
                self.got_hit(enemy)
                self.display_health(enemy.health, start=0)
                self.display_health(self.health, start=(self.width - self.health))
            else:
                self.got_hit(self)
                self.display_health(self.health, start=0)
                self.display_health(enemy.health, start=(enemy.width - enemy.health))
            pygame.display.update()
            self.clock.tick(self.fps)
    def display_health(self, health, start=0):
        if 125 < health <= 200:
            pygame.draw.rect(self.display, colors['GREEN'], (start, self.height-20, health, 15))
        elif 65 < health <= 125:
            pygame.draw.rect(self.display, power_colors['YELLOW'], (start, self.height-20, health, 15))
        elif health <= 65:
            pygame.draw.rect(self.display, colors['RED'], (start, self.height-20, health, 15))
    def automate(self, gravity):
        if self.time > 0:
            self.start_x += self.speed[0]
            self.time -= delta['right']
        if self.tur_time == 0:
            self.display_power()
            self.turretX = self.start_x + self.possible_t_pos[self.tur_pos][0]
            self.turretY = self.start_y + self.possible_t_pos[self.tur_pos][1]
            self.cur_x = self.possible_t_pos[self.tur_pos][0]
            self.cur_y = self.possible_t_pos[self.tur_pos][1] * self.power
            self.tur_time -= 1
            self.yet_fire = True
        if self.tur_time < 0 and self.time <= 0:
            self.turretX += self.cur_x
            self.turretY += self.cur_y
            self.cur_y += gravity
        if self.tur_time > 0 and self.time <= 0:
            #self.tur_pos += self.tur_change
            self.tur_time -= 1
            self.ready = True

class Barrier(object):
    def __init__(self, color):
        self.color = color
    def draw(self, surface, posX, posY, width, height):
        pygame.draw.rect(surface, self.color, (posX, posY, width, height))
        self.left = posX
        self.top = posY
        self.right = posX + width
        self.bottom = posY + height

class Main(object):
    def __init__(self):
        self.setup()
    def setup(self):
        pygame.init()
        global is_fire
        pygame.mixer.music.load(background_music)
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.menu_fps = 10
        with open('high_score.txt') as infile:
            for line in infile:
                fields = line.strip().split()
        self.high_score = int(fields[-1])
        self.gravity = 0.95
        self.pbar_width = 30
        self.pbar_height = 10
        self.pbar_displace = self.pbar_height + 1
        size = (self.width, self.height) = (700, 500)
        self.game_display = pygame.display.set_mode(size)
        pygame.display.set_caption('Tanks')
        pygame.display.set_icon(pygame.image.load('ball.png'))
        self.start_pbarX = self.width - self.pbar_width - 5
        self.start_pbarY = 88  # number possible power bars * pbar height + (1 * 8)
        self.messages = Text_render()
        self.barrier = Barrier(colors['BROWN'])
        self.ground = Barrier(colors['GREY'])
        self.game_display.fill(colors['WHITE'])
        pygame.display.update()
    def button(self, text, buttonX, buttonY, button_width, button_height, color1, color2, text_color, action=None, size='small'):
        cur = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if buttonX <= cur[0] <= buttonX+button_width and buttonY <= cur[1] <= buttonY+button_height:
            pygame.draw.rect(self.game_display, color2, (buttonX, buttonY, button_width, button_height))
            if click[0] == 1 and action != None:
                if action == 'play':
                    self.game_start = True
                    self.controlled = False
                    self.homed = False
                    self.game_overed = False
                    self.score = 0
                elif action == 'quit':
                    pygame.quit()
                    quit()
                elif action == 'controls':
                    self.controlled = True
                    self.homed = False
                elif action == 'main':
                    self.controlled = False
                    self.paused = False
                    self.game_overed = False
                    self.homed = True
                elif action == 'resume':
                    self.paused = False
                    self.main_gamed = True
                elif action == 'next_level':
                    self.game_start = True
                    self.game_overed = False

        else:
            pygame.draw.rect(self.game_display, color1, (buttonX, buttonY, button_width, button_height))

        centerX, centerY = buttonX + button_width / 2, buttonY + button_height / 2
        self.messages.to_screen(text, text_color, self.game_display, centerX, centerY, size=size)

    def detect_collision(self, posX1, posY1, width1, height1, posX2, posY2, width2, height2, speedX, speedY):
        if speedY != 0:
            if posX1 <= posX2 + width2 and posX2 <= posX1 + width1 and posY1 <= posY2 + height2 and posY2 <= posY1 + height1:
                if self.player.speed[0] < 0:
                    self.player.start_x += 5
                else:
                    self.player.start_x -= 5
                self.player.speed[0] = 0
        elif speedX < 0:
            if posX2 <= posX1 + width1:
                self.player.start_x += 5

    def find_power(self, gunX, gunY, playerX, playerY, barrierX, barrierY, barrierWidth, accuracy=50):
        found = False
        count = 0
        while not found:
            power = (random.randrange(20, int(self.player.max_power * 100)) + 0.00) / 100
            #print power
            count += 1
            if count > (1 / accuracy) * 500000:
                self.enemy.power = 1.00
                found = True
            turretX = self.enemy.start_x + gunX
            turretY = self.enemy.start_y + gunY
            moveY = gunY * power
            #while (barrierWidth + barrierX >= turretX >= barrierX and turretY >= barrierY) == False or (turretY >= self.ground_y) == False:
            while turretY <= self.ground_y:
                turretX += gunX
                turretY += moveY
                moveY += self.gravity
                if playerX - accuracy <= turretX <= playerX + accuracy and playerY - accuracy <= turretY <= playerY + accuracy:
                    self.enemy.power = power
                    turretY = self.ground_y + 10
                    found = True

    def in_screen(self, width, height, posX, posY, width2, height2, speedX, speedY):
        if speedY != 0:
            if 0 >= posY:
                self.player.start_y += 5
            elif height <= posY + height2:
                self.player.start_y += -5
        elif speedX != 0:
            if 0 >= posX:
                self.player.start_x += 5
            elif width <= posX + width2:
                self.player.start_x += -5

    def pause(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

        self.messages.to_screen('PAUSED',
                                colors['RED'],
                                self.game_display,
                                self.width/2,
                                self.height/4,
                                size='large')

        self.button('MENU',
                    self.width/2 - 250,
                    self.height/2,
                    150,
                    50,
                    colors['BLUE'],
                    colors['SEABLUE'],
                    colors['BLACK'],
                    action='main',
                    size='medium')
        self.button('CONTINUE',
                    self.width/2 - 75,
                    self.height/2,
                    150,
                    50,
                    colors['GREEN'],
                    colors['YELLOW'],
                    colors['BLACK'],
                    action='resume',
                    size='medium')
        self.button('QUIT',
                    self.width/2 + 100,
                    self.height/2,
                    150,
                    50,
                    colors['ORANGE'],
                    colors['RED'],
                    colors['BLACK'],
                    action='quit',
                    size='medium')

        pygame.display.update()
        self.clock.tick(self.menu_fps)
    def game_controls(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.main_gamed = True
                self.controlled = False
                self.homed = False

        self.game_display.fill(colors['WHITE'])

        self.messages.to_screen('CONTROLS',
                                colors['RED'],
                                self.game_display,
                                self.width/2,
                                self.height/4,
                                size='large')
        self.messages.to_screen("'SPACE': Fire",
                                colors['BLACK'],
                                self.game_display,
                                self.width/2,
                                self.height/2-30,
                                size='medium')
        self.messages.to_screen("'UP' and 'DOWN' arrows: Move turret",
                                colors['BLACK'],
                                self.game_display,
                                self.width/2,
                                self.height/2,
                                size='medium')
        self.messages.to_screen("'LEFT' and 'RIGHT' arrows: Move tank",
                                colors['BLACK'],
                                self.game_display,
                                self.width/2,
                                self.height/2+30,
                                size='medium')
        self.messages.to_screen("'P': Pause",
                                colors['BLACK'],
                                self.game_display,
                                self.width/2,
                                self.height/2+60,
                                size='medium')

        self.button('PLAY',
                    self.width/2-50,
                    self.height-100,
                    100,
                    50,
                    colors['BLUE'],
                    colors['SEABLUE'],
                    colors['BLACK'],
                    action='play',
                    size='medium')
        self.button('Main',
                    self.width/2-230,
                    self.height-90,
                    100,
                    40,
                    colors['ORANGE'],
                    colors['YELLOW'],
                    colors['BLACK'],
                    action='main')
        self.button('QUIT',
                    self.width/2+130,
                    self.height-90,
                    100,
                    40,
                    colors['RED'],
                    colors['PURPLE'],
                    colors['BLACK'],
                    action='quit')

        pygame.display.update()
        self.clock.tick(self.menu_fps)

    def home(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game_start = True
                self.controlled = False
                self.homed = False
                self.score = 0

        self.game_display.fill(colors['WHITE'])

        self.messages.to_screen('WELCOME TO TANKS',
                                colors['RED'],
                                self.game_display,
                                self.width/2,
                                self.height/4,
                                size='large')
        self.messages.to_screen('Destroy the other tank before it destroys you!',
                                colors['BLUE'],
                                self.game_display,
                                self.width/2,
                                self.height/2,
                                size='small')
        self.messages.to_screen('The more you destroy the harder they get!',
                                colors['BLUE'],
                                self.game_display,
                                self.width/2,
                                self.height/2+25,
                                size='small')

        self.button('PLAY',
                    self.width/2-50,
                    self.height-100,
                    100,
                    50,
                    colors['BLUE'],
                    colors['SEABLUE'],
                    colors['BLACK'],
                    action='play',
                    size='medium')
        self.button('CONTROLS',
                    self.width/2-230,
                    self.height-90,
                    100,
                    40,
                    colors['ORANGE'],
                    colors['YELLOW'],
                    colors['BLACK'],
                    action='controls')
        self.button('QUIT',
                    self.width/2+130,
                    self.height-90,
                    100,
                    40,
                    colors['RED'],
                    colors['PURPLE'],
                    colors['BLACK'],
                    action='quit')

        pygame.display.update()
        self.clock.tick(self.menu_fps)

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

        self.game_display.fill(colors['WHITE'])

        if self.player_died:
            self.messages.to_screen('YOU DIED!', colors['RED'], self.game_display, self.width // 2, self.height // 4, size='large')
            self.messages.to_screen('Score: %s' % str(self.score), colors['BLUE'], self.game_display, self.width // 2, self.height // 4 + 75, size='medium')
            self.messages.to_screen('High Score: %s' % str(self.high_score), colors['GREEN'], self.game_display, self.width // 2, self.height // 4 + 115, size='medium')
        else:
            self.messages.to_screen('YOU WON!', colors['RED'], self.game_display, self.width // 2, self.height // 4, size='large')
            self.button('Continue',
                        self.width // 2 - 50,
                        self.height - 90,
                        100,
                        40,
                        colors['BLACK'],
                        colors['GREY'],
                        colors['WHITE'],
                        action='next_level')
        self.button('Home',
                    self.width // 2 - 230,
                    self.height - 90,
                    100,
                    40,
                    colors['GREEN'],
                    colors['LAWNGREEN'],
                    colors['BLACK'],
                    action='main')
        self.button('Quit',
                    self.width/2+130,
                    self.height-90,
                    100,
                    40,
                    colors['ORANGE'],
                    colors['RED'],
                    colors['BLACK'],
                    action='quit')

        pygame.display.update()
        self.clock.tick(self.menu_fps)

    def main_game(self):

        if not self.player_turn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = True
                        self.main_gamed = False

            if self.enemy_calc:
                self.enemy.ready = False
                self.enemy.tur_time = 0
                #self.enemy.power = random.randint(75, 200) / 100
                self.enemy.yet_fire = False
                self.enemy.shell_land = False
                self.enemy.tur_direction = random.randint(0, 1)
                self.enemy.speed_num = random.randint(0, 1)
                poss_left = self.enemy.start_x - (self.enemy.tank_width // 2)
                poss_right = self.barrier_x - self.enemy.start_x - (self.enemy.tank_width // 2)
                if self.enemy.speed_num == 0 and (self.enemy.start_x - self.enemy.tank_width // 2) > 5:
                    self.enemy.speed[0] = delta['left']
                    self.enemy.time = random.randint(0, poss_left)
                elif self.enemy.start_x < (self.barrier_x - 5):
                    self.enemy.speed[0] = delta['right']
                    self.enemy.time = random.randint(0, poss_right)
                if self.enemy.tur_direction == 0 and self.enemy.tur_pos > 9:
                    self.enemy.tur_time = random.randint(0, self.enemy.tur_pos - 9)
                    self.enemy.tur_change = -1
                elif self.enemy.tur_direction == 1 and self.enemy.tur_pos < 18:
                    self.enemy.tur_time = random.randint(0, 18 - self.enemy.tur_pos)
                    self.enemy.tur_change = 1
                self.enemy_calc = False
            if self.enemy.ready:
                self.find_power(self.enemy.possible_t_pos[self.enemy.tur_pos][0],
                                self.enemy.possible_t_pos[self.enemy.tur_pos][1],
                                self.player.start_x,
                                self.player.start_y,
                                self.barrier_x,
                                self.barrier_y,
                                self.barrier_width,
                                accuracy=self.level)
                pygame.mixer.Sound.play(self.enemy.sounds['fire'])
                self.enemy.ready = False
            self.enemy.automate(self.gravity)
            if self.enemy.tur_time < 0 and self.enemy.time <= 0 and (self.enemy.turretY >= self.ground_height or
                                                                         (self.enemy.turretY > self.barrier_y and self.barrier_x < self.enemy.turretX < (self.barrier_x + self.barrier_width))):
                self.player_turn = True
                self.enemy.explosion(int(self.enemy.turretX), int(self.enemy.turretY), self.player, 'player')

        else:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.player.can_fire:
                self.player.power += 0.05

            if self.player.power > self.player.max_power:
                self.player.power = self.player.max_power

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.player.can_move:
                        self.player.speed[0] = delta['left']
                    elif event.key == pygame.K_RIGHT and self.player.can_move:
                        self.player.speed[0] = delta['right']
                    elif event.key == pygame.K_DOWN and self.player.tur_pos > 0:
                        self.player.tur_change = delta['turret_l']
                    elif event.key == pygame.K_UP and self.player.tur_pos < 18:
                        self.player.tur_change = delta['turret_r']
                    elif event.key == pygame.K_p:
                        self.paused = True
                        self.main_gamed = False
                    elif event.key == pygame.K_w:
                        self.enemy.health -= 50
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.player.speed[0] = 0
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        self.player.tur_change = 0
                    elif event.key == pygame.K_SPACE and self.player.can_fire:
                        self.player.is_fire = True
                        self.player.can_fire = False
                        pygame.mixer.Sound.play(self.player.sounds['fire'])
                        self.gunX = self.player.start_x+self.player.possible_t_pos[self.player.tur_pos][0]
                        self.gunY = self.player.start_y+self.player.possible_t_pos[self.player.tur_pos][1]
                        self.current_x = self.player.possible_t_pos[self.player.tur_pos][0]
                        self.current_y = self.player.possible_t_pos[self.player.tur_pos][1] * self.player.power
                        self.player.can_move = False

            self.detect_collision(self.barrier_x,
                                  self.barrier_y,
                                  self.barrier_width,
                                  self.barrier_height,
                                  self.player.start_x-self.player.tank_width//2,
                                  self.player.start_y-self.player.tank_height//2,
                                  self.player.tank_width,
                                  self.player.tank_height,
                                  self.player.speed[0],
                                  self.player.speed[1])
            self.in_screen(self.width,
                           self.height,
                           self.player.start_x-self.player.tank_width//2,
                           self.player.start_y-self.player.tank_height//2,
                           self.player.tank_width,
                           self.player.tank_height,
                           self.player.speed[0],
                           self.player.speed[1])
            self.player.start_x += self.player.speed[0]
            self.player.start_y += self.player.speed[1]
            self.player.tur_pos += self.player.tur_change

            if self.player.tur_pos <= 0 or self.player.tur_pos >= 18:
                self.player.tur_change = 0

        if self.player.health <= 0:
            self.main_gamed = False
            self.game_overed = True
            self.player_died = True
            if self.score > self.high_score:
                with open('high_score.txt', 'w') as infile:
                    infile.write(str(self.score))
                with open('high_score.txt') as infile:
                    for line in infile:
                        fields = line.strip().split()
                self.high_score = int(fields[-1])
        elif self.enemy.health <= 0:
            self.score += 1
            self.main_gamed = False
            self.game_overed = True
            self.player_died = False

        self.game_display.fill(colors['WHITE'])

        self.player.display_power()
        self.messages.to_screen(str(self.score), colors['BLACK'], self.game_display, 20, 20, size='medium')

        self.barrier.draw(self.game_display, self.barrier_x, self.barrier_y, self.barrier_width, self.barrier_height)
        self.ground.draw(self.game_display, 0, self.ground_y, self.width, self.ground_height)
        self.player.draw(colors['BLACK'],
                         self.player.start_x,
                         self.player.start_y,
                         self.player.tank_width,
                         self.player.tank_height,
                         self.player.turret_width,
                         self.player.num_wheels,
                         self.player.wheel_width)
        self.enemy.draw(colors['RED'],
                        self.enemy.start_x,
                        self.enemy.start_y,
                        self.enemy.tank_width,
                        self.enemy.tank_height,
                        self.enemy.turret_width,
                        self.enemy.num_wheels,
                        self.enemy.wheel_width)

        if not self.player_turn and not self.enemy.shell_land:
            try:
                self.enemy.fire_shell(self.enemy.turretX, self.enemy.turretY, self.enemy.start_x, self.enemy.start_y)
            except Exception as e:
                #self.enemy.turretX = -1
                #self.enemy.turretY = -1
                pass

        if self.player.is_fire:
            if self.gunY > self.ground_height:
                self.player.can_fire = True
                self.player.is_fire = False
                self.player.can_move = True
                self.player.power = self.player.original_power
                self.player.hit_x = int((self.gunX * self.ground_height) / self.gunY)
                self.player.hit_y = int(self.ground_height)
                self.player.explosion(self.player.hit_x, self.player.hit_y, self.enemy, 'enemy')
                self.player_turn = False
                self.enemy_calc = True

            elif self.gunY > self.barrier_y and self.barrier_x < self.gunX < (self.barrier_x + self.barrier_width):
                self.player.can_fire = True
                self.player.is_fire = False
                self.player.can_move = True
                self.player.power = self.player.original_power
                self.player.hit_x = int(self.gunX)
                self.player.hit_y = int(self.gunY)
                self.player.explosion(self.player.hit_x, self.player.hit_y, self.enemy, 'enemy')
                self.player_turn = False
                self.enemy_calc = True

            self.player.fire_shell(self.gunX,
                                   self.gunY,
                                   self.player.start_x,
                                   self.player.start_y)
            self.gunX += self.current_x
            self.gunY += self.current_y
            self.current_y += self.gravity

        self.player.display_health(self.player.health, start=(self.width-self.player.health))
        self.enemy.display_health(self.enemy.health, start=0)

        pygame.display.update()
        self.clock.tick(self.fps)

    def event_loop(self):

        self.homed = True
        self.paused = False
        self.controlled = False
        self.main_gamed = False
        self.game_overed = False
        self.game_start = False
        self.level = 115
        self.barrier_level = 0.10
        health_level = 0

        while True:
            if self.game_start and self.level >= 10:
                self.barrier_width = int(random.randint(0.05*self.width, int(self.barrier_level*self.width)))
                self.barrier_height = int(random.randint(0.2*self.height, int((self.barrier_level*3)*self.height)))
                self.barrier_x = int(random.randint(int(0.4*self.width), int(0.5*self.width)))
                self.barrier_y = self.height - self.barrier_height
                self.ground_y = int(random.randint(0.85*self.height, 0.95*self.height))
                self.ground_height = self.height - (self.height - self.ground_y)
                self.player = Tank(self.ground_y, self.game_display, self.clock, self.fps, pygame.display.get_surface().get_rect().width * 0.9, self.start_pbarX, self.start_pbarY, self.pbar_width, self.pbar_height, self.pbar_displace)
                self.enemy = Tank(self.ground_y, self.game_display, self.clock, self.fps, random.randrange(50, self.barrier_x), self.start_pbarX, self.start_pbarY, self.pbar_width, self.pbar_height, self.pbar_displace)
                self.player.can_move = True
                self.player_turn = True
                self.enemy_calc = True
                self.enemy.tur_pos = 11
                self.level -= 25
                health_level += 15
                self.enemy.health = 20 + health_level
                self.barrier_level += 0.05
                self.game_start = False
                self.main_gamed = True
            while self.homed:
                self.home()
            while self.paused:
                self.pause()
            while self.controlled:
                self.game_controls()
            while self.main_gamed:
                self.main_game()
            while self.game_overed:
                self.game_over()

            self.clock.tick(self.fps)


if __name__ == '__main__':
    app = Main()
    app.event_loop()

