from pwn import *

r = remote("crypto.chal.csaw.io", 1003)

hash_val = r.recvline().strip()
print(hash_val)
#_ = r.recvline()

test = 1
for i in range(1,1000):
	test = 2 * test
	print("sending ",test,"---------------------------------------------------")
	r.send(str(test) + "\n")

	_ = r.recvline() #parrot response
	response = r.recvline().strip()

	h1 = response[:32]
	h2 = response[32:64]
	h3 = response[64:96]
	h4 = response[96:]

	assert(h1+h2+h3+h4 == response)
	#print("resp=",response)

	r.send(str(test+1) + "\n") #increase by 1

	_ = r.recvline() #parrot response
	resp2 = r.recvline().strip()

	t1 = resp2[:32]
	t2 = resp2[32:64]
	t3 = resp2[64:96]
	t4 = resp2[96:]

	print(h1==t1,h2==t2,h3==t3,h4==t4,test)

	r.send(str(test+10005) + "\n") #increase by 10^5

	_ = r.recvline() #parrot response
	resp2 = r.recvline().strip()

	t1 = resp2[:32]
	t2 = resp2[32:64]
	t3 = resp2[64:96]
	t4 = resp2[96:]

	print(h1==t1,h2==t2,h3==t3,h4==t4,test+10005)

# for i in range(1,100):
# 	print("trying power of 10**5=",i, "sending ",10**(5*i))
# 	r.send(str(10**(5*i)) + "\n")
# 	_ = r.recvline() #parrot response
# 	response = r.recvline().strip()[64:]
# 	print("resp=",response)

# 	if hash_val[64:] == response:
# 		print("FOUND IT",i)

# 	r.send(str(10**(5*i)+14125) + "\n")
# 	print("checking against",10**(5*i)+14125)
# 	_ = r.recvline() #parrot response
# 	resp2 = r.recvline().strip()[64:]
# 	print(response,resp2)
# 	assert(response == resp2)


# for i in range(1,100):
# 	print("trying power of 10**",i, "sending ",10**i)
# 	r.send(str(10**i) + "\n")
# 	_ = r.recvline() #parrot response
# 	response = r.recvline().strip()[32:]
# 	print("resp=",response)

# 	if hash_val[32:] == response:
# 		print("FOUND IT",i)

# 	r.send(str(10**i+1) + "\n")
# 	_ = r.recvline() #parrot response
# 	resp2 = r.recvline().strip()[32:]
# 	print(response,resp2)
# 	assert(response == resp2)


# #60a3ea56b8589fb305f3b047143c6a01098761862567ffe31e72af2bf4b8672238011e4684469a258a63f14d8d900c9b1a7a02238093873fb1efc5aaf63d8c7e >100
# #ef9f5618d02355809da5da44af0be8fa3fe57760095556f4ee373eb6e02f933d25f8eb6e075a216f65f2576693f0713512aad56decad5835864da8a6672c83e7


same = '70be5916fc0820f2ba35a0bc743bba92beb5af75924da3272855e2ff34a5fbe23d02bd9a19530e83b06ec7f3b77cd396'
print(len(same))
diff = "78b2e63a9cbe81a92f700a5c6b883fa2"
print(len(diff)) #it would appear that this is a mash of 4 hashes together, im guessing its by digit


# '78b2e63a9cbe81a92f700a5c6b883fa270be5916fc0820f2ba35a0bc743bba92beb5af75924da3272855e2ff34a5fbe23d02bd9a19530e83b06ec7f3b77cd396'
# '7630e3d62bcc385c6dc226b4b33dfda470be5916fc0820f2ba35a0bc743bba92beb5af75924da3272855e2ff34a5fbe23d02bd9a19530e83b06ec7f3b77cd396'

# #78b2e63a9cbe81a92f700a5c6b883fa2 ?? was response to 0
# #7630e3d62bcc385c6dc226b4b33dfda4 ?? was response to 1

# #16 byte hashes