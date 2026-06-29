total = 0 
for i in range(1, 99999999):
    total += i**3

total2 = sum(i for i in range(1, 99999999))

print(total == total2**2)