import pygame
import random

class PowerUp:
    # Constructor for PowerUp class
    def __init__(self, powerupImages, possibleXValues, y):
        # Set power-up's type
        self.type = self.determineType()
        
        # Load appropriate sprite
        self.powerup_sprite = powerupImages[self.type]

        # Initialize sprite rectangle
        self.sprite_rect = self.powerup_sprite.get_rect(y = -500) # -500 to make sure the power-up appears out of the screen

        # Powerup's dimensions
        self.width = self.sprite_rect.width
        self.height = self.sprite_rect.height

        # Power-up's coordinates
        self.possible_x_values = possibleXValues
        self.x = random.randint(possibleXValues[0] + self.width, possibleXValues[1] - self.width)
        self.y = y - self.height # Subtract height to make sure it is shown on top of the surface it was placed on

        # Initialize power-up's hitbox
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    # Method that gets called every frame
    def tick(self):
        self.updateHitbox()

    # Returns True if the power-up touches the target
    def collidedWith(self, target):
        return self.hitbox.colliderect(target.hitbox)

    # Method to apply a certain effect depending on the power-up's type 
    def applyEffect(self, controls, frameRate):
        if self.type == 'invincibility':
            controls["invincibility"]["timer"] = frameRate * 3 # Make power-up last 3 seconds

        elif self.type == 'double_points':
            controls["double_points"]["timer"] = frameRate * 5 # Make power-up last 5 seconds

        elif self.type == 'score_boost':
            controls["score_boost"]["timer"] = frameRate * 0.8 # For animation purposes
            
            controls["score"] += 5

    # Method to update power-up's hitbox
    def updateHitbox(self):
        EXTRA_PX_SIDES = 10

        self.hitbox.update(self.x - EXTRA_PX_SIDES, self.y, self.width + EXTRA_PX_SIDES * 2, self.height)

    # Method to determine power-up's type
    def determineType(self):
        random_number = random.randint(1, 100)

        # Create an invincibility power-up - 33% chance
        if random_number < 33:
            return "invincibility"

        # Create a double-points power-up - 33% chance
        elif random_number < 66:
            return "double_points"

        # Create a score-boost power-up - 34% chance
        else:            
            return "score_boost"