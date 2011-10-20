import re

def fix(s, table=False):
    """
    input: (string) s
    output: (string) s
    takes any number in s and replaces the format
    '8e-08' with '8\e{-08}'
    """
    i = re.search('e[-+]\d\d', s)
    while i != None:
	before = s[:i.start()]
	number = s[i.start()+1:i.start()+4]
	after = s[i.end():]
	# print 'before', before
# 	print 'number', number
# 	print 'after', after
        if table:
            num = "%(#)+03d" % {'#': int(number)}
        else:
            num = "%(#)3d" % {'#': int(number)}
            
        s = '%s\\e{%s}%s' % (before, num, after)            
	i = re.search('e[-+]\d\d', s)
    return s
