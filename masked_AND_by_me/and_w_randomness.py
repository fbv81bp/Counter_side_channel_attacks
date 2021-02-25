def masked_AND(shares, a_masked, b_masked, random):
    
    # calculate AND between shares...
    c_masked = [a_masked[i] & b_masked[i] for i in range(shares)]
    # ...with refreshing the output's mask 
    c_masked = [c_masked[i] ^ random[i] for i in range(shares)]
    
    # calculating correction terms: some terms of the parities'
    # cancel outat the end in case of an odd number of elements
    for i in range(shares):
        parity_a = 0
        parity_b = 0
        # calculating parities of all corresponding Aj and Bj bits...
        for j in range(shares):
            # ...corresponding means all but the Ai and Bi bits
            if i!=j:
                parity_a ^= a_masked[j]
                parity_b ^= b_masked[j]

        # addig correction term to the particular output share
        # which is the "AND" between the parities
        c_masked[i] ^= parity_a & parity_b
    return c_masked

# BEGIN TESTING

a = 0x76a57f6e
b = 0x5432d1f2
print("A:      ", hex(a))
print("B:      ", hex(b))
print("AND:    ", hex(a & b))

# preparing odd pieces of random numbers because the masking
# algorithm doesn't work with an even number of shares!

shares = 5  # comment to test even number of shares
#shares = 6 # uncomment to test even number of shares
ra =[0x67978544,
     0xa6f328ab,
     0x68979586,
     0xc9876d3e]
     #0xa7656b36] # uncomment to test even number of shares
rb =[0x6abdc744,
     0x895728ab,
     0xfe45c8d6,
     0xc9876d3e]
     #0x86f675ed] # uncomment to test even number of shares

# random numbers for mask refreshing
random_bits = [0xef6437bc,
               0x7588a768,
               0x9653bcd1,
               0xa6754e8d]
rndsum = 0
for rbit in random_bits:
    rndsum ^= rbit
random_bits.append(rndsum)

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
bm[shares-2] ^= b #index is arbitrary

# test vectors for VHDL code
#for s in am:
#    print(hex(s))# test vectors for VHDL code
#for s in bm:
#    print(hex(s))

# double checking the sum of shares
a = 0
b = 0
for i in range(shares):
    a ^= am[i]
    b ^= bm[i]
print("A sum:  ", hex(a))
print("B sum:  ", hex(b))

# AND calculation between masked shares
cm = masked_AND(shares, am, bm, random_bits)

# test vectors for VHDL code
#for s in cm:
#    print(hex(s))

#summing up the result shares
c = 0
for k in range(len(cm)):
    c ^= cm[k]
print("Result: ", hex(c))