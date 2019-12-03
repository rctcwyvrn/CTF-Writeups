import hashlib, shlex

import string, itertools
from rsa import _hash

#send = "ls | cat"
send = "ls|xargs cat"

#def _hash(message):
#    return hashlib.sha256(message).digest()[0:1]


goal = _hash(send.encode())

test = b''
count = 0
cur_len = 1
#tests = list(itertools.permutations(string.ascii_letters + string.punctuation,4))

print("list built")
#while (test != goal):
for test_left in itertools.permutations(string.ascii_letters + string.punctuation,4):
	left = ''.join(test_left)

	if len(left) > cur_len:
		print("cur_len = ",cur_len)
		cur_len+=1

	command = f"convert womancat.jpg \( -pointsize 40 -size 504x -gravity Center {shlex.quote('caption:' + left)} {shlex.quote('caption:' + left)} +append \) -gravity Center -append png:-"
	test = _hash(command.encode())

	assert(len(goal) == len(test))
	if goal == test:
		break

	# count+=3
	# if count % 50000 == 0:
	# 	print(count)

	if goal == test:
		break
		
else:
	print("FUCK")

print(command)
print(_hash(send.encode()))
print(_hash(command.encode()))

#convert womancat.jpg \( -pointsize 40 -size 504x -gravity Center 'caption:~}|{' 'caption:~}|{' +append \) -gravity Center -append png:-