import pygame
import sys

from classes.Player import Player
from classes.Platform import Platform
from classes.Enemy import Enemy
from classes.PowerUp import PowerUp
from classes.Database import Database
from classes.Button import Button

from animations.animateInAndOut import *

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 800
NORMAL_FRAME_RATE = 45

# Color RGB codes
LIGHT_GREEN = (100, 255, 100)
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()
surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pluto")
clock = pygame.time.Clock()

# Initialize Font
FONT_FAMILY = "calibri, helvetica, arial"
font_size = 25
font_margin = 20
game_font = pygame.font.SysFont(FONT_FAMILY, font_size, bold = True)

# Load images
load = pygame.image.load
backgroundPath = "static/images/background"
characterPath = "static/images/character"
platformPath = "static/images/platforms"
enemyPath = "static/images/enemy"
powerupPath = "static/images/powerups"

background_image = load(f"{backgroundPath}/space.jpg")
cloud_image = load(f"{backgroundPath}/clouds.png")
playerImages = {
    "right": [load(f"{characterPath}/R1Pluto.png"), load(f"{characterPath}/R2Pluto.png"), load(f"{characterPath}/R3Pluto.png"), load(f"{characterPath}/R4Pluto.png")],
    "left": [load(f"{characterPath}/L1Pluto.png"), load(f"{characterPath}/L2Pluto.png"), load(f"{characterPath}/L3Pluto.png"), load(f"{characterPath}/L4Pluto.png")],
    "idle": [load(f"{characterPath}/I1Pluto.png"), load(f"{characterPath}/I2Pluto.png"), load(f"{characterPath}/I3Pluto.png"), load(f"{characterPath}/I4Pluto.png")],
}
platformImage = load(f"{platformPath}/platform.png")
enemyImages = {
    'left': load(f"{enemyPath}/enemyL.png"),
    'right': load(f"{enemyPath}/enemyR.png"),
    'idle': load(f"{enemyPath}/spike.png"),
}
powerupImages = {
    'invincibility': load(f"{powerupPath}/invincibility.png"),
    'double_points': load(f"{powerupPath}/2x.png"),
    'score_boost': load(f"{powerupPath}/add.png"),
}

# Database instance
db = Database()

# Player instance
pluto = Player(playerImages)
PLUTO_PERSONAL_SPACE = 15 # Distance between the satellite/power-up cues and pluto's image

# Set window icon to one of pluto's images
pygame.display.set_icon(pluto.sprites_right[0])

# Dictionary to store dynamic variables
DYNAMIC = {
    "score": 0,
    "high_score": db.getHighScore(),
    "invincibility": {
        "active": False,
        "timer": 0
    },
    "double_points": {
        "active": False,
        "timer": 0
    },
    "score_boost": {
        "active": False,
        "timer": 0
    },
    "background_y_position": 1,
    "target_background_y_position": None
}

# Dictionary to store game settings
SETTINGS = {
    "frame_rate": NORMAL_FRAME_RATE
}

# Lists with game objects
PLATFORMS = []
ENEMIES = []
POWERUPS = []

# Play music
pygame.mixer.music.load('static/audio/music.ogg')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Flag to control game state
running = True

