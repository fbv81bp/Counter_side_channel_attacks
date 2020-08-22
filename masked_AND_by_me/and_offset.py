# AND function calculation between an odd number of XOR masked data shares

# calculates roughly Ci = [XOR(k!=i: Ak) AND XOR(j!=i: Bj)] XOR (A(not i) AND B(not i))

# meaning every ANDed value between two respective shares has to be corrected with the
# parity of all other shares, but for non-completeness, the output shares are computed
# with ANDed shares that have a different index than the missing value in the parity,
# still all AND-ed share values have to be added excatly once (or some odd times) to
# a suitable parity value

def masked_AND(am, bm):

    # offsets of length 5, need to be updated if r changed
    offset1 = [1,3,0,2,4] # any arbitrary order is allowed in the parity
    offset2 = [3,1,4,0,2] # calculationt to shuffle power consumption traces
    offset3 = [3,4,1,0,2] # anything but the position itself is allowed!
                          # random shuffled is the best: it enforces summing
                          # up the measurement results and searching for data
                          # in much greater noise
    
    cm = [am[i] & bm[i] for i in range(r)]
    for i in range(r):
        suma = 0 # perhaps initializing these for every cycle with mostly random values,
                 # which sum up to 0, or at least their AND products sum up to 0,
                 # may mask each parity value well enough so that the input shares unmasked
                 # sum can't be recovered because of adding up all but one of the shares
        sumb = 0 # periodically
        for j in range(r):
            if i==offset1[j]: # parities are still being calculated without the ith
                continue      # slice, but the order of slices may be random...
            suma ^= am[offset1[j]]
        for j in range(r):
            if i==offset2[j]:
                continue
            sumb ^= bm[offset2[j]]
        cm[offset3[i]] ^= suma & sumb #the AND-ed versions may be added to any parity
                                      #due to linearity, this way it is a thresold impl.
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
