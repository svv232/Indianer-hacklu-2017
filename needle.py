def cstr(s):
    return s[:s.index('\x00')]

request = 'GET /asdf.html?dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=cat_/etc/passwd HTTP/1.1\x00'
underscore = ord('n')
trigger = 1 if 'GET' in request else 0
counter = 0
needle = [chr(0) for _ in range(0x100)]

for i in range(0, 512, 9):
    needle[i % 35] = chr(((underscore & 1) + i) % 24 + ord('a'))

needle[underscore] = chr(0)
print(''.join(needle))

underscore += 1

if counter <= 1:
    counter += 1


LL = len(request)

assert ''.join(needle[:0x22]) in cstr(request)

bak = request[request.find(''.join(needle[:0x22])) + len(cstr(needle)):]
sa = bak[1:]
assert bak[0] == '='
print(sa)
print(sa.replace('_', ' '))
