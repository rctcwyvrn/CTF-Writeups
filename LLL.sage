import time
import random
import socket
import multiprocessing
import sys
from ctypes import cdll
import hashlib
import struct


PRIMES=set([35184372092843, 35184372091397, 35184372091399, 35184372089353, 35184372090379, 35184372089357, 35184372089371, 35184372091933, 35184372089887, 35184372090971, 35184372092453, 35184372089863, 35184372089903, 35184372090419, 35184372092473, 35184372088891, 35184372089917, 35184372090433, 35184372089413, 35184372090953, 35184372088907, 35184372092003, 35184372090457, 35184372091483, 35184372090199, 35184372089443, 35184372092017, 35184372091667, 35184372092029, 35184372092297, 35184372088961, 35184372090499, 35184372091871, 35184372088967, 35184372091529, 35184372092561, 35184372089491, 35184372092383, 35184372090523, 35184372090013, 35184372090529, 35184372088997, 35184372092587, 35184372090541, 35184372090031, 35184372089011, 35184372090037, 35184372092087, 35184372091579, 35184372090557, 35184372089539, 35184372090061, 35184372089551, 35184372091601, 35184372092743, 35184372091091, 35184372089047, 35184372092879, 35184372092641, 35184372091109, 35184372092647, 35184372091637, 35184372090107, 35184372090631, 35184372091663, 35184372092689, 35184372089107, 35184372091669, 35184372091159, 35184372090649, 35184372090139, 35184372089117, 35184372091679, 35184372092209, 35184372089653, 35184372089143, 35184372092729, 35184372089147, 35184372092213, 35184372090677, 35184372090689, 35184372092231, 35184372090191, 35184372089687, 35184372090713, 35184372090209, 35184372092083, 35184372091241, 35184372092267, 35184372088979, 35184372090229, 35184372089719, 35184372092851, 35184372089731, 35184372091273, 35184372091951, 35184372089747, 35184372089239, 35184372091801, 35184372089249, 35184372089257, 35184372091819, 35184372092339, 35184372092341, 35184372091837, 35184372089791, 35184372090821, 35184372092321, 35184372091343, 35184372090839, 35184372092377, 35184372089309, 35184372089509, 35184372089827, 35184372091879, 35184372089833, 35184372089323, 35184372090863, 35184372089843, 35184372092917, 35184372090871, 35184372089849, 35184372091903, 35184372089341, 35184372090367])


NCHALLENGES = int(3)
#solution_dict = None

class AlreadyFound(Exception):
    pass

############################################
# Config
##########################################

"""
Setting debug to true will display more informations
about the lattice, the bounds, the vectors...
"""
debug = True

"""
Setting strict to true will stop the algorithm (and
return (-1, -1)) if we don't have a correct 
upperbound on the determinant. Note that this 
doesn't necesseraly mean that no solutions 
will be found since the theoretical upperbound is
usualy far away from actual results. That is why
you should probably use `strict = False`
"""
strict = False

"""
This is experimental, but has provided remarkable results
so far. It tries to reduce the lattice as much as it can
while keeping its efficiency. I see no reason not to use
this option, but if things don't work, you should try
disabling it
"""
helpful_only = True
dimension_min = 7 # stop removing if lattice reaches that dimension

############################################
# Functions
##########################################

def bl(n):                                                                         
    return int(n).bit_length()

# display stats on helpful vectors
def helpful_vectors(BB, modulus):
    nothelpful = 0
    for ii in range(BB.dimensions()[0]):
        if BB[ii,ii] >= modulus:
            nothelpful += 1

    print nothelpful, "/", BB.dimensions()[0], " vectors are not helpful"

# display matrix picture with 0 and X
def matrix_overview(BB, bound):
    for ii in range(BB.dimensions()[0]):
        a = ('%02d ' % ii)
        for jj in range(BB.dimensions()[1]):
            a += '0' if BB[ii,jj] == 0 else 'X'
            if BB.dimensions()[0] < 60:
                a += ' '
        if BB[ii, ii] >= bound:
            a += '~'
        print a

# tries to remove unhelpful vectors
# we start at current = n-1 (last vector)
def remove_unhelpful(BB, monomials, bound, current):
    # end of our recursive function
    if current == -1 or BB.dimensions()[0] <= dimension_min:
        return BB

    # we start by checking from the end
    for ii in range(current, -1, -1):
        # if it is unhelpful:
        if BB[ii, ii] >= bound:
            affected_vectors = 0
            affected_vector_index = 0
            # let's check if it affects other vectors
            for jj in range(ii + 1, BB.dimensions()[0]):
                # if another vector is affected:
                # we increase the count
                if BB[jj, ii] != 0:
                    affected_vectors += 1
                    affected_vector_index = jj

            # level:0
            # if no other vectors end up affected
            # we remove it
            if affected_vectors == 0:
                #print "* removing unhelpful vector", ii
                BB = BB.delete_columns([ii])
                BB = BB.delete_rows([ii])
                monomials.pop(ii)
                BB = remove_unhelpful(BB, monomials, bound, ii-1)
                return BB

            # level:1
            # if just one was affected we check
            # if it is affecting someone else
            elif affected_vectors == 1:
                affected_deeper = True
                for kk in range(affected_vector_index + 1, BB.dimensions()[0]):
                    # if it is affecting even one vector
                    # we give up on this one
                    if BB[kk, affected_vector_index] != 0:
                        affected_deeper = False
                # remove both it if no other vector was affected and
                # this helpful vector is not helpful enough
                # compared to our unhelpful one
                if affected_deeper and abs(bound - BB[affected_vector_index, affected_vector_index]) < abs(bound - BB[ii, ii]):
                    #print "* removing unhelpful vectors", ii, "and", affected_vector_index
                    BB = BB.delete_columns([affected_vector_index, ii])
                    BB = BB.delete_rows([affected_vector_index, ii])
                    monomials.pop(affected_vector_index)
                    monomials.pop(ii)
                    BB = remove_unhelpful(BB, monomials, bound, ii-1)
                    return BB
    # nothing happened
    return BB

