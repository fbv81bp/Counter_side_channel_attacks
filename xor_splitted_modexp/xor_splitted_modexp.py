# Boolean Exponent Splitting for modular exponentiation - Algorithm 2

# helper function
def bitof(m, n):
    m >>= n
    m &= 1
    return m

# input data
x = 0xab1a
k = 0xcd2b

# mask
a = 0xef3c

# splitting k to a and b
b = k ^ a

# register of the ladder
r = [1,1]
bb = 0 # or 1
r[not bb] = x

# dealing with <32 bit integers
for i in range(32, -1, -1):
    r[bitof(a,i)], r[not bitof(a,i)] = (r[bitof(b,i) ^ bb ^ bitof(a,i)]) ** 2, r[0] * r[1]
    bb = bitof(b,i)
    
# test value
print("Test succesful:", r[bb] == x ** k)
