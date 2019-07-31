Cryptopals set 1: The qualifer
===
Writeup by rctcwyvrn

Hi, a simple writeup for the cryptopals set 1 challenges for the crypto noob from a crypto noob. There are plenty of other tutorials, so look for a better one if this one makes no sense

This is gonna mostly be a tutorial for how to do this byte stuff in python, which is really unintuitive to me anyway


*NOTE: Some of the most trouble I had in these challenges was getting the data to the right types, and it involved lots and lots of stackoverflow and following other guides, remember there's no shame in doing that and don't feel bad when you see your 10th TypeError in a row*

Challenge 1: Convert hex to base64
---
For this challenge you just need to know how to do this stuff in python, I used the codecs library

Decode: Some encoded format like hex or base64 or ascii --> bytearray
Encode: bytearray --> Some encoded format like hex or base64 or ascii

So following the hint you convert like this: hex -> bytes -> base64

Here's some examples for how it works

def hex_to_bytes(hex_in):
	return codecs.decode(hex_in, 'hex')

def base64_to_bytes(hex_in):
	return codecs.decode(hex_in, 'utf-8')

def bytes_to_hex(byte_in):
	return codecs.encode(byte_in,'hex').decode()


Challenge 2: Fixed XOR
---
For this one you want to use python's ^ operator, which acts on two bytes and returns the logical XOR
So the steps are
1. Convert both hex strings to bytes
2. Create a new bytearray for the output
3. Loop on the bytearrays for the two input strings
4. Append the result of ^ to the output 
5. Encode the output bytes back to hex (im too lazy to check if i actually have to do this)


Challenge 3 Single-byte XOR cipher
---
I see why these are in order now...
Theoretically it's not hard, the problem for me was getting the stupid python syntax correct...

Here's the framework
1. Convert to bytes as usual
2. Loop from 0 to 255 to loop over all the possible single chars
3. Do a single-byte xor on each of those, here's code from the tutorial I found 

def single_char_xor(in_raw, char_val):
	output_bytes = b''
	for byte in in_raw:
		output_bytes+=bytes([byte ^ char_val])
	return output_bytes

Source: https://laconicwolf.com/2018/05/29/cryptopals-challenge-3-single-byte-xor-cipher-in-python/ 

For all the other python things, follow along with laconicwolf and google. I'll lay out the rest of the framework, I would recomend just trying it from here and referring back here when you get stuck

1. Calculate a "english_score", using something like this https://en.wikipedia.org/wiki/Letter_frequency to determine if something is a phrase or not
2. Create a dictionary of score/bytearray pairs and sort them to find which bytearray has the best score

Since the best score = most like an english phrase, the key that makes the best english phrase is (probably) the best key. So thats it!

Challenge 4 Detecting single-byte XOR cipher
---
It's challenge 3 but literally just more

1. file = open("data.txt")
2. Loop through the file line by line by using python magic, for line in file: detect_single_char_xor(line), where that function is your code from Challenge 3
3. Do the same sorting proccess as challenge 3 to again which determine which bytearray has the best score

Now the party is really going!

Aside 1: Converting plaintext strings and chars to bytes
---
1. Declare an empty list, I called mine temp
2. Append [ord(char)] for each char in the plaintext to temp
3. my_bytes = bytes(temp)

ord converts a char to it's byte value, so we just make a bytearray of the bytes and we have the string in it's bytes for us to mess around with!

Aside 2: Having an empty bytearray to start appending bytes to
---
1. Literally just output_bytes = b''

What the hell python, how is this legal. You can redo the code from aside 1 with this new information btw


Challenge 5: Repeating-key XOR
---
Mostly a combination of what we've seen already, I would reccomend making sure you can do this on your own before reading any guides, since it should be mostly copy paste from challenges 3 and 4
1. Take the key and plaintext
2. Convert the plaintext into bytes
3. Loop over the bytes and append on bytes([ord(key[count]) ^ byte]) where count is incremented and modded over the length of the keystring
4. Return and you're done!

Challenge 6: Break repeating-key XOR
===
The big bad!

