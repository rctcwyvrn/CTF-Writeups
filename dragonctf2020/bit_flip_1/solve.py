import task
import base64
from Crypto.Util.number import bytes_to_long, long_to_bytes

# attempt to recover alice's seed by using the bitflips to shift the value
# bitflip the 3rd bit, then the seed is +/- 8, so it should take either 4 more or 4 less iterations to get to the prime

# problem: once we start flipping higher bits the shift becomes too large and it begins to always hit a prime that wasn't the original, which throws off the entire algo

chal = task.Chal()
def send(bit_str, debug=True):
    if debug:
        return chal.send(bit_str)


base_iter = send("")
print(f"base iter: {base_iter}")
seed = "0"

# generator for bitstrings to test, assumes we know the seed up to the i-1th bit
def get_next(i, seed):
    pos_diff = 2**(i-1) 
    neg_diff = -1 * 2**(i-1)
    x = 2**i
    for (j, known_bit) in enumerate(seed):
        if j == 0:
            continue
        if known_bit == "1":
            x += 2**j
            extra_flip = -1 * 2**(j-1)
            pos_diff += extra_flip
            neg_diff += extra_flip

    bit_str = base64.b64encode(long_to_bytes(x))
    yield bit_str, pos_diff, neg_diff # try to make the smallest positive diff

    pos_diff = 2**(i-1) 
    neg_diff = -1 * 2**(i-1)
    x = 2**i
    for (j, known_bit) in enumerate(seed):
        if j == 0:
            continue
        if known_bit == "0":
            x += 2**j
            extra_flip = 2**(j-1)
            pos_diff += extra_flip
            neg_diff += extra_flip

    bit_str = base64.b64encode(long_to_bytes(x))
    yield bit_str, pos_diff, neg_diff # try to make the smallest negative diff

    # for (j, known_bit) in enumerate(seed):
    #     if j == 0:
    #         bit_str = base64.b64encode(long_to_bytes(2**i))
    #         pos_diff = 2**(i-1) 
    #         neg_diff = -1 * 2**(i-1)
    #         yield bit_str, pos_diff, neg_diff # try the basic one first
    #         continue
    #     bit_str = base64.b64encode(long_to_bytes(2**i + 2**j))
    #     extra_flip = 2**(j-1) if known_bit == "0" else -1 * 2**(j-1)
    #     yield bit_str, pos_diff + extra_flip, neg_diff + extra_flip

for i in range(1,30):
    for bit_str, pos_diff, neg_diff in get_next(i, seed):
        iters = send(bit_str)
        diff = iters - base_iter
        if diff == pos_diff: # took more iterations, number went down, bit was 1
            seed = "1" + seed
            break
        elif diff == neg_diff:
            seed = "0" + seed
            break
        else:
            print(f"i = {i} | known = {seed} | expected {pos_diff} or {neg_diff}, got {diff} instead")
            #seed = "_" + seed
            #break
    else:
        print(f"Failed at i = {i}")
        seed = "_" + seed
        
    
print(seed)