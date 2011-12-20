from matrix2latex import *

features = ['environment', 'headerRow', 'multiline headerRow',
            'headerColumn', 'multiline headerColumn',
            'transpose', 'caption', 'label',
            'format', 'formatColumn', 'alignment']

versions = ['Python', 'Matlab']

p = {'environment':1, 'headerRow':1, 'multiline headerRow':1,
     'headerColumn':1, 'multiline headerColumn':0,
     'transpose':1, 'caption':1, 'label':1,
     'format':1, 'formatColumn':1, 'alignment':1}
m = {'environment':1, 'headerRow':1, 'multiline headerRow':0,
     'headerColumn':1, 'multiline headerColumn':0,
     'transpose':1, 'caption':1, 'label':1,
     'format':1, 'formatColumn':1, 'alignment':1}

def fillList(dict):
    l = list()
    for f in features:
        if dict[f]: l.append('True')
        else: l.append('False')
    return l

python = fillList(p)
matlab = fillList(m)

versions.insert(0, 'Feature')
print matrix2latex([python, matlab], 'features.tex', transpose=True,
                   headerColumn=features, headerRow=versions,
                   caption='What feature is currently available in which language?')
