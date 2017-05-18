## crawling
from SS_Yomicom import *

import sys
argvs = sys.argv
argc = len(argvs)
if argc != 2:
    print("Usage # python {} textfile".format(argvs[0]))
    quit()

#sample_text="562.txt"
sample_text=argvs[1]
Debug_text_convert_json(sample_text)