# Function with game's main logic
def main():
    global running
    running = True
    
    # Main loop
    while running:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exitGame()

            # Mute or unmute the music when pressing 'm'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                pygame.mixer.music.fadeout(500) if pygame.mixer.music.get_busy() else pygame.mixer.music.play(-1, 1, 500)

            # Cheats: Add 5 points when pressing 'o'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                DYNAMIC["score"] += 5
                DYNAMIC["score_boost"]["timer"] = 0.8 * SETTINGS["frame_rate"]

        # Manage game objects
        createObjects()
        removeOffScreenObjects()

        # Manage power-up effects
        handlePowerups()

        # Update Player instance every frame
        pluto.tick(PLATFORMS)

        # Check if the player has fallen off the screen
        if playerFell(): running = False


        # Get the keys that are being pressed
        keys = pygame.key.get_pressed()
        
        # Movement controls
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            pluto.move(-pluto.speed)

            pluto.current_direction = "left"
            pluto.current_sprites = pluto.sprites_left

        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            pluto.move(pluto.speed)

            pluto.current_direction = "right"
            pluto.current_sprites = pluto.sprites_right

        else:
            pluto.current_direction = "idle"
            pluto.current_sprites = pluto.sprites_idle

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            pluto.jump()

        # Cheats: 'i' to activate invincibility - 'u' to activate double points
        if keys[pygame.K_i]: DYNAMIC["invincibility"]["timer"] = 20
        if keys[pygame.K_u]: DYNAMIC["double_points"]["timer"] = 30

        # Cheats: 'y' to double frame rate - 't' to halve frame rate
        SETTINGS["frame_rate"] = (NORMAL_FRAME_RATE * 2) if keys[pygame.K_y] else (NORMAL_FRAME_RATE / 2) if keys[pygame.K_t] else NORMAL_FRAME_RATE


        # Draw background
        updateBackgroundYPosition()
        surface.blit(background_image, (0, DYNAMIC["background_y_position"]))

        # Draw clouds if needed
        if (pluto.camera_y_offset < WINDOW_HEIGHT):
            CLOUDS_POSITION = (0, WINDOW_HEIGHT - (cloud_image.get_rect().height - 10) + pluto.camera_y_offset)
            surface.blit(cloud_image, CLOUDS_POSITION)
        
        # Draw pluto's satellite
        SATELLITE_RADIUS = 10
        SATELLITE_COLOR = (
            min(DYNAMIC["score"] * 255 / 200, 255), # Red value: (score:value) 0:0, 200:255
            max(255 - DYNAMIC["score"] * 255 / 200, 0), # Green value: (score:value) 0:255, 200:0
            0, # Blue value
        )
        pygame.draw.circle(surface, SATELLITE_COLOR, (pluto.x, pluto.y + pluto.camera_y_offset), SATELLITE_RADIUS)
            
        # Draw pluto
        surface.blit(pluto.current_sprites[int(pluto.current_frame)], pluto.sprite_rect)
        pluto.sprite_rect.update(pluto.x, pluto.y + pluto.camera_y_offset, pluto.width, pluto.height)

        # Draw enemies
        for enemy in ENEMIES:
            surface.blit(enemy.current_sprite, enemy.sprite_rect)
            enemy.sprite_rect.update(enemy.x, enemy.y + pluto.camera_y_offset, enemy.width, enemy.height)

            # Update Enemy instance every frame
            enemy.tick(WINDOW_WIDTH, WINDOW_HEIGHT)

            # Handle enemy collision with pluto
            if enemy.collidedWith(pluto):
                if DYNAMIC["invincibility"]["active"]:
                    enemy.die(playerFeetCoordinates = (pluto.x + pluto.width / 2, pluto.y + pluto.height - 10))

                else:
                    pluto.die()

        # Draw power-ups
        for powerup in POWERUPS:
            surface.blit(powerup.powerup_sprite, powerup.sprite_rect)
            powerup.sprite_rect.update(powerup.x, powerup.y + pluto.camera_y_offset, powerup.width, powerup.height)

            # Update Power-Up instance every frame
            powerup.tick()

            # Handle power-up collision with pluto
            if powerup.collidedWith(pluto): 
                powerup.applyEffect(DYNAMIC, SETTINGS["frame_rate"])

                # Move power-up out of the screen so it's deleted by removeOffScreenObjects function
                powerup.y = WINDOW_HEIGHT * 2

        # Draw platforms
        for platform in PLATFORMS:
            surface.blit(platform.platform_sprite, platform.sprite_rect)
            platform.sprite_rect.update(platform.x, platform.y + pluto.camera_y_offset, platform.width, platform.height)

            # Update Platform instance every frame
            platform.tick(pluto)

            # Increase score if the platform is touched for the first time
            if platform.touched and not platform.hasChangedScore:
                DYNAMIC["score"] += 2 if DYNAMIC["double_points"]["active"] else 1
                platform.hasChangedScore = True

        # Draw active power-up's visual effect
        if DYNAMIC["invincibility"]["active"]:
            # Draw a force field around Pluto
            animateCircleInAndOut(surface, colorRGB=(60, 60, 255), center=pluto.sprite_rect.center, initialRadius=0, maxRadius=pluto.height, 
                               maxAlpha=50, totalDuration=3, timeLeft=DYNAMIC["invincibility"]["timer"] / SETTINGS["frame_rate"], animationDuration=0.2)
            
        if DYNAMIC["score_boost"]["active"]:
            # Draw "+5" next to Pluto
            animateTextInAndOut(surface, game_font, text="+5", initialSize=0, maxSize=30, color="green",
                             center=(pluto.x + pluto.width + PLUTO_PERSONAL_SPACE, pluto.y + pluto.camera_y_offset), totalDuration=0.8,
                             timeLeft=DYNAMIC["score_boost"]["timer"] / SETTINGS["frame_rate"], animationDuration=0.2)
            
        elif DYNAMIC["double_points"]["active"]:
            # Draw "2x" next to Pluto
            animateTextInAndOut(surface, game_font, text = "2x", initialSize=0, maxSize=30, color="chartreuse",
                             center=(pluto.x + pluto.width + PLUTO_PERSONAL_SPACE, pluto.y + pluto.camera_y_offset), totalDuration=5,
                             timeLeft=DYNAMIC["double_points"]["timer"] / SETTINGS["frame_rate"], animationDuration=0.3)


        # Display current score
        score_text = f"Score: {DYNAMIC['score']}"
        score_surface = game_font.render(score_text, True, WHITE)
        score_coordinates = (font_margin, font_margin)
        surface.blit(score_surface, score_coordinates)

        # Display high score
        high_score_text = f"High Score: {max(DYNAMIC['high_score'], DYNAMIC['score'])}"
        high_score_color = WHITE if DYNAMIC["score"] <= DYNAMIC["high_score"] else LIGHT_GREEN # Change text color if new high score is being set
        high_score_surface = game_font.render(high_score_text, True, high_score_color)
        high_score_text_width = high_score_surface.get_width()
        high_score_coordinates = (WINDOW_WIDTH - high_score_text_width - font_margin, font_margin)
        surface.blit(high_score_surface, high_score_coordinates)
        

        # Update the display
        pygame.display.flip()

        # Set frame rate
        clock.tick(SETTINGS["frame_rate"])

    # Display end screen
    displayEndScreen()


