# See: https://en.wikipedia.org/wiki/Oblivious_transfer
# See: http://www.lix.polytechnique.fr/~catuscia/teaching/papers_and_books/SigningContracts.pdf
import random
from Crypto.PublicKey import RSA

MSG_SIZE = 32
RND_SIZE = 32

random.seed()

# What Alice knows
# Generate RSA key pair
RSAkey = RSA.generate( 1024 )
# n = 10142789312725007
# e = 5
# d = 8114231289041741

n = getattr(RSAkey,'n')
e = getattr(RSAkey,'e')
d = getattr(RSAkey,'d')

# Alice's secrets
m0, m1 = random.getrandbits(MSG_SIZE), random.getrandbits(MSG_SIZE)
# Alice's random messages
x0, x1 = random.getrandbits(MSG_SIZE), random.getrandbits(MSG_SIZE)

# What Bob knows
b = 0 # or 1
k = random.getrandbits(RND_SIZE)

# Step 1: Bob sends `v' to Alice
v = pow( k, e, n ) + (x0 if 0==b else x1)
v = v % n


# Step 2: Alice computes boths message transforms, sends to Bob
k0, k1 = pow(v-x0, d, n), pow(v-x1, d, n)
m00, m11 = m0 + k0, m1 + k1

# Step 3: Bob computes the b-th message
mb = (m00 if 0==b else m11) - k

print 'b  = ', b
print 'm0 = ', m0
print 'm1 = ', m1
print 'mb = ', mb
