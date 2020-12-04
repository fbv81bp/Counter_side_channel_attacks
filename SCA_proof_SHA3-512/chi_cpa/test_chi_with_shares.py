import random 

order = 5 # number of shares that contribute to the masking

r = order

# Masked 'and' function for arbitrary odd number of shares
def masked_and(am, bm):
    #calculate AND between masked values
    cm = [am[i] & bm[i] for i in range(r)]
    #calculating correction terms
    for i in range(r):
        suma = 0
        sumb = 0
        #calculating parities of all corresponding Aj and Bj bits...
        for j in range(r):
            #...corresponding means all but the Ai and Bi bits
            if i==j:
                continue
            #parities
            suma ^= am[j]
            sumb ^= bm[j]
        #addig correction term to the particular output share
        #which is the "AND" between the parities
        cm[i] ^= suma & sumb
        #cm[i+1%r] ^= suma & sumb # kinda threshold this way
    return cm

def neg_array(arr):
    arr = [not arr[i] for i in range(len(arr))]
    return arr

def xor_arrays(arr1, arr2):
    if len(arr1) != len(arr2):
        return None # error
    arr = [arr1[i] ^ arr2[i] for i in range(len(arr1))]
    return arr

# Modelling non-linearity of the higher order Chi function to check its leakage
def chi_leakage(states_in):
    arrays = [[0 for i in range(order)] for j in range(5)]

    # convert integers to arrays
    arrays = []
    for state_in in states_in:
        array = [0,0,0,0,0]
        for i in range(5):
            if state_in % 2 == 1:
                array[4-i] = 1
            state_in //= 2
        arrays.append(array)

    # switching indices
    shares = [[arrays[x][y] for x in range(order)] for y in range(5)]

    # calculate 1 Chi on 5 bits: Chi's are calculated independently on 5-5 bits, if that's done parallely, it just adds algorithmic noise, but the correlation still works
    for x in range(5):
        shares[x] = xor_arrays(shares[x], masked_and(neg_array(shares[(x + 1) % 5]), shares[(x + 2) % 5]))

    # switching indices
    arrays = [[shares[x][y] for x in range(5)] for y in range(order)]

    # convert arrays to integers
    states_out = [0 for i in range(order)]
    for j in range(len(arrays)):
        for i in range(5):
            states_out[j] *= 2
            if arrays[j][i] == 1:
                states_out[j] += 1

    return states_out

# Modelling non-linearity of the Chi function to check its leakage: if this component can be made leakage free, the entire design will be so
def chi_original(state_in):
    array = [0 for i in range(5)]
    # convert integer to array
    for i in range(5):
        if state_in % 2 == 1:
            array[4-i] = 1
        state_in //= 2
    # calculate 1 Chi on 5 bits: Chi's are calculated independently on 5-5 bits, if that's done parallely, it just adds algorithmic noise, but the correlation still works
    for x in range(5):
        array[x] = array[x] ^ ((not array[(x + 1) % 5]) and array[(x + 2) % 5])
    # convert array to integer
    state_out = 0
    for i in range(5):
        state_out *= 2
        if array[i] == 1:
            state_out += 1
    return state_out



chi_in = [1,7,28,12,11]

chi_out = chi_leakage(chi_in)

print(chi_out)

chi_out_xored = 0
for i in range(order):
    chi_out_xored ^= chi_out[i]

print(chi_out_xored)

chi_in_xored = 0
for i in range(order):
    chi_in_xored ^= chi_in[i]

print(chi_original(chi_in_xored))