# Function to fill the PLATFORMS, ENEMIES and POWERUPS lists with respective instances
def createObjects():
    PLATFORM_GAP = 200
    PADDING = 20
    CAMERA_UPPER_BOUND = -pluto.camera_y_offset

    last_platform_y_position = PLATFORMS[-1].y if PLATFORMS else WINDOW_HEIGHT - PADDING
    
    # Create a new platform if no platforms have been created or if the last platform created is already on the screen
    if not PLATFORMS or last_platform_y_position > CAMERA_UPPER_BOUND:
        new_platform_y_position = last_platform_y_position - PLATFORM_GAP
        possible_x_values = [PADDING, WINDOW_WIDTH - PADDING]
        platform_instance = Platform(platformImage, possible_x_values, new_platform_y_position, currentScore = DYNAMIC["score"])

        PLATFORMS.append(platform_instance)

        # Add an enemy if needed
        if platform_instance.hasEnemy:
            possible_x_values = [platform_instance.x, platform_instance.x + platform_instance.width]
            y_position = platform_instance.y
            enemy_instance = Enemy(enemyImages, possible_x_values, y_position)
            
            ENEMIES.append(enemy_instance)

        # Add a power-up if needed
        elif platform_instance.hasPowerUp:
            possible_x_values = [platform_instance.x, platform_instance.x + platform_instance.width]
            y_position = platform_instance.y
            powerup_instance = PowerUp(powerupImages, possible_x_values, y_position)
            
            POWERUPS.append(powerup_instance)

# Function to remove the platforms that have gone off-screen
def removeOffScreenObjects():
    global PLATFORMS, ENEMIES, POWERUPS
    CAMERA_LOWER_BOUND = WINDOW_HEIGHT - pluto.camera_y_offset

    # Filter out the platforms, enemies, and power-ups whose y-coordinate is below the camera's lower bound
    PLATFORMS = [platform for platform in PLATFORMS if platform.y < CAMERA_LOWER_BOUND]
    ENEMIES = [enemy for enemy in ENEMIES if enemy.y < CAMERA_LOWER_BOUND]
    POWERUPS = [powerup for powerup in POWERUPS if powerup.y < CAMERA_LOWER_BOUND]

# Function to handle power-up effects
def handlePowerups():
    for powerup in DYNAMIC.values():
        if isinstance(powerup, dict):
            # Decrement the timer if necessary
            powerup['timer'] = max(0, powerup['timer'] - 1)

            # Set the active property based on the time left on the timer
            powerup['active'] = powerup['timer'] > 0

# Function to check if the player has lost
def playerFell():
    # A number that allows enough room below the screen so pluto can completely disappear before touching the trigger
    GAME_OVER_Y_POSITION = WINDOW_HEIGHT + pluto.height * 1.5 - pluto.camera_y_offset

    # An object placed just below the visible screen
    game_over_rect = pygame.Rect(-WINDOW_WIDTH, GAME_OVER_Y_POSITION, WINDOW_WIDTH * 3, 1)

    # Return True if pluto touches the trigger 
    return pluto.hitbox.colliderect(game_over_rect)


