.intel_syntax noprefix
.bits 32
	
.global asm1

#asm1(0xc8)

#calls
#asm1 -> part a -> part c continues on to part d and then returns

#so it returns param + 3
asm1:
	push	ebp
	mov	ebp,esp
	cmp	DWORD PTR [ebp+0x8],0x9a 
	jg 	part_a	#goto part a if param is greater than 9a
	cmp	DWORD PTR [ebp+0x8],0x8
	jne	part_b	#goto part b if param is not equal to 8
	mov	eax,DWORD PTR [ebp+0x8] #eax = param
	add	eax,0x3 #add 3 to eax 
	jmp	part_d #part d()
part_a:
	cmp	DWORD PTR [ebp+0x8],0x2c
	jne	part_c #goto part c if param != 0x2c
	mov	eax,DWORD PTR [ebp+0x8]
	sub	eax,0x3 #subtract 3
	jmp	part_d
part_b:
	mov	eax,DWORD PTR [ebp+0x8] #eax = param
	sub	eax,0x3	#subtract 3
	jmp	part_d
	cmp	DWORD PTR [ebp+0x8],0xc8
	jne	part_c
	mov	eax,DWORD PTR [ebp+0x8]
	sub	eax,0x3
	jmp	part_d
part_c:
	mov	eax,DWORD PTR [ebp+0x8]
	add	eax,0x3 #eax+=3
part_d:
	pop	ebp
	ret
