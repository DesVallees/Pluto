import pygame
import random
import math

class Enemy:
    # Constructor for Enemy class
    def __init__(self, sprites, possibleXValues, y, sounds):
        self.is_alive = True
        
        # Movement controls
        self.moving_enemy = self.oneInXChances(3) # ~33% chance
        self.speed = random.random() * 2
        self.direction = random.choice([-1, 1])  # 1 for right, -1 for left

        # Fly-away controls
        self.x_flying_speed = 0
        self.y_flying_speed = 0
        
        # Load sounds
        self.sounds = sounds
        if "enemyDeath" in self.sounds and self.sounds["enemyDeath"].get_volume() != 0:
            self.sounds["enemyDeath"].set_volume(0.5)
        
        # Load sprites
        self.sprite_left = sprites["left"]
        self.sprite_right = sprites["right"]
        self.sprite_idle = sprites["idle"]

        # Set current sprite and initialize sprite rectangle
        self.current_sprite = (self.sprite_right if self.direction == 1 else self.sprite_left) if self.moving_enemy else self.sprite_idle
        self.sprite_rect = self.current_sprite.get_rect(y = -500) # -500 to make sure the enemy appears out of the screen

        # Enemy's dimensions
        self.width = self.sprite_rect.width
        self.height = self.sprite_rect.height - 2
        
        # Enemy's initial coordinates
        self.min_x_value = possibleXValues[0]
        self.max_x_value = possibleXValues[1] - self.width
        self.x = random.randint(self.min_x_value + 10, self.max_x_value)
        self.y = y - self.height  # Adjust y to ensure it's shown on top of the surface it was placed on

        # Initialize enemy's hitbox
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    # Method that gets called every frame
    def tick(self, windowWidth, windowHeight):
        self.updateHitbox()
        
        if not self.is_alive: self.flyAway(windowWidth, windowHeight)
        elif self.moving_enemy: self.move()

    # Move the enemy considering platform surface
    def move(self):
        self.x += self.speed * self.direction

        # If enemy has reached platform border
        if self.x < self.min_x_value or self.x > self.max_x_value:
            # Reverse direction
            self.direction *= -1

            # Update sprite
            self.current_sprite = self.sprite_left if self.direction == -1 else self.sprite_right

    # Returns True if the enemy touches the target while being alive
    def collidedWith(self, target):
        return self.hitbox.colliderect(target.hitbox) and self.is_alive
    
    # Method to update enemy's hitbox
    def updateHitbox(self):
        TRIM_PX_TOP = 7

        self.hitbox.update(self.x, self.y + TRIM_PX_TOP, self.width, self.height - TRIM_PX_TOP)

    # There is one in {argument} chances the method returns True
    def oneInXChances(self, x):
        return random.randint(1, 100) <= 100 / x
    
    # Method to call when the enemy is hit with the invincibility power-up active
    def die(self, playerFeetCoordinates):
        if self.is_alive:
            # Get the player's feet position
            player_x, player_y = playerFeetCoordinates

            # Calculate the angle from where the enemy was hit
            dx = self.x + self.width / 2 - player_x # Horizontal distance between the player and the enemy
            dy = self.y + self.height / 2 - player_y # Vertical distance between the player and the enemy
            angle = math.atan2(dy, dx) # Get the angle in radians

            # Calculate fly-away speeds based on the angle
            self.y_flying_speed = math.sin(angle) * 65
            self.x_flying_speed = math.cos(angle) * (25 if abs(self.y_flying_speed) > 20 else 60)

            # Play dying sound
            if "enemyDeath" in self.sounds:
                self.sounds["enemyDeath"].play()

            # Update enemy's state
            self.is_alive = False

    # Method that makes the enemy fly away
    def flyAway(self, windowWidth, windowHeight):
        # Check if the enemy is still on the screen
        if 0 <= self.x <= windowWidth and 0 <= self.sprite_rect.y <= windowHeight:
            # Update position
            self.x += self.x_flying_speed
            self.y += self.y_flying_speed

        else:
            # Move the enemy below the screen so it's deleted by removeOffScreenObjects function
            self.y = 2000