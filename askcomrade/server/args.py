a = input('Please enter your integer: ')
total = 0
while True:
    y = a % 10
    total += y
    a /= 10
    if a == 0:
        print('the total is {0}'.format(total))
        break

x = input('Please enter another integer: ')
total2 = 0
while True:
    y = x % 10
    total2 += y
    x /= 10
    if x == 0:
        full_total = total+total2
        print('the total is {0} and the full total is {1}'.format(total2, full_total))
        break

