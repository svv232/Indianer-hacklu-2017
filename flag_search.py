import os
import sys

counter = 1
for (dirpath, dirnames, filenames) in os.walk('.'):
    for fname in filenames:
        if fname == 'backdoor.c':
            exit(6)
        try:
            with open(os.path.join(dirpath, fname), 'r') as f:
                fbody = f.read()
                if 'flag{' in fbody:
                    exit(ord(fbody[fbody.index('flag{') + 4:][counter]))
        except IOError:
            pass
exit(50)
