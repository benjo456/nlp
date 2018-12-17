import OntologyTree
def addFileToTreeCat(t,cat,id):
    #if isinstance(tree,list):
    #    tree.append(cat)
    for k,v in t.items():
        if k == cat:
            v.append(id)
            return
        elif not v:
            continue
        else:
            addFileToTreeCat(v,cat,id)

tree = OntologyTree.tree
addFileToTreeCat(tree,"software engineering",3)
addFileToTreeCat(tree,"ai",5)
print(tree)