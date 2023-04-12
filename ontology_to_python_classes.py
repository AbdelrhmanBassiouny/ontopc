import owlready2 as owlr
import argparse


parser = argparse.ArgumentParser(description='Convert an OWL ontology to a python class file.')
parser.add_argument('--input', '-i', type=str, required=True, help='Input OWL file')
parser.add_argument('--output', '-o', type=str, required=True, help='Output python file')
parser.add_argument('--add_parent', '-ap', type=str, default=None, help='Add a parent class to all classes in the ontology.')
args = parser.parse_args()
infile = args.input
outfile = args.output
add_parent = args.add_parent

onto = owlr.get_ontology(infile)
onto.load()

# Find superclasses
class_list = list(onto.classes())
class_dicts= []
subclasses = {}
class_dict_by_name = {}
class_dict_by_name['owl.Thing'] = {'superclasses': [], "comment": []}
if add_parent is not None:
    class_dict_by_name[add_parent] = {'superclasses': [], "comment": []}
for c in class_list:
    superclasses = c.is_a
    superclasses = [str(s) for s in superclasses]
    if add_parent is not None and len(superclasses) == 0:
        superclasses.append(add_parent)
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
if add_parent is not None:
    sorted_classes.append(add_parent)
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


import os
import textwrap

filepath = os.getcwd()
def MakeFile(file_name, class_dict):
    with open(file_name, 'w') as f:
        for c in class_dict:
            cd = class_dict_by_name[c] 
            if len(cd['superclasses']) == 0:
                sc = '' if add_parent is None else add_parent
            else:
                sc = cd['superclasses'][0].split('.')[-1].replace('CRAM', '')
            if sc == 'Thing':
                sc = '' if add_parent is None else add_parent
            cname = c.split('.')[-1].replace('CRAM', '')
            if cname == sc:
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