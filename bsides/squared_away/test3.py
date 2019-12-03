import rabin



for i in range(10):
	print(f"loop {i}")
	priv_key = rabin.keygen(1024)
	diff = priv_key.q - priv_key.p 
	print(diff/priv_key.q)