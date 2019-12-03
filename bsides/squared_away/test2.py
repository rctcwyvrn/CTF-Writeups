import os, random, math

def is_prime(n):
    """Check whether n is a prime number"""
    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(40):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break

        else:
            return False

    return True


def next_prime_3mod4(n):
    """
    Return the first prime greater than or equal to n that is also congruent
    to 3 modulo 4.

    Aguments:
    n -- the starting point for the search. Must be congruent to 3 modulo 4.
    """
    while True:
        if is_prime(n):
            return n
        n += 4


def random_prime_3mod4(bits):
    """
    Return a random prime that is congruent to 3 modulo 4

    Arguments:
    bits -- length of the prime in bits. Must be a multiple of 8.
    """
    x = int.from_bytes(os.urandom(bits // 8), byteorder="big")
    return next_prime_3mod4(x | (1 << (bits - 1)) | 3)


xs = []
bound = 2 **((1024+5)/4)
for i in range(50):
   print(f"looking for {i}th prime")
   #xs.append(random_prime_3mod4(1024 // 2))
   p1 = random_prime_3mod4(1024 // 2)
   p2 = random_prime_3mod4(1024 // 2)
   if (abs(p2-p1) >= bound):
    print("death")
    break
   else:
    print(abs(p2-p1) - bound)
   #print((p2-p1)/p1)


#print("total # of primes", len(xs),"total # of unique primes", len(set(xs)))