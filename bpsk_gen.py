## Script to create a quick BPSK to match filter across an imported file

# Import Modules
from math import sqrt
import numpy as np
import shutil
import pandas as pd
import matplotlib.pyplot as plt

# --------------------- User inputs -----------------------
fc = 1 # Carrier Frequency in Hz
bit_dur = 1 # Size of bit in time
sample_rate = 100000 # Sample Rate in Hz
bpsk_bits_str = '010001001101' # BPSK Series in BPSK shorthand
bpsk_bits_hex = ''

# Convert inputs
bpsk_bits = list(map(int, bpsk_bits_str))

# Create waveform series
t = np.linspace(0, 1, sample_rate)  # Time
t_total = np.linspace(0, len(bpsk_bits), sample_rate * len(bpsk_bits))
carrier_wave = sqrt(2 / bit_dur) * np.sin(2 * np.pi * fc * t)  # carrier frequency sine wave

# Modulate Waveform Series
total_wave = []
bit_carrier = []
t1 = 0
t2 = bit_dur
for x in bpsk_bits:
    t = np.linspace(t1, t2, sample_rate)
    if x == 1:
        bit_state = np.ones((1, len(t)))
    else:
        bit_state = (-1) * np.ones((1, len(t)))
    bit_wave = carrier_wave * bit_state
    total_wave = np.append(total_wave, bit_wave)
    bit_carrier = np.append(bit_carrier, carrier_wave)

# Plot generated wave

fig, axs = plt.subplots(3,constrained_layout=True)
fig.suptitle('BPSK waveforms for: '+bpsk_bits_str)
for x in range(0,3,1):
    axs[x].grid(True)
    axs[x].set_xticks(range(0,len(bpsk_bits)+1,1))

axs[0].plot(t_total, total_wave)
axs[0].set_title('Modulated waveform')
axs[1].plot(t_total, bit_carrier)
axs[1].set_title('Carrier waveform')
axs[2].plot(t_total, (total_wave / bit_carrier))
axs[2].set_title('In-phase (+1) and Out of phase (-1)')

plt.show()