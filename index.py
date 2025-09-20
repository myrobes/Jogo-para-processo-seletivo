from Pygame.zero.builtins import Actor, Rect, keyboard, keys, screen
import random
import math

# Constantes do jogo
WIDTH = 800
HEIGHT = 600
HERO_SPEED = 3
INIMIGO_SPEED = 1.5
HERO_MAX_HP = 100
FPS = 60


# Classe base
class Personagem:
    def __init__(self, start_pos, speed, max_hp, sprite_sheet):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.speed = speed
        self.actor = Actor(sprite_sheet[0], pos=start_pos)
        self.sprite_sheet = sprite_sheet
        self.animation_index = 0
        self.animation_timer = 0
        self.frame_duration = FPS // 8
        self.animation_frames = len(sprite_sheet)
        self.vivo = True

    def mover(self, dx, dy):
        if self.vivo:
            self.actor.x += dx * self.speed
            self.actor.y += dy * self.speed
            self.animar()

    def animar(self):
        if self.vivo:
            self.animation_timer += 1
            if self.animation_timer >= self.frame_duration:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % self.animation_frames
                self.actor.image = self.sprite_sheet[self.animation_index]

    def desenhar(self):
        if not self.vivo:
            return
        self.actor.draw()
        hp_bar_width = self.actor.width
        hp_bar_height = 5
        hp_bar_fill = (self.current_hp / self.max_hp) * hp_bar_width

        border_rect = Rect((self.actor.x - hp_bar_width / 2, self.actor.top - 10), (hp_bar_width, hp_bar_height))
        hp_rect = Rect((self.actor.x - hp_bar_width / 2, self.actor.top - 10), (hp_bar_fill, hp_bar_height))

        screen.draw.filled_rect(border_rect, (0, 0, 0))
        screen.draw.filled_rect(hp_rect, (255, 0, 0))

    def receber_dano(self, dano):
        self.current_hp -= dano
        if self.current_hp <= 0:
            self.current_hp = 0
            self.vivo = False
            # Para o inimigo morto, você precisa ter uma imagem 'dead.png'
            self.actor.image = 'dead'
            return True
        return False


# Herói
class Heroi(Personagem):
    def __init__(self, start_pos):
        hero_sprites = [f'hero_walk{i + 1}' for i in range(8)]
        super().__init__(start_pos, HERO_SPEED, HERO_MAX_HP, hero_sprites)
        self.experience = 0
        self.level = 1
        self.inventory = []

    def coletar_item(self, item):
        self.inventory.append(item)

    def atacar(self, inimigo):
        if not inimigo.vivo:
            return

        # Corrigido: Usar Rect para área de ataque em vez de inflate
        attack_rect = Rect((self.actor.x - 20, self.actor.y - 20), (40, 40))
        enemy_rect = Rect(inimigo.actor.topleft, inimigo.actor.size)

        if attack_rect.colliderect(enemy_rect):
            dano = random.randint(10, 20)
            if inimigo.receber_dano(dano):
                self.ganhar_experiencia(inimigo.experiencia_ao_morrer)

    def ganhar_experiencia(self, xp):
        self.experience += xp
        if self.experience >= self.level * 100:
            self.level += 1
            self.experience = 0
            self.max_hp += 20
            self.current_hp = self.max_hp


# Inimigo
class Inimigo(Personagem):
    def __init__(self, start_pos):
        enemy_sprite = ['enemy1']
        super().__init__(start_pos, INIMIGO_SPEED, 50, enemy_sprite)
        self.experiencia_ao_morrer = 50

    def seguir_heroi(self, heroi):
        if not self.vivo or not heroi.vivo:
            return
        dx = heroi.actor.x - self.actor.x
        dy = heroi.actor.y - self.actor.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist
        self.mover(dx, dy)


# --- Instâncias do jogo
hero = Heroi((WIDTH / 2, HEIGHT / 2))
inimigo = Inimigo((100, 100))


# --- Funções do Pygame Zero
def draw():
    screen.clear()
    hero.desenhar()
    inimigo.desenhar()
    screen.draw.text(f"XP: {hero.experience}  Nível: {hero.level}", (10, 10), color="white")


def update():
    dx, dy = 0, 0
    if keyboard.left:
        dx = -1
    if keyboard.right:
        dx = 1
    if keyboard.up:
        dy = -1
    if keyboard.down:
        dy = 1

    if dx != 0 or dy != 0:
        hero.mover(dx, dy)

    inimigo.seguir_heroi(hero)


def on_key_down(key):
    if key == keys.SPACE:
        hero.atacar(inimigo)

