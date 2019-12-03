# Python bytecode 2.7 (62211)
# Embedded file name: ./encoder.py
# Compiled at: 2019-10-10 13:14:05
# Decompiled by https://python-decompiler.com
import base64, sys
from random import shuffle

def encode(f, inp):
    s = string.printable
    init = lambda : (list(s), []) #init is a function that returns s as a list and an empty array?
    bag, buf = init() #bag = list(s), buf = []
    for x in inp: #inp = base64 of input file, so for each base64 char in the file
        if x not in s: #if its not in s, then skip it -> if it's not a printable string then skip it
            continue
        while True:
            r = bag[0] 
            bag.remove(r) #r starts at the first printable string and moves down
            diff = (ord(x) - ord(r) + len(s)) % len(s) #diff = 0 iff ord(x) - ord(r) == 0 mod len(s), so if it equals 0 , len(s), -len(s) etc
            if diff == 0 or len(bag) == 0: #diff = 0 or out of chars in bag
                shuffle(buf) #shuffle, before this buf = [a diff # of '0's, a diff # of '1's etc]
                f.write(('').join(buf)) #write buf
                f.write('\x00') #null terminated sections
                bag, buf = init() #restart
                shuffle(bag) #shuffled bag this time though
            else:
                break

        buf.extend(r * (diff - 1)) #add the char r, diff -1 times to the buf that's gonna get written later
        f.write(r) #once the diff is nonzero, write r to the file

    shuffle(buf) #shuffle the buff
    f.write(('').join(buf)) #write again with no null termination, this is the last section


    #file structure:
        #null terminated blocks, where each is made up of
            #chars r where the char x had a non-zero diff with r
                #these chars come in random order from string.printable
                #same with x
            #the buf then gets diff - 1 entries of r
            #then once either the bag runs out of chars, or there's one with a diff of 0 (r = x is the simplest case)
                #then we finish the block with the shuffled contents of buf

    #to decode:
        #need to figure out what each x is, can determine this from what diff and r were
            #determine diff[r] by looking at the shuffled buf section
                #just look at how many times r appears in buf
            #determine order of x and r by looking at inital written char r before shuffled buf section
                #loop through pre and undo to get x from diff[char] and char

    #THE NEXT SECTION STARTS WITH THE CHAR THAT CAUSED THE DIFF = 0 IN THE LAST SECTION!

    #to determine the startpoint of buf (general case):
        #the start of buf MUST be a duplicate and must be the first duplicate
            #need proof for that heh

            
    #to determine the startpoint of buf (first section only):
        #look for the value in the section with the largest value (in string.printable), that must be the farthest it got because otherwise it wouldnt ahve been written or a part of buf

if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as (r):
        w = open(sys.argv[1] + '.enc', 'wb')
        b64 = base64.b64encode(r.read())
        encode(w, b64)