Part 1: Hamming distance function
---
List of mistakes I made along the way
1. You want to compare bits, not bytes, so convert the byte (which is really just an int) into a string of bits (Stackoverflow it, no shame in doing so)
2. The bits may not have the same length, so you need to add the distance between their lengths to the dist
3. Make sure you are indexing the string in the right direction
4. Make sure not to index off the end of the bit string


Part 2: Rest of the fucking owl
---
Honestly I don't know how my code managed to be bug free, but it somehow was...

Here's the functions I used:
1. hdist(bytes1,bytes2), hamming distance function
2. take_block(in_bytes, a, b), returns the bytes from a to b
3. blockify(in_bytes, block_size), converts the bytes into a list of block_size sized bytes
4. transpose(blocks), takes the list from blockify and transposes it as detailed in the challenge (step 6)
5. break_repeating_key_xor(enc_bytes, guess_len), the big boi

hdist was explained in part 1 and the other functions are fairly self explanatory except for 5.

Here's what break_repeating_key_xor() did:
1. Loop over keysizes from 2 to guess_len
2. Break the entire...
As I was writing this I realized that I just rewrote the code for blockify(), basically line for line...
2. (revised) Call blockify to create the list of blocks
3. Use some nice python magic to make a list of all the dists for all the combinations of two blocks
4. Sum it up and normalize it by the length of the list and the key_size
5. Add it into the list of potential key_sizes
6. (out of the key_size loop now) Sort the list
7. Blockify by the optimal key_size
8. Transpose them
9. Call break_single_byte_xor() from challenge 3 to get a single-byte key
10. Put em all together, use chr() to convert them back to ascii and you get your final key!

Key = {Terminator X : Bring the noise}
My code is available, but I would really not recommend comparing your answer to them as I am fairly inexperienced in writing _good_ python code, I write _just barely good enough_ python code. There's defintely one or two off by one bugs in my code too.

Challenge 7 AES in ECB mode
---
I'm stupid and didn't read the instructions, do this in code because you'll need it alot later. I used pycrpyto

Challenge 8 Detecting AES in ECB mode
---
The main part of the challenge is figuring out how to actually detect ECB encryption, and the hint isn't super helpful.

The idea is that if there is a duplicate 16 byte plaintext in the original message, then it will also be duplicated in the ECB. But why we can assume that there is duplicated plaintext is beyond me...
Here's what I followed: https://crypto.stackexchange.com/questions/20941/why-shouldnt-i-use-ecb-encryption 
and https://obrien.io/writeups/crypto/2018/02/01/cryptopals-set-1-writeup/ to check my answers

Anyway you want to do the type wrangling you're probably used to now
1. Open the file
2. lines = f.readlines()
3. for line in lines
4. unhexlify(line.strip()), the strip() is important! Don't be dumb like me and forget it
5. Append those onto a new list enc[]
6. Loop through enc and call is_ecb() on them until it finds something

is_ecb() is easy once you understand how to actually detect ecb
1. Find the # of bytes in in_bytes
2. Find the # of bytes in in_bytes without duplicates
3. If they're the same length then it's not ECB, but if the second is smaller then it's probably ECB encoded

The answer doesn't seem to be something that's "obviously correct" like in the earlier challenges, but I'm reasonable sure my code is correct.



And that concludes Set 1! Pretty fun but also defintely frustrating at times when you get nothing but TypeErrors for 20 minutes straight trying to convert the input to what you want.
Set 2 coming soon _tmtm_




Set 2
===

Challenge 9: PKCS#7 padding
---
Fairly straightforward. Helpful tip: bytes([number]) will make bytes like b'\number' for the padding

Challenge 10: CBC mode
---
AES is how the actual encryption/decrpytion happens
ECB is the function from set 1 that takes 16 bytes and a key to encode/decode
CBC then extends that to arbitrary length as long as its multiples of 16 bytes long

Honestly the hardest part was understanding what the challenge was even asking for
1. Take the file
2. Decode into bytes
3. Split into blocks of size 16
4. Take the first block and decode it with AES with the key
5. XOR that with the IV, append it to the return
6. Repeat except XOR the each decoded block with the previous block, not decoded, also append it to the return

_play that funky music_

Challenge 11: Oracle
---

This one was fairly straightforward, write the oracle as they describe and use the same ECB detector from earlier challenges

Challenge 12: One byte at a time (easy)
---

