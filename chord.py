from fractions import Fraction
import math, pygame, synthesizer
from ranges import Range
from typing import Self
from consts import *


def find_max_depth_interval(interval_dict: dict[Range, int], interval2: Range):
    results = []
    for interval in interval_dict:
        depth = interval_dict[interval]
        intersect = interval.intersection(interval2)
        if intersect:
            results.append(depth)
    
    i = 0
    return max(results, default=-1) + 1

def find_max_depth(interval_dict: dict[Range, int], num: int):
    results = []
    for interval in interval_dict:
        depth = interval_dict[interval]
        intersect = num in interval
        if intersect:
            results.append(depth)
    
    i = 0
    return max(results, default=-1) + 1
        

class Note:
    def __init__(self, derivatives: list[tuple[int, int, Self]] = None, is_silent: bool = False, ratio: Fraction = Fraction(1, 1)):
        self.derivatives = derivatives if derivatives else []
        self.is_silent = is_silent
        self.set_ratio(ratio)
        self.parent = None
    def set_parent_chord(self, chord):
        self.parent_chord = chord
        
    def add_derivative(self, exponent, extent, is_silent=False):
        new_ratio = self.ratio*RATIOS[exponent]**extent
        if new_ratio in self.get_root().get_ratios():
            return
        note = Note([], is_silent, new_ratio)
        note.parent = self
        note.set_parent_chord(self.parent_chord)
        self.derivatives.append((exponent, extent, note))
        self.parent_chord.reset_layers()
        self.parent_chord.recalc_freqs()


    def set_ratio(self, ratio):
        self.ratio = ratio
        for derivative in self.derivatives:
            new_ratio = ratio*RATIOS[derivative[0]]**derivative[1]
            derivative[2].set_ratio(new_ratio)

    def get_root(self):
        if self.parent:
            return self.parent.get_root()
        return self

    def get_ylevels(self, y, octheight):
        result = []
        if True:
            result.append(y)
        for derivative in self.derivatives:
            result += derivative[2].get_ylevels(y-(INTERVALLENGTHS[derivative[0]]*derivative[1]*octheight), octheight)
        return result
    
    def get_notes(self):
        result = []
        if True:
            result.append(self)
        for derivative in self.derivatives:
            result += derivative[2].get_notes()
        return result
    
    def get_ratios(self):
        result = []
        if True:
            result.append(self.ratio)
        for derivative in self.derivatives:
            result += derivative[2].get_ratios()
        return result
    
    def get_notes_and_ylevels(self, y=0, octheight=1):
        result = {}
        if True:
            result[y] = self
        for derivative in self.derivatives:
            result |= derivative[2].get_notes_and_ylevels(y-(INTERVALLENGTHS[derivative[0]]*derivative[1]*octheight), octheight)
        return result
    
    def get_bars(self, y, octheight):
        bars = []
        for derivative in self.derivatives:
            match derivative[0]:
                case 2:
                    if derivative[1] > 0:
                        bars.append((Range(y-octheight*INTERVALLENGTHS[2]*derivative[1], y), derivative[2].left_layer))
                    elif derivative[1] < 0:
                        bars.append((Range(y, y-octheight*INTERVALLENGTHS[2]*derivative[1]), derivative[2].left_layer))
                case 3:
                    if derivative[1] > 0:
                        bars.append((Range(y-octheight*INTERVALLENGTHS[3]*derivative[1], y), derivative[2].left_layer))
                    elif derivative[1] < 0:
                        bars.append((Range(y, y-octheight*INTERVALLENGTHS[3]*derivative[1]), derivative[2].left_layer))
        
            bars += derivative[2].get_bars(y-octheight*INTERVALLENGTHS[derivative[0]]*derivative[1], octheight)
        return bars
    
    def get_all_ranges_with_pos(ranges, pos):
        output = {}
        for range in ranges:
            output[range] = ranges[range]

        return output

    
    def precompute_positions(self):
        notes: dict[Fraction, Self] = {}
        intervals: dict[Fraction, list[Range]] = {}
        bars: dict[Range, int] = {}
        layers: dict[Fraction, int] = {Fraction(1): 0}
        bars_right: dict[Range, int] = {}
        layers_right: dict[Fraction, int] = {Fraction(1): 0}
        notes[Fraction(1)] = self
        stack = [Fraction(1)]
        while stack:
            node = stack.pop()
            intervals[node] = [] # new list of intervals originating from the node
            for derivative in notes[node].derivatives:
                ratio = node*RATIOS[derivative[0]]**derivative[1] # find ratio of new node
                stack.append(ratio) # add it to stack
                range = Range(min(node, ratio), max(node, ratio), include_start=False)
                intervals[node].append(range)
                if derivative[0] == 2:
                    bars[range] = layers[node]
                if derivative[0] == 3:
                    bars_right[range] = layers_right[node]
                layers[ratio] = layers[node]
                layers_right[ratio] = layers_right[node]

                # check for collision
                # if new node collides with bar:
                notes[ratio] = derivative[2]
                while True: 
                    for bar in bars:
                        if ratio in bar and layers[ratio] == bars[bar]:
                            layers[ratio] += 1
                            
                            current_parent = notes[ratio].parent
                            previous_parent = notes[ratio]
                            while True: # yes i do this a lot

                                if not current_parent:
                                    break
                                if previous_parent.ratio / current_parent.ratio not in [Fraction(3, 2), Fraction(2, 3)]:
                                    break
                                if current_parent.ratio in layers.keys():
                                    layers[current_parent.ratio] += 1
                                parent_range = Range(min(current_parent.ratio, previous_parent.ratio), max(current_parent.ratio, previous_parent.ratio), include_start=False)
                                if parent_range in bars.keys():
                                    bars[parent_range] += 1
                                previous_parent = current_parent
                                current_parent = current_parent.parent
                            #print(previous_parent.ratio)
                            #layers[previous_parent.ratio] += 1
                            break
                    else:
                        break
                while True:
                    for bar in bars_right:
                        if ratio in bar and layers_right[ratio] == bars_right[bar]:
                            layers_right[ratio] += 1

                            current_parent = notes[ratio].parent
                            previous_parent = notes[ratio]
                            while True: # yes i do this a lot
                                #print("prie")
                                if not current_parent:
                                    break
                                if previous_parent.ratio / current_parent.ratio not in [Fraction(5, 4), Fraction(4, 5)]:
                                    break
                                if current_parent.ratio in layers_right.keys():
                                    layers_right[current_parent.ratio] += 1
                                parent_range = Range(min(current_parent.ratio, previous_parent.ratio), max(current_parent.ratio, previous_parent.ratio), include_start=False)
                                if parent_range in bars_right.keys():
                                    bars_right[parent_range] += 1
                                previous_parent = current_parent
                                current_parent = current_parent.parent
                            #print(previous_parent.ratio)
                            #layers[previous_parent.ratio] += 1
                            break
                    else:
                        break
                        #print("eoijds")


                

                if range in bars.keys():
                    while True:
                        for note in notes:
                            if note in range and bars[range] == layers[note]:
                                note_children = notes[note].get_notes()
                                if notes[node] in note_children or derivative[0] == 2 and derivative[1] < 0:
                                    layers[node] += 1
                                    #layers[note]  = layers[node]
                                    if range in bars.keys():
                                        bars[range] += 1
                                    current_parent = notes[node].parent
                                    previous_parent = notes[node]
                                    while True: # yes i do this a lot

                                        if not current_parent:
                                            break
                                        if previous_parent.ratio / current_parent.ratio not in [Fraction(3, 2), Fraction(2, 3)]:
                                            break
                                        if current_parent.ratio in layers.keys():
                                            layers[current_parent.ratio] += 1
                                        parent_range = Range(min(current_parent.ratio, previous_parent.ratio), max(current_parent.ratio, previous_parent.ratio))
                                        if parent_range in bars.keys():
                                            bars[parent_range] += 1
                                        previous_parent = current_parent
                                        current_parent = current_parent.parent
                                else:
                                    layers[note] += 1
                                    stack.append(note)

                                break
                            

                        else:
                            break
                if range in bars_right.keys():
                    while True:
                        for note in notes:

                            if note in range and bars_right[range] == layers_right[note]:
                                note_children = notes[note].get_notes()
                                if notes[node] in note_children or derivative[0] == 3 and derivative[1] < 0:
                                    layers_right[node] += 1
                                    #layers[note]  = layers[node]
                                    if range in bars_right.keys():
                                        bars_right[range] += 1
                                    current_parent = notes[node].parent
                                    previous_parent = notes[node]
                                    while True: # yes i do this a lot

                                        if not current_parent:
                                            break
                                        if previous_parent.ratio / current_parent.ratio not in [Fraction(5, 4), Fraction(4, 5)]:
                                            break
                                        layers_right[current_parent.ratio] += 1
                                        parent_range = Range(min(current_parent.ratio, previous_parent.ratio), max(current_parent.ratio, previous_parent.ratio))
                                        if parent_range in bars_right.keys():
                                            bars_right[parent_range] += 1
                                        previous_parent = current_parent
                                        current_parent = current_parent.parent
                                else:
                                    layers_right[note] += 1
                                    stack.append(note)

                                break
                        else:
                            break
        
        return layers, layers_right
                        
                
            
    def delete_node(self, node):
        removals = None
        for i, derivative in enumerate(self.derivatives):
            if node == derivative[2]:
                removals = i
        del self.derivatives[removals]
        self.parent_chord.reset_layers()
        self.parent_chord.recalc_freqs()

    def as_json(self):
        obj = {}
        obj["derivatives"] = []
        obj["numberator"] = self.ratio.numerator
        obj["denominator"] = self.ratio.denominator
        obj["muted"] = self.is_silent
        for derivative in self.derivatives:
            obj["derivatives"].append({"dimension": derivative[0], "direction": derivative[1], "note": derivative[2].as_json()})
        return obj
                

        
    
    
    def draw(self, window, x, y, width, octheight, thickness, layers, layers_right, current_left=0, current_right=1, root=1, highlighted=True, voicenum=0):
        bar_width = width // 10

        LINE_COLOR = [i * (1 if highlighted==True else 3/4) for i in [(255, 255, 255), RED, GREEN, PURPLE, YELLOW, LIME][voicenum]]
        if not self.is_silent:
            pygame.draw.line(window, LINE_COLOR, (x+width*current_left, y), (x+width*current_right, y), 3)
        else:
            draw_dotted_line(window, LINE_COLOR, (x+width*current_left, y), (x+width*current_right, y), 3)
        #layers = self.precompute_positions()
        for derivative in self.derivatives:
            dimnum = derivative[0]
            dimext = derivative[1]
            ratio = root*RATIOS[derivative[0]]**derivative[1]
            node = derivative[2]
            test_interval = None
                                
            linedepthl = layers[ratio]
            linedepthr = layers_right[ratio]
            if dimnum == 1:
                if dimext > 0:
                    pygame.draw.rect(window, (128, 128, 128), pygame.Rect(x+width*1/2, y-OCTAVE*dimext*octheight, 1, OCTAVE*octheight*dimext))
                if dimext < 0:
                    pygame.draw.rect(window, (128, 128, 128), pygame.Rect(x+width*1/2, y, 1, -OCTAVE*octheight*dimext))
            if dimnum == 2:
                if dimext > 0:
                    pygame.draw.rect(window, RED, pygame.Rect(x+width*current_left, y-PERFECTFIFTH*dimext*octheight, bar_width, PERFECTFIFTH*octheight*dimext))
                if dimext < 0:
                    pygame.draw.rect(window, RED, pygame.Rect(x+width*current_left, y, bar_width, -PERFECTFIFTH*octheight*dimext))
            if dimnum == 3:
                if dimext > 0:
                    pygame.draw.rect(window, GREEN, pygame.Rect(x+width*current_right - bar_width+1, y-MAJORTHIRD*dimext*octheight, bar_width, MAJORTHIRD*octheight*dimext))
                    
                if dimext < 0:
                    pygame.draw.rect(window, GREEN, pygame.Rect(x+width*current_right - bar_width+1, y, bar_width, -MAJORTHIRD*octheight*dimext))

            if dimnum == 4:
                if dimext > 0:
                    pygame.draw.polygon(window, PURPLE, [(x+width*current_left, y), 
                                                         (x+width*current_left+bar_width, y), 
                                                         (x+width*(1-linedepthr*0.15), y-SEVENTH*dimext*octheight), 
                                                         (x+width*(1-linedepthr*0.15)-bar_width, y-SEVENTH*dimext*octheight)])
                if dimext < 0:
                    pygame.draw.polygon(window, PURPLE, [(x+width*current_right, y), 
                                                         (x+width*current_right-bar_width, y), 
                                                         (x+width*linedepthl*0.15, y-SEVENTH*dimext*octheight), 
                                                         (x+width*linedepthl*0.15+bar_width, y-SEVENTH*dimext*octheight)])
            
            if dimnum == 5:
                if dimext > 0:
                    pygame.draw.polygon(window, YELLOW, [(x+width*current_right-bar_width, y), 
                                                         (x+width*current_right, y), 
                                                         (x+width*linedepthl*0.15+bar_width, y-ELEVENTH*dimext*octheight), 
                                                         (x+width*linedepthl*0.15, y-ELEVENTH*dimext*octheight)])
                if dimext < 0:
                    pygame.draw.polygon(window, YELLOW, [(x+width*current_left, y), 
                                                         (x+width*current_left+bar_width, y), 
                                                         (x+width*current_right, y-ELEVENTH*dimext*octheight), 
                                                         (x+width*current_right-bar_width, y-ELEVENTH*dimext*octheight)])

            if dimnum == 6:
                if dimext > 0:
                    pygame.draw.polygon(window, LIME, [(x+width*current_left, y), 
                                                       (x+width*current_left+bar_width, y),
                                                       (x+width*current_left-bar_width, y-THIRTEENTH/2*dimext*octheight),
                                                       (x+width*current_left+bar_width, y-THIRTEENTH*dimext*octheight),
                                                       (x+width*current_left, y-THIRTEENTH*dimext*octheight),
                                                       (x+width*current_left-2*bar_width, y-THIRTEENTH/2*dimext*octheight),
                                                       ])
                if dimext < 0:
                    pygame.draw.polygon(window, LIME, [(x+width*current_left, y), 
                                                       (x+width*current_left+bar_width, y),
                                                       (x+width*current_left-bar_width, y-THIRTEENTH/2*dimext*octheight),
                                                       (x+width*current_left+bar_width, y-THIRTEENTH*dimext*octheight),
                                                       (x+width*current_left, y-THIRTEENTH*dimext*octheight),
                                                       (x+width*current_left-2*bar_width, y-THIRTEENTH/2*dimext*octheight),
                                                       ])






            node.draw(window, x, y - INTERVALLENGTHS[dimnum]*dimext*octheight, width, octheight, thickness, layers, layers_right, linedepthl*0.15, 1-linedepthr*0.15, root=ratio, highlighted=highlighted, voicenum=voicenum)

    def get_pitches(self, freq):
        result = []
        if not self.is_silent:
            result.append(freq)
        for derivative in self.derivatives:
            result += derivative[2].get_pitches(freq*(RATIOS[derivative[0]]**derivative[1]))
        return result
    
    @classmethod
    def from_json(cls, data):
        # 1. Reconstruct the Ratio
        # Note: Using "numberator" to match your save function's key
        numerator = data["numberator"] 
        denominator = data["denominator"]
        is_silent = data["muted"]
        ratio = Fraction(numerator, denominator)
        
        # 2. Create the Note instance
        note_instance = cls(ratio=ratio, is_silent=is_silent)
        
        # 3. Recursively reconstruct derivatives
        # data["derivatives"] is a list of dicts: 
        # {"dimension": x, "direction": y, "note": nested_note_obj}
        if "derivatives" in data:
            for d in data["derivatives"]:
                dimension = d["dimension"]
                direction = d["direction"]
                # Recursive call to load the nested note
                nested_note = cls.from_json(d["note"])
                note_instance.derivatives.append((dimension, direction, nested_note))
                
        return note_instance
    
