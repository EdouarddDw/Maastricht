#trying a couple of things out
print("hello world!")

#comments
#this is a comment
#long comments
''' this is a long comment
    that spans multiple lines
'''

#diffrent data types

#integers
print(1)
#float
print(1.0)
#string
print("abc")
#boolean
print(True)
print(False)
#'not' accts like ! in java
print(not 1 == 2)
#list
print([1,2,3])
#dictionary
print({"a":1,"b":2})
#tuple
print((1,2,3))
#set
print({1,2,3})

#variables
a = 1
print(a)

#operators
''' + is addition, - is subtraction, * is multiplication, / is division,
 % is modulus, // is floor division, ** is exponentiation
'''
print(1+2)
print(1-2)
print(1*2)
print(1/2)
print(1%2)
print(1//2)
print(1**2)

#comparision operators
''' == is equal to, != is not equal to, > is greater than, < is less than,
 >= is greater than or equal to, <= is less than or equal to
'''

#logical operators
''' and, or, not
'''
print(1 == 1 and 2 == 2)
print(1 == 1 or 2 == 2)
print(not 1 == 2)

#conditional statements
a = 3
if a == 1:
    print("yes")
elif a == 2:
    print("no")
else:
    print("maybe")

#loops
for i in range(5):
    print(i)

i = 0
while i < 5:
    print(i)
    i += 1

#functions
def add(a,b):
    return a + b

print(add(1,2))

#classes
class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print("hello, my name is " + self.name)

p = Person("Alice")
p.say_hello()

p2 = Person("Bob")
p2.say_hello()

#modules
import math
print(math.sqrt(16))
