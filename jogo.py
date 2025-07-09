import pygame
import sys
import random
import time
import os

start_time = time.time()



RANKING_FILE = "ranking.txt"
def salvar_ranking(novo_tempo):
    tempos = []
    # Lê tempos existentes
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "r") as f:
            for line in f:
                try:
                    tempos.append(float(line.strip()))
                except:
                    pass

    # Adiciona o novo tempo
    tempos.append(novo_tempo)
    tempos = sorted(tempos)
    # Salva os 5 melhores tempos
    with open(RANKING_FILE, "w") as f:
        for tempo in tempos[:5]:
            f.write(f"{tempo:.2f}\n")
    return tempos[:5]

def ler_ranking():
    tempos = []
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "r") as f:
            for line in f:
                try:
                    tempos.append(float(line.strip()))
                except:
                    pass
    return tempos

# Função para escalar um frame
def scale_frame(frame):
    return pygame.transform.scale(frame, (scaled_width, scaled_height))

def colisao_tile(x, y, mapa, tiles_solidos):
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    if 0 <= row < len(mapa) and 0 <= col < len(mapa[0]):
        return mapa[row][col] in tiles_solidos
    return False

# Inicializa o Pygame
pygame.init()

# Configurações da janela
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 950
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crystal Hunt")

TILE_SIZE = 64  # Tamanho do tile
tileset = pygame.image.load('assets/sprites/tileset.png').convert_alpha()
with open("map.txt", "r") as f:
    mapa = [line.strip() for line in f.readlines()]

tile_dict = {
    'P': (4, 0),
    'D': (4, 1),
    'B': (1, 2),
    'C': (3, 2),
    'G': (4, 2),
    'S': (5, 2),
    'E': (1, 6),
    'F': (2, 1),
    'H': (2, 2),
    'I': (2, 0),
    'J': (1, 0),
    'K': (1, 5),
}

# Cores
BLACK = (0, 0, 0)

# Fator de escala para aumentar o personagem
SCALE_FACTOR = 2.5 

# Carrega a spritesheets
title = pygame.image.load('assets/sprites/title.png').convert_alpha()
title = pygame.transform.scale(title, (title.get_width()/3, title.get_height()/3))  # Escala o título para preencher a tela
spritesheet = pygame.image.load('assets/sprites/player.png')
ranger = pygame.image.load('assets/sprites/ranger.png')
missile = pygame.image.load('assets/sprites/missile.png')
heart = pygame.image.load('assets/sprites/heart.png')
heart = pygame.transform.scale(heart, (64*3, 64*3))  # Escala o coração para um tamanho adequado
ranger_projectile = pygame.image.load('assets/sprites/arrow.png').convert_alpha()
ranger_projectile = pygame.transform.rotate(ranger_projectile, 90)  # Gira 90 graus para a esquerda
ranger_projectile = pygame.transform.scale(ranger_projectile, (64, 24))
shuriken = pygame.image.load('assets/sprites/shuriken.png').convert_alpha()
shuriken = pygame.transform.scale(shuriken, (48, 48))  # Escala o shuriken para um tamanho adequado

# Configurações da spritesheet 
frame_width = 32  # Largura da personagem
frame_height = 32  # Altura da personagem
scaled_width = int(frame_width * SCALE_FACTOR)  # Largura escalada
scaled_height = int(frame_height * SCALE_FACTOR)  # Altura escalada
cols = 10  # Número de colunas na spritesheet
rows = 10  # Número de linhas na spritesheet


def setup_nivel(nivel):
    enemy_rangers = []
    if nivel == 1:
        quantidade = 2
        proj_speed = 10
    elif nivel == 2:
        quantidade = 3
        proj_speed = 10
    else:
        quantidade = 4
        proj_speed = 16  # aumenta a velocidade no nível 3

    for i in range(quantidade):
        espacamento = 100
        x = SCREEN_WIDTH - scaled_width - 50
        y = 100 + i * (scaled_height + espacamento) + 70
        rect = pygame.Rect(x, y, scaled_width, scaled_height)
        enemy_rangers.append({
            'x': x,
            'y': y,
            'alive': True,
            'rect': rect,
            'death_frame': 0,
            'death_counter': 0,
            'animation_counter': 0,
            'current_frame': 0,
            'shoot_timer': random.randint(60, 180)
        })
    return enemy_rangers, proj_speed