def get_shasavic(size):
    return pygame.font.Font("assets/fonts/icons.ttf", size)


class Chord:
    def __init__(self, note: Note, duration: Fraction, timeval: Fraction):
        self.note = note
        self.duration = duration
        self.time = timeval
        self.layers_cache, self.layers_right_cache = self.note.precompute_positions()
        self.freqs_cache = self.note.get_pitches(1)
        self.note.set_parent_chord(self)
        self.cached_pitches = None
        self.cached_surf = pygame.Surface((1280, 720))

    def get_freqs(self, freq):
        return [i*freq for i in self.freqs_cache]

    def reset_layers(self):
        self.layers_cache, self.layers_right_cache = self.note.precompute_positions()
    
    def recalc_freqs(self):
        self.freqs_cache = self.note.get_pitches(1)
    
    def recalc_surface(self):
        self.draw(self.cached_surf, root_height, t0_x, bar_width, octave_height, chords[selected_chord_index] is self, 0 if chords is voice1 else 1)
    
    def actual_draw(self, window):
        window.blit(self.cached_surf, (0, 0))
    
    def draw(self, window, rooty, t0, barwidth, octheight, highlighted=True, voicenum=0):
        #layers, layers_right = 
        #print(layers)
        self.note.draw(window, t0 + barwidth*self.time, rooty, self.duration*barwidth, octheight, 1, self.layers_cache, self.layers_right_cache, highlighted=highlighted, voicenum=voicenum, current_left=self.layers_cache[Fraction(1)]*0.15, current_right = 1-self.layers_right_cache[Fraction(1)]*0.15)
        root_text = get_shasavic(15).render(visualise_ratio(self.note.ratio, ignore_twos=True), True, (255, 255, 255), ACCENT)
        root_rect = root_text.get_rect()
        root_rect.center = (t0+barwidth*self.time+self.duration*barwidth/2, rooty)
        #window.blit(root_text, root_rect)

    def as_json(self):
        obj = {}
        obj["note"] = self.note.as_json()
        obj["duration"] = self.duration
        obj["time"] = self.time
 
        return obj
    
    @classmethod
    def from_json(cls, data):
        # 1. Reconstruct the Note object first
        note_obj = Note.from_json(data["note"])
        
        # 2. Extract simple fields
        duration = data["duration"]
        time = data["time"]
        
        # 3. Return new Chord
        return cls(note_obj, duration, time)

            