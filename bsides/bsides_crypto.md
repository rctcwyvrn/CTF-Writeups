Bsides Ottawa crypto challenges

---



blah blah blah ctf writeups need to format this better for when I submit this to the website



These were by far the best cryptology challenges I've had the pleasure of doing in a CTF. They were fun, difficult, unique, and very rewarding. In hindsight, there really wasn't any close staring at the code for bugs or googling for similar problems in past CTFs for any of these challenges. Most of them were just good ol' math, and not extremely difficult math either.



I'm rambling, but they were really really good challenges, and I had a ton of fun. So much fun that I accidently missed out on some talks I had wanted to attend. But hey I solved all the crypto and our team got 5th so that's something right?



Anyway, on with the writeups



## Squared away

### Flag 1 (150 points)

Definitely the easiest crypto challenge of the 4, but still a fairly high point value.



The challenge is to decode a ciphertext for the [Rabin cryptosystem](https://en.wikipedia.org/wiki/Rabin_cryptosystem) given a decryption oracle. The catch is that it won't let you submit the encrypted flag itself, but it'll happily decrypt everything else.

The attack is then very straightforward, since Rabin is "just RSA with e=2" for the purposes of this challenge, we can apply the same kind of attack we would use for a similar problem in RSA, namely a [blinding attack](https://cryptopals.com/sets/6/challenges/41). We can just send the ciphertext C multiplied by 4, which will decrypt to the plaintext (which is the flag) times 2. So just multiply the thing we get back by inverse(2) mod n and we get our flag.



<insert flag here>



### Flag 2 (200 points)

This one was much tougher to crack since it had a major red herring. The challenge was to factor the modulus and the server ran it's own prime generation algorithm, which made it seem like that was the vulnerability was hiding.



But nope, the vulnerability was actually Rabin's inherent weakness to chosen ciphertext attacks. Since I couldn't find any well documented guides on how to pull off this attack, I'll try to explain it in detail.



How does Rabin work?

1. Generate two primes p and q that are both 3 mod 4 
2. Encrypt using pow(m,2,n)
3. Decrypt using some math magic to generate the 4 valid square roots of m in the modulo integer ring
4. Return the root that resembles the message



The "resembling the message" part is done by adding some redundancy to the message before encrypting

1. Take the message you want to encrypt
2. Append on an copy of the last byte
3. Then encrypt it by doing pow(m,2,n)
4. When decrypting, return the root that has a duplicated last byte (after stripping off the redundancy)

**Note: This is not the standard way to do redundancy, you'll see why in a second**



Why do we need to make sure that we return the correct root? **Because if we don't and return all 4 roots, then anyone can factor the modulus.**



god im too lazy to relearn how to use latex

Assume we have our first two roots, x and -x mod n 

x^2  = S + n*j



And we can convince the server to return us the other two roots, h and -h mod n

h^2 = S + n*k



Then

x^2 - h^2 = (j-k)*n

(x+h)(x-h) = (j-k)*n



And we know that n is the product of exactly 2 primes, so a simple gcd between x+h % n and n gives us one of our primes.



**So how do we trick the decryption oracle into giving us h?**



If we give it x^2 mod n where x is properly redundant, then we just get x back.

If we give it x^2 mod n where x is not properly redundant, then we get usually get an error message because the server can't find a redundant root.



But there's the trick, we only **usually** get an error message back. We sometimes choose an x that doesn't have the redundancy property, but x^2 mod n happens to have a root that does have the redundancy property, in which case the oracle happily gives us that root (with the redundant byte stripped off). This happens reasonably often because of how weak the redundancy property is, in standard operation the last 64 bits, or 8 bytes get duplicated, instead of just 1 byte.



So all we have to do is send random x^2 mod n's until the server responds with a non-error.

This means that either:

1. We accidently hit an x that has the redundancy property and we get x back, in which case we just keep going
2. We hit an x^2 mod n that has a root h with the redundancy property, and the server returned us h with the redundant byte stripped off 

In the second case all we need to do is to re-add the redundant byte and calculate the gcd to get our factors!



<insert flag here>



Note: I figured out the last half of the solution in the last 15 minutes of the CTF. I got my first valid h about 5 before the end and submitted the flag as the organizers made their way to the front to close off the event. Talk about cutting it about as close as physically possible lol.



## Meme generator (200 points)

**Credits for the solve to Xander** (I really hope I didn't remember/spell your name wrong...)

This one was another one with red herrings. An RSA signing forgery challenge that doesn't involve Bleichenbacher's e=3 attack? Impossible!!



So here's the challenge:

1. We can submit left and right text to the meme generator, which gets added to a bash command to generate the meme.
2. This command gets signed and sent to the server
3. The server verifies the signature and runs the command if it is valid
4. The result of the command (which is usually the image bytes) gets base64'd and sent back to the webpage.



The details:

1. e=65537
2. Self implemented PKCS1.5 padding
3. Signature check is done by calculating the signature from the message, and comparing to the one that was given. This cuts out the aforementioned Bleichenbacher attack since the entire signature is checked, and also cuts out any padding oracle attack since the padding validity is never checked on it's own
4. 2048 bit RSA
5. Prime generation from a crypto library



If you've looked at the challenge code yourself, you might be wondering why I bothered listing out all these small details and other attacks when there's obviously something weird in the padding function.

```python
def _hash(message):
    return hashlib.sha256(message).digest()[0:6]
```



The hash is only the first 6 bytes! We can just manipulate the hash of the command with our inputs until we hit a collision between the command's hash and the hash of, lets say, `ls | xargs cat`.



One slight problem, brute forcing 6 bytes is still on the order of 2^48, much too high for pedestrian hardware. So thinking this was a dead end, I moved on to try and find vulnerabilities elsewhere, leading to the list details that I had up there and eventually to me just giving up. However one of my teammates figured out the correct approach, the birthday attack.



The birthday attack is just a cryptographic attack using the birthday paradox as it's basis. Google "Birthday paradox" if you don't know what it is, there's hundreds of people who have done a better job explaining it than I could (also I'm lazy). 

But how do we apply it to colliding hashes? Much like how the chance of finding a birthday pair is surprisingly high given a small n, we can make the probability of a collision between two groups of hashes surprisingly high given a small set of hashes. 



Here's how:

1. Generate a big list of hashes (ideally 2^24 but we managed with a much smaller list) that you want to find a collision against. In our case we used `ls | xargs cat; echo <random ascii letters>`
2. Start generating hashes for values that you can control, in our case this would be hashes that we could get out of valid inputs to the meme generator.
3. Continue until you find a collision between the hashes from 1 and a hash from 2.



But wait, how is that any faster? Think about each hash that you generate in the second step. Each one gets compared against 2^24 hashes, meaning on average you only need to generate 2^24 hashes in the second step to find a collision (2^48 total comparisons). 

So we expect to only generate 2 * 2^24 hashes, and since creating a hash is a lot more time consuming than just comparing two hashes, our much lower # of hashes makes the collision finding much much faster. So now all that's left is to find collisions for the commands we want to execute and voila! Flag!

`flag{48_b1ts_sH0u1D_b3_en0ugH_f0R_4ny0n3}`



## Old school (400 points and a prize for first solve)

*The one that most people reading this writeup are actually interested in.* 

Some context, this challenge was the only challenge worth this amount, I think the next highest was 300? Even so there weren't very many above or at 200 at all, most challenges were in the 50-150 point range. And to top it off, the first solver would be awarded a mysterious prize, which ended up being a [Hak5 WiFi Pineapple nano](https://shop.hak5.org/products/wifi-pineapple)!

Now I'm telling you this because I want to show off how cool I am for being the first solve and being only one of two teams that ended up solving this challenge, but really me winning the prize was me getting lucky. They actually doubled the point value and announced the prize on the morning of the second day, and lucky me decided to work on this challenge for most of the first day and had gotten the flag right after the event had stopped on the first day. So I got to walk in on the second day and collect my 400 points and my prize!



The challenge itself was actually relatively straightforward in terms of what we had do. We're given a decryption oracle that runs NDS, New Data Seal. Our job is to decrypt the given ciphertext. Like **Squared Away 1** , the oracle does check if we try to submit a block that matches the ciphertext but this time we can't do any blinding tricks.



So what is the algorithm we're dealing with here? [New Data Seal](https://en.wikipedia.org/wiki/New_Data_Seal) is a [Feistel cipher](https://en.wikipedia.org/wiki/Feistel_cipher) based symmetric encryption algorithm that was developed at IBM at around the same time as [DES](https://en.wikipedia.org/wiki/Data_Encryption_Standard). The short Wikipedia article actually gives us only bit of intel that we need to get started, NDS is vulnerable to a type of attack called a [slide attack](https://en.wikipedia.org/wiki/Slide_attack) (NDS was actually the cipher that this attack was first demonstrated with!) .



### Slide attacks???

What is a [slide attack](https://en.wikipedia.org/wiki/Slide_attack)? **I barely understand it myself since I didn't bother trying to find a textbook with a proper explanation**. I can try to explain the high level idea though. Most modern symmetric ciphers (eg AES and DES) are based on [rounds of substitutions and permutations](https://www.youtube.com/watch?v=O4xNJsjtN6E). 

Each "round" of the cipher usually consists of something like

1. Adding the key to the ciphertext (eg using XOR)
2. Substituting
3. Permutating

For example in AES each round a key gets mixed in, some bytes are substituted using an s-box, the "rows" are shifted, and then the "columns" are mixed together. The goal is to mix the key into each round such that it's difficult to figure out where bytes of the plaintext and bytes of the key end up in the final ciphertext. This is made especially difficult when the # of rounds is high, so even if you can figure out some properties after one round, after 16 rounds all traces of them are ([hopefully](https://en.wikipedia.org/wiki/Differential_cryptanalysis)) gone.



So what is a slide attack? A slide attack accomplishes the goal of **not having to worry about the number of rounds**, and instead focus on brute forcing out what happens during one round, or more specifically one key cycle.



After like 3 paragraphs, here's the one line answer to what a slide attack is:

Let F be one or multiple rounds of a block cipher where after F rounds the key that gets "mixed" in is the same as the one in the first round. For the sake of simplicity (and since NDS has a cycle count of 1 anyway), we're going to assume F represents one round of the 16 round cipher.



So we can represent the encryption function E as just F(F(...F(plaintext)...)), as 16 individual rounds. From this representation **we see that F(E(ptxt)) is actually equal to E(F(ptxt)).**

**Slide attacks are attacks abusing this property of block ciphers to completely ignore the problem with the number of rounds.** Since people at the time believed that more rounds would solve all of their problems (cough cough triple DES), this type of attack was (probably? I have no idea but it seems like it was) very important.



### The actual attack on NDS

Theory out of the way, what's the attack?

NDS is a Feistel cipher as mentioned before, which means in each round you

1. Split the block in half
2. The new left block is the old right block
3. The new right block is  = old_left XOR F(old_right, key)



Where F is that round function I mentioned before. What is F in NDS?

NDS's round function F:

1. Takes the first bit of each of the bytes in the 8 byte input (NDS has a 16 byte block size, so old_right is 8 bytes)
2. Converts it to a number i \in [0:255] and take the ith byte of the key (NDS has a massive 256 byte key)
3. Uses that byte of the key in some complex permutations and stuff that you don't need to worry about



**How do we use the slide attack property to recover the secret key?**

The idea is that we can guess what a byte of the secret key is, and know if we were right or not by looking at what the decryption returns.

1. Send the server the message M to get E(M)
2. Guess that the secret byte that get's used in the first round is b
3. Calculate F(M) using that b
4. Send F(M) to the server to get E(F(M))
5. Compare E(M) and E(F(M))

We know that if we guessed b correctly, then F will correctly simulate the first round of the cipher, which means F(E(M)) will be E(F(M)). But to calculate F(E(M)) we would need another F function and another key byte guess...



BUT we have a Feistel cipher, and we know that only half of the block actually uses the key. This means we can check if F(E(M)) == E(F(M)) while only having to guess one byte of the key at a time!

1. Guess a key byte and use it for calculating F(M)
2. If it was correct then we should see that E(M) is one round behind E(F(M)))
3. In the context of a Feistel cipher, **one round behind means that the right block of E(M) is equal to the left block of E(F(M))**



So all we need to do is to do that for each guess b until we hit one that has that right block left block match, and then do that for every single one of the 256 key bytes and we have our entire secret key!

<insert flag here>



Note: We want to control which byte of the key gets used in the first round so we need to choose our message carefully. If we want to get the 14th byte of the key, then we want the first bits of the 8 bytes on the right to be 00001110, so we send a message of 

`<whatever 8 bytes you want> || \x00\x00\x00\x00\x80\x80\x80\x00`

This guarantees that the first round of NDS will use the 14th key byte, so once we find our slide pair (? not sure if that's a slide pair but w/e) we know that we just found the 14th key byte.



Thanks to Julie for finding some [random university notes](http://anthony-zhang.me/University-Notes/CO487/CO487.html) that I was able to slowly figure out the attack from. (ctrl+f "new data seal" to find the section)

I just randomly found [this presentation](http://www.cs.haifa.ac.il/~orrd/BlockCipherSeminar/NadavGreenberg.pdf) that I wish I had found during the CTF, but oh well. Gonna read it later, seems like a much better general explanation of slide attacks. Hopefully it doesn't show that I have no idea what I'm talking about.





Anyway that's it. Try the old school if you have time, it's a good exercise I think. (Or do [cryptopals](https://cryptopals.com/)!)