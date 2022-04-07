src_competences = 'referentiel-competences.md'
dst_competences = 'referentiel-competences.html'
src_ues = 'liste-ue.md'
dst_ues = 'liste-ues.html'
css_file = 'essai-css.css'

def trees_of_md_lines(lines):
    children_at_level = [[]]
    for line in lines:
        line = line.strip()
        if line == '' : continue
        try : 
            level = line.rindex('#') + 1
        except:
            children_at_level[-1].append(line.strip())
            continue
        s2 = line[level:].strip()
        children = []
        newtree = (s2, children)
        assert(level - 1 < len(children_at_level)) # sinon on saute un niveau
        children_at_level[level - 1].append(newtree)
        try:
            children_at_level[level] = children
        except:
            children_at_level.append(children)
        children_at_level = children_at_level[:level + 1]
    return children_at_level[0]

def single_out_verb_in(s):
    beg, fin = s.index('*'), s.rindex('*')
    verb = s[beg+2: fin-1]
    complement = s[fin+1:]
    return (verb, complement)

def single_out_tag_in(s):
    beg, fin = s.rindex('['), s.rindex(']')
    ue_tag = s[beg+1: fin]
    ue_desc = s[:beg].strip()
    return (ue_desc, ue_tag)

def wrap_in_span(s, classe):
    return f"""<span class="{classe}">
{s}
</span>"""

def html_of_md_string(s):
    if 'RNCP' in s: return wrap_in_span(s, 'RNCP')
    elif '**' in s:
        (verb, complement) = single_out_verb_in(s)
        return wrap_in_span(verb, 'verb') + ' ' + wrap_in_span(complement, 'complement')
    elif '[' in s:
        (ue_desc, ue_tag) = single_out_tag_in(s)
        return wrap_in_span(ue_desc, 'ue_desc') + ' ' + wrap_in_span(ue_tag, 'ue_tag')
    else:
        return s

def html_of_summary(s, level):
    return f"""<span class="level{level}">
{html_of_md_string(s)}
</span>"""

def html_of_trees(trees, level=0):
    return "\n".join([html_of_tree(t, level) for t in trees])

def html_of_tree(tree, level=0):
    if type(tree) == str:
        return html_of_md_string(tree) + ' <br>'
    else :
        (summary, trees) = tree
        return f"""<details>
<summary>
{html_of_summary(summary, level)}
</summary>
{html_of_trees(trees, level+1)}
</details>"""

def wrap(body, css_file=None, standalone=False):
    css_content = ''
    if css_file != None:
        if standalone:
            with open(css_file) as fd:
                css_content = f"<style>\n{fd.read()}</style>\n"
        else:
            css_content = f'<link rel="stylesheet" href="{css_file}">'
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
{css_content}
</head>
<body>
{body}
</body>
</html>
"""

def iter_on_competence_trees(trees):
    for icomp in range(len(trees)):
        (competence, niveaux_competence) = trees[icomp]
        niveaux_competence = [x for x in niveaux_competence if type(x)==tuple]
        for iniv in range(len(niveaux_competence)):
            (niv, acs) = niveaux_competence[iniv]
            for iac in range(len(acs)):
                (ac, ues) = acs[iac]
                ues = [ue.strip() for line in ues for ue in line.split(' ')]
                yield {
                    'icomp': icomp, 'iniv':iniv, 'iac': iac,
                    'competence': competence,
                    'niv': niv,
                    'ac': ac,
                    'ues': ues
                }

def matrix_of_competence_trees(trees, liste_ues):
    M = {}
    for item in iter_on_competence_trees(trees): 
        ues = [x.strip() for x in " ".join(item['ues']).split(' ')]
        desc = f'AC{item["icomp"]+1}.{item["iniv"]+1}.{item["iac"]+1}'
        M[desc] = [ue in ues for ue in liste_ues]
    return M

def csv_of_matrix(M, liste_ues):
    res = ';' + ";".join(f'"{ue}"' for ue in liste_ues) + '\n'
    for desc in M:
        res += desc + ';' + ";".join('X' if x else '' for x in M[desc]) + '\n'
    return res

def tag_of_ue(ue):
    i, j = ue.index('['), ue.rindex(']')
    return ue[i+1:j]

def liste_ues_of_trees(ues_trees):
    res = []
    for (_, ues) in ues_trees:
        for (ue,_) in ues:
            res.append(tag_of_ue(ue))
    return res

def dic_ues_of(liste_ues, competence_trees):
    res = {}
    for ue in liste_ues:
        res[ue] = {
            'competence':set(), 
            'niv':set(),
            'ac':set()
        }
    for item in iter_on_competence_trees(competence_trees):
        for ue in item['ues']:
            ue = ue.strip()
            for key in res[ue].keys():
                res[ue][key].add(item[key])
    return res

def add_competences(dic_ues, ue):
    (summary, details) = ue
    (ue_desc, ue_tag) = single_out_tag_in(summary)
    det = list(details)
    for k in ['competence', 'niv', 'ac']:
        for i in dic_ues[ue_tag][k]:
            det.append(i)
    return (summary, det)

def trees_of_ues_trees(dic_ues, ues_trees):
    trees = []
    for (sem, ues) in ues_trees:
        sem_desc  = wrap_in_span(sem, 'semestre')
        ues2 = [add_competences(dic_ues, ue) for ue in ues]
        trees.append((sem_desc, ues2))
    return trees

def html_of_ues(dic_ues, ues_trees):
    t = trees_of_ues_trees(dic_ues, ues_trees)
    return html_of_trees(t)

if __name__ == '__main__':
    with open(src_competences) as fd:
        competence_trees = trees_of_md_lines(fd)
    with open(src_ues) as fd:
        ues_trees = trees_of_md_lines(fd)
    liste_ues = liste_ues_of_trees(ues_trees)
    dic_ues = dic_ues_of(liste_ues, competence_trees)
    print(dic_ues)
    input()
    ref_comp_html = wrap(html_of_trees(competence_trees), css_file=css_file, standalone=True)
    with open(dst_competences, "w") as fd: fd.write(ref_comp_html)
    liste_ues_html = wrap(html_of_ues(dic_ues, ues_trees))
    with open(dst_ues, "w") as fd: fd.write(liste_ues_html)
#    liste_ues = ['SYS1', 'SYS2', 'RESEAU']
#    M = matrix_of_competence_trees(competence_trees, liste_ues)
#    print(csv_of_matrix(M, liste_ues))