src_competences = 'referentiel-competences.md'
src_ues = 'liste-ue.md'
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

def single_out_verb_in_tree(tree):
    (summary, details) = tree
    beg, fin = summary.index('*'), summary.rindex('*')
    verb = summary[beg+2: fin-1]
    rest = summary[fin+1:]
    return (verb, [rest] + single_out_verb_in_trees(details))

def single_out_verb_in_trees(trees):
    def f(x):
        if type(x) == tuple:
            return single_out_verb_in_tree(x)
        else:
            return x
    return list(map(f, trees))

def html_of_md_string(s): 
    return s

def html_of_trees(trees, level=0):
    return "\n".join([html_of_tree(t, level) for t in trees])

def html_of_tree(tree, level=0):
    if type(tree) == str:
        return html_of_md_string(tree) + ' <br>'
    else :
        (summary, trees) = tree
        return f"""<details>
<summary>
<h{level+1}>
{html_of_md_string(summary)}
</h{level+1}>
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

def matrix_of_competence_trees(trees, liste_ues):
    M = {}
    for icomp in range(len(trees)):
        (competence, niveaux_competence) = trees[icomp]
        niveaux_competence = [x for x in niveaux_competence if type(x)==tuple]
        for iniv in range(len(niveaux_competence)):
            (niv, acs) = niveaux_competence[iniv]
            for iac in range(len(acs)):
                print(acs[iac])
                (ac, ues) = acs[iac]
                ues = [x.strip() for x in " ".join(ues).split(' ')]
                desc = f'AC{icomp+1}.{iniv+1}.{iac+1}'
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

if __name__ == '__main__':
    with open(src_competences) as fd:
        competence_trees = trees_of_md_lines(fd)
    with open(src_ues) as fd:
        ues_trees = trees_of_md_lines(fd)
    liste_ues = liste_ues_of_trees(ues_trees)
#    trees = single_out_verb_in_trees(trees)
#    print(wrap(html_of_trees(trees), css_file=css_file, standalone=True))
    liste_ues = ['SYS1', 'SYS2', 'RESEAU']
    M = matrix_of_competence_trees(competence_trees, liste_ues)
    print(csv_of_matrix(M, liste_ues))