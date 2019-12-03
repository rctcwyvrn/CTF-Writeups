import string, base64, sys

f = open("decodeme.png.enc", 'rb') 

# parts = []
# running = b""
# for byte in f.read():
# 	if byte != 0:
# 		running+=bytes([byte])
# 	else:
# 		parts.append(running)
# 		running = b""

# parts.append(running)
# running = b""

parts = f.read().split(b'\x00')
#print(len(parts))
#print(parts[0])

# def make_rev_lookup(char_list):
# 	table = {}
# 	i = 0
# 	for char in char_list:
# 		table[char] = i
# 		i+=1
# 	return table

#t = make_rev_lookup(string.printable)
	#print(t)

# print(parts[1])

def solve(parts):
	count=0
	final =""
	for part in parts:
		count+=1
		print("starting part #{}/{} --------------------------".format(count,len(parts)))
		asc = part.decode()
		if len(asc) == 0:
			print("len was 0")
			continue #if it happens to shuffle the r that caused a diff of 0 back to the front again we get an asc with length 0

		def find_buf(asc):
			#unique = list(set(list(asc)))
			#print(unique)
			seen = []
			i = 0
			for char in asc:
				if char not in seen:
					seen.append(char)
				else:
					#print("found first repeat was {}, char # {}".format(char,i))
					pre = asc[:i]
					buf = asc[i:]
					break
				i+=1
			return pre, buf

		pre, buf = find_buf(asc)
		#found = False
		# for char in string.printable[::-1]:
		# 	if char in asc:
		# 		found = True
		# 		break

		# for i in range(len(asc)):
		# 	if asc[i] == char:
		# 		buf = asc[i+1:]
		# 		pre = asc[:i+1]
		# 		break

		#makes a map of diffs given the buf array
		def make_map(buf):
			m = {}
			for char in buf:
				try:
					m[char]+= 1
				except:
					m[char] = 1
			return m

		#print(pre,buf)
		#print(parts[1].decode()[0])
		diffs = make_map(buf)

		# print_me = []
		# for char in pre:
		# 	try:
		# 		print_me.append([char,diffs[char]])
		# 	except KeyError:
		# 		#so it didn't show up in buf, which means diff = 1
		# 		print("weirdo")
		# 		print_me.append([char,0])

		#print(print_me)

		def is_base64(x):
			return x == 43 or x == 47 or x == 61 or 48<=x<=57 or 65<=x<=90 or 97<=x<=122

		def undo(diff, r):  
			diff+=1
			#print("diff was:",diff)
			guess = (ord(r) + diff) % len(string.printable)

			#ord(res) lies somewhere in [9-13] or [32-126] because it must be part of string.printable, but it should also be a base64 character, so idk wtf is goign on
			#base64 is [48-57] and [65-90] and [97-122] and 43 and 47 and 61

			#while not ((9<=guess<=13) or (32<=guess<=126)):
			while not is_base64(guess):
				guess += len(string.printable)
				if guess > 200:
					print("EXITING")
					sys.exit(0)

			res = chr(guess)
			assert(diff == ((ord(res) - ord(r)) % len(string.printable)))
			return res

		s = ""
		# another_map = {}	
		# for r,diff in print_me:
		# 	#print(undo(diff,r))
		# 	x = undo(diff,r)
		# 	another_map[r] = x

		for char in pre:
			#s+=another_map[char]
			try:
				diff_val = diffs[char]
			except KeyError:
				diff_val = 0 #so it didn't show up in buf, which means diff = 0 (actually 1 but i add 1 later so its fine don't worry about it)

			s+=undo(diff_val,char)

		#print("s='{}'".format(s))
		final+=s
		#print("wtf")
		#print(final,base64.b64decode(final))

	#print("out of loop")
	#print("'{}'".format(final))
	#print(base64.b64decode(final))
	print("done")
	output = open("res.png","wb")
	output.write(base64.b64decode(final))
	output.close()
	return final

final = solve(parts)	