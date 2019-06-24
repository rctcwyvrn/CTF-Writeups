from fpylll import *

A = IntegerMatrix.from_matrix([[1,2,3,4],[30,4,4,5],[1,-2,3,4]])
print(A)
A = LLL.reduction(A)
print(A)
t = (1, 2, 5, 5)
v0 = CVP.closest_vector(A, t)
print(v0)