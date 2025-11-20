import pygame
import random
import time
import sys

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAX_HP = 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (200, 0, 200)

# Game states
MAIN_MENU = 0
STORY_CHOICE = 1
COMBAT = 2
GAME_OVER = 3
VICTORY = 4

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game of Guidance")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("arial", 48)
menu_font = pygame.font.SysFont("arial", 36)
text_font = pygame.font.SysFont("arial", 24)

class Player:
    def __init__(self):
        self.hp = MAX_HP
        self.sanity = 100
        self.choice = 0

class Enemy:
    def __init__(self, enemy_type=0):
        self.hp = MAX_HP
        self.type = enemy_type  # 0: Thought Demon, 1: Fear Entity, 2: Doubt Shadow
        self.names = ["Thought Demon", "Fear Entity", "Doubt Shadow"]
        self.name = self.names[enemy_type]
        self.attack_msgs = [
            "The Thought Demon overwhelms you with negative thinking!",
            "The Fear Entity paralyzes you with dread!",
            "The Doubt Shadow undermines your confidence!"
        ]

# Game variables
current_state = MAIN_MENU
player = Player()
enemy = None
story_progress = 0
combat_turn = 0  # 0 for player's turn, 1 for enemy's turn
message = ""
message_timer = 0

def reset_game():
    global player, enemy, story_progress, combat_turn, current_state
    player = Player()
    enemy = None
    story_progress = 0
    combat_turn = 0
    current_state = MAIN_MENU

def draw_text(text, font, color, x, y, centered=False):
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect

def draw_health_bar(x, y, width, height, hp, max_hp, name):
    # Draw background
    pygame.draw.rect(screen, RED, (x, y, width, height))
    # Draw health
    health_width = int((hp / max_hp) * width)
    pygame.draw.rect(screen, GREEN, (x, y, health_width, height))
    # Draw border
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
    # Draw name
    draw_text(name, text_font, WHITE, x, y - 25)

