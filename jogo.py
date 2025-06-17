import pygame
import sys

# Função para escalar um frame
def scale_frame(frame):
    return pygame.transform.scale(frame, (scaled_width, scaled_height))

# Inicializa o Pygame
pygame.init()

# Configurações da janela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Movimento com Spritesheet - WASD")

# Cores
BLACK = (0, 0, 0)

# Fator de escala para aumentar o personagem
SCALE_FACTOR = 3 

# Carrega a spritesheets
spritesheet = pygame.image.load('assets/sprites/player.png')
missile = pygame.image.load('assets/sprites/missile.png')
heart = pygame.image.load('assets/sprites/heart.png')
heart = pygame.transform.scale(heart, (64*3, 64*3))  # Escala o coração para um tamanho adequado

# Configurações da spritesheet 
frame_width = 32  # Largura da personagem
frame_height = 32  # Altura da personagem
scaled_width = int(frame_width * SCALE_FACTOR)  # Largura escalada
scaled_height = int(frame_height * SCALE_FACTOR)  # Altura escalada
cols = 10  # Número de colunas na spritesheet
rows = 10  # Número de linhas na spritesheet

missile_width = int(91/3)  # Largura do míssil
missile_height = int(103/3)  # Altura do míssil
cols_missile = 15  # Número de colunas do míssil
rows_missile = 16  # Número de linhas do míssil
frames_missile = {
    'missile_direita': [],
    'missile_esquerda': []
                  } 

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
        if row == 12:
            frames_missile['missile_direita'].append(frame)
frames_missile['missile_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames_missile['missile_direita']]

# Prepara os frames da personagem
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
        scaled_frame = scale_frame(frame)  # Aplica o scale aqui
        
        # Organiza os frames
        if row == 7:
            frames['down_direita'].append(scaled_frame)
            frames['direita'].append(scaled_frame)
            frames['up_direita'].append(scaled_frame)
        elif row == 5:
            frames['stand_direita'].append(scaled_frame)  
        elif row == 8:
            frames['attack_direita'].append(scaled_frame)

# Cria os frames para esquerda espelhando os da direita (já escalados)
frames['esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['direita']]
frames['attack_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['attack_direita']]
frames['stand_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['stand_direita']]
frames['down_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['down_direita']]
frames['up_esquerda'] = [pygame.transform.flip(frame, True, False) for frame in frames['up_direita']]

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

# Relógio para controlar o FPS
clock = pygame.time.Clock()

# Variável para controlar a direção do personagem
facing = 'direita'

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
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not is_attacking:
            is_attacking = True
            attack_frame = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                vidas -= 1
                if vidas <= 0:
                    running = False
    
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
    
    # Desenha o personagem
    if is_attacking:
        # Escolhe a animação de ataque baseada na direção
        attack_direction = f'attack_{facing}'
        player_img = frames[attack_direction][attack_frame]
    else:
        player_img = frames[player_direction][current_frame]
    
    screen.blit(player_img, (player_x, player_y))
    for i in range(vidas):
        screen.blit(heart, (-40+i*75, -40))  # Desenha o coração no canto superior esquerdo

    # Verifica se a tecla Q foi pressionada (apenas uma vez por pressionamento)

    # Mantém o jogador dentro da tela (agora usando as dimensões escaladas)
    player_x = max(0, min(player_x, SCREEN_WIDTH - scaled_width))
    player_y = max(0, min(player_y, SCREEN_HEIGHT - scaled_height))
    
    # Atualiza a tela
    pygame.display.flip()
    
    # Controla o FPS
    clock.tick(60)

# Encerra o Pygame
pygame.quit()
sys.exit()