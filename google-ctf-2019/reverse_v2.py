import random, itertools
import subprocess
def step_automata(state):
	next_state = ""
	for i in range(len(state)):
		L = state[(i-1) % len(state)]
		C = state[i]
		R = state[(i+1) % len(state)]
		if(L == "0" and C == "0" and R == "0") or (L == "1" and C == "1" and R == "1"):
			next_state+="0"
		else:
			next_state+="1"
	return next_state

def step_automata_ignore_edge(state):
	next_state = ""
	for i in range(len(state)):
		if i != 0 and i != len(state)-1:
			L = state[(i-1)]
			C = state[i]
			R = state[(i+1)]
			if(L == "0" and C == "0" and R == "0") or (L == "1" and C == "1" and R == "1"):
				next_state+="0"
			else:
				next_state+="1"
	return next_state
def format(state):
	return state.replace("0","O").replace("1","~")



given = "66de3c1bf87fdfcf"
original = int(given,16)
init_state = "{0:b}".format(original)
init_state = "0"*(64-len(init_state)) + init_state
l = len(init_state)
print("original:\n",format(init_state))
print(init_state)
print("len = ",l)

first = init_state[-1:] + init_state[:11] + init_state[11]
second = init_state[11] + init_state[12:23] + init_state[23]
third = init_state[23] + init_state[24:34] + init_state[34]
fourth = init_state[34] + init_state[35:45] + init_state[45]
fifth = init_state[45] + init_state[46:56] + init_state[56]
sixth = init_state[56] + init_state[57:]
print(first[1:]+second[1:]+third[1:]+fourth[1:]+fifth[1:]+sixth[1:])

print(len(first))
print(len(second))
print(len(third))
print(len(fourth))
print(len(fifth))
print(len(sixth))

a = ""+first+second+third+fourth+fifth+sixth
print("a=",a)
print("len=",len(a))

def solve_and_fit(stuff):
	to_fit = []
	for goal in stuff:
		print("starting goal=",goal)
		answers = []
		for i in range(2**len(goal)-1):
			to_test = "{0:b}".format(i)
			to_test = "0"*(len(goal)-len(to_test)) + to_test
			res = step_automata_ignore_edge(to_test)
			if res == goal[1:-1]:
				answers.append(to_test)
		to_fit.append(answers)
		print("done, # solns=",len(answers))
	#print(to_fit)
	zipped = list(itertools.product(*to_fit))
	print(len(zipped))
	#print(zipped[0])
	m = ""
	for part in zipped[0]:
		m+=part[1:-2]
	print(m)
	to_test = []
	for potential in zipped:
		good = True
		last = potential[-1][-1]
		for part in potential:
			if part[0] == last:
				last = part[-1]
			else:
				good=False
				break
		if good:
			m = ""
			for part in potential:
				m+=part[1:]
			to_test.append(m)
	print(len(to_test))
	return to_test
	
res = solve_and_fit([first,second,third,fourth,fifth,sixth])


valid = []
for to_test in res:
	next_state = step_automata(to_test)
	#print(format(next_state))
	#print(format(init_state))
	if(next_state == init_state):
		valid.append(to_test)

#print(valid)
print("number of valid solutions found=",len(valid))

# print(format(init_state))
# print(format(step_automata(valid[0])))


# c = 0
# maybe_flag = []
# #subprocess.call(args, *, stdin=None, stdout=None, stderr=None, shell=False)
# for to_test in valid:
# #to_test = valid[0]
# 	flag = "U2FsdGVkX18+Wl0awCH/gWgLGZC4NiCkrlpesuuX8E70tX8t/TAarSEHTnpY/C1D"
# 	as_int = int(to_test,2)
# 	hex_in = hex(as_int)
# 	res = subprocess.call(["./automata_dec.sh",hex_in])
# 	out = open("std_err.txt")
# 	a = out.readline()
# 	if a != "bad decrypt\n":
# 		print("Maybe a flag?",a,c)
# 		maybe_flag.append(c)
# 		try:	
# 			out = open("std_out.txt")
# 			print(out.readlines())
# 		except UnicodeDecodeError:
# 			print("ignore")
# 			#pass
# 	c+=1

#UnicodeDecodeError
# echo "404c368b" > /tmp/plain.key; xxd -r -p /tmp/plain.key > /tmp/enc.key
# echo "U2FsdGVkX18+Wl0awCH/gWgLGZC4NiCkrlpesuuX8E70tX8t/TAarSEHTnpY/C1D" | openssl enc -d -aes-256-cbc -pbkdf2 -md sha1 -base64 --pass file:/tmp/enc.key