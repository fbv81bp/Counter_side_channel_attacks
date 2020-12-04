'''
MIT License

Copyright (c) 2020 pkdoshinji
Copyright (c) 2020 fbv81bp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

''' 
Author: Patrick kelly
Github: pkdoshinji
Last updated: May 22, 2020
'''

'''
Rewritten by: Balazs Valer Fekete
Github: fbv81bp
Last updated: 28.09.2020
Modifications: removed NumPy dependency, added masked AND calculation for possible side channel attck protection
Description: this code is meant to test if the masking of the AND gate results in the very same output regardless of
    the number or content of XOR mask values
'''

#text : abcdef
# hex : 6162636465660a
# out : 01309a45c57cd7faef9ee6bb95fed29e5e2e0312af12a95fffeee340e5e5948b4652d26ae4b75976a53cc1612141af6e24df36517a61f46a1a05f59cf667046a

# Keccak constants, hard-coded for the SHA3 family of hashes 
#l_list = [0,1,2,3,4,5,6]
#l = l_list[6]
w = 64 #(2 ** l)
b = 1600 #25 * w

# Precalculated values for rho function bitshifts
shifts = [[0,  36, 3,  41, 18],
          [1,  44, 10, 45, 2 ],
          [62, 6,  43, 15, 61],
          [28, 55, 25, 21, 56],
          [27, 20, 39, 8,  14]]

# Precalculated values for iota function round constants
RCs = [0x0000000000000001, 0x0000000000008082, 0x800000000000808a,
       0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
       0x8000000080008081, 0x8000000000008009, 0x000000000000008a,
       0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
       0x000000008000808b, 0x800000000000008b, 0x8000000000008089,
       0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
       0x000000000000800a, 0x800000008000000a, 0x8000000080008081,
       0x8000000000008080, 0x0000000080000001, 0x8000000080008008]

def string_to_array(string,w=64):
    # Convert a bitstring to (5,5,w) array
    state_array = [[[0 for i in range(w)] for j in range(5)] for k in range(5)]
    for x in range(5):
        for y in range(5):
            for z in range(w):
                if (w*(5*x+y)+z) < len(string):
                    state_array[y][x][z] = string[w*(5*x+y)+z]
    return state_array

def nproll(array, roll):
    return array[roll:]+array[:roll]

def xor_arrays(arr1, arr2):
    return [arr1[i] ^ arr2[i] for i in range(len(arr1))]

def hex2binarray(hexstring, length):
    # Helper function
    binarray = [0 for i in range(length)]
    for i in range(length):
        if hexstring & 1 == 1:
            binarray[i] = 1
        hexstring //= 2
    return binarray

def theta(array, w=64):
    # For each column, XOR the parity of two adjacent columns
    array_prime = array.copy()
    C = [[0 for i in range(w)] for j in range(5)]
    D = [[0 for i in range(w)] for j in range(5)]
    for x in range(5):
        for y in range(5):
            C[x] = xor_arrays(C[x], array[x][y]) # C[x] is a lane, each entry represents the column parity
    for x in range(5):
        D[x] = xor_arrays(C[(x-1)%5], nproll(C[(x+1)%5],1)) # D[x] is a placeholder
    for x in range(5):
        for y in range(5):
            array_prime[x][y]  = xor_arrays(array_prime[x][y], D[x]) # For each lane, XOR the value of D[x]
    return array_prime

def rho(array, w=64):
    # Circular shift each lane by a precalculated amount (given by the shifts array)
    array_prime = [[[0 for i in range(w)] for j in range(5)] for k in range(5)]
    for x in range(5):
        for y in range(5):
            array_prime[x][y] = nproll(array[x][y], shifts[x][y])
    return array_prime

def pi(array, w=64):
    # 'Rotate' each slice according to a modular linear transformation
    array_prime = [[[0 for i in range(w)] for j in range(5)] for k in range(5)]
    for x in range(5):
        for y in range(5):
            array_prime[x][y] = array[((x) + (3 * y)) % 5][x]
    return array_prime

def neg_array(arr):
    return [arr[i] ^ 1 for i in range(len(arr))]

def and_arrays(arr1, arr2):
    return [arr1[i] & arr2[i] for i in range(len(arr1))]

def and_masked_arrays(am, bm):
    # mixing offsets: any offset series should be allowed: orderes, static random, dynamically random which is static during a single run
    
    offset = [m for m in range(shares)]
    
    #offset = [1, 2, 5, 0, 4, 6, 3] #may be manually updated if contains all numbers "<shares"
    
    # AND values of respective bits to be corrected by parities
    cm = [and_arrays(am[i], bm[i]) for i in range(shares)]
    # initializing summing - maybe randomizing helps a bit to mask the parities
    suma = [0 for m in range(w)]
    sumb = [0 for m in range(w)]
    # initializing parity: data at first offset is omitted
    for i in range(shares-1):
        suma = xor_arrays(suma, am[offset[i+1]])
        sumb = xor_arrays(sumb, bm[offset[i+1]])
    # calculating diverse parities in a rolling manner: only subtracting and adding 1-1 share at a time
    for i in range(shares-1):
        # needs an offset so that it fulfills non-completeness, a displacement by -1 is more than nothing
        # any offset does the trick, as long as the cm value does not have the index of the missing
        # value in the parity
        cm[offset[i]-1] = xor_arrays(cm[offset[i]-1], and_arrays(suma, sumb))
        # subtracting the next value to be missing from the parity at first in order not to unmask original value
        suma = xor_arrays(suma, am[offset[i+1]])
        sumb = xor_arrays(sumb, bm[offset[i+1]])
        # adding the currently missed value only afterwards - in hardware these prev. and next two operations may
        # glitch: if the addition is faster than the subtraction, the unmasked value appears for a short time!!
        # a fully asynchronous implementation is thus not suggested...
        suma = xor_arrays(suma, am[offset[i]])
        sumb = xor_arrays(sumb, bm[offset[i]])
    #correcting the AND-ed value on the last offset with its parities
    cm[offset[shares-1]-1] = xor_arrays(cm[offset[shares-1]-1], and_arrays(suma, sumb))
    return cm

def chi(array, w=64):
    # Bitwise transformation of each row according to a nonlinear function
    array_prime = [[[[0 for i in range(w)] for j in range(5)] for k in range(5)] for m in range(shares)]
    for x in range(5):
        for y in range(5):
            negated = [[0 for i in range(w)] for m in range(shares)]
            for m in range(shares):
                negated[m] = neg_array(array[m][(x + 1) % 5][y])
            array_piece = [array[m][(x + 2) % 5][y] for m in range(shares)]
            anded = and_masked_arrays(negated, array_piece)    
            for m in range(shares):
                array_prime[m][x][y] = xor_arrays(array[m][x][y], anded[m])
    return array_prime

def iota(array, round_index, w=64):
    # XOR each lane with a precalculated round constant
    RC = hex2binarray(RCs[round_index], 64)
    RC = RC[::-1]
    array_prime = array.copy()
    array_prime[0][0] = xor_arrays(array_prime[0][0], RC)
    return array_prime

def keccak(state):
    # The keccak function defines one transformation round, SHA-3 has 24 in total
    for round_index in range(24):
        for i in range(shares):
            state[i] = theta(state[i])
            state[i] = rho(state[i])
            state[i] = pi(state[i])
        state = chi(state)
        for i in range(shares):
            state[i] = iota(state[i], round_index)
    return state

def squeeze(array):
    hash = 0
    for i in range(5):
        for j in range(5):
            for k in range(0,64,8):
                for n in range(0,8):
                    hash *= 2
                    hash += array[j][i][-k-8+n]
    return hash >> 1600-512


# Number of shares has to be odd for masked AND to function (here up to 9, because "mask" has yet has 8 entries)
# This parameter is what should* control strength against side channel analysis.
# (*Should, because it is not yet a publicly reviewed implementation, but based on my idea - fbv81bp.)
shares = 9
#shares = 7
#shares = 5
#shares = 3

# Masking values: any random numbers to create shares with (extend with any entries for "shares" above 9)
mask = [0x134578031870153130875420637835986125107782356039812751762002896308574171287013589329817527812803425780932589215686015380325801268160254073269591,
        0x129875483923284795493878198345894837278934598774839291878293459875849000086518652754562754167461679065068516744722574471675964056340252123426253,
        0x40000000000000000000073452324765376475,
        0x543645246536475867586497853674564,
        0x87654321,
        0xabcdef987654567898765abcdef,
        0x76756453542354658768769758647536435465768754321302110123465790465786745634,
        0xcdf]
mask = mask [:shares-1]

# Calculate capacity and rate from outbits
outbits = 512
capacity = 2 * outbits
rate = b - capacity

# Pad the bitstring according to the pad10*1 function (see SHA3 specifications)
padded = 0x000666656463626100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000

sponge_rounds = 1 #len(padded) // rate

last_mask = padded
for i in range(shares - 1):
    last_mask ^= mask[i]
mask.append(last_mask)

for i in range(shares):
    mask[i] <<= 1600-576
    mask[i] = hex2binarray(mask[i], 1600)
    mask[i] = mask[i][::-1]

state = [[[[0 for i in range(w)] for j in range(5)] for k in range(5)] for m in range(shares)]

for n in range(shares):
    current_string = mask[n][0 : rate]
    array = string_to_array(current_string, w=64)
    state[n] = [[[state[n][k][j][i] ^ array[k][j][i] for i in range(w)] for j in range(5)] for k in range(5)]

state = keccak(state) # single round because of short test message

# The 'squeeze' phase outputs the final hash value
print()
result = 0
for i in range(shares):
    result ^= squeeze(state[i])
print('hash result:', hex(result))

