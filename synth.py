import numpy as np
import pyaudio
import time
from threading import Thread, Lock
from collections import defaultdict
import math

# i just copied this from ai
# i don't want to code a synth

class PolyphonicSynth:
    def __init__(self, sample_rate=44100, polyphony=16):
        self.sample_rate = sample_rate
        self.polyphony = polyphony
        
        # Active notes: frequency -> [voice_index, velocity, age]
        self.active_notes = {}
        self.voices = []
        self.voice_counter = 0
        
        # Audio stream setup
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        
        # Voice allocation strategy
        self.voice_lock = Lock()
        
        # Synth parameters
        self.waveform = 'sine'  # sine, square, saw, triangle
        self.attack = 0.01
        self.decay = 0.1
        self.sustain = 0.7
        self.release = 0.2
        
    def get_wave_function(self, waveform):
        """Return waveform generator function"""
        if waveform == 'sine':
            return lambda phase: np.sin(2 * np.pi * phase)
        elif waveform == 'square':
            return lambda phase: 1.0 if (phase % 1.0) < 0.5 else -1.0
        elif waveform == 'saw':
            return lambda phase: 2.0 * (phase % 1.0) - 1.0
        elif waveform == 'triangle':
            return lambda phase: 2.0 * abs(2.0 * (phase % 1.0) - 1.0) - 1.0
        else:
            return lambda phase: np.sin(2 * np.pi * phase)
    
    def adsr_envelope(self, time_in_note, note_duration, velocity):
        """ADSR envelope generator"""
        if time_in_note < self.attack:
            # Attack phase
            return (time_in_note / self.attack) * velocity
        elif time_in_note < self.attack + self.decay:
            # Decay phase
            decay_time = time_in_note - self.attack
            decay_progress = decay_time / self.decay
            return velocity * (1.0 - decay_progress * (1.0 - self.sustain))
        elif note_duration == -1 or time_in_note < note_duration:
            # Sustain phase
            return velocity * self.sustain
        else:
            # Release phase
            release_time = time_in_note - note_duration
            if release_time < self.release:
                return velocity * self.sustain * (1.0 - release_time / self.release)
            return 0.0
    
    def allocate_voice(self, frequency, velocity):
        """Allocate a voice for a new note"""
        with self.voice_lock:
            # Check if frequency already playing (re-trigger)
            if frequency in self.active_notes:
                voice_idx = self.active_notes[frequency][0]
                self.voices[voice_idx]['start_time'] = time.time()
                self.voices[voice_idx]['velocity'] = velocity
                return voice_idx
            
            # Find free voice
            for i, voice in enumerate(self.voices):
                if not voice['active']:
                    voice.update({
                        'frequency': frequency,
                        'phase': 0.0,
                        'start_time': time.time(),
                        'note_duration': -1,  # -1 means still held
                        'velocity': velocity,
                        'active': True
                    })
                    self.active_notes[frequency] = [i, velocity, time.time()]
                    return i
            
            # No free voice - steal oldest voice
            if self.active_notes:
                oldest_note = min(self.active_notes.items(), 
                                key=lambda x: x[1][2])  # Compare by age
                old_freq = oldest_note[0]
                voice_idx = self.active_notes[old_freq][0]
                
                # Update voice
                self.voices[voice_idx].update({
                    'frequency': frequency,
                    'phase': 0.0,
                    'start_time': time.time(),
                    'note_duration': -1,
                    'velocity': velocity,
                    'active': True
                })
                
                # Update active notes
                del self.active_notes[old_freq]
                self.active_notes[frequency] = [voice_idx, velocity, time.time()]
                return voice_idx
            
            return -1
    
    def note_on(self, frequency, velocity=0.7):
        """Start playing a note"""
        if len(self.active_notes) >= self.polyphony:
            # Polyphony limit reached
            return False
        
        voice_idx = self.allocate_voice(frequency, velocity)
        return voice_idx != -1
    
    def note_off(self, frequency):
        """Stop playing a note"""
        with self.voice_lock:
            if frequency in self.active_notes:
                voice_idx = self.active_notes[frequency][0]
                if self.voices[voice_idx]['note_duration'] == -1:  # Still held
                    self.voices[voice_idx]['note_duration'] = (
                        time.time() - self.voices[voice_idx]['start_time']
                    )
                # Don't remove immediately - let release phase complete
                return True
        return False
    
    def generate_samples(self, num_samples):
        """Generate audio samples for all active voices"""
        samples = np.zeros(num_samples, dtype=np.float32)
        wave_func = self.get_wave_function(self.waveform)
        current_time = time.time()
        
        with self.voice_lock:
            # Process each active voice
            voices_to_remove = []
            
            for i, voice in enumerate(self.voices):
                if not voice['active']:
                    continue
                
                freq = voice['frequency']
                phase = voice['phase']
                time_in_note = current_time - voice['start_time']
                
                # Generate samples for this voice
                voice_samples = np.zeros(num_samples, dtype=np.float32)
                for j in range(num_samples):
                    # Calculate envelope
                    envelope = self.adsr_envelope(
                        time_in_note + j/self.sample_rate,
                        voice['note_duration'],
                        voice['velocity']
                    )
                    
                    if envelope <= 0.001:  # Voice is silent
                        voice['active'] = False
                        if freq in self.active_notes:
                            del self.active_notes[freq]
                        break
                    
                    # Generate waveform
                    voice_samples[j] = wave_func(phase) * envelope * 0.3  # Volume scaling
                    
                    # Update phase
                    phase += freq / self.sample_rate
                    if phase >= 1.0:
                        phase -= 1.0
                
                # Update voice phase for next chunk
                voice['phase'] = phase
                
                # Mix voice into output
                samples += voice_samples
        
        # Prevent clipping
        if np.max(np.abs(samples)) > 1.0:
            samples = samples / np.max(np.abs(samples))
        
        return samples
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback function"""
        samples = self.generate_samples(frame_count)
        return (samples.astype(np.float32), pyaudio.paContinue)
    
    def start(self):
        """Start the audio stream"""
        # Initialize voices
        self.voices = [{
            'active': False,
            'frequency': 0.0,
            'phase': 0.0,
            'start_time': 0.0,
            'note_duration': -1,
            'velocity': 0.0
        } for _ in range(self.polyphony)]
        
        # Open audio stream
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=256,
            stream_callback=self.audio_callback
        )
        
        self.running = True
        self.stream.start_stream()
        print(f"Polyphonic synth started with {self.polyphony} voices")
    
    def stop(self):
        """Stop the audio stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        self.running = False
    
    def set_waveform(self, waveform):
        """Change oscillator waveform"""
        valid_waveforms = ['sine', 'square', 'saw', 'triangle']
        if waveform in valid_waveforms:
            self.waveform = waveform
    
    def set_adsr(self, attack, decay, sustain, release):
        """Update ADSR envelope parameters"""
        self.attack = max(0.001, attack)
        self.decay = max(0.001, decay)
        self.sustain = max(0.0, min(1.0, sustain))
        self.release = max(0.001, release)

