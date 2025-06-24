import pygame
import sys
import random

# Função para escalar um frame
def scale_frame(frame):
    return pygame.transform.scale(frame, (scaled_width, scaled_height))

# Inicializa o Pygame
pygame.init()

# Configurações da janela
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Movimento com Spritesheet - WASD")

# Cores
BLACK = (0, 0, 0)

# Fator de escala para aumentar o personagem
SCALE_FACTOR = 3 

# Carrega a spritesheets
spritesheet = pygame.image.load('assets/sprites/player.png')
ranger = pygame.image.load('assets/sprites/ranger.png')
missile = pygame.image.load('assets/sprites/missile.png')
heart = pygame.image.load('assets/sprites/heart.png')
heart = pygame.transform.scale(heart, (64*3, 64*3))  # Escala o coração para um tamanho adequado
ranger_projectile = pygame.image.load('assets/sprites/arrow.png').convert_alpha()
ranger_projectile = pygame.transform.rotate(ranger_projectile, 90)  # Gira 90 graus para a esquerda
ranger_projectile = pygame.transform.scale(ranger_projectile, (64, 24))

# Configurações da spritesheet 
frame_width = 32  # Largura da personagem
frame_height = 32  # Altura da personagem
scaled_width = int(frame_width * SCALE_FACTOR)  # Largura escalada
scaled_height = int(frame_height * SCALE_FACTOR)  # Altura escalada
cols = 10  # Número de colunas na spritesheet
rows = 10  # Número de linhas na spritesheet

missile_width = 256  # Largura do míssil
missile_height = 128  # Altura do míssil
cols_missile = 4  # Número de colunas do míssil
rows_missile = 1  # Número de linhas do míssil
frames_missile = {
    'missile_direita': [],
    'missile_esquerda': []
}  # Dicionário para armazenar os frames do míssil
ranger_missiles = []
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
        scaled_missile = pygame.transform.scale(frame, (missile_width*0.5, missile_height*0.5))
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

# Variáveis do jogador
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_speed = 5
player_direction = 'down'
current_frame = 0
animation_speed = 0.15
animation_counter = 0

# Variáveis de ataque
is_attacking = False
attack_animation_speed = 0.2
attack_frame = 0
attack_animation_length = len(frames['attack_direita'])
attack_cooldown = 0

# Variáveis do míssil
missiles = []  # Lista para armazenar os mísseis ativos
missile_speed = 10
missile_animation_speed = 0.2
missile_frame = 0

# Relógio para controlar o FPS
clock = pygame.time.Clock()

# Variável para controlar a direção do personagem
facing = 'direita'

# Lista de rangers inimigos
enemy_rangers = []
for i in range(3):
    x = SCREEN_WIDTH - scaled_width - 50
    y = 100 + i * (scaled_height + 150)
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
        'shoot_timer': random.randint(60, 180)  # 1 a 3 segundos (considerando 60 FPS)
    })

# Loop principal do jogo
running = True
vidas = 3  # Variável para o número de vidas
while running:
    # Limpa a tela
    screen.fill(BLACK)
    
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:#event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not is_attacking:
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
        player_direction = f'stand_{facing}'  # Padrão quando não está se movendo
        
        if keys[pygame.K_w]:  # Cima
            player_y -= player_speed
            player_direction = f'up_{facing}'
        if keys[pygame.K_s]:  # Baixo
            player_y += player_speed
            player_direction = f'down_{facing}'
        if keys[pygame.K_a]:  # Esquerda
            facing = 'esquerda'
            player_x -= player_speed
            player_direction = 'esquerda'
        if keys[pygame.K_d]:  # Direita
            facing = 'direita'
            player_x += player_speed
            player_direction = 'direita'
    
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
            current_frame = (current_frame + 1) % len(frames[player_direction])
    
    # Atualiza a animação dos rangers inimigos
    for ranger in enemy_rangers:
        if ranger['alive']:
            ranger['animation_counter'] += animation_speed
            if ranger['animation_counter'] >= 1:
                ranger['animation_counter'] = 0
                ranger['current_frame'] = (ranger['current_frame'] + 1) % len(frames_ranger['attack_esquerda'])
            # Atualiza temporizador de tiro
            ranger['shoot_timer'] -= 1
            if ranger['shoot_timer'] <= 0:
                # Ranger atira um míssil para a esquerda
                missile_x = ranger['x']
                missile_y = ranger['y'] + scaled_height // 2 - missile_height // 6
                ranger_missiles.append({
                    'x': missile_x,
                    'y': missile_y,
                    'rect': pygame.Rect(missile_x, missile_y, missile_width//4, missile_height//4),
                    'frame': 0
                })
                ranger['shoot_timer'] = random.randint(60, 180)  # Reinicia temporizador

        else:
            if ranger['death_frame'] < len(frames_ranger['morrer_esquerda']) - 1:
                ranger['death_counter'] += 0.2
                if ranger['death_counter'] >= 1:
                    ranger['death_counter'] = 0
                    ranger['death_frame'] += 1
    # Atualiza mísseis dos rangers
    for missile in ranger_missiles[:]:
        missile['x'] -= missile_speed  # Move para a esquerda
        missile['rect'].x = missile['x']
        # Remove se sair da tela
        if missile['x'] < -missile_width:
            ranger_missiles.remove(missile)

    # Verifica colisão dos projéteis dos rangers com o jogador
    for missile in ranger_missiles[:]:
        if missile['rect'].colliderect(player_rect):
            vidas -= 1
            ranger_missiles.remove(missile)
            if vidas <= 0:
                running = False
    # Atualiza os mísseis
    for missile_data in missiles[:]:
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
        pygame.draw.rect(screen, (255, 0, 0), missile['rect'], 2)  # Caixa de colisão

    # Desenha o personagem
    if is_attacking:
        # Escolhe a animação de ataque baseada na direção
        attack_direction = f'attack_{facing}'
        player_img = frames[attack_direction][attack_frame]
    else:
        player_img = frames[player_direction][current_frame]
    
    screen.blit(player_img, (player_x, player_y))

    # Adiciona 3 sprites do ranger atacando para a esquerda no lado direito da tela
    for ranger in enemy_rangers:
        if ranger['alive']:
            ranger_attack_img = frames_ranger['attack_esquerda'][ranger['current_frame'] % len(frames_ranger['attack_esquerda'])]
            screen.blit(ranger_attack_img, (ranger['x'], ranger['y']))
            pygame.draw.rect(screen, (0, 0, 255), ranger['rect'], 2)
        elif ranger['death_frame'] < len(frames_ranger['morrer_esquerda']):
            ranger_death_img = frames_ranger['morrer_esquerda'][ranger['death_frame']]
            screen.blit(ranger_death_img, (ranger['x'], ranger['y']))
            pygame.draw.rect(screen, (0, 0, 255), ranger['rect'], 2)

    if not ranger['alive'] and ranger['death_frame'] >= len(frames_ranger['morrer_esquerda']):
        ranger['rect'].width = 0
        ranger['rect'].height = 0
    # Atualiza a posição do retângulo do jogador
    player_rect = pygame.Rect(player_x, player_y, scaled_width, scaled_height)
    
    # Desenha as vidas
    for i in range(vidas):
        screen.blit(heart, (-40+i*75, -40))  # Desenha o coração no canto superior esquerdo

    # Mantém o jogador dentro da tela (agora usando as dimensões escaladas)
    player_x = max(0, min(player_x, SCREEN_WIDTH - scaled_width))
    player_y = max(0, min(player_y, SCREEN_HEIGHT - scaled_height))
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