def show_main_menu():
    screen.fill(BLACK)
    draw_text("Game of Guidance", title_font, PURPLE, SCREEN_WIDTH//2, 100, True)
    draw_text("A Psychological Journey", menu_font, BLUE, SCREEN_WIDTH//2, 180, True)
    
    # Start button
    start_rect = draw_text("Begin Journey", menu_font, WHITE, SCREEN_WIDTH//2, 300, True)
    exit_rect = draw_text("Exit", menu_font, WHITE, SCREEN_WIDTH//2, 370, True)
    
    return start_rect, exit_rect

def show_story_choice():
    screen.fill(BLACK)
    draw_health_bar(50, 50, 200, 30, player.hp, MAX_HP, "Your Willpower")
    
    if story_progress == 1:
        draw_text("Where am I?", menu_font, WHITE, SCREEN_WIDTH//2, 150, True)
        option1 = draw_text("1) Inside your mind", text_font, BLUE, SCREEN_WIDTH//2, 200, True)
        option2 = draw_text("2) Inside a nightmare", text_font, BLUE, SCREEN_WIDTH//2, 240, True)
        return [option1, option2]
    elif story_progress == 2:
        draw_text("Mind? Am I overpowered by my thoughts?", text_font, WHITE, SCREEN_WIDTH//2, 150, True)
        draw_text("You have two options:", text_font, WHITE, SCREEN_WIDTH//2, 190, True)
        option1 = draw_text("1) Yes, your thoughts have brought you here", text_font, BLUE, SCREEN_WIDTH//2, 240, True)
        option2 = draw_text("2) No, you are here to fight your inner demons", text_font, BLUE, SCREEN_WIDTH//2, 280, True)
        return [option1, option2]
    elif story_progress == 3:
        draw_text("You have chosen to run away from your inner demons.", text_font, WHITE, SCREEN_WIDTH//2, 150, True)
        draw_text("You have two options:", text_font, WHITE, SCREEN_WIDTH//2, 190, True)
        option1 = draw_text("1) Face your fears", text_font, BLUE, SCREEN_WIDTH//2, 240, True)
        option2 = draw_text("2) Continue running", text_font, BLUE, SCREEN_WIDTH//2, 280, True)
        return [option1, option2]

def show_combat():
    screen.fill(BLACK)
    draw_health_bar(50, 50, 200, 30, player.hp, MAX_HP, "Your Willpower")
    draw_health_bar(SCREEN_WIDTH-250, 50, 200, 30, enemy.hp, MAX_HP, enemy.name)
    
    if combat_turn == 0:
        draw_text(f"{enemy.name} stands before you...", text_font, WHITE, SCREEN_WIDTH//2, 150, True)
        draw_text("Your turn - choose an attack:", menu_font, GREEN, SCREEN_WIDTH//2, 200, True)
        
        attack1 = draw_text("1) Rational Strike", text_font, WHITE, SCREEN_WIDTH//2, 250, True)
        attack2 = draw_text("2) Courageous Blow", text_font, WHITE, SCREEN_WIDTH//2, 290, True)
        attack3 = draw_text("3) Focused Attack", text_font, WHITE, SCREEN_WIDTH//2, 330, True)
        attack4 = draw_text("4) Defensive Maneuver", text_font, WHITE, SCREEN_WIDTH//2, 370, True)
        
        return [attack1, attack2, attack3, attack4]
    else:
        draw_text("Enemy's turn...", menu_font, RED, SCREEN_WIDTH//2, 250, True)
        return []

def show_game_over():
    screen.fill(BLACK)
    draw_text("GAME OVER", title_font, RED, SCREEN_WIDTH//2, 150, True)
    
    if story_progress == 3 and player.choice == 2:
        draw_text("You chose to keep running from your demons...", text_font, WHITE, SCREEN_WIDTH//2, 230, True)
        draw_text("They will always be with you.", text_font, WHITE, SCREEN_WIDTH//2, 270, True)
    else:
        draw_text("Your willpower was broken.", text_font, WHITE, SCREEN_WIDTH//2, 230, True)
        draw_text("The inner demons have won.", text_font, WHITE, SCREEN_WIDTH//2, 270, True)
    
    continue_rect = draw_text("Press any key to continue", text_font, WHITE, SCREEN_WIDTH//2, 350, True)
    return continue_rect

def show_victory():
    screen.fill(BLACK)
    draw_text("VICTORY!", title_font, GREEN, SCREEN_WIDTH//2, 150, True)
    
    if enemy.type == 0:
        draw_text("You've overcome your negative thoughts!", text_font, WHITE, SCREEN_WIDTH//2, 230, True)
    elif enemy.type == 1:
        draw_text("You've faced and conquered your fears!", text_font, WHITE, SCREEN_WIDTH//2, 230, True)
    else:
        draw_text("You've silenced your doubts!", text_font, WHITE, SCREEN_WIDTH//2, 230, True)
    
    draw_text("But the journey continues...", text_font, WHITE, SCREEN_WIDTH//2, 270, True)
    continue_rect = draw_text("Press any key to continue", text_font, WHITE, SCREEN_WIDTH//2, 350, True)
    return continue_rect

def handle_combat_choice(choice):
    global player, enemy, combat_turn, current_state, message, message_timer
    
    if combat_turn == 0:  # Player's turn
        enemy_counter = random.randint(1, 4)
        
        if choice != enemy_counter:
            damage = random.randint(10, 25)
            enemy.hp -= damage
            if enemy.hp < 0:
                enemy.hp = 0
            
            message = f"Your attack hits for {damage} damage!"
            message_timer = pygame.time.get_ticks()
            
            if enemy.hp <= 0:
                current_state = VICTORY
                return
        else:
            message = "Your attack was countered!"
            message_timer = pygame.time.get_ticks()
        
        combat_turn = 1
    else:  # Enemy's turn
        enemy_attack = random.randint(1, 4)
        player_counter = random.randint(1, 4)
        
        if enemy_attack != player_counter:
            damage = random.randint(10, 25)
            player.hp -= damage
            if player.hp < 0:
                player.hp = 0
            
            message = f"{enemy.attack_msgs[enemy.type]}\nYou take {damage} damage!"
            message_timer = pygame.time.get_ticks()
            
            if player.hp <= 0:
                current_state = GAME_OVER
                return
        else:
            message = "You countered the enemy's attack!"
            message_timer = pygame.time.get_ticks()
        
        combat_turn = 0

def main():
    global current_state, player, enemy, story_progress, combat_turn, message, message_timer
    
    reset_game()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        # Clear screen
        screen.fill(BLACK)
        
        # Show current game state
        if current_state == MAIN_MENU:
            start_rect, exit_rect = show_main_menu()
            
            if click:
                if start_rect.collidepoint(mouse_pos):
                    current_state = STORY_CHOICE
                    story_progress = 1
                elif exit_rect.collidepoint(mouse_pos):
                    running = False
        
        elif current_state == STORY_CHOICE:
            options = show_story_choice()
            
            if click:
                for i, option in enumerate(options):
                    if option.collidepoint(mouse_pos):
                        player.choice = i + 1
                        
                        if story_progress == 1:
                            story_progress = 2 if player.choice == 1 else 3
                        elif story_progress == 2:
                            enemy = Enemy(0 if player.choice == 1 else 2)
                            current_state = COMBAT
                            combat_turn = 0
                        elif story_progress == 3:
                            if player.choice == 1:
                                enemy = Enemy(1)
                                current_state = COMBAT
                                combat_turn = 0
                            else:
                                current_state = GAME_OVER
        
        elif current_state == COMBAT:
            attacks = show_combat()
            
            if combat_turn == 0 and click:
                for i, attack in enumerate(attacks):
                    if attack.collidepoint(mouse_pos):
                        handle_combat_choice(i + 1)
            elif combat_turn == 1:
                pygame.display.flip()
                pygame.time.delay(1500)  # Pause for enemy turn
                handle_combat_choice(0)
        
        elif current_state == GAME_OVER:
            continue_rect = show_game_over()
            if click:
                reset_game()
        
        elif current_state == VICTORY:
            continue_rect = show_victory()
            if click:
                reset_game()
        
        # Display message if any
        if message and pygame.time.get_ticks() - message_timer < 2000:
            lines = message.split('\n')
            for i, line in enumerate(lines):
                draw_text(line, text_font, WHITE, SCREEN_WIDTH//2, 400 + i*30, True)
        else:
            message = ""
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
