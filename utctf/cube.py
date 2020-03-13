a = [("B'", "U'"), ("F", "B", "F"), ("R'", "D"), ("B", "D'")]
b = [("R" "D","L'"),("D","U'","B"),("U","F'"),("L'","F")]

a_bar = [("B","D'","R'","D","R","D","L'","D'","R","D","B'"),("B","D'","R'","D","D","U'","B","D'","R","D","B'"),
("B","D'","R'","D","U","F'","D'","R","D","B'"),("B","D'","R'","D","L'","F","D'","R","D","B'")]

b_bar = [("U" ,"F'", "R", "D" ,"L'" ,"B'" ,"U'", "L" ,"D'", "R'" ,"F" ,"U'"), ("U" ,"F'", "R" ,"D" ,"L'", "F" ,"B" ,"F" ,"L" ,"D'", "R'" ,"F" ,"U'"), 
("U" ,"F'" ,"R" ,"D", "L'", "R'" ,"D", "L" ,"D'" ,"R'" ,"F", "U'"), ("U" ,"F'" ,"R" ,"D" ,"L'" ,"B" ,"D'" ,"L", "D'", "R'" ,"F", "U'")]

A = ("D'","R","D","B'")
A_inverse = ("B","D'","R'","D")

B = ("L" ,"D'" ,"R'" ,"F", "U'")
B_inverse = ("U" ,"F'" ,"R" ,"D", "L'")

password = 

# compute A_inverse * b_bar

# # Multiplies all elements in the given list
# def mult(xs):
# 	for x in xs:
# 		pass # do rubiks cube stuff

# def inverse(x):
# 	pass

# def bruteforce(pub):
# 	guesses = []
# 	for i in range(2**len(pub)):
# 		guess = []
# 		bits = "{0:b}".format(i)
# 		bits = (len(pub) - len(bits))*"0" + bits
# 		print(bits)
# 		for x in range(len(pub)):
# 			if(bits[x] == "0"):
# 				guess.append(pub[x])
# 			else:
# 				guess.append(inverse(pub[x]))
# 		guesses.append(mult(guess))


# possible_As = bruteforce(a)

# # Computes a_bar = [priv_key ^ -1 * x * priv_key for x in braid]
# def compute(priv_key, braid):
# 	return [mult(inverse(priv_key),x,priv_key) for x in braid]

# for guess in possible_As:
# 	a_bar_guess = compute(guess,b)
# 	if(a_bar_guess == a_bar):
# 		print("found ya!")