This one looks straightforward at first, and it kind of is. Getting the first byte is easy but the harder part is getting your code to automate the process for going through the rest of it

General description of my code:
1. Start with sending 15 bytes of A's 
2. Get a byte of the secret by sending 15 A's and a guess
3. Send 14 A's 
4. Get the next byte of the secret by sending 14 A's + the byte of the secret you got earlier + a guess
5. Repeat until you get a full 16 bytes of the secret
6. Loop back to sending 15 bytes of A's
7. Get the next byte by sending 15 A's + 16 bytes of secret + a guess
8. Remember to compare against the second block now

So by pure luck I managed to get this all packaged nicely into two for loops, good luck!

Challenge 13: ECB Cut and paste
---
The title is a pretty big hint, the idea is that you want to copy over some ciphertext of what you want and paste it in

So
1. Make a bogus account that you're going to edit admin into, make sure that the role part is in its own block
2. Make a second account with admin in it's name where the word "admin" is at the beginning of a block
3. Cut the block from the second ciphertext and paste it into the second
4. ???
5. Profit!


Challenge 14: Byte at a time (harder)
---
I got stuck on this one for awhile because I wasn't sure how difficult the challenge was supposed to be.
1. Is the prefix length random for each time you call the oracle?
2. Are the prefix bytes random for each time you call the oracle?

I wrote my solution assuming no to both of those. The only real change from challenge 12 is that you need to find the prefix length first and change your first block accordingly

To find the prefix length just send A's of increasing length, eventually the first block will go from
prefix + A's + first byte of secret to
prefix + A's

And then after that the first block will stay constant, so just look for when the first block starts to be the same as the last and you get your prefix length

Ideas for the harder version:
If prefix length and value was random each time the problem is that you need a method of determining prefix length given any ciphertext
If only the length was random then maybe if you could manage to get the prefix, maybe something like sending 20 A's and always looking at the first block and then just copy pasting that onto future blocks?

Challenge 15: Padding verifier+stripper
---
Easy peasy?

Challenge 16: CBC bitflipping
---
Imagine ciphertext with blocks A,B,C...

Remember that CBC decrypts block B by putting it through AES decryption, lets say decrypt(B) = x, and then xors it with the previous ciphertext A
So if we have a block of encrypted "A"s in B then we just need to modify the block A so that when it gets xor'd with x it becomes ";admin=true;"

x XOR A = "AAAAAAA"

We can change ~~reality~~ A to be whatever we want since we have access to the ciphertext,
*snaps fingers*
Now A is replaced with A xor ";admin=true;" xor "AAAAAAA"

So when CBC decrypts it the first block becomes jarbled, but when it does the second block

x xor A xor ";admin=true;" xor "AAAAAAA" 
= "AAAAAA" xor "AAAAAA xor ";admin=true;"
= ";admin=true;"

And we're in!

Set 3
===

Challenge 17: Padding oracle attack
---
https://en.wikipedia.org/wiki/Padding_oracle_attack
The idea is that since the server/function you're attacking will tell you if padding is valid, try random things until you end up with a last byte of \0x01, which will return as proper padding


Ciphertext blocks = c1 c2

So you can mess with the ciphertext however you want, completely rewrite c1
Let c1 = 15 * "A" + a random int i

Now trace the CBC decryption process, c2 -> intermediate 2 using AES
Then intermediate 2 xor c1 = plaintext block

The idea is that you can now just try random ints i until the plaintext block ends in \0x01, and the oracle will tell you because it'll be the only attempt that results in valid padding

So now you know i XOR last byte of the intermediate = \0x01, so last byte of the intermdiate = \0x01 XOR i, and you just stole a byte of unencrypted intermediate
To get the plaintext you just xor it with the original ciphertext as part of the normal CBC proccess

Much like earlier challenges, this attack is not theoretically difficult but it is very hard to get working correctly in actuality. Some tips:
1. Print statements everywhere
2. Start with just the loop for finding one byte, then make it work for 16 bytes, then make it work for all blocks
3. The very first block of the ciphertext is tricky, you can either mess with the IV or make a reordered ciphertext like I did
4. Like the hint says, the fact that the actual plaintext is padded is actually completely irrelevant. Make sure you understand why this is before moving on, it's an important conceptual link.

