import random, itertools

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

def format(state):
	return state.replace("0","O").replace("1","~")

def count_letter(word,letter):
	i=0
	for l in word:
		if l == letter:
			i+=1
	return i

def fix_A(parts_of_A):
	list_of_list = []
	list_5 = ["00100","01000","00010","01100","01010","00110"]
	list_2 = ["00"]
	list_7 = ['0100110', '0101010', '0110010', '0110110']
	list_4 = ["0100","0010","0110"]
	for length in parts_of_A:
		listo = []
		if length == 2:
			list_of_list.append(list_2)
		if length == 5:
			list_of_list.append(list_5)
		if length == 7:
			list_of_list.append(list_7)
		if length == 4:
			list_of_list.append(list_4)
	return list_of_list
#original = random.randint(0,2**64-1)
# state = "{0:b}".format(original)

given = "66de3c1bf87fdfcf"
original = int(given,16)
init_state = "{0:b}".format(original)
l = len(init_state)
print("original:\n",format(init_state))
print(init_state)
state = init_state

list_7 = []
for i in range(2**5-1):
	aa = "{0:b}".format(i)
	aa = "0"+aa+"0"
	#print(aa)
	next_s = step_automata(aa)
	if next_s == "1"*4:
		list_7.append(aa)

print(list_7)
# print("Initial given state:",format(state))

# for i in range(20):
# 	state = step_automata(state)
# 	print(format(state))

#SEems like all 0's are pred by a line of 1's so lets try that first

test_one=["A"]*l

i = 0
for bit in init_state:
	if bit == "0":
		test_one[(i-1) % l] = "1"
		test_one[i] = "1"
		test_one[(i+1) % l] = "1"
	i+=1


result_one = ""

for i in test_one:
	result_one+=i


#print(result_one)
#print(format(state))

#we know below these A's are all 1's so lets figure this part out
# parts_of_A = []
# in_A = False

# for bit in result_one:
# 	if in_A:
# 		if bit != "A":
# 			parts_of_A.append(count)
# 			in_A = False
# 		count+=1
# 	else:
# 		if bit == "A":
# 			in_A = True
# 			count=1
# print(parts_of_A)

parts_of_A = [2,2,5,7,5,4]

res = fix_A(parts_of_A) #Create lists of possible ways to fit in each set of A's

def make_list(res,list_of_list):
	print(list_of_list,res)
	combinations = list(itertools.product(*list_of_list))
	print("ex:",combinations[0])
	posib = []
	# gaft_1 = "1111111111"
	# gaft_2 = "11111"
	mess = "1000011100010"
	gaft_3 = "1111111111"
	gaft_4 = "111111"
	gaft_5 = "111"
	gaft_6 = "1111"

	for comb in combinations:
		frankenstein = mess + comb[1] + gaft_3 + comb[2] + gaft_4 + comb[3] + gaft_5 + comb[4] + gaft_6 + comb[5]
		#print(format(frankenstein))
		#print(frankenstein)
		test = step_automata(frankenstein)
		print(format(test))
		if test == original:
			print("!!!")
			break
		posib.append(frankenstein)

	return posib

final = make_list(result_one,res) #ZIp eveerything together
#Patterns observed:
print(format(init_state))
print("-"*100)
#Seems to usually end up in grouings of 0's and 1's

#Series of 0's are always before a series of 1's or series of 0's
	#IF a series of 0's then its one smaller on each end, forming the upsidedown triangle
	#If a series of 1's then it is one longer on each end

#0111111111100111110011111111110011011111101101101110011011110110
#O~~~~~~~~~~OO~~~~~OO~~~~~~~~~~OO~~O~~~~~~O~~O~~O~~~OO~~O~~~~O~~O

#Wrong
#~~OOOOOOOO~~~~OOO~~~~OOOOOOOO~~~~~~~OOOO~~~~~~~~~O~~~~~~~OO~~~~~
#yyyynnynnyyyyyyyyyyyyyyyyynnyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

#test
#100001110001011110011111111110011011111101101101110011011110110


#Correct
#110011011011110001111000001101111111000011111111101111111001111
#~~OO~~O~~O~~~~OOO~~~~OOOOO~~O~~~~~~~OOOO~~~~~~~~~O~~~~~~~OO~~~~

goal = "1100110110111"
print(goal)
for i in range(2**13-1):
	aa = "{0:b}".format(i)
	aa = "0"*(len(goal)-len(aa))+aa
	#print(aa)
	test = step_automata(aa)
	if test == goal:
		print("found one:",aa)
bad_guess = "100001110001011111001111111000111011111101101101110011011110110"

print(bad_guess)
print(format(bad_guess))
print(format(step_automata(bad_guess)))
print(format(init_state))