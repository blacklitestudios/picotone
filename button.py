import pygame


class Button:
    def __init__(self, x, y, surface):
        """
        Create a visual button with hover and click animations.
        
        Args:
            x, y: Position of the button center
            surface: pygame.Surface to use as the button's appearance
        """
        self.base_x = x
        self.base_y = y
        self.base_surface = surface
        self.base_width = surface.get_width()
        self.base_height = surface.get_height()
        
        # Animation state
        self.scale = 1.0
        self.target_scale = 1.0
        self.is_hovered = False
        self.is_clicked = False
        
        # Animation speed
        self.scale_speed = 0.5
    
    def update(self, mouse_pos, mouse_pressed):
        """
        Update button state based on mouse position and input.
        
        Args:
            mouse_pos: Tuple of (x, y) mouse position
            mouse_pressed: Boolean indicating if mouse button is pressed
        """
        # Check if mouse is hovering over button
        current_rect = self.get_rect()
        self.is_hovered = current_rect.collidepoint(mouse_pos)
        
        # Determine target scale
        if mouse_pressed and self.is_hovered:
            self.is_clicked = True
            self.target_scale = 1.0
        elif self.is_hovered:
            self.is_clicked = False
            self.target_scale = 1.2
        else:
            self.is_clicked = False
            self.target_scale = 1.0
        
        # Smoothly interpolate to target scale
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * self.scale_speed
        else:
            self.scale = self.target_scale
    
    def get_rect(self):
        """Get the current rect based on scale."""
        current_width = self.base_width * self.scale
        current_height = self.base_height * self.scale
        return pygame.Rect(
            self.base_x - current_width / 2,
            self.base_y - current_height / 2,
            current_width,
            current_height
        )
    
    def draw(self, window):
        """
        Draw the button on the given window.
        
        Args:
            window: Pygame surface to draw on
        """
        # Get current dimensions
        rect = self.get_rect()
        
        # Create scaled surface
        scaled_width = int(self.base_width * self.scale)
        scaled_height = int(self.base_height * self.scale)
        
        if scaled_width > 0 and scaled_height > 0:
            scaled_surface = pygame.transform.smoothscale(self.base_surface, (scaled_width, scaled_height))
            
            # Convert to support alpha if the original has alpha
            if self.base_surface.get_flags() & pygame.SRCALPHA:
                scaled_surface = scaled_surface.convert_alpha()
            
            # Darken the surface if clicked (preserving alpha)
            if self.is_clicked:
                # Create a dark overlay with alpha support
                dark_overlay = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                dark_overlay.fill((128, 128, 128, 255))  # 50% gray with full alpha
                # Use BLEND_RGBA_MULT to darken (multiplies RGB values, preserving alpha)
                scaled_surface.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw the surface centered at button position
            window.blit(scaled_surface, rect.topleft)
