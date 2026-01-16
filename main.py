import pygame
import synth
from chord import Note, Chord
import math
from fractions import Fraction
from consts import *
from button import Button

pygame.init()
WIDTH = 1024
HEIGHT = 720
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1)

running = True

BG = (177, 176, 184)
ACCENT = (92, 89, 107)
FONT = pygame.font.Font("ripoffFont.ttf", 15)
SHASAV = pygame.font.Font("shasav.ttf", 15)

def font(size):
    return pygame.font.Font("ripoffFont.ttf", size)



test_chord1 = Chord(
    Note([
            (2, 1, Note([
                (3, -1, Note()),
                (2, 1, Note([
                    (3, -1, Note())
                ],
                is_silent=True))
            ])),
            
        ],
        #is_silent=True
    ),
    duration=1, 
    timeval=0
)
test_chord2 = Chord(
    Note(
        [(2, -1, Note([
            (2, 1, Note([
                (3, -1, Note())
            ])),
            (2, 2, Note([
                (3, -1, Note())
            ],
            is_silent=True)),
        ]))],
        is_silent=True
    ),
    
    duration=1, 
    timeval=1
)

test_chord3 = Chord(
    Note(
        [(1, -1, Note(
            [(2, 1, Note([
                (2, 1, Note([
                    (3, -1, Note())
                ])),
                (2, 2, Note([
                    (3, -1, Note())
                ],
                is_silent=True)),
            ]))],
            is_silent=True
        ),)],
        is_silent=True
    ),
    duration=1, 
    timeval=2
)

test_chord4 = Chord(
    Note(
        [(3, -1, Note(
            [(2, 1, Note(
                [(3, 1, Note())]
            )),
            (3, 1, Note()),
            ]
        ))],
        is_silent=True
    ),
    duration=1,
    timeval=3

)

synthesizer = synth.PolyphonicSynth()
synthesizer.set_waveform("triangle")
synthesizer.set_adsr(0.01, 0.1, 0.8, 0.2)
synthesizer.start()

prev_synth = synth.PolyphonicSynth()
prev_synth.set_waveform("triangle")
prev_synth.set_adsr(0.01, 0.1, 0.8, 0.2)
prev_synth.start()

timer = 0
clock = pygame.time.Clock()

octave_height = 120
bar_width = 100
root = 440
root_height = HEIGHT // 2
t0_x = 0


PRIMES = [2, 3, 5, 7, 11]
def pf(num: int):
    twos = 0
    threes = 0
    fives = 0
    sevens = 0
    elevens = 0
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
    return (twos, threes, fives, sevens, elevens)

three_names = {1: "chy", 2:"scy", 3:"xcy", -1: "fu", -2: "schu", -3: "ju"}
five_names = {1: "ly", 2:"dry", 3:"drvy", -1: "su", -2: "sru", -3: "srvu"}
seven_names = {1: "my", 2:"mry", -1: "pu", -2: "pru"}
eleven_names = {1: "zy", 2:"zry", -1: "tschu", -2: "kru"}

names = [None, three_names, five_names, seven_names, eleven_names]

def name_ratio(ratio: Fraction):
    try:
        numerator = pf(ratio.numerator)
        denominator = pf(ratio.denominator)
        combined_factors = [0, 0, 0, 0, 0]
        for i in range(5):
            combined_factors[i] = combined_factors[i] + numerator[i] - denominator[i]
        num_primes = 0
        name = ""
        for i in range(1, 5):
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
    

chords = [test_chord1, test_chord2, test_chord3, test_chord4]
test_chord = Chord(
    Note([
        (2, -1, Note(
            [
                (3, -1, Note(
                    [
                        (2, 1, Note())
                    ]
                ))
            ]
        )),
    ]),
    1,
    0
)

test_chord = Chord(
    Note(),
    1,
    0
)

closest = None