missile_width = 256  # Largura do míssil
missile_height = 128  # Altura do míssil
cols_missile = 4  # Número de colunas do míssil
rows_missile = 1  # Número de linhas do míssil
frames_missile = {
    'missile_direita': [],
    'missile_esquerda': []
}  # Dicionário para armazenar os frames do míssil

#Cria os frames do shuriken
shuriken_frames = []
for i in range(4):
    shuriken_frames.append(pygame.transform.rotate(shuriken, 15*i))# Rotaciona o shuriken 

# Carrega a os frames da spritesheet dos cristais
blue = []
for i in range(4):
    blue.append(pygame.image.load(f'assets/sprites/Crystal_Animation/Blue/blue_crystal_000{i}.png').convert_alpha())
red = []
for i in range(4):
    red.append(pygame.image.load(f'assets/sprites/Crystal_Animation/Red/red_crystal_000{i}.png').convert_alpha())
green = []
for i in range(4):
    green.append(pygame.image.load(f'assets/sprites/Crystal_Animation/Green/Green_crystal_000{i}.png').convert_alpha())

# Prepara os frames do míssil
for row in range(rows_missile):
    for col in range(cols_missile):
        frame_rect = pygame.Rect(
            col * missile_width,
            row * missile_height,
            missile_width,
            missile_height
        )
        frame = missile.subsurface(frame_rect)
        scaled_missile = pygame.transform.scale(frame, (int(missile_width*0.5), int(missile_height*0.5)))
        frames_missile['missile_direita'].append(scaled_missile)
            
