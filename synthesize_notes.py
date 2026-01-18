
import math
import struct
import wave
import random
import os

# Configuration
SAMPLE_RATE = 44100
DURATION = 4.0  # Seconds (Long tail)
VOLUME = 0.5

# C Minor Pentatonic Scale
# C4, Eb4, F4, G4, Bb4
NOTES = {
    "note_1_C4": 261.63,
    "note_2_Eb4": 311.13,
    "note_3_F4": 349.23,
    "note_4_G4": 392.00,
    "note_5_Bb4": 466.16
}

def generate_tone(frequency, duration_samples):
    """
    Generates a stereo synth pluck with FM synthesis, slight detuning, 
    and a pseudo-granular texture.
    """
    audio = []
    
    # Synthesis parameters
    carrier_freq = frequency
    mod_freq = frequency * 2.0  # Ratio 2:1 for bell/pluck harmonics
    mod_index_start = 3.0       # Stronger FM at start (pluck)
    mod_index_end = 0.5         # Softer FM at end
    
    decay_rate = 3.0            # Exponential decay factor
    
    # Stereo Phase offset for width (radians)
    phase_offset = 0.05 
    
    # Granular/Noise seed
    noise_seed = [random.uniform(-1, 1) for _ in range(1000)]
    
    for i in range(duration_samples):
        t = i / SAMPLE_RATE
        
        # Envelope (ADSR - like)
        # Fast attack, exponential decay
        envelope = math.exp(-decay_rate * t) * min(1.0, i / 200.0) 
        
        # Modulator Index Envelope
        current_mod_index = mod_index_start * envelope + mod_index_end * (1 - envelope)
        
        # FM Synthesis
        # Modulator
        modulator = math.sin(2.0 * math.pi * mod_freq * t) * current_mod_index
        
        # Carrier (Stereo)
        # Left
        sample_l = math.sin(2.0 * math.pi * carrier_freq * t + modulator)
        # Right (Phase shift)
        sample_r = math.sin(2.0 * math.pi * carrier_freq * t + modulator + phase_offset)
        
        # Add "Shimmer" layer (Octave up, washing in later)
        shimmer_vol = math.sin(t * 0.5) * 0.3 * envelope
        shimmer_l = math.sin(2.0 * math.pi * (carrier_freq * 2.002) * t) # detuned
        shimmer_r = math.sin(2.0 * math.pi * (carrier_freq * 1.998) * t)
        
        sample_l += shimmer_l * shimmer_vol
        sample_r += shimmer_r * shimmer_vol

        # Add "Granular" texture (Low pass filtered noise burst at start)
        if i < 20000:
             noise_vol = (1.0 - (i / 20000.0)) * 0.1
             n_val = noise_seed[i % len(noise_seed)]
             sample_l += n_val * noise_vol
             sample_r += n_val * noise_vol
        
        # Master volume and Envelope application
        sample_l *= envelope * VOLUME
        sample_r *= envelope * VOLUME
        
        audio.append([sample_l, sample_r])
        
    return audio

def apply_reverb(audio_data):
    """
    Simple feedback delay network to simulate reverb.
    """
    delay_samples = int(0.2 * SAMPLE_RATE) # 200ms delay
    decay = 0.6
    
    # Create a buffer for the reverb tail
    # Extended length
    output_len = len(audio_data) + delay_samples * 8
    output = [[0.0, 0.0] for _ in range(output_len)]
    
    # Copy original signal
    for i in range(len(audio_data)):
        output[i][0] += audio_data[i][0]
        output[i][1] += audio_data[i][1]
        
    # Apply delay/echo loop
    for k in range(1, 8): # 8 taps
        current_decay = decay ** k
        tap_delay = delay_samples * k
        
        for i in range(len(audio_data)):
            target_idx = i + tap_delay
            if target_idx < output_len:
                # Feedback with slight cross-feed for diffusion
                l = audio_data[i][0]
                r = audio_data[i][1]
                
                output[target_idx][0] += (l * 0.7 + r * 0.3) * current_decay
                output[target_idx][1] += (r * 0.7 + l * 0.3) * current_decay
                
    return output

def save_wav(filename, audio_data):
    print(f"Saving {filename}...")
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2) # Stereo
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        
        # Convert float samples to 16-bit integers
        packed_data = bytearray()
        for sample in audio_data:
            # Clip
            l = max(-1.0, min(1.0, sample[0]))
            r = max(-1.0, min(1.0, sample[1]))
            
            # Scale to 16-bit
            l_int = int(l * 32767)
            r_int = int(r * 32767)
            
            packed_data += struct.pack('<hh', l_int, r_int)
            
        wav_file.writeframes(packed_data)

def main():
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        
    for name, freq in NOTES.items():
        print(f"Synthesizing {name} ({freq} Hz)...")
        # 2.5s synthesis, reverb will extend it
        raw_audio = generate_tone(freq, int(2.5 * SAMPLE_RATE)) 
        processed_audio = apply_reverb(raw_audio)
        
        save_wav(f"sounds/{name}.wav", processed_audio)
        
    print("Done!")

if __name__ == "__main__":
    main()
