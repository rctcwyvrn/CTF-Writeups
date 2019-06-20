from pwn import *
import codecs


def toascii(nums):
	return "".join([chr(x) for x in nums])

def octaltoascii(oct_strings):
	return "".join([chr(int(boi,8)) for boi in oct_strings])

context.update(arch='amd64', log_level='debug')
s = remote("2018shell.picoctf.com", 1225)

_ = s.recvline()

key = s.recvline()

challenge1 = s.recvline()

_ = s.recvline() 
_ = s.recvline()


in_binary = True
values = []
print(challenge1)

binary = ""
for char in challenge1:
	if (char == "0" or char == "1"):
		binary+=char

for i in range(0,len(binary),8):
	values.append(int(binary[i:i+8],2))

print("values",values)

pay1 = toascii(values)
pay1 += "\n"

s.send(pay1)



challenge2 = s.recvline()
print("c2=",challenge2)
hex_chal = challenge2.split()[4]
print(hex_chal)

pay2 = codecs.decode(hex_chal,'hex').encode('ascii')
pay2+="\n"

s.send(pay2)

_ = s.recvline()
challenge3 = s.recvline()
l = challenge3.split()


print("c3=",challenge3)
print(l)

values2 = []
count = 0

for word in l:
	if count >= 4 and count <= 8:
		values2.append(word)
	count+=1


pay3 = octaltoascii(values2)
pay3 += "\n"

s.send(pay3)

s.interactive()
