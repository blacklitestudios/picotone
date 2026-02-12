import pygame
import synth
from chord import Note, Chord
import math
from fractions import Fraction
from consts import *
from button import Button
from ranges import Range
import sys
import json

import bisect  # At top of file

# Helper function
def find_visible_chords(chord_times, min_time, max_time, chords_dict):
    """Use binary search to find only chords visible in viewport."""
    if not chord_times:
        return []
    
    start_idx = max(0, bisect.bisect_left(chord_times, min_time) - 1)
    end_idx = min(len(chord_times), bisect.bisect_right(chord_times, max_time))
    
    visible = []
    for i in range(start_idx, end_idx):
        t = chord_times[i]
        if t not in chords_dict:
            continue

        chord = chords_dict[t]
        if chord.time + chord.duration >= min_time and chord.time <= max_time:
            visible.append(t)
    
    return visible


# init window
pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.SRCALPHA, vsync=1)
pygame.display.set_caption("PicoTone")
pygame.display.set_icon(pygame.image.load("assets/icon.bmp"))
running = True

# colors & fonts

FONT = pygame.font.Font("assets/fonts/lisa.ttf", 15)
SHASAV = pygame.font.Font("assets/fonts/icons.ttf", 15)

def get_font(size):
    return pygame.font.Font("assets/fonts/lisa.ttf", size)

def get_shasavic(size):
    return pygame.font.Font("assets/fonts/icons.ttf", size)

# synths
WAVE = "triangle"
synthesizer = synth.PolyphonicSynth()
synthesizer.set_waveform(WAVE)
synthesizer.set_adsr(0.01, 0.1, 0.8, 0.01)
synthesizer.start()

synthesizer2 = synth.PolyphonicSynth()
synthesizer2.set_waveform(WAVE)
synthesizer2.set_adsr(0.01, 0.1, 0.8, 0.01)
synthesizer2.start()




prev_synth = synth.PolyphonicSynth()
prev_synth.set_waveform(WAVE)
prev_synth.set_adsr(0.01, 0.1, 0.8, 0.01)
prev_synth.start()

# timekeeping
timer = 0
clock = pygame.time.Clock()




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





    


# voices & chords
test_chord_1 = Chord(
    Note(),
    1,
    0
)
test_chord_2 = Chord(
    Note(ratio=Fraction(2)),
    1,
    0
)



