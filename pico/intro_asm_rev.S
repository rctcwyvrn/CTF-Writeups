.intel_syntax noprefix
.bits 32
	
.global asm0

asm0:
	push	ebp #base pointer
	mov	ebp,esp #base = stack
	mov	eax,DWORD PTR [ebp+0x8]  #eax is the primary arthmetic , ebp+8, so parameter 1?
	mov	ebx,DWORD PTR [ebp+0xc]  #ebx = second parameter
	mov	eax,ebx	#eax = param2
	mov	esp,ebp #stack = base 
	pop	ebp	 #pop base ptr
	ret
