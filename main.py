from tkinter.font import BOLD
import pygame
import random
import os

# 不更改的變數，通常用大寫命名
FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)

# 遊戲初始化 & 創建視窗
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
blackground_img = pygame.image.load(os.path.join("img","background.png")).convert()
player_img = pygame.image.load(os.path.join("img","player.png ")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join("img","bullet.png")).convert()
# rock_img = pygame.image.load(os.path.join("img","rock.png"))
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img",f"rock{i}.png")).convert())

# explo_img
expl_anim = {} # create dictionary
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []

for i in range(9):
    expl_img = pygame.image.load(os.path.join("img",f"expl{i}.png")) # 載入圖片到expl_img
    expl_img.set_colorkey(BLACK) # 圖片去背
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75))) # 圖片s加入到key = lg的value
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join("img",f"player_expl{i}.png")) # 載入圖片到expl_img
    player_expl_img.set_colorkey(BLACK) # 圖片去背
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img","shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img","gun.png")).convert()

# music
shoot_sound = pygame.mixer.Sound(os.path.join("sound","shoot.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound","rumble.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound","pow0.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound","pow1.wav"))
expls_sounds = []

for i in range(2):
    expls_sounds.append(pygame.mixer.Sound(os.path.join("sound",f"expl{i}.wav")))
pygame.mixer.music.load(os.path.join("sound","background.wav"))
pygame.mixer.music.set_volume(0.3)

font_name = os.path.join("font.ttf")
# pygame.font.match_font(BOLD, "arial")

# 把文字寫在畫面上
def draw_text(surf, text, size, x, y): #寫在什麼平面上，寫的文字，文字的大小，文字的坐標
    font = pygame.font.Font(font_name, size) # 字體，文字的大小
    text_surface = font.render(text, True, WHITE)  # 渲染文字（文字，要不要讓文字變得滑順，顏色）
    text_rect = text_surface.get_rect() # 設定位置參數
    text_rect.centerx = x 
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH  # 血條長度
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT) # 創建血條外框
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT) # 創建血條
    pygame.draw.rect(surf, GREEN, fill_rect) # 在畫面畫出血條
    pygame.draw.rect(surf, WHITE, outline_rect, 2) # 在畫面畫出外框

def new_rock():
    r = Rock()  # 創建石頭
    all_sprites.add(r)  # 將石頭加到sprite
    rocks.add(r)  # 將石頭sprite加到石頭sprite群組

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(blackground_img, (0,0))
    draw_text(screen, "Game", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "← →移動飛船 空白鍵發射子彈", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "按任意鍵開始遊戲", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)  # 每秒最多只能執行FPS次
        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() # 框起來，定位
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):

        if self.gun > 1 and pygame.time.get_ticks() - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = pygame.time.get_ticks() 
 
        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        # 鍵盤上的每個按鍵是否有被按，有會return true，else false
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx      

        if self.rect.right > WIDTH: 
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
        # self.rect.x += 2
        # if self.rect.x > WIDTH:
        #     self.rect.right = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() # 框起來，定位
        self.radius = int(self.rect.width * 0.85 /2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center # 儲存原來的中心點
        self.rect = self.image.get_rect() # 重新定位
        self.rect.center = center # 新的中心點 = 舊的中心點

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK) # 去背
        self.rect = self.image.get_rect() # 框起來，定位
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect() # 框起來，定位
        self.rect.center = center
        self.frame = 0 # 更新到第幾張圖片
        self.last_update = pygame.time.get_ticks() # 獲取從初始化到現在獲得的毫秒數
        self.frame_rate = 50 # 至少要經過多少毫秒才會更新到下一張圖片

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.ract = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK) # 去背
        self.rect = self.image.get_rect() # 框起來，定位
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

# create a sprite group

pygame.mixer.music.play(-1) # 無限重複播放

running = True
show_init = True

# 遊戲迴圈
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        # create player
        player = Player()
        all_sprites.add(player)

        #creat rock
        # rock = Rock()
        # all_sprites.add(rock)
        for i in range(8):
            new_rock()

        score = 0

    clock.tick(FPS)  # 每秒最多只能執行FPS次

    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新遊戲
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks,bullets,True,True) # 會回傳一個dictionary，裡面寫我們碰撞到的rock = key和bullet = value
    for hit in hits:
        random.choice(expls_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        new_rock()
        player.health -= hit.radius
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()

    # 判斷寶物和飛船相撞
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == 'shield':
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        if hit.type == 'gun':
            player.gunup()
            gun_sound.play()

    if player.lives == 0 and not(death_expl.alive()):
        show_init = True

    # 渲染畫面顯示
    screen.fill(BLACK)
    screen.blit(blackground_img, (0,0))
    all_sprites.draw(screen) # 將全部sprite畫到screen
    draw_text(screen,str(score), 40, WIDTH *6/7, 5)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH/2 - 100, 15)
    pygame.display.update()

pygame.quit()