import ctypes
import pathlib

test = ctypes.CDLL("./libtests.so") # gcc -shared -o libtests.so tests.c 

strfry_from_seed = test.strfry_from_seed
strfry_from_seed.restype = ctypes.c_char_p
test_str = "abcdefghijklmnopqrstuvwxyz"

def test_seed(sec, nsec, expected):
    c_test_str = ctypes.c_char_p(test_str.encode()) #has to be recreated here, because strfry_from_seed modifies c_test_str in place
    t_sec = ctypes.c_longlong(sec)
    t_nsec = ctypes.c_long(nsec)

    res = strfry_from_seed(c_test_str, t_sec, t_nsec)
    return (res == expected, res)

expected = b"zrkpfemugjxwcdtolbyvihsnaq"


sec_guess_start = 51446
nsec_guess_start = 724446569
print(test_seed(sec_guess_start, nsec_guess_start, expected))
# print(test_seed(sec_guess_start, nsec_guess_start, expected))
# print(test_seed(sec_guess_start, nsec_guess_start, expected))
# print(test_seed(sec_guess_start, nsec_guess_start, expected))
# print(test_seed(sec_guess_start, nsec_guess_start, expected)) takes about 6.5 seconds

# for j in range(2):
#     for i in range(1000):
#         res = test_seed(sec_guess_start + j, nsec_guess_start + i, expected)
#         if res[0]:
#             print(res)