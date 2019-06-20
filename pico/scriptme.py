from pwn import *

def insert_left(a,b):
	#insert b into a
	res = a[:len(a)-1]+b+")"
	return res

def insert_right(a,b):
	#insert a into b
	res = "("+a + b[1:]
	return res

def solve(bracket_string):
	parts = bracket_string.split(" + ")

	#fix the last one
	parts[len(parts)-1] = parts[len(parts)-1][:len(parts[len(parts)-1])-7]
	print(parts)

	levels = []
	for thing in parts:
		level = 0
		temp  = 0
		for b in thing:
			if b == "(":
				temp+=1
			if b == ")":
				temp-=1
			if temp > level:
				level = temp
		levels.append(level)
		
	print(levels)

	parts.append("")
	levels.append(0)
	for i in range(len(parts)-1):
		if levels[i] > levels[i+1]:
			parts[i+1] = insert_left(parts[i],parts[i+1])
			levels[i+1] = levels[i]
		else:
			if levels[i] < levels[i+1]:
				parts[i+1] = insert_right(parts[i],parts[i+1])
			else:
				parts[i+1] = parts[i] + parts[i+1]
	print(parts[len(parts)-1])

	return parts[len(parts)-1]


context.update(arch='amd64', log_level='debug')
s = remote("2018shell.picoctf.com", 22973)

s.recvuntil("warmup.\n")

chal1 = s.recvline()
res = solve(chal1)
s.send(res+"\n")

_ = s.recvuntil("cookin!\n")
chal2 = s.recvline()
res = solve(chal2)
s.send(res+"\n")

_ = s.recvuntil("one.\n")
chal3 = s.recvline()
res = solve(chal3)
s.send(res+"\n")

_ = s.recvuntil("bigger!\n")
chal4 = s.recvline()
res = solve(chal4)
s.send(res+"\n")

_ = s.recvuntil("Round.\n")
chal5 = s.recvline()
res = solve(chal5)
s.send(res+"\n")

s.interactive()