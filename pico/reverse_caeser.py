ciphertext = "vgefmsaapaxpomqemdoubtqdxoaxypeo"

def shift_up(string, index):
	out = ""
	for char in string:
		as_num = (ord(char)+index)
		#print(as_num)
		if (as_num >122):
			as_num = as_num % 122 + 97
		out += (chr(as_num))
	return out 

def shift_down(string, index):
	out = ""
	for char in string:
		as_num = (ord(char)-index)
		#print(as_num)
		if (as_num < 97):
			as_num = 123 - (97 - as_num)
		out += (chr(as_num))
	return out 

for i in range(28):
	print("res = ",shift_down(ciphertext,i))