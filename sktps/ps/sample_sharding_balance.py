
# redis cluster sharding rule
# slot = crc16(key) mod 16384
import crc16


def which_node(raw):
    if int(raw) <= 5461:
        return 0
    if int(raw) <= 5461 * 2:
        return 1
    return 2


def balance(raw):
    zero = 0
    one = 0
    two = 0
    
    for item in raw:
        if item == 0:
            zero += 1
        if item == 1:
            one += 1
        if item == 2:
            two += 1
            
    sum_up = zero + one + two
    return zero, one, two, float(zero) / sum_up


tails = []
heads1 = []
heads2 = []

for i in range(0, 999):
    tails.append(
        which_node(crc16.crc16xmodem(('t123-0000001-%3d' % i)) % 16384))
    
for i in range(0, 999):
    heads1.append(
        which_node(crc16.crc16xmodem(('%3d-t123-0000001' % i)) % 16384))
    
for i in range(0, 999):
    heads2.append(
        which_node(crc16.crc16xmodem(('%d-t123-0000001' % i)) % 16384))

print(balance(tails))
print(balance(heads1))
print(balance(heads2))
