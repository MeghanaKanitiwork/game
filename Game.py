import pygame
import time

# Initialize pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
WALL_COLOR = (169, 169, 169)
TELEPORT_COLOR = (0, 0, 255)

# Define screen size
screen_width = 400
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))

# Game variables
player_size = 20
player = pygame.Rect(150, 150, player_size, player_size)
player_color = WHITE

# Red boxes (danger zones)
red_boxes = [pygame.Rect(50, 50, player_size, player_size), pygame.Rect(200, 200, player_size, player_size)]
red_box_states = [RED, RED]  # Color of the red boxes
red_box_timers = [0, 0]  # Timers for each red box to darken
red_box_priority = [0, 0]  # Track which red box is darker (higher priority)

# Walls (immovable obstacles)
walls = [pygame.Rect(100, 100, player_size, player_size), pygame.Rect(250, 250, player_size, player_size), 
         pygame.Rect(150, 300, player_size, player_size), pygame.Rect(200, 100, player_size, player_size)]

# Teleporters
teleporters = [pygame.Rect(50, 250, player_size, player_size), pygame.Rect(250, 50, player_size, player_size)]

# Timers and round management
game_clock = pygame.time.Clock()
round_time = 60  # Time in seconds for each round
round_number = 1
game_over = False
darkening_speed = 0.5  # How fast the red boxes darken per second
darkness_level = 0  # Darkness level of the white pixel
player_brightness = 255  # Brightness level of the player
score = 0

# Game loop
running = True
while running:
    screen.fill(GREEN)

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    last_player_position = player.x, player.y
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_UP]:
        player.y -= 5
    if keys[pygame.K_DOWN]:
        player.y += 5

    # Collision with walls
    for wall in walls:
        if player.colliderect(wall):
            # Prevent player from moving through walls
            player.x, player.y = last_player_position  # Undo movement

    # Teleportation logic
    if player.colliderect(teleporters[0]):
        player.x, player.y = teleporters[1].x, teleporters[1].y
    elif player.colliderect(teleporters[1]):
        player.x, player.y = teleporters[0].x, teleporters[0].y

    # Red box darkening logic and prioritization
    darker_boxes_first = False
    for i, red_box in enumerate(red_boxes):
        fps = game_clock.get_fps()
        if fps > 0:
            red_box_timers[i] += darkening_speed / fps  # Increment darkening timer
        else:
            red_box_timers[i] += darkening_speed / 30  # Default to 30 FPS if get_fps() is zero

        if red_box_timers[i] >= 10:  # If timer exceeds threshold, make the box dark red
            red_box_states[i] = DARK_RED
            red_box_priority[i] = 2  # Higher priority
        elif red_box_timers[i] >= 5:
            red_box_states[i] = RED
            red_box_priority[i] = 1  # Lower priority

        # Check if the player reaches the red box
        if player.colliderect(red_box):
            if red_box_states[i] == DARK_RED:
                score += 10  # Add 10 points for reaching dark red box
                red_box_states[i] = GREEN  # Turn the red box green
                red_box_timers[i] = 0  # Reset the timer for that box
                darker_boxes_first = True
                player_brightness = 255  # Brighten the player
            elif red_box_states[i] == RED and not darker_boxes_first:
                score += 5  # Add 5 points for reaching light red box
                red_box_states[i] = GREEN  # Turn the red box green
                red_box_timers[i] = 0  # Reset the timer for that box
                player_brightness = 255  # Brighten the player

    # Darken the white pixel if no red box is reached
    if not darker_boxes_first:
        player_brightness = max(0, player_brightness - 0.25)  # Decrease brightness even more slowly
    player_color = (player_brightness, player_brightness, player_brightness)

    # Game over logic if the player is completely dark
    if player_color == (0, 0, 0):
        font = pygame.font.SysFont(None, 55)
        game_over_text = font.render('Game Over!', True, BLACK)
        screen.blit(game_over_text, (100, 150))
        pygame.display.flip()
        time.sleep(3)  # Show "Game Over" for 3 seconds
        running = False  # Exit the game loop

    # Check if all red boxes are green (round complete)
    if all(color == GREEN for color in red_box_states):
        font = pygame.font.SysFont(None, 55)
        round_complete_text = font.render(f'Round {round_number} Complete! Score: {score}', True, BLACK)
        screen.blit(round_complete_text, (50, 150))
        pygame.display.flip()
        time.sleep(3)  # Show "Round Complete" for 3 seconds
        
        # Proceed to the next round
        round_number += 1
        player_color = WHITE  # Reset the player color
        player_brightness = 255  # Reset brightness
        darkness_level = 0  # Reset darkness
        player.x, player.y = 150, 150  # Reset player position
        red_box_states = [RED, RED]  # Reset red boxes
        red_box_timers = [0, 0]  # Reset red box timers
    
    # Draw player and obstacles
    pygame.draw.rect(screen, player_color, player)
    for red_box, color in zip(red_boxes, red_box_states):
        pygame.draw.rect(screen, color, red_box)
    for wall in walls:
        pygame.draw.rect(screen, WALL_COLOR, wall)
    for teleporter in teleporters:
        pygame.draw.rect(screen, TELEPORT_COLOR, teleporter)

    # Display round number and score
    font = pygame.font.SysFont(None, 30)
    round_display = font.render(f'Round: {round_number}', True, BLACK)
    screen.blit(round_display, (10, 10))
    score_display = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_display, (10, 40))

    # Update display and tick clock
    pygame.display.flip()
    game_clock.tick(30)

pygame.quit()
