Hacklu 2017/ Indianer write-up  pwn/web
========================================

This is a joint write-up for the hacklu 2017 ctf problem indianer; completed by Sai Vegasena and Roy Xu, two members of NYUSEC. The challenge was tagged web/pwn.

Initially, the challenge included a [binary](svv232/Indianer-hacklu-2017/blob/master/backdoor.so) and a link to a [regular website](https://indianer.flatearth.fluxfingers.net/) that had a "super secret" backdoor.

Inline-style:
![alt text]()

After downloading and unzipping, we noticed the .so file header on the binary, indicating that it was a shared object. This meant it was a small part of a whole-some code base that we did not have access to. There was also nothing that could be executed within the file meaning dynamic analysis was not a plausible strategy. Fortunately, after opening the file in binary ninja we uncovered a few key points that brought forth some clarity. 

[picture]()

The binary was essentially a libc wrapper that the Apache server the website was hosted on was using as an API. We concluded it was an Apache server after making the webpage error out , by typing random gibberish in the url, and reading the error-message. Your usual set of functions were being used in the wrapper, except for a custom strlen function. Analyzing the control flow of strlen introduced some abnormality and exploitability. 

[strlen dissasembly]()
----------------------


[picture]()

First off, there  was a system call in this block of the function, so the remainder of our exploitation was geared towards writing into the sys-call to leak the flag.

[picture]()

Looking back at the start of the function, strcmp is called at 0xa0c checking if
data_da0, or the string 'GET' ,indicated in hex view, was the request type. Trigger, a variable in the GOT, was incremented if that was the case. The string "ndex.html" was then checked for at 0xa48; if "ndex.html" exists and a variable apr_hook_debug_enabled is set a visible error message appears. The value of apr_hook_debug_enabled is set to the equivalent bash error code of the first argument plus the first byte of the "index.html" argument in the url. Error code 1 for example would result in
the debug variable being set to i + 1 or j. So we knew that the error code could be controlled for exploitation as an exit code can be set to any value via the command ...

``` exit(any integer)'''


[picture]

If "ndex.html" was not present in the url the debug code would jump to a block that would still execute any plausible exploit, but no error message would appear making any sort of exfiltration impossible.

[picture]

After a succesful GET request with a sufficient argument was sent the message would be directed to this block of code. 

[picture]

There an algorithm with ordinal operations, bit swapping, and string operations would be implemented on the variable _ , and the counter and trigger variables would be updated accordingly. _ was set to the ordinal of 'n'. From there the algorithm used _ to set the value of a magic string needle. If needle was set to the right value by the end of all the string operations and sent within a GET request equal to a command, low priority shell access would be granted.

Ex. - url/needle=command

[picture]() 


[picture]()

Reproducing the needle was starting to get slightly more difficult, so we decided to open up the shared object binary in IDA, and used hexrays to decipher what the algorithm was doing with the _ variable in the GOT.

Here is the [IDA disassembly]()
-------------------------------

As you can see it is much neater. Lines 31 - 74 were what we reversed and re 
wrote to spot the behavior , and reemulate the algorithm.

needle was first set to a string of null bytes at  size hex 100
looping from 0 to 512 in increments of 9 needles ith element % 35 was set
to the value of chr(((_ & 1) + i) mod 24 + the ordinal of 'a')

All strings equal to '_' or underscore in the request would then be replaced with 
a space.

This fact was useful during command injection.

[picture]()

We used this code to write a [python script]() that reproduced the magic string with 
some help from our friend [Josh](www.hypersonic.me), another member of NYUSEC.

The output of the script was ...
    ``` dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp ```

So we had succesfully recreated the magic_string!!!

We tested with the following command 

``` https://indianer.flatearth.fluxfingers.net/0ndex.html dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=sleep_10_%23 ```

There was a succesfull sleep!!
