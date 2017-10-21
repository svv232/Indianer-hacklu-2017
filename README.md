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

> After a succesful GET request with "ndex.html" was sent the message would be directed to this block of code. There an algorithm with ordinal operations, bit swapping, and string operations would be implemented on the variable _ in the GOT, and the counter and trigger variables would be updated accordingly. By the end of all the string operations on _ ,a magic string would be created. Essentially, if this magic string was in the GET request and set equal to a command low priority
shell access would be granted.

> Ex. - url/magic_string=command

[picture]() 


[picture]()

> Reproducing the magic string was starting to get slightly more difficult, so we decided to open up the shared object binary in IDA, and used hexrays to decipher what the algorithm was doing with the _ variable in the GOT. This way we could reproduce
the string and gain command injection into the system call as a relatively unprivelaged user.

Here is the [IDA disassembly]()
-------------------------------

> As you can see it is much neater. Lines 31 - 74 were what we reversed and re 
wrote to spot the behavior , and reemulate the algorithm.

[picture]()

> We used this code to write a [python script]() that reproduced the magic string with 
some help from our friend [Josh](hypersonic.me), another member of NYUSEC.

The output of the script was ...
    ``` python dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp ```

So we had succesfully recreated the magic_string!!!

> We tested with the following command 

'https://indianer.flatearth.fluxfingers.net/0ndex.html/ dpdpdpamamamamajvjvjvjvgsgsgsgsgpdp=' + sleep(10) + '_%23'

There was a succesfull sleep!!

We also got excited and found that both nano and gdb were on the box, as the website would load forever and then spit out a bad gateway error.