""" 
Returns:
* 0,0   if it fails
* -1,-1 if `strict=true`, and determinant doesn't bound
* x0,y0 the solutions of `pol`
"""
def boneh_durfee(pol, modulus, mm, tt, XX, YY, ppp=1, N=0):
    """
    Boneh and Durfee revisited by Herrmann and May
    
    finds a solution if:
    * d < N^delta
    * |x| < e^delta
    * |y| < e^0.5
    whenever delta < 1 - sqrt(2)/2 ~ 0.292
    """

    print "ppp", ppp
    modulus *= ppp

    # substitution (Herrman and May)
    PR.<u, x, y> = PolynomialRing(ZZ)
    Q = PR.quotient(x*y + 1 - u) # u = xy + 1
    polZ = Q(pol).lift()

    UU = XX*YY + 1

    #if N in #solution_dict:
        #raise AlreadyFound()


    # x-shifts
    gg = []
    for kk in range(mm + 1):
        for ii in range(mm - kk + 1):
            xshift = x^ii * modulus^(mm - kk) * polZ(u, x, y)^kk
            gg.append(xshift)
    gg.sort()

    # x-shifts list of monomials
    monomials = []
    for polynomial in gg:
        for monomial in polynomial.monomials():
            if monomial not in monomials:
                monomials.append(monomial)
    monomials.sort()

    #if N in #solution_dict:
        #raise AlreadyFound()
    
    # y-shifts (selected by Herrman and May)
    for jj in range(1, tt + 1):
        for kk in range(floor(mm/tt) * jj, mm + 1):
            yshift = y^jj * polZ(u, x, y)^kk * modulus^(mm - kk)
            yshift = Q(yshift).lift()
            gg.append(yshift) # substitution
    
    # y-shifts list of monomials
    for jj in range(1, tt + 1):
        for kk in range(floor(mm/tt) * jj, mm + 1):
            monomials.append(u^kk * y^jj)

    #if N in #solution_dict:
        #raise AlreadyFound()

    # construct lattice B
    nn = len(monomials)
    BB = Matrix(ZZ, nn)
    for ii in range(nn):
        BB[ii, 0] = gg[ii](0, 0, 0)
        for jj in range(1, ii + 1):
            if monomials[jj] in gg[ii].monomials():
                BB[ii, jj] = gg[ii].monomial_coefficient(monomials[jj]) * monomials[jj](UU,XX,YY)

    # Prototype to reduce the lattice
    if helpful_only:
        # automatically remove
        BB = remove_unhelpful(BB, monomials, modulus^mm, nn-1)
        # reset dimension
        nn = BB.dimensions()[0]
        if nn == 0:
            print "failure"
            return 0,0

    # check if vectors are helpful
    if debug:
        helpful_vectors(BB, modulus^mm)
    
    # check if determinant is correctly bounded
    det = BB.det()
    bound = modulus^(mm*nn)
    diff = (log(det) - log(bound)) / log(2)
    if det >= bound:
        print "We do not have det < bound. Solutions might not be found."
        print "Try with highers m and t."
        if debug:
            print "size det(L) - size e^(m*n) = ", floor(diff)
        if strict:
            return -1, -1
    else:
        print "%d: det(L) < e^(m*n) (good! If a solution exists < N^delta, it will be found)" % floor(diff)

    # display the lattice basis
    #if debug:
    #    matrix_overview(BB, modulus^mm)

    # LLL
    if debug:
        print "optimizing basis of the lattice via LLL, this can take a long time"


   # if N in #solution_dict:
        #raise AlreadyFound()

    BB = BB.LLL()

    #if N in #solution_dict:
        #raise AlreadyFound()

    if debug:
        print "LLL is done!"

    # transform vector i & j -> polynomials 1 & 2
    if debug:
        print "looking for independent vectors in the lattice"
    found_polynomials = False
    
    for pol1_idx in range(nn - 1):
        for pol2_idx in range(pol1_idx + 1, nn):
            # for i and j, create the two polynomials
            PR.<w,z> = PolynomialRing(ZZ)
            pol1 = pol2 = 0
            for jj in range(nn):
                pol1 += monomials[jj](w*z+1,w,z) * BB[pol1_idx, jj] / monomials[jj](UU,XX,YY)
                pol2 += monomials[jj](w*z+1,w,z) * BB[pol2_idx, jj] / monomials[jj](UU,XX,YY)

            # resultant
            PR.<q> = PolynomialRing(ZZ)
            rr = pol1.resultant(pol2)

            # are these good polynomials?
            if rr.is_zero() or rr.monomials() == [1]:
                continue
            else:
                print "found them, using vectors", pol1_idx, "and", pol2_idx
                found_polynomials = True
                break
        if found_polynomials:
            break

    if not found_polynomials:
        print "no independant vectors could be found. This should very rarely happen..."
        return 0, 0
   
    #if N in #solution_dict:
        #raise AlreadyFound()

    rr = rr(q, q)

    # solutions
    soly = rr.roots()

    if len(soly) == 0:
        print "Your prediction (delta) is too small"
        return 0, 0

    soly = soly[0][0]
    ss = pol1(q, soly)
    solx = ss.roots()[0][0]



    #
    return solx, soly