Pitfalls:
1. Make sure that you are generating the correct bytes in c1 for the bytes that you already know the intermediate values of
2. Make sure your verify+strip function from set 2 is bugless, it should accept a block that is all padding but reject a block with no padding
3. A general coding tip but you should try to keep your eventual goal in mind as you build up the function
4. You decrypt the bytes in reverse order, so make sure you account for that
5. At the very end remember to XOR the intermediates with the IV + cipher_text

Challenge 18: CTR Mode
---
The wikipedia article for CTR mode gives a good explanation, and overall CTR mode is very simple, just don't be dumb like me and get your key and block reversed
https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)
Also remember to use little endian versions of the nonce and counter: https://en.wikipedia.org/wiki/Endianness#Little-endian , if you don't know it basically means the bytes are stored in reverse order of what we expect; least significant bytes first.

Challenge 19/20: Breaking a constant nonce CTR
---
I'm not sure what they wanted for challenge 19, I just wrote the code for what I thought they wanted me to do and ended up doing challenge 20...
I went straight for the way we broke repeating key XOR in set 1, where you guess all possible bytes it could be and generate a score from the resulting XOR's

Also this is the first challenge so far where the first time I ran the code it worked! Congrats to me!!!

Challenge 21: Implementing some PRNG
---

I didn't like this challenge at all to be honest, I understand wanting us to learn how the twister worked but just copying down some psuedocode doesn't really do that.

I just traced the algorithm a few times and then copied the code from someone's solutions

Challenge 22: Break time seeding PRNG
---

Fairly straightforward, just try all the seeds near the current time and you'll find one that matches

Challenge 23: Untemper and clone MT
---

This one was not coding difficult, but was a bit mathematically tricky to understand.

Looking at the last tempering, y =x xor (x>> 18) we can get the general pattern for how we want to solve these.

y gets shifted right by 18, so the largest 18 bits of y must come directly from x, then the smaller bits of y come from x xor x >> 18. We can then recover x one bit at a time because 

x_n = y_n xor x_(n-18) n=18...

And it turns out this approach works for the other type of shift and also the ones with & so yay

The cloning part is simple, just make a constructor that takes a MT state array instead of a seed

Challenge 24: Write the MT stream cipher and break it
---
Writing the cipher: straightforward  
Breaking it: Not obvious but it turns out that 2^16 keys isn't that many keys, and testing them is very quick. So you can literally just test all the keys  

Very unclimactic....

You can modify the function to look for whatever you want, I made it look for things that looked like english sentences.


Set 4 
===

Challenge 25: Break read/write AES CTR
---
Tldr; don't let people mess with ciphertexts in any way

So we can change the plaintext to say whatever we want, so why not make it all 0's? If it's all 0's then the ciphertext will just be the keystream, and with the keystream we can just xor it with the original ciphertext

Challenge 26: CTR bitflipping
---
The function will remove all ;'s and ='s so we need to trick it into encrypting something that has the admin token, which is very simple because CTR just uses XOR

let x = admintoken
y = AAAAAAAAAA

1. Send the function x XOR y, which will just be random garbled text
2. It'll encrypt it and send back x XOR y XOR stream
3. Take the ciphertext and XOR it with y again to get x XOR stream
4. Send back x XOR stream to the decoder, which will happily decode it back to x
5. Profit!

Challenge 27: Steal the key from IV=Key CBC
---
Why would anyone do this...but I bet the cryptopals team have seen this enough which is why it's here but still.

The instructions actually give a very detailed explanation for the attack, nothing much that I really want to add. Go back to the wikipedia article if you've forgotten exactly how CBC works. Make sure you understand why the attack works instead of just copying the instructions!

Challenge 28: Implement a SHA-1 MAC
---
The implementation I used: https://github.com/ajalt/python-sha1

For the fellow crypto noob, MAC stands for Message Authentication Code. The idea is that the hashing function (sha-1) takes the message+key and generates a hash. The important part of this hash is that small modifications to the resulting hash do not correspond in any way to small changes to the plaintext that was sent, so no bitflipping attacks or anything like that.

