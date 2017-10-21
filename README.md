Hacklu 2017/ Indianer write-up  pwn/web
========================================

> This is a joint write-up for the hacklu 2017 ctf problem indianer; completed by Sai Vegasena and Roy Xu, two members of NYUSEC. The challenge was tagged web/pwn.

> Initially, the challenge included a [binary](svv232/Indianer-hacklu-2017/blob/master/backdoor.so) and a link to a [regular website](https://indianer.flatearth.fluxfingers.net/) that had a "super secret" backdoor.

> After downloading and unzipping, we noticed the .so file header on the binary, indicating that it was a shared object. This meant it was a small part of a whole-some code base that we did not have access to. There was also nothing that could be executed within the file meaning dynamic analysis was not a plausible strategy. Fortunately, after opening the file in binary ninja we uncovered a few key points that brought forth some clarity. 

> The binary was essentially a libc wrapper that the Apache server the website was hosted on was using as an API. We concluded it was an Apache server after making the webpage error out by typing random gibberish in the url and reading the error-message. Your usual set of functions were being used in the wrapper, except for a custom strlen function. Analyzing the control flow of strlen introduced some abnormality and exploitability. 

Here is an image of the [strlen dissasembly] in binja if you'd like to take a look.
--------------------------------------------------------------------------

[picture]()

> First off, there  was a system call in this block of the function, so the remainder of our exploitation was geared towards writing into the sys-call to leak the flag.

[picture]()