def solve(N, e, ppp=1):
    #if N in #solution_dict:
        #raise AlreadyFound()
    ############################################
    # How To Use This Script
    ##########################################

    #
    # The problem to solve (edit the following values)
    #
    #
    # Lattice (tweak those values)
    #

    # you should tweak this (after a first run), (e.g. increment it until a solution is found)
    m = 8 # size of the lattice (bigger the better/slower) 
    # with Nsize=1234:
    # 0.27 --> 6
    # 0.273 --> 7
    # 0.275 --> 8
    delta = 0.2946 #0.294532 

    # you need to be a lattice master to tweak these
    t = int((1-2*delta) * m) + 4  # optimization from Herrmann and May
    X = 2*floor(N^delta)  # this _might_ be too much
    Y = floor(N^(1/2))    # correct if p, q are ~ same size

    #
    # Don't touch anything below
    #

    # Problem put in equation
    P.<x,y> = PolynomialRing(ZZ)
    A = int((N+1)/2)
    pol = 1 + x * (A + y)

    #
    # Find the solutions!
    #


    solx, soly = boneh_durfee(pol, e, m, t, X, Y, ppp, N)

    # found a solution?
    if solx > 0:
        print "solution found"
        print pol
        print "x:", solx
        print "y:", soly

        fd = int(pol(solx, soly) / e)
        print "private key found:", fd
        return (True, fd)
    else:
        print "no solution was found"

    return (False, 0)



def example():
    ############################################
    # How To Use This Script
    ##########################################

    #
    # The problem to solve (edit the following values)
    #

    # the modulus
    N = 0xc2fd2913bae61f845ac94e4ee1bb10d8531dda830d31bb221dac5f179a8f883f15046d7aa179aff848db2734b8f88cc73d09f35c445c74ee35b01a96eb7b0a6ad9cb9ccd6c02c3f8c55ecabb55501bb2c318a38cac2db69d510e152756054aaed064ac2a454e46d9b3b755b67b46906fbff8dd9aeca6755909333f5f81bf74db
    # the public exponent
    e = 0x19441f679c9609f2484eb9b2658d7138252b847b2ed8ad182be7976ed57a3e441af14897ce041f3e07916445b88181c22f510150584eee4b0f776a5a487a4472a99f2ddc95efdd2b380ab4480533808b8c92e63ace57fb42bac8315fa487d03bec86d854314bc2ec4f99b192bb98710be151599d60f224114f6b33f47e357517

    # the hypothesis on the private exponent (the theoretical maximum is 0.292)
    delta = .18 # this means that d < N^delta

    #
    # Lattice (tweak those values)
    #

    # you should tweak this (after a first run), (e.g. increment it until a solution is found)
    m = 5 # size of the lattice (bigger the better/slower)

    # you need to be a lattice master to tweak these
    t = int((1-2*delta) * m)  # optimization from Herrmann and May
    X = 2*floor(N^delta)  # this _might_ be too much
    Y = floor(N^(1/2))    # correct if p, q are ~ same size

    #
    # Don't touch anything below
    #

    # Problem put in equation
    P.<x,y> = PolynomialRing(ZZ)
    A = int((N+1)/2)
    pol = 1 + x * (A + y)

    #
    # Find the solutions!
    #

    # Checking bounds
    if debug:
        print "=== checking values ==="
        print "* delta:", delta
        print "* delta < 0.292", delta < 0.292
        print "* size of e:", int(log(e)/log(2))
        print "* size of N:", int(log(N)/log(2))
        print "* m:", m, ", t:", t

    # boneh_durfee
    if debug:
        print "=== running algorithm ==="
        start_time = time.time()

    solx, soly = boneh_durfee(pol, e, m, t, X, Y)

    # found a solution?
    if solx > 0:
        print "=== solution found ==="
        if False:
            print "x:", solx
            print "y:", soly

        d = int(pol(solx, soly) / e)
        print "private key found:", d
    else:
        print "=== no solution was found ==="

    if debug:
        print("=== %s seconds ===" % (time.time() - start_time))

if __name__ == "__main__":
    example()

