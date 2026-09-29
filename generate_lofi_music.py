import numpy as np
import scipy.io.wavfile as wavfile

# Lo-Fi parameters
sample_rate = 44100
bpm = 84
beat_duration = 60.0 / bpm
total_duration = 28.0 # Match video duration (26.68s)
total_samples = int(sample_rate * total_duration)

t = np.linspace(0, total_duration, total_samples, endpoint=False)
audio = np.zeros(total_samples)

# Chord progression in C Major / A Minor: Am7 -> Fmaj7 -> Cmaj7 -> G7
# Note frequencies (Hz)
notes = {
    'A2': 110.00, 'C3': 130.81, 'E3': 164.81, 'G3': 196.00,
    'F2': 87.31,  'A3': 220.00, 'C4': 261.63, 'E4': 329.63,
    'C3': 130.81, 'G3': 196.00, 'B3': 246.94, 'D4': 293.66,
    'G2': 98.00,  'B2': 123.47, 'D3': 146.83, 'F3': 174.61,
    'E4': 329.63, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25
}

chords = [
    [notes['A2'], notes['C3'], notes['E3'], notes['G3'], notes['C4']], # Am7
    [notes['F2'], notes['A3'], notes['C4'], notes['E4']],             # Fmaj7
    [notes['C3'], notes['E3'], notes['G3'], notes['B3'], notes['E4']], # Cmaj7
    [notes['G2'], notes['B2'], notes['D3'], notes['F3'], notes['B3']]  # G7
]

bar_duration = 4 * beat_duration # ~2.85s per chord bar
num_bars = int(np.ceil(total_duration / bar_duration))

# 1. Warm Rhodes-style Piano Chords with soft tremolo & detuning
for bar in range(num_bars):
    chord = chords[bar % len(chords)]
    bar_start = int(bar * bar_duration * sample_rate)
    bar_len = int(bar_duration * sample_rate)
    bar_end = min(bar_start + bar_len, total_samples)
    
    t_bar = np.linspace(0, (bar_end - bar_start) / sample_rate, bar_end - bar_start)
    envelope = np.exp(-1.4 * t_bar) # gentle decay
    
    chord_wave = np.zeros(bar_end - bar_start)
    for freq in chord:
        # Subtle lo-fi chorus / detune
        tone = (
            np.sin(2 * np.pi * freq * t_bar) +
            0.5 * np.sin(2 * np.pi * (freq * 1.002) * t_bar) +
            0.25 * np.sin(2 * np.pi * (freq * 2.001) * t_bar)
        )
        chord_wave += tone
        
    # Tremolo modulation (4 Hz)
    tremolo = 1.0 + 0.15 * np.sin(2 * np.pi * 4.2 * t_bar)
    audio[bar_start:bar_end] += 0.18 * chord_wave * envelope * tremolo

# 2. Smooth Sub-Bass line
for bar in range(num_bars):
    root_freq = chords[bar % len(chords)][0] # bass root
    bar_start = int(bar * bar_duration * sample_rate)
    bar_len = int(bar_duration * sample_rate)
    bar_end = min(bar_start + bar_len, total_samples)
    
    t_bar = np.linspace(0, (bar_end - bar_start) / sample_rate, bar_end - bar_start)
    bass_env = np.exp(-0.8 * t_bar)
    # Warm sine bass
    bass_tone = np.sin(2 * np.pi * root_freq * t_bar) + 0.3 * np.sin(2 * np.pi * (root_freq * 2) * t_bar)
    audio[bar_start:bar_end] += 0.22 * bass_tone * bass_env

