import base64, sys, string
from random import shuffle

#original = ""
class snake_oil:
	def __init__(self):
		self.key = []
		self.done = False

	def set_key(self,key):
		self.key = key
		self.done = True
		self.filename = ""

	def enc_file(self,ptxt_file):
		self.filename=ptxt_file
		if self.done:
			print("you cant encrypt two different files, make a new snake oil")
			return
		with open(ptxt_file, 'rb') as (r):
			w = open(ptxt_file + '.enc', 'wb')
			b64 = base64.b64encode(r.read())

			#global original
			#original = b64

			self.key = self.encode(w, b64)
			self.done = True
			#print(self.key)
		f = open("key_file.py","w")
		keystring = "["
		for i in self.key:
			keystring+=str(i)+","
		keystring+="]"

		f.write("key="+keystring)
		f.close()

	def dec_file(self,enc_file="",out_file=""):
		if enc_file == "":
			enc_file = self.filename+".enc"

		if out_file == "":
			out_file = enc_file[:-3]

		if not self.done:
			print("encrypt something first")
			return

		parts = []
		last = 0
		total = open(enc_file,"rb").read()
		for point in self.key:
			parts.append(total[last:point])
			last = point

		parts.append(total[last:])
		res = self.solve(parts)
		#output = open("scheme_res.png","wb")
		output = open(out_file,"wb")
		output.write(res)
		output.close()

	def solve(self,parts):
		print("starting decryption")
		count=0
		final =""
		for part in parts:
			count+=1
			#print("starting part #{}/{} --------------------------".format(count,len(parts)))
			asc = part.decode()
			if len(asc) == 0:
				#print("len was 0")
				continue #if it happens to shuffle the r that caused a diff of 0 back to the front again we get an asc with length 0

			def find_buf(asc):
				if len(asc) == 1:
					#diff was 1 for 1 character and then the next one had a diff of 0
					return [asc],[]
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
		# output = open("res.png","wb")
		# output.write(base64.b64decode(final))
		# output.close()
		res = base64.b64decode(final)
		# try:
		# 	res = base64.b64decode(final)
		# 	#print(len(final) % 4,len(final) % 8)
		# except:
		# 	print("fuck")
		# 	print(len(final) % 4,len(final) % 8)
		# 	# for x,y in zip(original,final):
		# 	# 	if not chr(x) == y:
		# 	# 		print(chr(x),y)
		# 	# 	else:
		# 	# 		print("ok")
		# 	print("original had {} more bytes".format(len(original)-len(final)))
		# 	print(original[len(final):])
		# 	sys.exit(0)
		return res

	def encode(self, f, inp):
		#print(inp)
		print("starting encryption")
		inp = inp.decode()
		s = string.printable
		init = lambda : (list(s), []) #init is a function that returns s as a list and an empty array?
		bag, buf = init() #bag = list(s), buf = []
		count = 0
		key = []
		for x in inp: #inp = base64 of input file, so for each base64 char in the file
			#print(inp[:10])
			if x not in s: #if its not in s, then skip it -> if it's not a printable string then skip it
				continue
			while True:
				r = bag[0] 
				bag.remove(r) #r starts at the first printable string and moves down
				diff = (ord(x) - ord(r) + len(s)) % len(s) #diff = 0 iff ord(x) - ord(r) == 0 mod len(s), so if it equals 0 , len(s), -len(s) etc
				if diff == 0 or len(bag) == 0: #diff = 0 or out of chars in bag
					shuffle(buf) #shuffle, before this buf = [a diff # of '0's, a diff # of '1's etc]
					f.write((b'').join([x.encode() for x in buf])) #write buf
					count+=len(buf)
					key.append(count)
					#f.write('\x00') #null terminated sections
					bag, buf = init() #restart
					shuffle(bag) #shuffled bag this time though
				else:
					break

			buf.extend(r * (diff - 1)) #add the char r, diff -1 times to the buf that's gonna get written later
			f.write(r.encode()) #once the diff is nonzero, write r to the file
			count+=1

		shuffle(buf) #shuffle the buff
		f.write((b'').join([x.encode() for x in buf])) #write again with no null termination, this is the last section
		print("done")
		return key
filename = "test.png"
s = snake_oil()
# s.enc_file(filename)
# s.dec_file()

import key_file
s.set_key(key_file.key)
s.dec_file(filename+".enc","hhahaitworks.png")