def enc(x):  # BV加密函数
    table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
    xor = 177451812
    add = 8728348608
    s = [11, 10, 3, 8, 4, 6]
    x = (x ^ xor) + add
    r = list("BV1  4 1 7  ")
    for i in range(6):
        r[s[i]] = table[x // 58**i % 58]
    return "".join(r)


table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
tr = {}
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608


def dec(x):  # BV解密函数
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58**i
    return (r - add) ^ xor