So in an actual setting:
1. Alice and Bob share a key
2. Alice tells Bob she is sending message X
3. Alice sends Bob sha-1(key+x)
4. Bob recieves the hash and compares it with his own sha-1(key+x), and if they match then he authenticates her

I'm guessing the messages x would all be something like "auth=____" with user/admin/whatever and Bob would just try them all until one worked, and then give out the proper authority. So to cheat this we need to be able to send fake hashes without knowing the key, which seems impossible at first beause a small change in input results in a completely different hash output.

SHA stands for secure hash algorithm, so it's probably safe right?

Challenge 29: Break SHA-1 Keyed MAC
---
Oh... "Secret prefix SHA-1 MACs are trivially breakable"

I sort of fumbled my way though this one, and the instructions are super not helpful

Useful information:
1. SHA-1 works kinda like the twister from earlier, it has an internal state which it uses to generate it's result. So if we know the state we can generate more, which is why we need to do the same thing as the fake_twister where we could plug in the entire state array and use that as a clone, except this time we use our clone to generate a longer hash which includes our secret sauce

Here's how SHA works (kinda)
1. Take an input and turn it into bits
2. Append a 1
3. Append 0's until the length is 448
4. The length of the message is converted into 64 bits and added to make a mod 512 == 0 bit message
5. Each 512 bit chunk is then put through the hashing function with an internal state, the state updating for each block
6. At the very end it returns the state variables concatenated together

So since each 512 bit chunk is done seperately, if we can make a sha-1 clone that has the correct state of just finishing the last block of the original message, we can continue on and hash whatever we want

So the plan is
1. Get state from hash, which coresponds to hashing key+message+padding
2. Create a fake sha-1 with that state
3. Ask the fake sha-1 to hash a ;admin=true; token
4. The result turns out to be the same as if you asked it to hash key+message+padding+token, which is exactly what we wanted

I was confused for a while about why we needed to go through the hassle of generating the padding, it's so that we can check to make sure that the hash is what we wanted, and for literally no other reason. We can generate the fake key+message+padding+token but if we wanted to make sure its right we need to actually hash key+message+padding+token


Challenge 30: Break MD4 Keyed MAC
---

Almost identical to challenge 29, but the padding for MD4 uses a little endian representation of the msg length, not big endian like SHA-1

Challenge 31: Artificial timing leak HMAC-SHA1
---
So the main hint for this challenge comes from the aptly named insecure_compare function. How can we exploit the fact that it compares one byte at a time and delays?

The idea is that we can just try all the possible first bytes, and for one of them the insecure_compare will find one correct byte and delay once, and for the rest it won't delay at all.

The plan:
1. Guess a byte
2. Make known_signature + guess
3. Pad it out to 40 bytes
4. Send it and record the time taken
5. Floor time_taken / delay to get the number of successful compares that insecure_compare did
6. If that's greater than what we already have then add it on to known and loop

This one takes forever to run on the default 50ms delay though, my solution worked until 20ms delays so I would try running that first

Challenge 32: Less artificial timing leak
---
How to make the attack more consistent? Replace step 5 because the delays are too small to really be consistent, instead just make a list of all the times and take whatever guess caused the longest time. Also running each guess 3 times and taking the average probably helps.

My solution worked for 5ms delays but not really for anything less. Maybe taking the 10 longest times and running them all 10 times each, then taking the longest time out of that to be the best?


Set 5 Diffie Hellman and friends
===

I went through these challenges super quick, and most don't really need any sort of hints or explanation so I'm gonna do them rapid fire

Challenge 33: Just follow the instructions  

Challenge 34: Do the math, think about what each side is going to generate their secret to be  

Challenge 35: Again, do the math and figure out what the S is (or could be). Remember as the man in the middle you can send _anything_  

Challenge 36: Just follow the instructions. If you have no idea how to setup a login server like me then you want to use socketserver, look at my srp_server.py for details  

Challenge 37: I don't know what they meant by &c either, maybe just a constant times n? You get the idea by now  

Challenge 38: This one was weird, just a brute force attack using common words  

Challenge 39: Use Crypto.Util.number to generate primes and do invmod

Challenge 40: Mathematical basis of the black magic that is [the chinese remainder theorem](https://crypto.stanford.edu/pbc/notes/numbertheory/crt.html)