mute_button_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
mute_button_surface.fill((0, 0, 0, 0))
pygame.draw.rect(mute_button_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
mute_button_surface.blit(pygame.transform.scale(pygame.image.load("assets/sym/pitch-line-canceled.png"), (40, 8)), (5, 20))
mute_button = Button(35, HEIGHT-50, mute_button_surface)

symbol_1d = pygame.image.load("assets/sym/1d-symbol.png")
button_1d_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
button_1d_surface.fill((0, 0, 0, 0))
pygame.draw.rect(button_1d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
symbol_1d = pygame.transform.scale_by(symbol_1d, 1/5)
button_1d_surface.blit(symbol_1d, (25-symbol_1d.get_width()//2, 25-symbol_1d.get_height()//2))
button_1d = Button(50+60*1, HEIGHT-50, button_1d_surface)

symbol_2d = pygame.image.load("assets/sym/2d-symbol.png")
button_2d_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
button_2d_surface.fill((0, 0, 0, 0))
pygame.draw.rect(button_2d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
symbol_2d = pygame.transform.scale_by(symbol_2d, 1/5)
button_2d_surface.blit(symbol_2d, (25-symbol_2d.get_width()//2, 25-symbol_2d.get_height()//2))
button_2d = Button(50+60*2, HEIGHT-50, button_2d_surface)

symbol_3d = pygame.image.load("assets/sym/3d-symbol.png")
button_3d_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
button_3d_surface.fill((0, 0, 0, 0))
pygame.draw.rect(button_3d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
symbol_3d = pygame.transform.scale_by(symbol_3d, 1/5)
button_3d_surface.blit(symbol_3d, (25-symbol_3d.get_width()//2, 25-symbol_3d.get_height()//2))
button_3d = Button(50+60*3, HEIGHT-50, button_3d_surface)

symbol_4d = pygame.image.load("assets/sym/4d-symbol.png")
button_4d_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
button_4d_surface.fill((0, 0, 0, 0))
pygame.draw.rect(button_4d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
symbol_4d = pygame.transform.scale_by(symbol_4d, 1/5)
button_4d_surface.blit(symbol_4d, (25-symbol_4d.get_width()//2, 25-symbol_4d.get_height()//2))
button_4d = Button(50+60*4, HEIGHT-50, button_4d_surface)

symbol_5d = pygame.image.load("assets/sym/5d-symbol.png")
button_5d_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
button_5d_surface.fill((0, 0, 0, 0))
pygame.draw.rect(button_5d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
symbol_5d = pygame.transform.scale_by(symbol_5d, 1/5)
button_5d_surface.blit(symbol_5d, (25-symbol_5d.get_width()//2, 25-symbol_5d.get_height()//2))
button_5d = Button(50+60*5, HEIGHT-50, button_5d_surface)

symbol_arrow_up = pygame.image.load("assets/sym/ascent-symbol.png")
symbol_arrow_down = pygame.image.load("assets/sym/descent-symbol.png")
button_arrow_surface_up = pygame.Surface((50, 50), pygame.SRCALPHA)
button_arrow_surface_up.fill((0, 0, 0, 0))
button_arrow_surface_down = pygame.Surface((50, 50), pygame.SRCALPHA)
button_arrow_surface_down.fill((0, 0, 0, 0))
pygame.draw.rect(button_arrow_surface_up, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
pygame.draw.rect(button_arrow_surface_down, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
symbol_arrow_up = pygame.transform.scale_by(symbol_arrow_up, 1/5)
symbol_arrow_down = pygame.transform.scale_by(symbol_arrow_down, 1/5)
button_arrow_surface_up.blit(symbol_arrow_up, (25-symbol_arrow_up.get_width()//2, 25-symbol_arrow_up.get_height()//2))
button_arrow_surface_down.blit(symbol_arrow_down, (25-symbol_arrow_down.get_width()//2, 25-symbol_arrow_down.get_height()//2))
button_arrow = Button(75+60*6, HEIGHT-50, button_arrow_surface_up)

add_direction = 1



while running:
    # event loop
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    closest: Note
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                timer = 0
                pitches = test_chord.note.get_pitches(440)
                for freq in pitches:
                    freq_float = float(freq)
                    result = synthesizer.note_on(freq_float)
            if event.key == pygame.K_ESCAPE:
                closest = None
            
            if True:
                if event.key == pygame.K_1:
                    if closest: closest.add_derivative(1, add_direction)
                if event.key == pygame.K_2:
                    if closest: closest.add_derivative(2, add_direction)
                if event.key == pygame.K_3:
                    if closest: closest.add_derivative(3, add_direction)
                if event.key == pygame.K_4:
                    if closest: closest.add_derivative(4, add_direction)
                if event.key == pygame.K_5:
                    if closest: closest.add_derivative(5, add_direction)
                
                if event.key == pygame.K_x:
                    if closest:
                        closest.is_silent = not closest.is_silent

            if event.key == pygame.K_BACKSPACE:
                closest.parent.delete_node(closest)
                closest = None
            if event.key == pygame.K_p:
                print(test_chord.note.get_bars(y=root_height, octheight=octave_height))
            if event.key == pygame.K_LSHIFT:
                add_direction = -1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                for freq in list(synthesizer.active_notes.keys()):
                    synthesizer.note_off(freq)
            if event.key == pygame.K_LSHIFT:
                add_direction = 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            
            
            if mute_button.get_rect().collidepoint((mouse_x, mouse_y)):
                if closest:
                    closest.is_silent = not closest.is_silent
            elif button_arrow.get_rect().collidepoint((mouse_x, mouse_y)):
                add_direction = -add_direction

            elif button_1d.get_rect().collidepoint((mouse_x, mouse_y)):
                if closest: closest.add_derivative(1, add_direction)
            elif button_2d.get_rect().collidepoint((mouse_x, mouse_y)):
                if closest: closest.add_derivative(2, add_direction)
            elif button_3d.get_rect().collidepoint((mouse_x, mouse_y)):
                if closest: closest.add_derivative(3, add_direction)
            elif button_4d.get_rect().collidepoint((mouse_x, mouse_y)):
                if closest: closest.add_derivative(4, add_direction)
            elif button_5d.get_rect().collidepoint((mouse_x, mouse_y)):
                if closest: closest.add_derivative(5, add_direction)
            
            elif pygame.Rect(10, 50, WIDTH-20, HEIGHT-150).collidepoint((mouse_x, mouse_y)):
                nodes: list[Note] = test_chord.note.get_notes()
                ylevels: list[tuple[float, int]] = list(zip(test_chord.note.get_ylevels(root_height, octave_height), range(len(nodes))))
                ylevels.sort(key=(lambda i: abs(i[0]-mouse_y)))
                closest_tuple = ylevels[0]
                closest = nodes[closest_tuple[1]]
                closest_ratio = closest.ratio
                prev_synth.note_on(440*closest_ratio)
            else:
                closest = None
        
        if event.type == pygame.MOUSEBUTTONUP:
            for freq in list(prev_synth.active_notes.keys()):
                prev_synth.note_off(freq)

    if add_direction == 1:
        button_arrow.base_surface = button_arrow_surface_up
    else:
         button_arrow.base_surface = button_arrow_surface_down

    if keys[pygame.K_w]:
        root_height += 10
    if keys[pygame.K_s]:
        root_height -= 10
    if keys[pygame.K_a]:
        t0_x += 10
    if keys[pygame.K_d]:
        t0_x -= 10
    


    # draw
    window.fill(ACCENT)
    bg_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    bg_surface.get_rect().topleft = (0, 0)
    bg_surface.fill(BG)
    pygame.draw.rect(bg_surface, (0, 0, 0, 0), pygame.Rect(10, 50, WIDTH-20, HEIGHT-150), border_radius=10)
    title_text = FONT.render("NAFCHALICA", True, ACCENT)
    title_text2 = FONT.render("MIKROTONOS", True, ACCENT)
    title_rect = title_text.get_rect()
    title_rect.topleft = (20, 10)
    title_rect2 = title_text2.get_rect()
    title_rect2.topleft = (20, 28)


    # guidelines
    current_y = root_height
    i = 0

    pygame.draw.line(window, (192, 192, 192), (max(t0_x, 0), root_height), (WIDTH, root_height))
    freq_text: pygame.Surface = FONT.render(str(440*2**i) + "Hz", True, (192, 192, 192))
    freq_text_width = freq_text.get_width()
    freq_rect = freq_text.get_rect()
    if t0_x < 12+freq_text_width:
        freq_rect.midleft = (12, current_y)
    else:
        freq_rect.midright = (t0_x-2, current_y)

    window.blit(freq_text, freq_rect)


    while current_y > 0:
        current_y -= octave_height
        i += 1
        pygame.draw.line(window, (128, 128, 128), (max(t0_x, 0), current_y), (WIDTH, current_y))
        freq_text: pygame.Surface = FONT.render(str(440*2**i) + "Hz", True, (BG))
        freq_text_width = freq_text.get_width()
        freq_rect = freq_text.get_rect()
        if t0_x < 12+freq_text_width:
            freq_rect.midleft = (12, current_y)
        else:
            freq_rect.midright = (t0_x-2, current_y)

        window.blit(freq_text, freq_rect)


    current_y = root_height
    i = 0
    while current_y < HEIGHT:
        current_y += octave_height
        i -= 1
        pygame.draw.line(window, (128, 128, 128), (max(t0_x, 0), current_y), (WIDTH, current_y))
        pygame.draw.line(window, (128, 128, 128), (max(t0_x, 0), current_y), (WIDTH, current_y))
        freq_text: pygame.Surface = FONT.render(str(440*2**i) + "Hz", True, (BG))
        freq_text_width = freq_text.get_width()
        freq_rect = freq_text.get_rect()
        if t0_x < 12+freq_text_width:
            freq_rect.midleft = (12, current_y)
        else:
            freq_rect.midright = (t0_x-2, current_y)

        window.blit(freq_text, freq_rect)


    test_chord.draw(window, root_height, t0_x, bar_width, octave_height)
    if closest:
        drawn_ylevel = root_height - math.log(closest_ratio, 2)*octave_height
        if closest.is_silent:
            draw_dotted_line(window, (255, 255, 255), (t0_x + bar_width*(test_chord.time), drawn_ylevel), (t0_x + bar_width*(test_chord.time + test_chord.duration), drawn_ylevel), 5)
        else:
            pygame.draw.line(window, (255, 255, 255), (t0_x + bar_width*(test_chord.time), drawn_ylevel), (t0_x + bar_width*(test_chord.time + test_chord.duration), drawn_ylevel), 5)
    pygame.draw.line(window, (128, 128, 128), (t0_x, 0), (t0_x, HEIGHT), 3)

    window.blit(bg_surface, bg_surface.get_rect())
    window.blit(title_text, title_rect)
    window.blit(title_text2, title_rect2)

    if closest:
        note_info_text = font(30).render(f"440Hz X {closest_ratio}", True, ACCENT)
        note_info_rect = note_info_text.get_rect()
        note_info_rect.topleft = (100, 10)
        window.blit(note_info_text, note_info_rect)

        note_name_text = font(30).render(f"{name_ratio(closest_ratio)}", True, ACCENT)
        note_name_rect = note_name_text.get_rect()
        note_name_rect.topright = (WIDTH-10, 10)
        window.blit(note_name_text, note_name_rect)
    
    for button in [mute_button, button_1d, button_2d, button_3d, button_4d, button_5d, button_arrow]:
        button.update((mouse_x, mouse_y), mouse_pressed)
        button.draw(window)

    
    pygame.display.flip()
    clock.tick(60)  # 60 FPS
    timer += clock.get_time()

    if closest: print(closest.parent)

synthesizer.stop()
pygame.quit()
