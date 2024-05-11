import pygame
import random

class Platform:
    # Constructor for Platform class
    def __init__(self, sprite, possibleXValues, y, currentScore = 0):           
        # Set platform type
        self.type = self.determinePlatformType()
        
        # Load sprite
        self.platform_sprite = sprite

        # Initialize sprite rectangle
        self.sprite_rect = self.platform_sprite.get_rect(y = -500) # -500 to make sure the platform appears out of the screen

        # Platform's dimensions
        self.width = self.sprite_rect.width
        self.height = self.sprite_rect.height
        
        # Platform's initial coordinates
        self.min_x_value = possibleXValues[0]
        self.max_x_value = possibleXValues[1] - self.width
        self.x = random.randint(self.min_x_value, self.max_x_value)
        self.y = y

        # Platform's state
        self.touched = False
        self.hasChangedScore = False
        self.hasEnemy = False
        self.hasPowerUp = False

        # Movement controls
        self.speed = random.random() * 2
        self.direction = random.choice([-1, 1])  # 1 for right, -1 for left

        # Place an enemy: Chances increase as score does - At 200 there is an enemy on (almost) every platform
        if self.oneInXChances(max(4 - currentScore / (200 / 3), 1.2)) and self.type == "normal":
            self.hasEnemy = True

        # Place a power-up: Chances increase as score does - Enemies still have priority over power-ups    
        elif self.oneInXChances(max(5 - currentScore / (200 / 4), 1.2)) and self.type == "normal":
            self.hasPowerUp = True

        # Initialize platform's hitbox
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    # Method that gets called every frame
    def tick(self, player):
        self.updateHitbox()
        
        if self.type == "moving":
            self.movePlatform(player)

    # Method to determine platform's type
    def determinePlatformType(self):
        # Create a moving platform: 10% chance
        return "moving" if self.oneInXChances(10) else "normal"

    # There is one in {argument} chances method returns True
    def oneInXChances(self, x):
        return random.randint(1, 100) <= 100 / x

    # Method to update platform's hitbox
    def updateHitbox(self):
        self.hitbox.x = self.x
        self.hitbox.y = self.y

    # Method that gets called every frame if it's a moving platform
    def movePlatform(self, player):
        self.x += self.speed * self.direction

        # Check if the player is standing on the platform
        if self.hitbox.colliderect(player.hitbox):
            # Move the player along with the platform
            player.x += self.speed * self.direction

        # If platform has reached screen edge
        if self.x < self.min_x_value or self.x > self.max_x_value:
            # Reverse direction
            self.direction *= -1