# Function to move the background as the player ascends
def updateBackgroundYPosition():
    # Calculate the maximum offset the background can move vertically
    max_offset = -(background_image.get_rect().height - WINDOW_HEIGHT)

    # Target background position
    target = max_offset if DYNAMIC["target_background_y_position"] == "start" else 0

    # Current background position
    position = DYNAMIC["background_y_position"]
    if position > 0: position = max_offset

    # Check if the target position has already been achieved
    target_accomplished = (DYNAMIC["target_background_y_position"] == None) or (target == position)

    # If the target has not been achieved...
    if not target_accomplished:
        # Calculate moving speed relative to frame rate for smooth transition
        MOVING_SPEED = (target + position) / NORMAL_FRAME_RATE

        # Determine the direction of movement -1 for up, 2 for down
        DIRECTION = -1 if target > position else 2

        # Update the position towards the target
        position += MOVING_SPEED * DIRECTION

        # Ensure the background y-position does not go out of bound and update it
        DYNAMIC["background_y_position"] = max(max_offset, min(0, position))
        
    # If the target has been achieved... (middle-game)
    else:
        # Reset the target marker
        DYNAMIC["target_background_y_position"] = None

        # Normalize the camera offset to a scale that makes the background movement smoother
        normalized_camera_offset = pluto.camera_y_offset / (35 * WINDOW_HEIGHT) # 35 is an arbitrary number, the background stops moving at a score of ~200

        # Ensure the normalized value stays within the range 0 to 1
        clamped_value = max(0, min(1, normalized_camera_offset))

        # Assign the background's y-position by scaling the max offset relative to the clamped value
        DYNAMIC["background_y_position"] = max_offset * (1 - clamped_value)


# Function to display the end screen
def displayEndScreen():
    global running
    DYNAMIC["target_background_y_position"] = "end"
    
    # Change high score if necessary
    DYNAMIC["high_score"] = max(DYNAMIC["score"], DYNAMIC["high_score"])
    
    # Constants
    GAP = 70
    CONTENT_Y_POSITION = WINDOW_HEIGHT // 2 - 25

    # Initialize score text
    score_text = f"Final Score: {DYNAMIC['score']}"
    score_font = pygame.font.SysFont(FONT_FAMILY, 37, bold = True)
    score_surface = score_font.render(score_text, True, WHITE)
    score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, CONTENT_Y_POSITION - GAP))

    # Button Instances
    play_again_button = Button(
            text="Play Again", callback=startGame,
            x=WINDOW_WIDTH // 4, y=CONTENT_Y_POSITION,
            shortcutKeys=[pygame.K_p, pygame.K_s, pygame.K_DOWN]
        )

    exit_button = Button(
            text="Exit Game", callback=exitGame,
            x=WINDOW_WIDTH // 4, y=CONTENT_Y_POSITION + GAP,
            shortcutKeys=[pygame.K_q, pygame.K_e, pygame.K_ESCAPE]
        )
    
    while not running:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()

            # Mute or unmute the music when pressing 'm'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                pygame.mixer.music.fadeout(500) if pygame.mixer.music.get_busy() else pygame.mixer.music.play(-1, 1, 500)

        # Draw the background
        updateBackgroundYPosition()
        surface.blit(background_image, (0, DYNAMIC["background_y_position"]))

        # Draw the score
        surface.blit(score_surface, score_rect)

        # Draw the buttons
        play_again_button.draw(surface)
        exit_button.draw(surface)

        # Update the display
        pygame.display.flip()
        clock.tick(NORMAL_FRAME_RATE)

# Function to start a new game
def startGame():
    # Reset player instance
    global pluto
    pluto = Player(playerImages)
    
    # Reset dynamic variables
    DYNAMIC["score"] = 0
    DYNAMIC["invincibility"]["timer"] = 0
    DYNAMIC["double_points"]["timer"] = 0
    DYNAMIC["score_boost"]["timer"] = 0
    DYNAMIC["target_background_y_position"] = "start"

    # Reset objects
    PLATFORMS.clear()
    ENEMIES.clear()
    POWERUPS.clear()

    # Call main function
    main()

# Function to exit the program
def exitGame():
    db.setHighScore(max(DYNAMIC["score"], DYNAMIC["high_score"]))
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    startGame()