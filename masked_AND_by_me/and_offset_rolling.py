# AND function calculation between an odd number of XOR masked data shares

# calculates roughly Ci = [XOR(k!=i: Ak) AND XOR(j!=i: Bj)] XOR (A(not i) AND B(not i))

# meaning every ANDed value between two respective shares has to be corrected with the
# parity of all other shares, but for non-completeness, the output shares are computed
# with ANDed shares that have a different index than the missing value in the parity,
# still all AND-ed share values have to be added excatly once (or some odd times) to
# a suitable parity value

# uses the rolling hash like property of parity, that any xor-ed data may be
# subtracted and a new one added, needing roughly 1/r amounts of XORs, but is probably
# not glitching resistant, and works only with processors

# still wondering if calculating all the parities of all but one shares is a good idea!
# namely those represent the original value masked by a single mask - on the other hand
# this is valid for all individual shares too: any of them can be expressed as the 
# original value xor sth
# however that "sth" - the parity of the rest(!) - is being computed here and might be
# obtained through the side channel: which however shouldn't matter, because every time
# the original value XOR a differet mask is the result

from random import randint as rdi 

def masked_AND(am, bm):

    # mixing offsets: any offset series should be allowed
    offset = [i for i in range(r)]
    for i in range(r):
        swap0 = rdi(0, r-1)
        swap1 = rdi(0, r-1) 
        offset[swap0], offset[swap1] = offset[swap1], offset[swap0]
    
    # AND values of respective bits to be corrected by parities
    cm = [am[i] & bm[i] for i in range(r)]
    
    # initializing summing - maybe randomizing helps a bit to mask the parities
    suma = 0
    sumb = 0
    
    # initializing parity: data at first offset is omitted
    for i in range(r-1):
        suma ^= am[offset[i+1]]
        sumb ^= bm[offset[i+1]]
    
    # calculating diverse parities in a rolling manner: only subtracting and adding 1-1 share at a time
    for i in range(r-1):
        
        # needs an offset so that it fulfills non-completeness, a displacement by -1 is more than nothing
        # any offset does the trick, as long as the cm value does not have the index of the missing
        # value in the parity
        cm[offset[i]-1] ^= suma & sumb
        
        # subtracting the next value to be missing from the parity at first in order not to unmask original value
        suma ^= am[offset[i+1]]
        sumb ^= bm[offset[i+1]]
        
        # adding the currently missed value only afterwards - in hardware these prev. and next two operations may
        # glitch: if the addition is faster than the subtraction, the unmasked value appears for a short time!!
        # a fully asynchronous implementation is thus not suggested...
        suma ^= am[offset[i]]
        sumb ^= bm[offset[i]]
    
    #correcting the AND-ed value on the last offset with its parities
    cm[offset[r-1]-1] ^= suma & sumb
    
    return cm


# BEGIN TESTING

a = 0x76857f6f
b = 0x5432f1f2
print("A:      ", hex(a))
print("B:      ", hex(b))
print("AND:    ", hex(a & b))

# preparing odd pieces of random numbers for masking
# the algorithm doesn't work with an even number of shares!

r = 5 #6
ra =[0x67978544,
     0xa6f328ab,
     0x68979586,
     0xc9876d3e]
     #0xa7656b36]
rb =[0x6abdc744,
     0x895728ab,
     0xfe45c8d6,
     0xc9876d3e]
     #0x86f675ed]

# the sum of the masks has to be zero at first...*1
rasum = 0
for ma in ra:
    rasum ^= ma
ra.append(rasum)
rbsum = 0
for mb in rb:
    rbsum ^= mb
rb.append(rbsum)

# *1...so that adding a and b to any arbitrary random number yields valid shares
am = ra
am[2] ^= a #index is arbitrary
bm = rb
bm[r-2] ^= b #index is arbitrary

# double checking the sum of shares
a = 0
b = 0
for i in range(r):
    a ^= am[i]
    b ^= bm[i]
print("A sum:  ", hex(a))
print("B sum:  ", hex(b))

# AND calculation between masked shares
cm = masked_AND(am, bm)

#summing up the result shares
c = 0
for k in range(len(cm)):
    c ^= cm[k]
print("Result: ", hex(c))