# Utility functions
def frequency_from_note(note_name):
    """Convert note name to frequency (A4 = 440Hz)"""
    notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 
             'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    
    if len(note_name) == 2:
        note, octave = note_name[0], int(note_name[1])
        semitone = notes.get(note.upper())
    elif len(note_name) == 3 and note_name[1] == '#':
        note, octave = note_name[:2], int(note_name[2])
        semitone = notes.get(note.upper())
    else:
        return 440.0  # Default to A4
    
    if semitone is None:
        return 440.0
    
    # Calculate frequency
    n = (octave - 4) * 12 + (semitone - 9)  # A4 is reference
    return 440.0 * (2.0 ** (n / 12.0))

# Example usage
if __name__ == "__main__":
    # Create and start synth
    synth = PolyphonicSynth(polyphony=8)
    synth.set_waveform('saw')
    synth.set_adsr(0.05, 0.1, 0.7, 0.3)
    
    try:
        synth.start()
        
        print("Playing a chord...")
        # Play a C major chord
        synth.note_on(frequency_from_note('C4'))  # C4
        synth.note_on(frequency_from_note('E4'))  # E4
        synth.note_on(frequency_from_note('G4'))  # G4
        time.sleep(2)
        
        # Release notes
        synth.note_off(frequency_from_note('C4'))
        synth.note_off(frequency_from_note('E4'))
        synth.note_off(frequency_from_note('G4'))
        time.sleep(0.5)
        
        print("Playing arpeggio...")
        # Arpeggio example
        notes = ['C4', 'E4', 'G4', 'C5', 'G4', 'E4']
        for note in notes:
            freq = frequency_from_note(note)
            synth.note_on(freq, velocity=0.6)
            time.sleep(0.15)
            synth.note_off(freq)
        
        time.sleep(1)
        
        print("Playing with different waveform...")
        synth.set_waveform('square')
        for note in ['A3', 'C4', 'E4']:
            synth.note_on(frequency_from_note(note), velocity=0.5)
        time.sleep(1.5)
        
        # Clean release
        for note in ['A3', 'C4', 'E4']:
            synth.note_off(frequency_from_note(note))
        time.sleep(1)
        
        print("Synth demo complete.")
        
    except KeyboardInterrupt:
        print("\nStopping synth...")
    finally:
        synth.stop()