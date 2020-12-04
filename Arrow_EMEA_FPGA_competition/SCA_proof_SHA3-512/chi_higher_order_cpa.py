import random 

order = 3 # number of shares that contribute to the masking

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

# Hamming weight of x
def count1s(x):
    y = 0
    while(x>0):
        if x%2==1:
            y+=1
        x=x//2
    return y

# PREPARATION
# -----------

# hypothesises of hamming weights for keys

hypothesises_for_key_share0 = [[] for i in range(32*32*32)]
k=0
print('calculate 32**3 hypothesises')
for key_share0 in range(32):
    print(key_share0)
    for key_share1 in range(32):
        for key_share2 in range(32):
            key_state = [key_share0, key_share1, key_share2]
            data_share1 = 0
            data_share2 = 0
            for data_share0 in range(32):
                data_state = [data_share0, data_share1, data_share2]
                # let's suppose a single share's leakage is measureable separately
                single_share = chi_leakage(xor_arrays(key_state, data_state))[0]
                hypothesises_for_key_share0[k].append(count1s(single_share)) 
            k+=1

# SIMULATE MEASUREMENTS
# ---------------------
guess_was_correct = True
for i in range(10): # guessing 10 different random keys, while hypothesises only have to be calculated and stored once

    # number of choosen plain texts
    run_length = 200

    # pick any random number between 0 and 31
    # if guess wasn't correct, try over again with new choosen plain texts
    if guess_was_correct:
        key_shares = [random.randint(0,31) for i in range(order)]

    # pick some random numbers you like to run hacking with
    choosen_plain_texts = [[random.randint(0,31),0,0] for i in range(run_length)]

    # simulate leakage
    print('calculate leakages')
    leakages = [count1s(chi_leakage(xor_arrays(key_shares, plain))[0]) for plain in choosen_plain_texts]

    # HACK IT
    # -------

    #calculating correlations with diverse hypothesises on assumed key values
    print('correlating share 0')
    most_likely_key = [0,0,0]
    highest_correlation = 0
    k=0
    for assumed_key_share0 in range(32):
        for assumed_key_share1 in range(32):
            for assumed_key_share2 in range(32):
                correlation = 0
                for i in range(len(leakages)):
                    correlation += hypothesises_for_key_share0[k][choosen_plain_texts[i][0]] * leakages[i]
                if correlation > highest_correlation:
                    highest_correlation = correlation
                    most_likely_key = assumed_key_share0
                k+=1
    print('real key:', key_shares)
    print('most likely share 0:', most_likely_key)
    guess_was_correct = key_shares[0] == most_likely_key
    print(' ', guess_was_correct)