# buttons
mute_button_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
mute_button_surface.fill((0, 0, 0, 0))
pygame.draw.rect(mute_button_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
mute_button_surface.blit(pygame.transform.scale(pygame.image.load("assets/sym/pitch-line-canceled.png"), (40, 8)), (5, 20))
mute_button = Button(35, HEIGHT-50, mute_button_surface)

dimension_images = [None]
for i in range(1, 7):
    dimension_images.append(pygame.transform.scale_by(pygame.image.load(f"assets/sym/{i}d-symbol.png"), 1/5))

def create_dimension_button(dimension, x, y):
    symbol_1d = pygame.image.load(f"assets/sym/{dimension}d-symbol.png")
    button_1d_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    button_1d_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(button_1d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
    symbol_1d = pygame.transform.scale_by(symbol_1d, 1/5)
    button_1d_surface.blit(symbol_1d, (25-symbol_1d.get_width()//2, 25-symbol_1d.get_height()//2))
    button_1d = Button(x, y, button_1d_surface)
    return button_1d

def create_button(file, x, y, size):
    symbol_1d = pygame.image.load(file)
    button_1d_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    button_1d_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(button_1d_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
    #symbol_1d = pygame.transform.scale_by(symbol_1d, 1/5)
    button_1d_surface.blit(symbol_1d, (25-symbol_1d.get_width()//2, 25-symbol_1d.get_height()//2))
    button_1d = Button(x, y, button_1d_surface)
    return button_1d

button_1d = create_dimension_button(1, 50+1*60, HEIGHT-50)
button_2d = create_dimension_button(2, 50+2*60, HEIGHT-50)
button_3d = create_dimension_button(3, 50+3*60, HEIGHT-50)
button_4d = create_dimension_button(4, 50+4*60, HEIGHT-50)
button_5d = create_dimension_button(5, 50+5*60, HEIGHT-50)
button_6d = create_dimension_button(6, 50+6*60, HEIGHT-50)

create_chord_buttons = []
for i in range(1, 7):
    create_chord_buttons.append(create_dimension_button(i, WIDTH//4+45+60, HEIGHT*1//4+60*i-30))

create_chord_buttons_plus = []
for i in range(1, 7):
    create_chord_buttons_plus.append(create_button("assets/plus.png", WIDTH//4+45+2*60, HEIGHT*1//4+60*i-30, 50))

create_chord_buttons_minus = []
for i in range(1, 7):
    create_chord_buttons_minus.append(create_button("assets/minus.png", WIDTH//4+45, HEIGHT*1//4+60*i-30, 50))

create_chord_confirm = create_button("assets/confirm.png", WIDTH*3//4 - 45, HEIGHT*3//4 - 45, 50)
create_chord_reset = create_button("assets/reset.png", WIDTH*3//4 - 45, HEIGHT*3//4 - 45-60, 50)

button_whole = create_button("assets/rhythm/whole.png", 60+14*60, HEIGHT-50, 50)
button_half = create_button("assets/rhythm/half.png", 60+13*60, HEIGHT-50, 50)
button_quarter = create_button("assets/rhythm/quarter.png", 60+12*60, HEIGHT-50, 50)
button_eighth = create_button("assets/rhythm/eigth.png", 60+11*60, HEIGHT-50, 50)
button_sixteenth = create_button("assets/rhythm/sixteenth.png", 60+10*60, HEIGHT-50, 50)
button_32nd = create_button("assets/rhythm/thirtysecond.png", 60+9*60, HEIGHT-50, 50)

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
button_arrow = Button(75+60*7, HEIGHT-50, button_arrow_surface_up)


add_chord_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
add_chord_surface.fill((0, 0, 0, 0))
pygame.draw.rect(add_chord_surface, ACCENT, pygame.Rect(0, 0, 50, 50), border_radius=10)
pygame.draw.line(add_chord_surface, (255, 255, 255), (15, 25), (35, 25), 3)
pygame.draw.line(add_chord_surface, (255, 255, 255), (25, 15), (25, 35), 3)
add_chord_button = Button(WIDTH-50, HEIGHT-50, add_chord_surface)
add_direction = 1

current_page = "chordograph"

current_menu = ""

add_chord_ratio = Fraction(1, 1)

current_time = 0
barspersecond = 1/3
paused = True

# Playback indices for optimized chord lookup
voice1_playback_idx = 0
voice2_playback_idx = 0

break_length = 1/32
selected_length = Fraction(0)

keychanges = {0: 1}
keys_order = [0]
key_playback_idx = 0


def find_chord(time, voice):
    """Optimized chord lookup using playback index - O(1) instead of O(n)"""
    global voice1_playback_idx, voice2_playback_idx
    
    if voice == 1:
        chordarr = voice1
        chordorder = voice1_order
        playback_idx = voice1_playback_idx
    elif voice == 2:
        chordarr = voice2
        chordorder = voice2_order
        playback_idx = voice2_playback_idx
    else:
        return None
    
    if len(chordorder) == 0:
        return None
    
    # Clamp index to valid range
    playback_idx = max(0, min(playback_idx, len(chordorder) - 1))
    
    # Get current chord
    chord_time = chordorder[playback_idx]
    chord = chordarr[chord_time]
    
    # Check if we need to advance to next chord
    while playback_idx < len(chordorder) - 1:
        next_chord_time = chordorder[playback_idx + 1]
        next_chord = chordarr[next_chord_time]
        
        # If time has passed the current chord's end, move to next
        if time >= chord.time + chord.duration and time >= next_chord.time:
            playback_idx += 1
            chord_time = next_chord_time
            chord = next_chord
        else:
            break
    
    # Check if we need to go back to previous chord (e.g., user seeked backwards)
    while playback_idx > 0:
        if time < chord.time:
            playback_idx -= 1
            chord_time = chordorder[playback_idx]
            chord = chordarr[chord_time]
        else:
            break
    
    # Update global playback index
    if voice == 1:
        voice1_playback_idx = playback_idx
    elif voice == 2:
        voice2_playback_idx = playback_idx
    
    # Check if time is within the chord's duration
    if time < chord.time or time > chord.time + chord.duration:
        return None
    
    return chord

def find_key(time):
    """Optimized chord lookup using playback index - O(1) instead of O(n)"""
    global key_playback_idx
    
    
    chordarr = keychanges
    chordorder = keys_order
    playback_idx = key_playback_idx

    
    if len(chordorder) == 0:
        return None
    
    # Clamp index to valid range
    playback_idx = max(0, min(playback_idx, len(chordorder) - 1))
    
    # Get current chord
    chord_time = chordorder[playback_idx]
    chord = chordarr[chord_time]
    
    # Check if we need to advance to next chord
    while playback_idx < len(chordorder) - 1:
        next_chord_time = chordorder[playback_idx + 1]
        next_chord = chordarr[next_chord_time]
        
        # If time has passed the current chord's end, move to next
        if time >= next_chord:
            playback_idx += 1
            chord_time = next_chord_time
            chord = next_chord
        else:
            break
    
    # Check if we need to go back to previous chord (e.g., user seeked backwards)
    while playback_idx > 0:
        if time < chordorder[playback_idx]:
            playback_idx -= 1
            chord_time = chordorder[playback_idx]
            chord = chordarr[chord_time]
        else:
            break
    
    # Update global playback index
    key_playback_idx = playback_idx
    
    return chord

def reset_playback_indices():
    """Reset playback indices when seeking or restarting playback"""
    global voice1_playback_idx, voice2_playback_idx
    voice1_playback_idx = 0
    voice2_playback_idx = 0

ROOT = 440

def save_to_json():
    obj = {}
    obj["voice1"] = []
    obj["voice2"] = []
    obj["root"] = ROOT
    for chord_time in voice1:
        chord_obj = voice1[chord_time].as_json()
        obj["voice1"].append(chord_obj)
    for chord_time in voice2:
        chord_obj = voice2[chord_time].as_json()
        obj["voice2"].append(chord_obj)
    
    return obj

# The Main Loading Function
def load_from_json(json_data):
    # If json_data is a string, parse it; if it's already a dict, use it directly
    if isinstance(json_data, str):
        obj = json.loads(json_data)
    else:
        obj = json_data

    # Initialize the structure to match your original global variables
    loaded_state = {
        "root": obj.get("root"),
        "voice1": {},
        "voice2": {}
    }

    # Reconstruct Voice 1
    # Your save function converted a Dict (time -> chord) to a List.
    # We must convert that List back to a Dict keyed by time.
    for chord_data in obj.get("voice1", []):
        chord = Chord.from_json(chord_data)
        loaded_state["voice1"][chord.time] = chord

    # Reconstruct Voice 2
    for chord_data in obj.get("voice2", []):
        chord = Chord.from_json(chord_data)
        loaded_state["voice2"][chord.time] = chord

    return loaded_state




resizing_chord = None
resize_start_duration = None
repositioning_chord = None
repos_start_time = None
repos_offset = None

while running:
    # event loop
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    # draw
    window.fill(ACCENT)
    bg_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    bg_surface.get_rect().topleft = (0, 0)
    bg_surface.fill(BG)
    pygame.draw.rect(bg_surface, (0, 0, 0, 0), pygame.Rect(10, 100, WIDTH-220, HEIGHT-250), border_bottom_left_radius=10, border_bottom_right_radius=10, border_top_right_radius=10)
    pygame.draw.rect(bg_surface, ACCENT, pygame.Rect(WIDTH-200, 100, 180, 100), border_radius=10)
    pygame.draw.rect(bg_surface, ACCENT, pygame.Rect(10, HEIGHT-140, WIDTH-220, 50), border_radius=10)
    other_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    other_layer.fill(BG)
    pygame.draw.rect(other_layer, (0, 0, 0, 0), pygame.Rect(10, 100, WIDTH-220, HEIGHT-250), border_bottom_left_radius=10, border_bottom_right_radius=10, border_top_right_radius=10)
    pygame.draw.rect(other_layer, ACCENT, pygame.Rect(WIDTH-200, 100, 180, 100), border_radius=10)
    pygame.draw.rect(other_layer, (0, 0, 0, 0), pygame.Rect(10, HEIGHT-140, WIDTH-220, 50), border_radius=10)
    title_text = get_font(30).render("PICOTONE", True, ACCENT)
    title_text2 = FONT.render("SHASAVIC", True, ACCENT)
    title_rect = title_text.get_rect()
    title_rect.topleft = (20, 10)
    title_rect2 = title_text2.get_rect()
    title_rect2.topleft = (20, 28)



    if current_page == "chordograph": # default visualisation mode
        # resolve test chords
        if 0 <= selected_chord_index < len(voice1_order):
            print(voice1, voice1_order)
            test_chord_1 = voice1[voice1_order[selected_chord_index]]
        else:
            test_chord_1 = Chord(Note(ratio=Fraction(0)), duration=0, timeval=0)
        if 0 <= selected_chord_index < len(voice2_order):
            test_chord_2 = voice2[voice2_order[selected_chord_index]]
        else:
            test_chord_2 = Chord(Note(ratio=Fraction(0)), duration=0, timeval=0)

        try:
            # chords_order provides the mapping from index -> time
            test_chord = chords[chords_order[selected_chord_index]]
        except Exception:
            test_chord = None
        
        closest: Note

        cursor_type = pygame.SYSTEM_CURSOR_ARROW
        is_near_edge = False

        if pygame.Rect(10, HEIGHT-140, WIDTH-220, 50).collidepoint(mouse_x, mouse_y):
            mouse_time = (mouse_x - t0_x) / bar_width
            for chord in chords.values():
                chord_start = t0_x + bar_width * chord.time
                chord_end = t0_x + bar_width * (chord.time + chord.duration)
                if abs(mouse_x - chord_end) < RESIZE_EDGE_THRESHOLD:
                    if mouse_y > 100 and mouse_y < HEIGHT - 50:  # within the drawing area
                        cursor_type = pygame.SYSTEM_CURSOR_SIZEWE  # horizontal resize cursor
                        is_near_edge = True
                        break
        pygame.mouse.set_cursor(cursor_type)


        for event in events:
            if event.type == pygame.QUIT:
                # quit the game
                running = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # play
                    paused = not paused
                    if paused:
                        for freq in synthesizer.active_notes:
                            freq_float = float(freq)
                            result = synthesizer.note_off((freq))
                        for freq in synthesizer2.active_notes:
                            freq_float = float(freq)
                            result = synthesizer2.note_off((freq))

                if event.key == pygame.K_SPACE:
                    # preview chord
                    pitches = test_chord_1.get_freqs(keychanges[find_key(test_chord_1.time)]*test_chord_1.note.ratio)
                    for freq in pitches:
                        freq_float = float(freq)
                        result = synthesizer.note_on((freq))

                    pitches = test_chord_2.get_freqs(ROOT*test_chord_2.note.ratio)
                    for freq in pitches:
                        freq_float = float(freq)
                        result = synthesizer.note_on((freq))

                if event.key == pygame.K_ESCAPE:
                    # stop selection
                    closest = None
                
                if not current_menu:
                    # no menu currently
                    if event.key == pygame.K_1:
                        # switch to voice 1
                        if keys[pygame.K_LCTRL]:
                            chords = voice1
                            chords_order = voice1_order
                            selected_chord_index = min(len(chords_order)-1, selected_chord_index) if len(chords_order) > 0 else 0
                            closest = None
                        else:
                            # 1d
                            if closest: closest.add_derivative(1, add_direction)

                    if event.key == pygame.K_2:
                        if keys[pygame.K_LCTRL]:
                            # switch to voice 2
                            chords = voice2
                            chords_order = voice2_order
                            selected_chord_index = min(len(chords_order)-1, selected_chord_index) if len(chords_order) > 0 else 0
                            closest = None
                        else:
                            # 2d
                            if closest: closest.add_derivative(2, add_direction)
                    if event.key == pygame.K_3:
                        # 3d
                        if closest: closest.add_derivative(3, add_direction)
                    if event.key == pygame.K_4:
                        # 4d
                        if closest: closest.add_derivative(4, add_direction)
                    if event.key == pygame.K_5:
                        # 5d
                        if closest: closest.add_derivative(5, add_direction)
                    if event.key == pygame.K_6:
                        # 6d
                        if closest: closest.add_derivative(6, add_direction)
                    
                    if event.key == pygame.K_x:
                        # silence note
                        if closest:
                            closest.is_silent = not closest.is_silent
                
                    if event.key == pygame.K_RIGHT:
                        # navigation
                        selected_chord_index += 1
                        if selected_chord_index >= len(chords_order):
                            selected_chord_index = max(0, len(chords_order)-1)
                        else:
                            t = chords_order[selected_chord_index]
                            closest_ratio = chords[t].note.ratio
                            closest = chords[t].note
                            test_chord = chords[t]
                    if event.key == pygame.K_LEFT:
                        if selected_chord_index > 0:
                            selected_chord_index -= 1
                            t = chords_order[selected_chord_index]
                            test_chord = chords[t]
                            closest_ratio = chords[t].note.ratio
                            closest = chords[t].note

                    if event.key == pygame.K_BACKSPACE:
                        # delete node/chord
                        if closest:
                            if closest.parent:
                                closest.parent.delete_node(closest)
                                closest = closest.parent
                                closest_ratio = closest.ratio
                                #closest = None
                            else:
                                # delete chord by time key
                                t = chords_order[selected_chord_index]
                                del chords[t]
                                chords_order.pop(selected_chord_index)
                                selected_chord_index = max(0, selected_chord_index-1)
                                if len(chords_order) == 0:
                                    selected_chord_index = 0
                                    closest = None

                    if event.key == pygame.K_LSHIFT:
                        # reverse direction
                        add_direction = -1
                    
                    

                    elif event.key == pygame.K_f:
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 0.125
                    elif event.key == pygame.K_g:
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 0.25
                    elif event.key == pygame.K_h:
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 0.5
                    elif event.key == pygame.K_j:
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 1
                    elif event.key == pygame.K_k:
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 2
                    elif event.key == pygame.K_l:
                        if not keys[pygame.K_LCTRL]:
                            if current_menu == "addchord":
                                current_menu = ""
                            else:
                                current_menu = "addchord"
                            add_chord_ratio = Fraction(1)
                            selected_length = 4
                    elif event.key == pygame.K_SEMICOLON:
                        if not keys[pygame.K_LCTRL]:
                            if current_menu == "addkeysig":
                                current_menu = ""
                            else:
                                current_menu = "addkeysig"
                            add_chord_ratio = Fraction(1)
                if event.key == pygame.K_RETURN:
                    # determine new chord time based on last chord time in order

                    if current_menu == "addchord":

                        if len(chords_order) > 0:
                            last_time = chords[chords_order[-1]].time + chords[chords_order[-1]].duration + break_length
                            new_time = last_time
                        else:
                            new_time = 0

                        new_chord = Chord(
                            Note(ratio=add_chord_ratio),
                            selected_length-break_length,
                            new_time,
                        )

                        # insert after selected index or append
                        insert_pos = selected_chord_index + 1
                        if insert_pos >= len(chords_order):
                            # append
                            chords[new_time] = new_chord
                            chords_order.append(new_time)
                            chords_order.sort()
                        else:
                            # insert at position
                            chords[new_time] = new_chord
                            chords_order.insert(insert_pos, new_time)
                            chords_order.sort()

                        current_menu = ""

                if event.key == pygame.K_s:
                    if keys[pygame.K_LCTRL]:
                        with open("save.json", "w") as f:
                            json.dump(save_to_json(), f)

                if event.key == pygame.K_l:
                    if keys[pygame.K_LCTRL]:
                        with open("save.json", "r") as f:
                            data = json.load(f)

                        restored_data = load_from_json(data)
                        voice1 = restored_data["voice1"]
                        voice1_order = list(voice1.keys())
                        voice2 = restored_data["voice2"]
                        voice2_order = list(voice2.keys())
                        root = restored_data["root"]
                    

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    # revert
                    add_direction = 1

                if event.key == pygame.K_SPACE:
                    # stop playing
                    for freq in synthesizer.active_notes:
                        synthesizer.note_off(freq)

            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if not current_menu:
                    # mote note
                    if mute_button.get_rect().collidepoint((mouse_x, mouse_y)):
                        if closest:
                            closest.is_silent = not closest.is_silent
                    
                    # reverse direction
                    elif button_arrow.get_rect().collidepoint((mouse_x, mouse_y)):
                        add_direction = -add_direction

                    # add note
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
                    elif button_6d.get_rect().collidepoint((mouse_x, mouse_y)):
                        if closest: closest.add_derivative(6, add_direction)

                    # time values
                    elif button_quarter.get_rect().collidepoint((mouse_x, mouse_y)):
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 1
                    elif button_half.get_rect().collidepoint((mouse_x, mouse_y)):
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 2
                    elif button_eighth.get_rect().collidepoint((mouse_x, mouse_y)):
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 0.5
                    elif button_sixteenth.get_rect().collidepoint((mouse_x, mouse_y)):
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 0.25
                    elif button_whole.get_rect().collidepoint((mouse_x, mouse_y)):
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 4
                    elif button_32nd.get_rect().collidepoint((mouse_x, mouse_y)):
                        if current_menu == "addchord":
                            current_menu = ""
                        else:
                            current_menu = "addchord"
                        add_chord_ratio = Fraction(1)
                        selected_length = 0.125
                    
                    # select notes
                    elif pygame.Rect(10, HEIGHT-140, WIDTH-220, 50).collidepoint(mouse_x, mouse_y):
                        print("tm")
                        for chord in list(voice1.values()) + list(voice2.values()):
                            chord_end_x = t0_x + bar_width * (chord.time + chord.duration)
                            if abs(mouse_x - chord_end_x) < RESIZE_EDGE_THRESHOLD:
                                resizing_chord = chord
                                resize_start_duration = chord.duration
                                break
                        else:
                            for chord in list(voice1.values()) + list(voice2.values()):
                                chord_start_x = t0_x + bar_width * (chord.time)
                                chord_end_x = t0_x + bar_width * (chord.time + chord.duration)
                                if chord_start_x < mouse_x and mouse_x < chord_end_x:
                                    old_time_idx = chords_order.index(chord.time)
                                    print("dofijf", chords_order, old_time_idx)
                                    repositioning_chord = chord
                                    repos_start_time = chord.time
                                    repos_offset = mouse_x - chord_start_x
                                    break
                    
                    if pygame.Rect(10, 100, WIDTH-20, HEIGHT-150).collidepoint((mouse_x, mouse_y)) and test_chord:
                        time = (mouse_x - t0_x) / bar_width
                        if True:
                            for chord in chords.values():
                                #print(time, chord.duration + chord.time ,chord.time)
                                if time < chord.duration + chord.time and time > chord.time:
                                    #t = chords_order[time]
                                    test_chord = chord
                                    
                                    selected_chord_index = chords_order.index(chord.time)
                                    nodes: list[Note] = test_chord.note.get_notes()
                                    ylevels: list[tuple[float, int]] = list(zip(test_chord.note.get_ylevels(root_height-math.log(test_chord.note.ratio, 2)*octave_height, octave_height), range(len(nodes))))
                                    ylevels.sort(key=(lambda i: abs(i[0]-mouse_y)))
                                    closest_tuple = ylevels[0]
                                    temp_closest = nodes[closest_tuple[1]]
                                    if True:
                                        closest = temp_closest
                                        closest_ratio = closest.ratio
                                        prev_synth.note_on(ROOT*closest_ratio)
                                        current_time = test_chord.time
                                        reset_playback_indices()  # Reset indices when seeking
                                    break

                    

                    

                    else:
                        closest = None

                
                elif current_menu == "addchord":
                    for i, button in enumerate(create_chord_buttons_plus):
                        if button.get_rect().collidepoint((mouse_x, mouse_y)):
                            add_chord_ratio *= RATIOS[i+1]
                            #print(add_chord_ratio)
                    for i, button in enumerate(create_chord_buttons_minus):
                        if button.get_rect().collidepoint((mouse_x, mouse_y)):
                            add_chord_ratio /= RATIOS[i+1]
                    if create_chord_confirm.get_rect().collidepoint((mouse_x, mouse_y)):
                        # determine new chord time based on last chord time in order
                        if len(chords_order) > 0:
                            last_time = chords[chords_order[-1]].time + chords[chords_order[-1]].duration + break_length
                            new_time = last_time
                        else:
                            new_time = 0

                        keysig = find_key(new_time)
                        new_chord = Chord(
                            Note(ratio=add_chord_ratio*keysig),
                            selected_length-break_length,
                            new_time,
                        )

                        # insert after selected index or append
                        insert_pos = selected_chord_index + 1
                        if insert_pos >= len(chords_order):
                            # append
                            chords[new_time] = new_chord
                            chords_order.append(new_time)
                            chords_order.sort()
                        else:
                            # insert at position
                            chords[new_time] = new_chord
                            chords_order.insert(insert_pos, new_time)
                            chords_order.sort()

                        current_menu = ""
                    if create_chord_reset.get_rect().collidepoint((mouse_x, mouse_y)):
                        add_chord_ratio = Fraction(1)
                elif current_menu == "addkeysig":
                    for i, button in enumerate(create_chord_buttons_plus):
                        if button.get_rect().collidepoint((mouse_x, mouse_y)):
                            add_chord_ratio *= RATIOS[i+1]
                            #print(add_chord_ratio)
                    for i, button in enumerate(create_chord_buttons_minus):
                        if button.get_rect().collidepoint((mouse_x, mouse_y)):
                            add_chord_ratio /= RATIOS[i+1]
                    if create_chord_confirm.get_rect().collidepoint((mouse_x, mouse_y)):
                        # determine new chord time based on last chord time in order
                        if len(chords_order) > 0:
                            last_time = chords[chords_order[-1]].time + chords[chords_order[-1]].duration + break_length
                            new_time = last_time
                        else:
                            new_time = 0

                        keysig = find_key(new_time)
                    

                        # insert after selected index or append
                        insert_pos = key_playback_idx + 1
                        if insert_pos >= len(chords_order):
                            # append
                            keychanges[new_time] = add_chord_ratio
                            keys_order.append(new_time)
                            keys_order.sort()
                        else:
                            # insert at position
                            keychanges[new_time] = add_chord_ratio
                            keys_order.insert(insert_pos, new_time)
                            keys_order.sort()

                        current_menu = ""
                    if create_chord_reset.get_rect().collidepoint((mouse_x, mouse_y)):
                        add_chord_ratio = Fraction(1)
            
            if event.type == pygame.MOUSEMOTION:
                if resizing_chord:
                    # Calculate new duration based on mouse position
                    new_duration = max(0.125, 0.03125*(round(32*((mouse_x - t0_x) / bar_width - resizing_chord.time))))
                    resizing_chord.duration = new_duration
                if repositioning_chord:
                    # Calculate new duration based on mouse position
                    
                    #print(0.03125*(round(32*(((mouse_x - t0_x)/bar_width) -repos_offset))))
                    new_position = max(0, 0.03125*(round(32*(((mouse_x - t0_x -repos_offset)/bar_width) ))))
                    repositioning_chord.time = new_position
                    
                        
            if event.type == pygame.MOUSEBUTTONUP:
                for freq in list(prev_synth.active_notes.keys()):
                    prev_synth.note_off(freq)
                
                if resizing_chord:
                    chords_order.sort()
                    chords_snap = chords.copy()
                    for i, chord in zip(chords_snap.keys(), chords_snap.values()):
                        if chord is not resizing_chord:
                            overlap = Range(chord.time, chord.time + chord.duration).union(
                                Range(resizing_chord.time, resizing_chord.time + resizing_chord.duration)
                            ) == Range(resizing_chord.time, resizing_chord.time + resizing_chord.duration)
                            if overlap:
                                # Remove from dict
                                if chord.time in chords:
                                    del chords[chord.time]
                                # Remove from order list - FIX FOR KEYERROR
                                if chord.time in chords_order:
                                    chords_order.remove(chord.time)
                    chords_order.clear() 
                    for i in list(chords.keys()): chords_order.append(i)
                    chords_order.sort()
                    test_chord = chords[chords_order[0]]
                    selected_chord_index = 0

                resizing_chord = None
                resize_start_duration = None
                
                if repositioning_chord:
                    old_time = chords_order[old_time_idx]
                    new_position = repositioning_chord.time
                    del chords[old_time]
                    chords_order.remove(old_time)
                    chords_order.append(new_position)
                    chords_order.sort()
                    if chords.get(new_position) is not None:
                        del chords[new_position]
                        #del chords_order[old_time_idx]
                        
                    
                    
                    chords[new_position] = repositioning_chord
                    print(old_time_idx)
                    print(chords_order)
                    
                    chords_order.sort()
                    chords_snap = chords.copy()
                    for i, chord in zip(chords_snap.keys(), chords_snap.values()):
                        if chord is not repositioning_chord:
                            overlap = Range(chord.time, chord.time + chord.duration).union(
                                Range(repositioning_chord.time, repositioning_chord.time + repositioning_chord.duration)
                            ) == Range(repositioning_chord.time, repositioning_chord.time + repositioning_chord.duration)
                            if overlap:
                                # Remove from dict
                                if chord.time in chords:
                                    del chords[chord.time]
                                # Remove from order list - FIX FOR KEYERROR
                                if chord.time in chords_order:
                                    chords_order.remove(chord.time)
                    chords_order.clear() 
                    for i in list(chords.keys()): chords_order.append(i)
                    chords_order.sort()
                    print(chords, chords_order)
                    test_chord = chords[chords_order[0]]
                    selected_chord_index = 0
                
                        
                        
                repositioning_chord = None
                repos_start_time = None
                repos_offset = None

            
                    

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
        

        


        # guidelines
        

        

        drawing_intervals = {}
        leftmost_time = -t0_x/bar_width
        rightmost_time = (-t0_x+WIDTH)/bar_width
        for i in range(len(keys_order)-1):
            if Range(leftmost_time, rightmost_time).intersection(Range(keys_order[i], keys_order[i+1])):
                drawing_intervals[Range(leftmost_time, rightmost_time).intersection(Range(keys_order[i], keys_order[i+1]))] = i
        
        if Range(leftmost_time, rightmost_time).intersection(Range(keys_order[-1], math.inf)):
                drawing_intervals[Range(leftmost_time, rightmost_time).intersection(Range(keys_order[-1], math.inf))] = len(keys_order)-1

        
        #print(drawing_intervals)

        for interval in drawing_intervals:
            rt = keychanges[keys_order[drawing_intervals[interval]]]
            current_y = root_height-math.log(rt, 2)*octave_height
            i = 0
            pygame.draw.line(window, (255, 255, 255), (max(t0_x, interval.start*bar_width+t0_x), current_y), ((interval.end)*bar_width+t0_x, current_y))
            while current_y > 0:
                
                current_y -= octave_height
                i += 1
                pygame.draw.line(window, (128, 128, 128), (max(t0_x, interval.start*bar_width+t0_x), current_y), ((interval.end)*bar_width+t0_x, current_y))
                freq_text: pygame.Surface = FONT.render(str(ROOT*2**i*rt) + "Hz", True, (BG))
                freq_text_width = freq_text.get_width()
                freq_rect = freq_text.get_rect()
                if t0_x < 12+freq_text_width:
                    freq_rect.midleft = (12, current_y)
                else:
                    freq_rect.midright = (t0_x-2, current_y)

                #window.blit(freq_text, freq_rect)


            current_y = root_height-math.log(rt, 2)*octave_height
            i = 0
            while current_y < HEIGHT:
                current_y += octave_height
                i -= 1
                #pygame.draw.line(window, (128, 128, 128), (max(t0_x, interval.start*bar_width+t0_x), current_y), ((interval.end-interval.start)*bar_width, current_y))
                pygame.draw.line(window, (128, 128, 128), (max(t0_x, interval.start*bar_width+t0_x), current_y), ((interval.end)*bar_width+t0_x, current_y))
                freq_text: pygame.Surface = FONT.render(str(ROOT*2**i) + "Hz", True, (BG))
                freq_text_width = freq_text.get_width()
                freq_rect = freq_text.get_rect()
                if t0_x < 12+freq_text_width:
                    freq_rect.midleft = (12, current_y)
                else:
                    freq_rect.midright = (t0_x-2, current_y)

                #window.blit(freq_text, freq_rect)

        if not paused:
            pygame.draw.line(window, (128, 128, 128), (t0_x+current_time*bar_width, 0), (t0_x+current_time*bar_width, HEIGHT))


        # draw voices in time order (only draw chords visible on screen for performance)
        # Calculate which chords are visible based on viewport
        min_visible_time = -t0_x / bar_width if bar_width > 0 else 0
        max_visible_time = (WIDTH - t0_x) / bar_width if bar_width > 0 else 0
        

        # Calculate which chords are visible based on viewport
        min_visible_time = -t0_x / bar_width if bar_width > 0 else 0
        max_visible_time = (WIDTH - t0_x) / bar_width if bar_width > 0 else 0

        # OPTIMIZED: Use binary search instead of linear iteration
        visible_voice1 = find_visible_chords(voice1_order, min_visible_time, max_visible_time, voice1)
        visible_voice2 = find_visible_chords(voice2_order, min_visible_time, max_visible_time, voice2)

        # Draw only visible chords
        for t in visible_voice1:
            chord = voice1[t]
            chord.draw(window, root_height-math.log(chord.note.ratio, 2)*octave_height, 
                    t0_x, bar_width, octave_height, highlighted=(chord == test_chord), voicenum=0)

        for t in visible_voice2:
            chord = voice2[t]
            chord.draw(window, root_height-math.log(chord.note.ratio, 2)*octave_height, 
                    t0_x, bar_width, octave_height, highlighted=(chord == test_chord), voicenum=1)
        if closest:
            drawn_ylevel = root_height - math.log(closest_ratio, 2)*octave_height
            if closest.is_silent and test_chord:
                if voice1 == chords:
                    draw_dotted_line(window, (255, 255, 255), (t0_x + bar_width*(test_chord.time), drawn_ylevel), (t0_x + bar_width*(test_chord.time + test_chord.duration), drawn_ylevel), 5)
                if voice2 == chords:
                    draw_dotted_line(window, RED, (t0_x + bar_width*(test_chord.time), drawn_ylevel), (t0_x + bar_width*(test_chord.time + test_chord.duration), drawn_ylevel), 5)
            else:
                if voice1 == chords and test_chord:
                    pygame.draw.line(window, (255, 255, 255), (t0_x + bar_width*(test_chord.time), drawn_ylevel), (t0_x + bar_width*(test_chord.time + test_chord.duration), drawn_ylevel), 5)
                if voice2 == chords:
                    pygame.draw.line(window, RED, (t0_x + bar_width*(test_chord.time), drawn_ylevel), (t0_x + bar_width*(test_chord.time + test_chord.duration), drawn_ylevel), 5)
        pygame.draw.line(window, (128, 128, 128), (t0_x, 0), (t0_x, HEIGHT), 3)

        for time in keychanges:
            pygame.draw.line(window, (128, 128, 128), (t0_x+bar_width*(time), 0), (t0_x+bar_width*(time), HEIGHT), 3)
            #pygame.draw.line(window, (128, 128, 128), (t0_x+bar_width*(time), HEIGHT-150), (t0_x+bar_width*(time), HEIGHT), 3)
        
        


        window.blit(bg_surface, bg_surface.get_rect())
        
        #window.blit(title_text2, title_rect2)
        #pygame.draw.line(window, ACCENT, (title_rect.right + 5, 10), (title_rect.right+5, 40), 1)
        for time in keychanges:
            pygame.draw.line(window, (128, 128, 128), (t0_x+bar_width*(time), HEIGHT-140), (t0_x+bar_width*(time), HEIGHT-90), 3)
        
        for chord in chords:
            pygame.draw.rect(window, (255, 255, 255), pygame.Rect((t0_x+bar_width*chords[chord].time), (HEIGHT-140), chords[chord].duration*bar_width, 50), border_radius=10)
        if not paused:
            pygame.draw.line(window, (128, 128, 128), (t0_x+current_time*bar_width, HEIGHT-140), (t0_x+current_time*bar_width, HEIGHT-90))
        window.blit(other_layer, (0, 0))

        pygame.draw.rect(window, ACCENT, pygame.Rect(title_rect.right + 5, 10, WIDTH-10-(title_rect.right + 5), 30), border_radius=10)
        pygame.draw.rect(window, ACCENT, pygame.Rect(10, 50, 200, 50), border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(window, (97, 93, 111), (10, 98), (209, 98), 3)
        chordogram_text = get_font(25).render("CHORD GRAPH", True, BG)
        chordogram_rect = chordogram_text.get_rect()
        chordogram_rect.topleft = (20, 60)
        window.blit(chordogram_text, chordogram_rect)

        chordogram_text = get_font(25).render(str(clock.get_fps()), True, ACCENT)
        chordogram_rect = chordogram_text.get_rect()
        chordogram_rect.topleft = (220, 60)
        window.blit(chordogram_text, chordogram_rect)
        if mute_button.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"mute note (x)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_1d.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 1D (1)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_2d.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 2D (2)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_3d.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 3D (3)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_4d.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 4D (4)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_5d.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 5D (5)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_6d.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 6D (6)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_arrow.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"change direction (shift)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_arrow.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"change direction (shift)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_32nd.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 32nd note (f)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_sixteenth.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 16th note (g)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_eighth.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add 8th note (h)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_quarter.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add quarter note (j)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_half.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add half note (k)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif button_whole.get_rect().collidepoint((mouse_x, mouse_y)):
            info_text = get_font(30).render(f"add whole note (l)", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        elif resizing_chord:
            info_text = get_font(30).render(f"duration: {(resizing_chord.duration)} beats", True, BG)
            info_rect = info_text.get_rect()
            info_rect.topleft = (140, 10)
            window.blit(info_text, info_rect)
        else:
            if closest and test_chord:
                current_key = find_key(test_chord.time)
                #print(current_key)
                note_info_text = get_font(30).render(f"{int(ROOT*current_key)}Hz X {closest_ratio/current_key}", True, BG)
                note_info_rect = note_info_text.get_rect()
                note_info_rect.topleft = (140, 10)
                window.blit(note_info_text, note_info_rect)

                note_name_text = get_font(30).render(f"{name_ratio(closest_ratio/current_key)}", True, BG)
                note_name_rect = note_name_text.get_rect()
                note_name_rect.topright = (WIDTH-20, 10)
                window.blit(note_name_text, note_name_rect)
        
        for button in [mute_button, 
                       button_1d, button_2d, button_3d, button_4d, button_5d, button_6d, 
                       button_arrow, 
                       button_quarter, button_eighth, button_half, button_sixteenth, button_whole, button_32nd]:
            button.update((mouse_x, mouse_y), mouse_pressed)
            button.draw(window)
        
        if current_menu == "addchord" or current_menu == "addkeysig":
            #pygame.draw.rect(window, (0, 0, 0, 128), pygame.Rect(0, 0, WIDTH, HEIGHT))
            pygame.draw.rect(window, BG, pygame.Rect(WIDTH//4, HEIGHT//4-50, WIDTH//2, HEIGHT//2+100), border_radius=10)
            menu_title_surf = get_font(30).render("ADD CHORD", True, ACCENT)
            menu_title_rect= menu_title_surf.get_rect()
            menu_title_rect.midtop = (WIDTH//2, HEIGHT//4 - 40)
            window.blit(menu_title_surf, menu_title_rect)
            
            for i, button in enumerate(create_chord_buttons):
                button.update((mouse_x, mouse_y), mouse_pressed)
                button.draw(window)
            for i, button in enumerate(create_chord_buttons_plus):
                button.update((mouse_x, mouse_y), mouse_pressed)
                button.draw(window)
            for i, button in enumerate(create_chord_buttons_minus):
                button.update((mouse_x, mouse_y), mouse_pressed)
                button.draw(window)
                #window.blit(dimension_images[i+1], button.get_rect())
            create_chord_confirm.update((mouse_x, mouse_y), mouse_pressed)
            create_chord_confirm.draw(window)
            create_chord_reset.update((mouse_x, mouse_y), mouse_pressed)
            create_chord_reset.draw(window)
            symbols_text = get_shasavic(30).render(f"{visualise_ratio(add_chord_ratio)}", True, ACCENT)
            symbols_rect = symbols_text.get_rect()
            symbols_rect.topright = (WIDTH//2 + WIDTH//4 - 20, HEIGHT//4)
            window.blit(symbols_text, symbols_rect)
            ratio_text = get_font(30).render(f"{add_chord_ratio}", True, ACCENT)
            ratio_rect = ratio_text.get_rect()
            ratio_rect.topright = (WIDTH//2 + WIDTH//4 - 20, HEIGHT//4 + 40)
            window.blit(ratio_text, ratio_rect)
            #print(add_chord_ratio)

        try:
            playback_key = find_key(current_time)
            voice1_text = get_shasavic(30).render(visualise_ratio(voice1[voice1_order[voice1_playback_idx]].note.ratio / playback_key, ignore_twos=True), True, (255, 255, 255))
            voice1_rect = voice1_text.get_rect()
            voice1_rect.topright = (WIDTH-30, 120)
            window.blit(voice1_text, voice1_rect)
            voice2_text = get_shasavic(30).render(visualise_ratio(voice2[voice2_order[voice2_playback_idx]].note.ratio / playback_key, True), True, RED)
            voice2_rect = voice2_text.get_rect()
            voice2_rect.topright = (WIDTH-30, 160)
            window.blit(voice2_text, voice2_rect)
        except Exception as e:
            pass

    window.blit(title_text, title_rect)
    pygame.display.flip()
    clock.tick()  # 60 FPS
    #print(clock.get_fps())
   
    
    if not paused:
        current_time += clock.get_time() / 1000
        voice1_chord = find_chord(current_time, 1)
        voice2_chord = find_chord(current_time, 2)
        
        # cache pitches
        voice1_pitches = voice1_chord.get_freqs(voice1_chord.note.ratio * ROOT) if voice1_chord else set()
        voice2_pitches = voice2_chord.get_freqs(voice2_chord.note.ratio * ROOT) if voice2_chord else set()
        
        # Update voice 1
        if voice1_chord and current_time <= voice1_chord.duration + voice1_chord.time:
            # turn off notes that shouldn't be playing
            for freq in list(synthesizer.active_notes.keys()):
                if freq not in voice1_pitches:
                    synthesizer.note_off(freq)
            # turn on notes that should be playing
            for freq in voice1_pitches:
                if freq not in synthesizer.active_notes:
                    synthesizer.note_on(freq)
        else:
            # turn everything off, nothing playing
            for freq in list(synthesizer.active_notes.keys()):
                synthesizer.note_off(freq)

        # Update voice 2
        if voice2_chord and current_time <= voice2_chord.duration + voice2_chord.time:
            # turn off notes that shouldn't be playing (excluding voice1 notes)
            for freq in list(synthesizer2.active_notes.keys()):
                if freq not in voice2_pitches and freq not in voice1_pitches:
                    synthesizer2.note_off(freq)
            # turn on notes that should be playing
            for freq in voice2_pitches:
                if freq not in synthesizer2.active_notes:
                    synthesizer2.note_on(freq)
        else:
            # turn everything off
            for freq in list(synthesizer2.active_notes.keys()):
                synthesizer2.note_off(freq)
    #if closest: print(closest.parent)

synthesizer.stop()
pygame.quit()
