  This is a joint write-up for the hacklu 2017 ctf problem indianer; completed by Sai Vegasena and Roy Xu, two members of NYUSEC. The challenge was tagged web/pwn.

  Initially, the challenge included a [binary](svv232/Indianer-hacklu-2017/blob/master/backdoor.so) and a link to a [regular website](https://indianer.flatearth.fluxfingers.net/) that had a "super secret" backdoor.

  After downloading and unzipping, we noticed the .so file header on the binary, indicating that it was a shared object. More simply put, a small part of a much larger code base that we did not have access to. There was also nothing that could 
be executed within the file meaning dynamic analysis was not a plausible strategy.
Fortunately, after opening the file in binja we uncovered a few key points that added
some sense to the problem.