# 3. Upbeat Lo-Fi Drum Groove (Kick on 1 & 3, Snare/Rimshot on 2 & 4, Hi-hats on 8ths)
total_beats = int(total_duration / beat_duration)
for beat in range(total_beats):
    beat_time = beat * beat_duration
    beat_sample = int(beat_time * sample_rate)
    
    # Kick Drum on beat 0 and beat 2.5 (upbeat syncopation)
    if beat % 4 == 0 or (beat % 4 == 2 and beat % 2 == 0):
        kick_dur = 0.22
        k_samples = min(int(kick_dur * sample_rate), total_samples - beat_sample)
        if k_samples > 0:
            t_k = np.linspace(0, kick_dur, k_samples)
            # Pitch drop for warm punchy lo-fi kick
            f_k = 120 * np.exp(-25 * t_k) + 45
            phase = 2 * np.pi * np.cumsum(f_k) / sample_rate
            kick_env = np.exp(-12 * t_k)
            audio[beat_sample:beat_sample + k_samples] += 0.35 * np.sin(phase) * kick_env

    # Soft Snare / Rimshot on beat 1 and 3
    if beat % 2 == 1:
        snare_dur = 0.18
        s_samples = min(int(snare_dur * sample_rate), total_samples - beat_sample)
        if s_samples > 0:
            t_s = np.linspace(0, snare_dur, s_samples)
            noise = np.random.normal(0, 1, s_samples)
            tone = np.sin(2 * np.pi * 180 * t_s)
            snare_env = np.exp(-22 * t_s)
            audio[beat_sample:beat_sample + s_samples] += 0.15 * (0.6 * noise + 0.4 * tone) * snare_env

    # Swung Hi-Hats every eighth note
    for sub in [0, 0.55]: # swing timing
        hat_time = beat_time + sub * beat_duration
        hat_sample = int(hat_time * sample_rate)
        hat_dur = 0.05
        h_samples = min(int(hat_dur * sample_rate), total_samples - hat_sample)
        if h_samples > 0:
            noise = np.random.normal(0, 1, h_samples)
            t_h = np.linspace(0, hat_dur, h_samples)
            hat_env = np.exp(-60 * t_h)
            audio[hat_sample:hat_sample + h_samples] += 0.06 * noise * hat_env

# 4. Vinyl Dust / Lo-Fi Crackle texture
vinyl_crackle = np.random.normal(0, 0.008, total_samples)
pop_indices = np.random.randint(0, total_samples, size=120)
for idx in pop_indices:
    pop_len = min(60, total_samples - idx)
    vinyl_crackle[idx:idx + pop_len] += np.random.uniform(0.04, 0.09) * np.exp(-np.linspace(0, 5, pop_len))
audio += vinyl_crackle

# 5. Pentatonic Bell / Lead Melody accents
lead_notes = [notes['E4'], notes['G4'], notes['A4'], notes['C5'], notes['D5'], notes['E5']]
for bar in range(num_bars):
    for step in [1, 2.5, 3.5]:
        note_time = (bar * 4 + step) * beat_duration
        note_sample = int(note_time * sample_rate)
        if note_sample < total_samples:
            lead_freq = np.random.choice(lead_notes)
            dur = 0.4
            l_samples = min(int(dur * sample_rate), total_samples - note_sample)
            t_l = np.linspace(0, dur, l_samples)
            bell_env = np.exp(-7 * t_l)
            bell_tone = np.sin(2 * np.pi * lead_freq * t_l) + 0.4 * np.sin(2 * np.pi * (lead_freq * 2) * t_l)
            audio[note_sample:note_sample + l_samples] += 0.10 * bell_tone * bell_env

# Master normalization with smooth fade out
audio = np.tanh(audio) # Analog soft saturation
fade_len = int(2.0 * sample_rate)
fade_out = np.linspace(1.0, 0.0, fade_len)
audio[-fade_len:] *= fade_out

# Scale to 16-bit PCM
audio_scaled = (audio * 32767 * 0.85).astype(np.int16)
wavfile.write('/config/Desktop/BuildWithGemini/upbeat_lofi.wav', sample_rate, audio_scaled)
print("Lo-Fi track generated successfully at /config/Desktop/BuildWithGemini/upbeat_lofi.wav")