# Cria os frames para esquerda espelhando os da direita (já escalados)
frames_missile['missile_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames_missile['missile_direita']]

# Prepara os frames da personagem
frames_ranger = {
    'direita': [],
    'esquerda': [], 
    'attack_direita': [],
    'attack_esquerda': [],
    'morrer_direita': [],
    'morrer_esquerda': [],
    }  # Dicionário para armazenar os frames do ranger
frames = {
    'down_direita': [],
    'down_esquerda': [], 
    'direita': [], 
    'up_direita': [], 
    'up_esquerda': [],
    'stand_direita': [],
    'stand_esquerda': [],
    'attack_direita': [],
    'attack_esquerda': [],
}

# Divide a spritesheet em frames e aplica o scale
for row in range(rows):
    for col in range(cols):
        frame_rect = pygame.Rect(
            col * frame_width,
            row * frame_height,
            frame_width,
            frame_height
        )
        frame = spritesheet.subsurface(frame_rect)
        frame_ranger = ranger.subsurface(frame_rect)  # Obtém o frame correspondente do ranger
        scaled_ranger = scale_frame(frame_ranger)  # Aplica o scale ao frame do ranger
        scaled_frame = scale_frame(frame)  # Aplica o scale aqui
        
        # Organiza os frames
        if row == 7:
            frames['down_direita'].append(scaled_frame)
            frames['direita'].append(scaled_frame)
            frames['up_direita'].append(scaled_frame)
            frames_ranger['direita'].append(scaled_ranger)  # Adiciona o frame do ranger para esquerda
        elif row == 5:
            frames['stand_direita'].append(scaled_frame)  
        elif row == 8:
            frames['attack_direita'].append(scaled_frame)
            frames_ranger['attack_direita'].append(scaled_ranger)  # Adiciona o frame do ranger para ataque
        elif row == 9:
            frames_ranger['morrer_direita'].append(scaled_ranger)  # Adiciona o frame do ranger para morrer
# Cria os frames para esquerda espelhando os da direita (já escalados)
frames['esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['direita']]
frames['attack_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['attack_direita']]
frames['stand_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['stand_direita']]
frames['down_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['down_direita']]
frames['up_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['up_direita']]
frames_ranger['esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames_ranger['direita']]
frames_ranger['attack_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames_ranger['attack_direita']]
frames_ranger['morrer_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames_ranger['morrer_direita']]

def tela_final(result):
    font = pygame.font.SysFont(None, 40)
    if result == 'gameover':
        text = font.render("Game Over! Pressione R para reiniciar ou ESC para sair.", True, (255, 0, 0))
    else:
        text = font.render("Você venceu! Pressione R para reiniciar ou ESC para sair.", True, (0, 255, 0))
        tempo_final = time.time() - start_time
        ranking = salvar_ranking(tempo_final)
        print("--- %s seconds ---" % tempo_final)
    screen.fill((0, 0, 0))
    # Desenha o mapa de tiles
    for row_idx, row in enumerate(mapa):
        for col_idx, tile_char in enumerate(row):
            if tile_char in tile_dict:
                tile_x, tile_y = tile_dict[tile_char]
                tile_rect = pygame.Rect(tile_x * 32, tile_y * 32, 32, 32)  # 32 é o tamanho original do tile no tileset
                tile_img = tileset.subsurface(tile_rect)
                tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))  # Escala para o novo tamanho
                screen.blit(tile_img, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))

    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()//2))

    # Exibe o ranking se venceu
    if result == 'win':
        font_ranking = pygame.font.SysFont(None, 32)
        ranking = ler_ranking()
        for i, tempo in enumerate(ranking):
            rank_text = font_ranking.render(f"{i+1}º: {tempo:.2f} segundos", True, (255, 255, 0))
            screen.blit(rank_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 40 + i*35))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

tiles_solidos = ['P', 'F', 'K', 'J', 'I', 'H']

# Loop principal do jogo
def main_game():
    DEBUG = False  # Flag para ativar/desativar o modo debug
    # Variáveis do jogo
    nivel = 1
    max_niveis = 3
    enemy_rangers, ranger_missile_speed = setup_nivel(nivel)
    ranger_missiles = []
    missiles = []
    shurikens = []
    shuriken_launchers = []
    vidas = 3

    cristal_ativo = False
    cristal_pego = False
    cristal_x = SCREEN_WIDTH // 2 - 64
    cristal_y = SCREEN_HEIGHT // 2 - 64
    cristal_frame = 0
    cristal_anim_counter = 0
    cristal_tipo = None
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2
    player_speed = 5
    player_direction = 'down'
    current_frame = 0
    animation_speed = 0.15
    animation_counter = 0
    is_attacking = False
    attack_animation_speed = 0.2
    attack_frame = 0
    missile_speed = 10
    attack_animation_length = len(frames['attack_direita']) if len(frames['attack_direita']) > 0 else 1
    missile_animation_speed = 0.2  # Define a velocidade da animação do míssil
    shuriken_speed = 8 # Velocidade do shuriken
    facing = 'direita'
    running = True

    clock = pygame.time.Clock()

    while running:
        # Limpa a tela
        screen.fill(BLACK)

        # Desenha o mapa de tiles
        for row_idx, row in enumerate(mapa):
            for col_idx, tile_char in enumerate(row):
                if tile_char in tile_dict:
                    tile_x, tile_y = tile_dict[tile_char]
                    tile_rect = pygame.Rect(tile_x * 32, tile_y * 32, 32, 32)  # 32 é o tamanho original do tile no tileset
                    tile_img = tileset.subsurface(tile_rect)
                    tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))  # Escala para o novo tamanho
                    screen.blit(tile_img, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if not is_attacking:  # Só permite atacar se não estiver atacando
                    is_attacking = True
                    attack_frame = 0
                    # Adiciona um novo míssil quando o jogador ataca
                    missile_rect = pygame.Rect(player_x, player_y, 112, 32)  
                    missiles.append({
                        'x': player_x,
                        'y': player_y,
                        'direction': facing,
                        'frame': 0,
                        'animation_counter': 0,
                        'rect': missile_rect
                    })

        # Movimento com WASD (desativado durante o ataque)
        keys = pygame.key.get_pressed()
        if not is_attacking:
            player_direction = f'stand_{facing}' # Padrão quando não está se movendo
            
            # Cima
            if keys[pygame.K_w]:
                new_y = player_y - player_speed
                if not colisao_tile(player_x, new_y, mapa, tiles_solidos) and not colisao_tile(player_x + scaled_width - 1, new_y, mapa, tiles_solidos):
                    player_y = new_y
                    player_direction = f'up_{facing}'
            # Baixo
            if keys[pygame.K_s]:
                new_y = player_y + player_speed
                if not colisao_tile(player_x, new_y + scaled_height - 1, mapa, tiles_solidos) and not colisao_tile(player_x + scaled_width - 1, new_y + scaled_height - 1, mapa, tiles_solidos):
                    player_y = new_y
                    player_direction = f'down_{facing}'
            # Esquerda
            if keys[pygame.K_a]:
                facing = 'esquerda'
                new_x = player_x - player_speed
                if not colisao_tile(new_x, player_y, mapa, tiles_solidos) and not colisao_tile(new_x, player_y + scaled_height - 1, mapa, tiles_solidos):
                    player_x = new_x
                    player_direction = f'{facing}'
            # Direita
            if keys[pygame.K_d]:
                facing = 'direita'
                new_x = player_x + player_speed
                if not colisao_tile(new_x + scaled_width - 1, player_y, mapa, tiles_solidos) and not colisao_tile(new_x + scaled_width - 1, player_y + scaled_height - 1, mapa, tiles_solidos):
                    player_x = new_x
                    player_direction = f'{facing}'
        # Atualiza a posição do retângulo do jogador
        player_rect = pygame.Rect(player_x, player_y, scaled_width, scaled_height)

        # Atualiza a animação de movimento ou ataque
        if is_attacking:
            # Animação de ataque
            animation_counter += attack_animation_speed
            if animation_counter >= 1:
                animation_counter = 0
                attack_frame += 1
                if attack_frame >= attack_animation_length:
                    is_attacking = False
                    attack_frame = 0
        else:
            # Animação de movimento normal
            animation_counter += animation_speed
            if animation_counter >= 1:
                animation_counter = 0
                if len(frames[player_direction]) > 0:
                    current_frame = (current_frame + 1) % len(frames[player_direction])
        
        for shuriken in shurikens:
            shuriken['y'] -= shuriken_speed  # Move para cima
            shuriken['anim_counter'] += 0.2
            if shuriken['anim_counter'] >= 1:
                shuriken['anim_counter'] = 0
                shuriken['frame'] = (shuriken['frame'] + 1) % len(shuriken_frames)
            shuriken['rect'].y = shuriken['y']
            shuriken['rect'].x = shuriken['x']

            # Remove se sair da tela
            if shuriken['y'] < -shuriken_frames[0].get_height():
                shurikens.remove(shuriken)
                continue

            # Remove se colidir com tile sólido
            if colisao_tile(shuriken['x'], shuriken['y'], mapa, tiles_solidos):
                shurikens.remove(shuriken)
                continue

            # Dano ao jogador
            if shuriken['rect'].colliderect(player_rect):
                vidas -= 1
                shurikens.remove(shuriken)
                if vidas <= 0:
                    return 'gameover'
                
        # Atualiza a animação dos rangers inimigos
        for ranger in enemy_rangers:
            if ranger['alive']:
                ranger['shoot_timer'] -= 1
                if ranger['shoot_timer'] <= 0:
                    ranger['attacking'] = True
                    ranger['current_frame'] = 0
                    ranger['animation_counter'] = 0
                    ranger['shoot_timer'] = random.randint(60, 180)  # Reinicia temporizador

            if ranger.get('attacking', False):
                ranger['animation_counter'] += animation_speed
                if ranger['animation_counter'] >= 1:
                    ranger['animation_counter'] = 0
                    ranger['current_frame'] += 1
                    # Dispara a flecha 2 frames antes do fim
                    if ranger['current_frame'] == len(frames_ranger['attack_esquerda']) - 2:
                        missile_x = ranger['x']
                        missile_y = ranger['y'] + scaled_height // 2 - missile_height // 6
                        ranger_missiles.append({
                            'x': missile_x,
                            'y': missile_y,
                            'rect': pygame.Rect(missile_x, missile_y, missile_width//4, missile_height//4),
                            'frame': 0
                        })
                    # Finaliza ataque normalmente
                    if ranger['current_frame'] >= len(frames_ranger['attack_esquerda']):
                        ranger['attacking'] = False
                        ranger['current_frame'] = 0
                else:
                    ranger['animation_counter'] += animation_speed
                    if ranger['animation_counter'] >= 1:
                        ranger['animation_counter'] = 0
                        ranger['current_frame'] = (ranger['current_frame'] + 1) % len(frames_ranger['attack_esquerda'])

            else:
                if ranger['death_frame'] < len(frames_ranger['morrer_esquerda']) - 1:
                    ranger['death_counter'] += 0.2
                    if ranger['death_counter'] >= 1:
                        ranger['death_counter'] = 0
                        ranger['death_frame'] += 1

        # Atualiza mísseis dos rangers
        for missile in ranger_missiles:
            missile['x'] -= ranger_missile_speed  # Usa a velocidade do nível
            missile['rect'].x = missile['x']
            # Verifica colisão com tile sólido
            if colisao_tile(missile['x'], missile['y'], mapa, tiles_solidos):
                ranger_missiles.remove(missile)
                continue
            if missile['x'] < -missile_width:
                ranger_missiles.remove(missile)

        # Atualiza os mísseis
        for missile_data in missiles:
            # Atualiza a posição do míssil
            if missile_data['direction'] == 'direita':
                missile_data['x'] += missile_speed
                missile_data['rect'].x = missile_data['x'] + 25
            else:
                missile_data['x'] -= missile_speed
                missile_data['rect'].x = missile_data['x'] - 50
            missile_data['rect'].y = missile_data['y'] + 30

            # Atualiza a animação do míssil
            missile_data['animation_counter'] += missile_animation_speed
            if missile_data['animation_counter'] >= 1:
                missile_data['animation_counter'] = 0
                missile_data['frame'] = (missile_data['frame'] + 1) % len(frames_missile['missile_direita'])
            
            # Verifica colisão com os rangers inimigos
            for ranger in enemy_rangers:
                if ranger['alive'] and missile_data['rect'].colliderect(ranger['rect']):
                    ranger['alive'] = False  # Mata o ranger
                    ranger['death_frame'] = 0
                    ranger['death_counter'] = 0
                    if missile_data in missiles:
                        missiles.remove(missile_data)
                    break

            # Remove mísseis que saíram da tela
            if missile_data['x'] < -100 or missile_data['x'] > SCREEN_WIDTH + 100:
                missiles.remove(missile_data)

        # Desenha os mísseis
        for missile_data in missiles:
            direction_key = f'missile_{missile_data["direction"]}'
            missile_img = frames_missile[direction_key][missile_data['frame']]
            if missile_data['direction'] == 'direita':
                screen.blit(missile_img, (missile_data['x']+25, missile_data['y']+20))
            else:
                screen.blit(missile_img, (missile_data['x']-50, missile_data['y']+20))
        # Desenha mísseis dos rangers
        for missile in ranger_missiles:
            screen.blit(ranger_projectile, (missile['x'], missile['y']))
            if DEBUG:
                pygame.draw.rect(screen, (255, 0, 0), missile['rect'], 2)  # Caixa de colisão

        # Desenhe as shurikens:
        for shuriken in shurikens:
            screen.blit(shuriken_frames[shuriken['frame']], (shuriken['x'], shuriken['y']))
        # Desenha o personagem
        if is_attacking:
            # Escolhe a animação de ataque baseada na direção
            attack_direction = f'attack_{facing}'
            player_img = frames[attack_direction][attack_frame]
        else:
            player_img = frames[player_direction][current_frame]
        
        screen.blit(player_img, (player_x, player_y))

        rangers_to_remove = []

        # Desenha os rangers inimigos
        for ranger in enemy_rangers:
            if ranger['alive']:
                if ranger.get('attacking', False):
                    ranger_attack_img = frames_ranger['attack_esquerda'][ranger['current_frame'] % len(frames_ranger['attack_esquerda'])]
                else:
                    ranger_attack_img = frames_ranger['attack_esquerda'][ranger['current_frame'] % len(frames_ranger['attack_esquerda'])]
                screen.blit(ranger_attack_img, (ranger['x'], ranger['y']))
                if DEBUG:
                    pygame.draw.rect(screen, (0, 0, 255), ranger['rect'], 2)
            elif ranger['death_frame'] < len(frames_ranger['morrer_esquerda']):
                ranger_death_img = frames_ranger['morrer_esquerda'][ranger['death_frame']]
                screen.blit(ranger_death_img, (ranger['x'], ranger['y']))
                if DEBUG:
                    pygame.draw.rect(screen, (0, 0, 255), ranger['rect'], 2)
            if not ranger['alive'] and ranger['death_frame'] >= len(frames_ranger['morrer_esquerda']):
                rangers_to_remove.append(ranger)
        for ranger in rangers_to_remove:
            enemy_rangers.remove(ranger)

        # Verifica colisão dos projéteis dos rangers com o jogador
        for missile in ranger_missiles:
            if missile['rect'].colliderect(player_rect):
                vidas -= 1
                ranger_missiles.remove(missile)
                if vidas <= 0:
                    return 'gameover'

        # Verifica se todos os rangers morreram para ativar o cristal da fase
        if nivel == 1 and all(not ranger['alive'] for ranger in enemy_rangers) and not cristal_pego and not cristal_ativo:
            cristal_ativo = True
            cristal_tipo = 'blue'
        if nivel == 2 and all(not ranger['alive'] for ranger in enemy_rangers) and not cristal_pego and not cristal_ativo:
            cristal_ativo = True
            cristal_tipo = 'red'
        if nivel == 3 and all(not ranger['alive'] for ranger in enemy_rangers) and not cristal_pego and not cristal_ativo:
            cristal_ativo = True
            cristal_tipo = 'green'

        # Atualiza e desenha as shurikens automáticas    
        if nivel >= 2:
            for launcher in shuriken_launchers:
                launcher['timer'] -= 1
                if launcher['timer'] <= 0:
                    x_shuriken = random.randint(0, SCREEN_WIDTH - shuriken_frames[0].get_width())
                    y_shuriken = SCREEN_HEIGHT - shuriken_frames[0].get_height()
                    shurikens.append({
                        'x': x_shuriken,
                        'y': y_shuriken,
                        'frame': 0,
                        'anim_counter': 0,
                        'rect': pygame.Rect(
                            x_shuriken, y_shuriken, shuriken_frames[0].get_width(), shuriken_frames[0].get_height()
    )
})
                    launcher['timer'] = 90  # 1,5 segundos
        # Exibe e anima o cristal se ativo
        if cristal_ativo and not cristal_pego:
            cristal_anim_counter += 0.15
            if cristal_anim_counter >= 1:
                cristal_anim_counter = 0
                cristal_frame = (cristal_frame + 1) % 4
            # Escolhe o sprite do cristal
            if cristal_tipo == 'blue':
                cristal_sprite = blue[cristal_frame]
            elif cristal_tipo == 'red':
                cristal_sprite = red[cristal_frame]
            elif cristal_tipo == 'green':
                cristal_sprite = green[cristal_frame]

            screen.blit(cristal_sprite, (cristal_x, cristal_y))
            cristal_rect = pygame.Rect(cristal_x, cristal_y, cristal_sprite.get_width(), cristal_sprite.get_height())
            if player_rect.colliderect(cristal_rect):
                cristal_pego = True
                cristal_ativo = False
                if nivel < max_niveis:
                    nivel += 1
                    enemy_rangers, ranger_missile_speed = setup_nivel(nivel)
                    ranger_missiles.clear()
                    cristal_pego = False  # Permite pegar o próximo cristal
                    cristal_frame = 0
                    cristal_anim_counter = 0
                    cristal_tipo = None

                    # Reinicializa as shurikens e lançadores
                    shurikens.clear()
                    shuriken_launchers.clear()
                    shuriken_launchers = []

                else:
                    return 'win'
                
                if nivel == 2:
                    for i in range(2):
                        shuriken_launchers.append({
                            'x': int((i+1) * SCREEN_WIDTH // 3),
                            'timer': i * 45
                        })
                elif nivel == 3:
                    for i in range(3):
                        shuriken_launchers.append({
                            'x': int((i+1) * SCREEN_WIDTH // 4),
                            'timer': i * 45
                        })

            
        # Desenha as vidas
        for i in range(vidas):
            screen.blit(heart, (10 + i*75, 10))  # Desenha o coração no canto superior esquerdo

        # Mantém o jogador dentro da tela (agora usando as dimensões escaladas)
        player_x = max(0, min(player_x, SCREEN_WIDTH - scaled_width))
        player_y = max(0, min(player_y, SCREEN_HEIGHT - scaled_height))


        if DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), player_rect, 2)  # jogador
            for missile in missiles:
                pygame.draw.rect(screen, (0, 255, 0), missile['rect'], 2)  # mísseis

        # Atualiza a tela
        pygame.display.flip()
        
        # Controla o FPS
        clock.tick(60)

    # Encerra o Pygame
    pygame.quit()
    sys.exit()

def menu_inicial():
    font_small = pygame.font.SysFont(None, 50)
    opcoes = ["Iniciar", "Ranking", "Sair"]
    selecionado = 0

    while True:
        screen.fill((0, 0, 0))
        # Desenha o mapa de tiles
        for row_idx, row in enumerate(mapa):
            for col_idx, tile_char in enumerate(row):
                if tile_char in tile_dict:
                    tile_x, tile_y = tile_dict[tile_char]
                    tile_rect = pygame.Rect(tile_x * 32, tile_y * 32, 32, 32)  # 32 é o tamanho original do tile no tileset
                    tile_img = tileset.subsurface(tile_rect)
                    tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))  # Escala para o novo tamanho
                    screen.blit(tile_img, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))

        # Desenha o título
        screen.blit(title, (SCREEN_WIDTH//2 -title.get_width()//2, -100))

        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            texto = font_small.render(opcao, True, cor)
            screen.blit(texto, (SCREEN_WIDTH//2 - texto.get_width()//2, 350 + i*80))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                elif event.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if opcoes[selecionado] == "Iniciar":
                        return "iniciar"
                    elif opcoes[selecionado] == "Ranking":
                        return "ranking"
                    elif opcoes[selecionado] == "Sair":
                        pygame.quit()
                        sys.exit()

def mostrar_ranking():
    font = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 40)
    ranking = ler_ranking()
    screen.fill((0, 0, 0))
    # Desenha o mapa de tiles
    for row_idx, row in enumerate(mapa):
        for col_idx, tile_char in enumerate(row):
            if tile_char in tile_dict:
                tile_x, tile_y = tile_dict[tile_char]
                tile_rect = pygame.Rect(tile_x * 32, tile_y * 32, 32, 32)
                tile_img = tileset.subsurface(tile_rect)
                tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))  # Escala para o novo tamanho
                screen.blit(tile_img, (col_idx * TILE_SIZE, row_idx * TILE_SIZE))

    titulo = font.render("Ranking", True, (0, 255, 255))
    screen.blit(titulo, (SCREEN_WIDTH//2 - titulo.get_width()//2, 120))
    if ranking:
        for i, tempo in enumerate(ranking):
            texto = font_small.render(f"{i+1}º: {tempo:.2f} segundos", True, (255, 255, 0))
            screen.blit(texto, (SCREEN_WIDTH//2 - texto.get_width()//2, 250 + i*50))
    else:
        texto = font_small.render("Nenhum tempo registrado.", True, (255, 255, 255))
        screen.blit(texto, (SCREEN_WIDTH//2 - texto.get_width()//2, 300))
    texto_voltar = font_small.render("Pressione ESC para voltar", True, (200, 200, 200))
    screen.blit(texto_voltar, (SCREEN_WIDTH//2 - texto_voltar.get_width()//2, SCREEN_HEIGHT - 100))
    pygame.display.flip()
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                esperando = False

# Loop externo:
while True:
    escolha = menu_inicial()
    if escolha == "iniciar":
        result = main_game()
        tela_final(result)
    elif escolha == "ranking":
        mostrar_ranking()
    else:
        break