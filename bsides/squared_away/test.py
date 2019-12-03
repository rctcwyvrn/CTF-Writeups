import random, os
#from Crypto.Utils import number


#probably the vuln for flag2

def is_prime(n):
    """Check whether n is a prime number"""
    r = 0
    d = n - 1 

    #if n is odd, ie d= n-1 is even then
    #increment r and divide d by 2 until it is odd
    while d % 2 == 0:
        r += 1
        d //= 2

    # n-1 = d * 2 ** r
    #print("n-1 = ",d*(2**r)) # = n -1
    print(f"pre loop d={d} r={r}")

    #so d =  (n-1) / 2**r

    for count in range(40):
        a = random.randint(2, n - 2) 
        x = pow(a, d, n)

        #x = random int between 2 and n-2 **  (n-1)/(2 ** r) mod n 
        #print(f"new cycle with new randoms a={a} \t x={x} \t loop nm={count}")

        if x == 1 or x == n - 1: 
            #print("x=1 or x=n-1, skipping cycle")
            continue

        #print("Entering internal loop")
        for count2 in range(r - 1):
            x = pow(x, 2, n)
            #print(f"> c2={count2} \t x={x}")
            if x == n - 1:
                #print("> breaking")
                break      
        else:
            print("Did not break in the loop")
            return False

    return True

def random_prime_3mod4(bits):
    """
    Return a random prime that is congruent to 3 modulo 4

    Arguments:
    bits -- length of the prime in bits. Must be a multiple of 8.
    """
    x = int.from_bytes(os.urandom(bits // 8), byteorder="big")
    #val = (x | (1 << (bits - 1)) | 3)
    val = (x | (1 << (bits - 1)) | 3) #second or makes it at least that large, third or makes it 3mod4
    #print(val)
    #print(val % 4)
    #print(val & 3)


# xs = []
# for _ in range(10):
#    xs.append(random_prime_3mod4(1024 // 2))

# print(len(xs), len(set(xs)))

# import gmpy2
# def primes():
#     n = 65537
#     while True:
#         yield n
#         n = gmpy2.next_prime(n)

# count = 0
# for prime in primes():
#     count+=1
#     print("testing ",prime)
#     if count >= 30000:
#         print("nothing")
#         break
#     if not is_prime(prime):
#         print("found!!")
#         break

#print("result of isPrime =",is_prime(65537))

