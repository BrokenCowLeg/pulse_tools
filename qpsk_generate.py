## Script for creating QPSK waveforms from a text prompt
## TODO: Add tone generation, add Unique word BPSK generation, fix sample padding between bits
## Convert the generation to DQPSK once we have the tone/UW added

# Import modules
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
import time

starttime = time.perf_counter()

# ------------------- START USER INPUT VALUES -----------------------------
tone_len = 4  # Length of tone in bits
unq_word = '01101'  # Bit sequence of the targeted Unique Word
msg_str = 'Hello'  # Text message to be sent
fc = 10  # Carrier Frequency in Hz

# ------------------- END USER INPUT VALUES -------------------------------

# Convert and count bits from strings
unq_word_bits = list(map(int, unq_word))
msg_bits = list(map(int, ''.join(bin(ord(x)) for x in msg_str).replace('b', '')))
msg_bit_len = len(msg_bits)
total_bits = tone_len + len(unq_word_bits) + len(msg_bits)
print('Total Bits in sequence: ' + str(total_bits))

# Create Even and Odd bits from binary message payload for I and Q
i_bits = [msg_bits[i] for i in range(0, msg_bit_len, 2)]
q_bits = [msg_bits[i] for i in range(1, msg_bit_len, 2)]

print("Msg bits: " + str(msg_bits))
print(str(msg_bit_len)+' = '+str(len(i_bits))+' + '+str(len(q_bits)))
print("I bits: " + str(i_bits))
print("Q bits: " + str(q_bits))

sample_rate = 100000
burst_dur = tone_len + len(unq_word) + len(msg_str)  # Duration of the Burst
bit_dur = 1  # Bit Duration
t = np.linspace(0, 1, sample_rate)  # Time
t_total = np.linspace(0, len(i_bits), sample_rate * len(i_bits))

# Create I and Q waveforms
i_phase = sqrt(2 / bit_dur) * np.sin(2 * np.pi * fc * t)  # carrier frequency sine wave
q_phase = sqrt(2 / bit_dur) * np.cos(2 * np.pi * fc * t)  # carrier frequency cosine wave

# Prep bit waveform arrays and time intervals
t1 = 0
t2 = bit_dur
all_i = []
all_q = []
i_carrier = []
q_carrier = []

# Create In-Phase waveform
for x in i_bits:
    t = np.linspace(t1, t2, sample_rate)
    if x == 1:
        bit_state = np.ones((1, len(t)))
    else:
        bit_state = (-1) * np.ones((1, len(t)))
    i_wave = i_phase * bit_state
    all_i = np.append(all_i, i_wave)
    i_carrier = np.append(i_carrier, i_phase)

# Create Quadrature-Phase waveform
for x in q_bits:
    t = np.linspace(t1, t2, sample_rate)
    if x == 1:
        bit_state = np.ones((1, len(t)))
    else:
        bit_state = (-1) * np.ones((1, len(t)))
    q_wave = q_phase * bit_state
    all_q = np.append(all_q, q_wave)
    q_carrier = np.append(q_carrier, q_phase)

print(str(len(i_phase))+" "+str(len(all_i))) # Check time samples of single symbol vs samples of waveform

# Create modulated QPSK waveform
qpsk_wav = np.sum([all_i, all_q], axis=0)/2
qpsk_carr = np.sum([i_carrier, q_carrier], axis=0)/2
qpsk_comp = qpsk_wav / qpsk_carr # The math for this is broken on non-180 degree shifts
qpsk_comp[qpsk_comp > 1] = 1
qpsk_comp[qpsk_comp < -1] = -1

# Pre-allocate correlation array
sig1 = all_i
sig2 = i_carrier
corr = (len(sig1) - len(sig2) + 1) * [0]

# Go through lag components one-by-one ----- Currently broke, idk dawg
for l in range(len(corr)):
    corr[l] = sum([sig1[i+l] * sig2[i] for i in range(len(sig2))])

print(corr)

# Total time to generate waveforms
print('Total time: ' + str(time.perf_counter() - starttime)+ ' seconds')

# Plot resulting waveforms
fig, axs = plt.subplots(8,constrained_layout=True)
fig.suptitle('QPSK outputs for the text: '+msg_str)
for x in range(0,8,1):
    axs[x].grid(True)
    axs[x].set_xticks(range(0,len(i_bits)+1,1))

axs[0].plot(t_total, all_i)
axs[0].set_title('Modulated I channel waveform')
axs[1].plot(t_total, i_carrier)
axs[1].set_title('I channel carrier waveform')
axs[2].plot(t_total, (all_i / i_carrier))
axs[2].set_title('I channel in-phase (+1) and out of phase (-1)')
axs[3].plot(t_total, all_q)
axs[3].set_title('Modulated Q channel waveform')
axs[4].plot(t_total, q_carrier)
axs[4].set_title('Q channel carrier waveform')
axs[5].plot(t_total, (all_q / q_carrier))
axs[5].set_title('Q channel in-phase (+1) and out of phase (-1)')
axs[6].plot(t_total, qpsk_wav)
axs[6].set_title('Modulated mixed I and Q channel waveform')
axs[7].plot(t_total, qpsk_carr)
axs[7].set_title('Mixed I and Q channel carrier waveform')
#axs[8].plot(t_total, qpsk_comp) # This is poopoo bad math
plt.show()

fig, axs = plt.subplots(2, constrained_layout=True)
for x in range(0,2,1):
    axs[x].grid(True)
    axs[x].set_xticks(range(0,len(i_bits)+1,1))

axs[0].plot(t_total,all_i,"r",t_total,all_q,'b',t_total,qpsk_wav,'g')
axs[0].set_title('Modulated IQ [Red: I, Q:Blue, IQ result:Green]')
axs[1].plot(t_total,i_carrier,"r",t_total,q_carrier,'b',t_total,qpsk_carr,'g')
axs[1].set_title('Carrier IQ [Red: I, Q:Blue, IQ result:Green]')

plt.show()
