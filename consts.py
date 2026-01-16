import math
from fractions import Fraction
import pygame
RED = (229, 139, 158)
GREEN = (145, 219, 145)
PURPLE = (186, 163, 235)
YELLOW = (247, 203, 104)

OCTAVE = 1
PERFECTFIFTH = math.log(3/2, 2)
MAJORTHIRD = math.log(5/4, 2)
SEVENTH = math.log(7/4, 2)
ELEVENTH = math.log(11/4, 2)

RATIOS = [None, Fraction(2), Fraction(3/2), Fraction(5/4), Fraction(7/4), Fraction(11/4)]
INTERVALLENGTHS = [None, OCTAVE, PERFECTFIFTH, MAJORTHIRD, SEVENTH, ELEVENTH]

def draw_dotted_line(surface, color, start_pos, end_pos, width=1, dash_length=10, gap_length=5):
    """
    Draw a dotted line on a pygame surface.
    
    Args:
        surface: The pygame surface to draw on
        color: Color of the line (RGB tuple)
        start_pos: Starting position (x, y)
        end_pos: Ending position (x, y)
        width: Width of the line
        dash_length: Length of each dash
        gap_length: Length of gaps between dashes
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    # Calculate line length and direction
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance == 0:
        return
    
    # Normalize direction
    dx = dx / distance
    dy = dy / distance
    
    # Draw dashes
    current_distance = 0
    while current_distance < distance:
        # Start of dash
        start_x = x1 + dx * current_distance
        start_y = y1 + dy * current_distance
        
        # End of dash
        end_distance = min(current_distance + dash_length, distance)
        end_x = x1 + dx * end_distance
        end_y = y1 + dy * end_distance
        
        # Draw the dash
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)
        
        # Move to next dash
        current_distance += dash_length + gap_length