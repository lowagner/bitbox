'''
Embeds binaries to C code. 
Outputs to stdout as a header file.
Define DATA_IMPLEMENTATION to include it as an include file.
'''

import sys
import re
import os.path
import argparse

LINELEN = 120 # line len in the file

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('files', nargs='+', metavar='file',help='filenames to embed. optionnally set filename:cname to use another symbol')
parser.add_argument('--prefix', default="data_", help='prefix for file names in C')
args=parser.parse_args()

# known extensions types ? 
PREFIX = args.prefix.upper()
# embed files

def printable(c) : 
    n=ord(c)
    # 0-9 to avoid octal clash, / to avoid comments , ? to avoid trigraphs
    return n>=32 and n<127 and c not in "\\\"0123456789/?" 

def gen_lines(data) :
    "generator of quoted lines from big string"
    s=""
    for c in data : 
        s+= c if printable(c) else "\%o"%ord(c)
        if len(s)>=LINELEN : 
            yield s
            s=""
    yield s

print "/* \n  file autogenerated by %s, do no edit."%os.path.basename(sys.argv[0])
print "  define %sIMPLEMENTATION to include the real data, once.\n*/\n"%args.prefix.upper()
all_files=[] 
for file in args.files : 
    if ':' in file : 
        file,quoted = file.split(':',1)
    else : 
        # only keep basename, quote special chars
        quoted = re.sub(r'(^[^a-zA-Z])|[^0-9a-zA-Z_]','_',os.path.basename(file))

    # get file size
    size = os.path.getsize(file)
    all_files.append((file, quoted, size))

print "#ifndef %sDECLARATION"%PREFIX
print "#define %sDECLARATION"%PREFIX
print
for f,q,n in all_files :
    print "extern const char %s%s[%d];\t// from %s"%(args.prefix, q,n,f)
print

print "\n#endif // %sDECLARATION"%PREFIX
print "\n#ifdef %sIMPLEMENTATION"%PREFIX + "  // "+"-"*80+"\n"

for f,q,n in all_files :
    print "const char %s%s[%d] = " % (args.prefix,q,n)
    print "\n".join(" \"%s\""%line for line in gen_lines(open(f).read()))+";\n"

print "\n#endif // %sIMPLEMENTATION"%PREFIX
