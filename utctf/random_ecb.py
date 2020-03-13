#this is just gonna be the byte-at-a-time attack
# we know the flag is 15 bytes from sending single letters, so let's use it to our advantage
import server

#context.update(arch='amd64', log_level='debug')

from pwn import *
s = remote("ecb.utctf.live", 9003)
s.recvuntil("Input a string to encrypt (input 'q' to quit):")

def send(pkg):
	#print("package =", pkg)
	res = set([]) # pair of results, because sometimes we get random bits
	while(len(res) < 2):
		s.send(pkg+"\n")
		val = s.recvuntil("Input a string to encrypt (input 'q' to quit):")
		res.add(val.split('\n')[2].strip())

	return list(res)

#def send(x):
#	return debug_send(x)

def debug_send(pkg):
	print("debug package =", pkg)
	res = set([]) # pair of results, because sometimes we get random bits
	while(len(res) < 2):
		res.add(server.encode_me(pkg))
	return list(res)


flag = ""
for index in range(31):
	print("finding flag char at index = ", index)
	# get the first byte of the flag by sending a set of 15 A's and then 15 A's + random guesses

	if index <=15:
		goals = [x[:32] for x in send("A"*(15-index))]
	else:
		goals = [x[32:64] for x in send("A"*(31-index))]
	poss = []
	for i in range(32,127):
		if index <=15:
			x,y = send("A"*(15-index) + flag + chr(i))
			poss.append((chr(i),x[:32]))
			poss.append((chr(i),y[:32]))
		else:
			x,y = send("A"*(31-index) + flag + chr(i))
			poss.append((chr(i),x[32:64]))
			poss.append((chr(i),y[32:64]))


	print("goal = ", goals)
	tried = set()
	found = {}
	blacklist = []

	for char,guess in poss:
		if guess not in tried and guess in goals and guess not in blacklist:
			print("found it!",char, guess, goals)
			found[guess] = char

		if guess in found and found[guess] is not char:
			print("found repeat solution =", char,guess, goals)
			found.pop(guess)
			blacklist.append(guess)

		tried.add(guess)

	if len(found) != 1:
		print("no find :c")
		print(goals, found, flag, index)
		asdf()
		#print(set(poss))
	else:
		print("found = ", found)
		flag += list(found.values())[0]
		print("flag = ", flag)

#utflag{3cb_w17h_r4nd0m_pr3f1x}