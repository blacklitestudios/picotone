import math
from fractions import Fraction
import pygame
RED = (229, 139, 158)
GREEN = (145, 219, 145)
PURPLE = (186, 163, 235)
YELLOW = (247, 203, 104)
LIME = (181,181, 57)

OCTAVE = 1
PERFECTFIFTH = math.log(3/2, 2)
MAJORTHIRD = math.log(5/4, 2)
SEVENTH = math.log(7/4, 2)
ELEVENTH = math.log(11/4, 2)
THIRTEENTH = math.log(13/4, 2)

BG = (177, 176, 184)
ACCENT = (92, 89, 107)

RATIOS = [None, Fraction(2), Fraction(3/2), Fraction(5/4), Fraction(7/4), Fraction(11/4), Fraction(13/4)]
INTERVALLENGTHS = [None, OCTAVE, PERFECTFIFTH, MAJORTHIRD, SEVENTH, ELEVENTH, THIRTEENTH]

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

three_names = { 1: "chy", 2:"scy",    3:"xcy",  4: "cvachy",  5: "dachy",  6: "tuichy",  7: "sachy",  8: "chlachy",  9: "yuchy",  10: "xychy", 11: "nuichy", 12: "kychy", 
               -1: "fu", -2: "schu", -3: "ju", -4: "cvafu",  -5: "dafu",  -6: "tuifu",  -7: "safu",  -8: "chlafu",  -9: "yufu",  -10: "xyfu", -11: "nuifu", -12: "kyfu"}
five_names = {1: "ly", 2:"dry", 3:"drvy", 4: "cvaly", 5: "daly", 6:"tuily", 7: "saly", 8: "chlaly", 9: "yuly", 10: "xyly", 11: "nuily", 12: "kyly",
              -1: "su", -2: "sru", -3: "srvu", -4: "cvasu", -5: "dasu", -6: "tuisu", -7: "sasu", -8: "chlasu", -9: "yusu", -10: "xysu", -11: "nuisu", -12: "kysu"}
seven_names = {1: "my", 2:"mry", 3:"mrvy", 4: "cvamy", 5: "damy", 6:"tuimy", 7: "samy", 8: "chlamy", 9: "yumy", 10: "xymy", 11: "nuimy", 12: "kymy",
              -1: "pu", -2: "pru", -3: "prvu", -4: "cvapu", -5: "dapu", -6: "tuipu", -7: "sapu", -8: "chlapu", -9: "yupu", -10: "xypu", -11: "nuipu", -12: "kypu"}
eleven_names = {1: "zy", 2:"zry", 3:"zrvy", 4: "cvazy", 5: "dazy", 6:"tuizy", 7: "sazy", 8: "chlazy", 9: "yuzy", 10: "xyzy", 11: "nuizy", 12: "kyzy",
              -1: "ku", -2: "kru", -3: "krvu", -4: "cvaku", -5: "daku", -6: "tuiku", -7: "saku", -8: "chlaku", -9: "yuku", -10: "xyku", -11: "nuiku", -12: "kyku"}
thirteen_names = {1: "gnay", 2:"gray", 3:"grvay", 4: "cvagnay", 5: "dagnay", 6:"tuignay", 7: "sagnay", 8: "chlagnay", 9: "yugnay", 10: "xygnay", 11: "nuignay", 12: "kygnay",
              -1: "gnau", -2: "grau", -3: "grvau", -4: "cvagnau", -5: "dagnau", -6: "tuignau", -7: "sagnau", -8: "chlagnau", -9: "yugnau", -10: "xygnau", -11: "nuignau", -12: "kygnau"}


names = [None, three_names, five_names, seven_names, eleven_names, thirteen_names]

# factorizations
PRIMES = [2, 3, 5, 7, 11, 13]
def pf(num: int):
    twos = 0
    threes = 0
    fives = 0
    sevens = 0
    elevens = 0
    thirteens = 0
    while num % 2 == 0:
        num /= 2
        twos += 1
    while num % 3 == 0:
        num /= 3
        threes += 1
    while num % 5 == 0:
        num /= 5
        fives += 1
    while num % 7 == 0:
        num /= 7
        sevens += 1
    while num % 11 == 0:
        num /= 11
        elevens += 1
    while num % 13 == 0:
        num /= 13
        thirteens += 1
    return (twos, threes, fives, sevens, elevens, thirteens)

def name_ratio(ratio: Fraction):
    try:
        numerator = pf(ratio.numerator)
        denominator = pf(ratio.denominator)
        combined_factors = [0, 0, 0, 0, 0, 0]
        for i in range(6):
            combined_factors[i] = combined_factors[i] + numerator[i] - denominator[i]
        num_primes = 0
        name = ""
        for i in range(1, 6):
            if combined_factors[i] != 0:
                num_primes += 1
                name += names[i][combined_factors[i]]
        
        if num_primes > 1:
            if name[-1] == "u":
                name = name[:-1]
            if name[-1] == "y":
                name = name[:-1] + "i"
        if num_primes == 0:
            name = "ah"
        
        name = name.title()
        return name.strip()
    except Exception:
        return "???"
    
def visualise_ratio(ratio: Fraction, ignore_twos=False):
        numerator = pf(ratio.numerator)
        denominator = pf(ratio.denominator)
        combined_factors = [0, 0, 0, 0, 0,  0]
        for i in range(6):
            combined_factors[i] = combined_factors[i] + numerator[i] - denominator[i]
        num_primes = 0
        name = ""
        dimensions = ['e', 'f', 'g', 'h', 'i', 'j', 'k']
        up = 'l'
        down = 'm'
        for i in range(1 if ignore_twos else 0, 6):
            if combined_factors[i] != 0:
                name += dimensions[i+1]
                if combined_factors[i] > 0:
                    name += up*combined_factors[i]
                else:
                    name += down*(-combined_factors[i])
                num_primes += 1

        if num_primes == 0:
            name = 'e'
        
        #name = name.title()
        return name.strip()