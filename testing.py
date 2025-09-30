""" Hint """

n1 = input().strip().split()
n2 = input().strip().split()
n3 = input().strip().split()

def check(x, a, b) :
    """ operator check """
    if x == "==" :
        return a == b
    if x == "!=" :
        return a != b
    if x == ">" :
        return a > b
    if x == "<" :
        return a < b
    if x == ">=" :
        return a >= b
    if x == "<=" :
        return a <= b
    return False

x1, y1 = n1[0], int(n1[1])
x2, y2 = n2[0], int(n2[1])
x3, y3 = n3[0], int(n3[1])

for i in range(1000) :
    unit = i % 10
    ten = (i // 10) % 10
    hund = (i // 100) % 10
    if (check(x1, unit, y1) and check(x2, ten, y2) and check(x3, hund, y3)) :
        print(f"{i :03d}")
