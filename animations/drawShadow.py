import pygame

def draw_shadow(surface, x, y, width, height=None, offset=10, alpha=64):
    # Set default height to half of the width if not provided
    height = height or width // 2

    # Create a transparent surface
    shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Define shadow color with transparency (alpha)
    SHADOW_COLOR = (4, 14, 29, alpha)

    # Draw the shadow as an ellipse on the transparent surface
    shadow_rect = pygame.Rect(0, 0, width, height)
    pygame.draw.ellipse(shadow_surface, SHADOW_COLOR, shadow_rect)

    # Calculate shadow position on the main surface
    shadow_position = (x, y + offset)

    # Blit the shadow surface onto the main surface
    surface.blit(shadow_surface, shadow_position)