
import math
import struct
import wave
import random
import os

# Configuration
SAMPLE_RATE = 44100
DURATION = 5.0  # Seconds
AMPLITUDE = 0.6

# C Minor Pentatonic
NOTES = {
    "felt_piano_1_C4": 261.63,
    "felt_piano_2_Eb4": 311.13,
    "felt_piano_3_F4": 349.23,
    "felt_piano_4_G4": 392.00,
    "felt_piano_5_Bb4": 466.16
}

def moving_average(data, window_size):
    """Simple moving average filter for smoothing."""
    output = []
    # Inefficient for large data but fine for short excitation bursts
    for i in range(len(data)):
        start = max(0, i - window_size + 1)
        segment = data[start:i+1]
        output.append(sum(segment) / len(segment))
    return output

def lowpass_filter(data, alpha=0.5):
    """One-pole lowpass filter."""
    output = []
    prev = 0.0
    for sample in data:
        val = prev + alpha * (sample - prev)
        output.append(val)
        prev = val
    return output

def generate_felt_piano_note(freq, duration_samples):
    """
    Generates a piano-like sound using Karplus-Strong with "felt" modifications.
    """
    # 1. Calculate buffer length (N)
    # Tuning adjustment: The low-pass filter in the loop adds a delay of ~0.5 samples.
    # N = SR / F - 0.5
    period_samples = float(SAMPLE_RATE) / freq
    N = int(period_samples - 0.5)
    
    # 2. Create Excitation Signal (The Hammer)
    # For a sharp pluck, we'd use white noise. 
    # For a felt hammer, we want a "thud" - heavily filtered noise.
    
    # Fill buffer with white noise first
    excitation = [random.uniform(-1, 1) for _ in range(N)]
    
    # Apply aggressive Low-pass filtering to simulate felt softness
    # Run multiple passes of moving average to smooth it out into a "hill" shape
    for _ in range(3):
        excitation = moving_average(excitation, window_size=int(N/4))
    
    # 3. Initialize wavetable (delay line)
    wavetable = list(excitation) # Copy
    output = list(excitation)    # Start output with excitation
    
    # 4. Mechanical Thump (Key mechanism noise)
    # A short low-freq sine burst at the start, mixed in
    thump_freq = 50.0
    thump_len = 1000
    thump = []
    for i in range(thump_len):
        t = i / SAMPLE_RATE
        env = math.exp(-i * 0.01) # fast decay
        thump_val = math.sin(2 * math.pi * thump_freq * t) * env * 0.15
        thump.append(thump_val)
        
    # Mix thump into initial output
    for i in range(min(len(output),  len(thump))):
         output[i] += thump[i]
    
    # 5. Karplus-Strong Loop (String Decay)
    current_sample_idx = N
    
    # Pointer for the circular buffer (wavetable)
    ptr = 0
    
    # Decay factor (Filter coefficient)
    # Standard KS is 0.5 * (y[n] + y[n-1]).
    # We tweak the mix to control brightness decay time.
    # Higher 'decay' keeps it ringing longer.
    decay = 0.992 
    
    # Filter smoothing (0.5 is average).
    # Slightly higher values can dampen high freqs faster (warmer).
    smoothing = 0.5 
    
    prev_val = 0.0
    
    while len(output) < duration_samples:
        # Read from delay line
        delayed_sample = wavetable[ptr]
        
        # Low-pass filter (Simulates energy loss in string)
        # y[n] = C * (x[n] + x[n-1]) ... simplified
        new_val = (smoothing * delayed_sample) + ((1 - smoothing) * prev_val)
        
        # Apply energy decay
        new_val *= decay
        
        # Update delay line (overwrite old value)
        wavetable[ptr] = new_val
        
        # Store for next iteration
        prev_val = delayed_sample
        
        # Increment pointer (circular)
        ptr = (ptr + 1) % N
        
        output.append(new_val)
        
    return output

def apply_room_ambience(audio_data):
    """
    Very subtle, short reverb/early reflections to simulate a small room.
    """
    # Simple comb filters for "room" feel
    delays = [int(0.01 * SAMPLE_RATE), int(0.023 * SAMPLE_RATE)] # 10ms, 23ms
    gains = [0.1, 0.05]
    
    output_len = len(audio_data) + max(delays)
    output = audio_data[:] + [0.0] * max(delays)
    
    for d, g in zip(delays, gains):
        for i in range(len(audio_data)):
            if i + d < len(output):
                output[i+d] += audio_data[i] * g
                
    return output

def save_wav_stereo(filename, audio_data):
    print(f"Saving {filename}...")
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2) # Stereo
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        
        packed_data = bytearray()
        for sample in audio_data:
            # Clip
            val = max(-1.0, min(1.0, sample * AMPLITUDE))
            
            # Simple panning/width: Center the piano
            # But let's add tiny variance for "stereo" feel?
            # For felt piano, it's often close-mic'd stereo.
            # We'll just duplicate mono to stereo for now to keep it focused (as requested "Focus" style).
            l = val
            r = val 
            
            l_int = int(l * 32767)
            r_int = int(r * 32767)
            
            packed_data += struct.pack('<hh', l_int, r_int)
            
        wav_file.writeframes(packed_data)

def main():
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        
    for name, freq in NOTES.items():
        print(f"Synthesizing {name} ({freq} Hz)...")
        # Generate Note
        raw_audio = generate_felt_piano_note(freq, int(DURATION * SAMPLE_RATE))
        
        # Add Room Ambience
        final_audio = apply_room_ambience(raw_audio)
        
        # Save
        save_wav_stereo(f"sounds/{name}.wav", final_audio)
        
    print("Done!")

if __name__ == "__main__":
    main()
