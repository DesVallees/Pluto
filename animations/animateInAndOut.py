# Functions to animate pygame objects when appearing and disappearing

import pygame

def animateTextInAndOut(surface, font, text, initialSize, maxSize, color, center, totalDuration, timeLeft, animationDuration):
    time_passed = totalDuration - timeLeft

    # Calculate current text scale
    if time_passed < animationDuration:
        # Growing phase
        scale = 1 * (time_passed / animationDuration)

    elif time_passed >  totalDuration - animationDuration:
        # Shrinking phase
        scale = 1 * ((totalDuration - time_passed) / animationDuration)

    else:
        # Middle phase
        scale = 1

    # Ensure scale is between 0 and 1
    scale = max(0, min(1, scale))

    # Calculate font size and opacity (alpha value)
    size = int(initialSize + (maxSize - initialSize) * scale)
    alpha = int(255 * scale)

    # Render the text
    text_surface = font.render(text, True, color)
    text_surface = pygame.transform.scale(text_surface, (size, size))
    text_surface.set_alpha(alpha)

    # Get the rect and set the position
    text_rect = text_surface.get_rect(center = center)

    # Display the text
    surface.blit(text_surface, text_rect)

def animateCircleInAndOut(surface, colorRGB, center, initialRadius, maxRadius, maxAlpha, totalDuration, timeLeft, animationDuration):
    time_passed = totalDuration - timeLeft

    # Calculate current circle scale
    if time_passed < animationDuration:
        # Growing phase
        scale = (time_passed / animationDuration)

    elif time_passed > totalDuration - animationDuration:
        # Shrinking phase
        scale = ((totalDuration - time_passed) / animationDuration)

    else:
        # Middle phase
        scale = 1

    # Ensure scale is between 0 and 1
    scale = max(0, min(1, scale))

    # Calculate radius and opacity (alpha value)
    radius = int(initialRadius + (maxRadius - initialRadius) * scale)
    alpha = min(int(255 * scale), maxAlpha)

    # Create a temporary surface with alpha support to draw the circle
    temp_surface = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)

    # Create an RGBA color tuple including the alpha value
    rgba_color = colorRGB + (alpha,)

    # Draw the circle
    pygame.draw.circle(temp_surface, rgba_color, (radius, radius), radius)

    # Get the rect and set the position
    circle_rect = temp_surface.get_rect(center=center)

    # Display the circle
    surface.blit(temp_surface, circle_rect)