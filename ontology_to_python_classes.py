import owlready2 as owlr
import json
import argparse


parser = argparse.ArgumentParser(description='Convert an OWL ontology to a python class file.')
parser.add_argument('--input', '-i', type=str, help='Input OWL file')
parser.add_argument('--output', '-o', type=str, help='Output python file')
args = parser.parse_args()
infile = args.input
outfile = args.output

onto = owlr.get_ontology(infile)
onto.load()

# Find superclasses
class_list = list(onto.classes())
class_dicts= []
subclasses = {}
class_dict_by_name = {}
class_dict_by_name['owl.Thing'] = {'superclasses': [], "comment": []}
for c in class_list:
    superclasses = c.is_a
    superclasses = [str(s) for s in superclasses]
    comment = c.comment
    print("Class: ", c)
    print("Superclasses: ", superclasses)
    print("Annotations: ", comment)
    print("")
    class_dicts.append({'name': str(c), 'superclasses': superclasses, "comment": comment})
    class_dict_by_name[str(c)] = {'superclasses': superclasses, "comment": comment}
    subc = c.subclasses()
    subc = [str(s) for s in subc]
    subclasses[str(c)] = subc

# sort classes
sorted_classes = ['owl.Thing']
non_rooted_classes = []
for c in class_dicts:
    ssc = None
    if len(c['superclasses']) == 0:
        non_rooted_classes.append(c)
    else:
        sc = c['superclasses'][0]
        sscl = [sc, c['name']]
        nsc = sc
        while ssc != '':
            assc = class_dict_by_name[nsc]['superclasses']
            ssc = '' if len(assc) == 0 else str(assc[0])
            if ssc != '':
                sscl = [ssc] + sscl
            nsc = ssc
        for s in sscl:
            if s not in sorted_classes:
                sorted_classes.append(s)
sorted_classes.extend(non_rooted_classes)

print(json.dumps(sorted_classes, indent=4, sort_keys=False))

import os
import textwrap

filepath = os.getcwd()
def MakeFile(file_name, class_dict):
    with open(file_name, 'w') as f:
        for c in class_dict:
            cd = class_dict_by_name[c] 
            if len(cd['superclasses']) == 0:
                sc = ''
            else:
                sc = cd['superclasses'][0].split('.')[-1].replace('CRAM', '')
            if sc == 'Thing':
                sc = ''
            cname = c.split('.')[-1].replace('CRAM', '')
            if cname == 'FailureDiagnosis' and sc == 'FailureDiagnosis':
                continue
            if len(cd['comment']) == 0:
                cd['comment'] = ''
            else:
                cd['comment'] = cd['comment'][0]
            f.write(textwrap.dedent(f'''\
                class {cname}({sc}):
                    \"\"\"{cd["comment"]}\"\"\"
                    def __init__(self):
                        super().__init__()        
                    '''))
    print('Execution completed.')

MakeFile(outfile, sorted_classes[1:])