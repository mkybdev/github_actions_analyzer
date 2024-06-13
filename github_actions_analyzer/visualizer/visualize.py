output = ""


def out(s):
    global output
    output += s


uniq = 1


def getID():
    global uniq
    n = str(uniq)
    uniq += 1
    return n


def asAttr(attr, val):
    escaped = val.replace('"', '\\"')  # " -> \"
    return " [" + attr + '="' + escaped + '"]'


def render(ast, name):

    lab = ""
    edges = []  # (from, to, attr)

    if type(ast) is dict:
        for key, val in ast.items():

            if type(val) is dict:
                child = getID()
                edges.append((name, child, asAttr("label", key)))
                render(val, child)

            elif type(val) is list:
                last = None
                for i in val:
                    child = getID()
                    edges.append((name, child, asAttr("label", key)))
                    render(i, child)
                    if last is not None:
                        edges.append((last, child, asAttr("style", "dashed")))
                    last = child

            else:
                lab += str(key) + ": " + str(val) + "\\n"

    else:
        lab += str(ast)

    # output vertex
    out(name + asAttr("label", lab) + ";\n")

    # output edges
    for src, dest, attr in edges:
        out(src + " -> " + dest + attr + ";\n")


def visualize(ast, name: str):
    out("digraph graphname {\n")

    render(ast, name)

    out("}\n")
    global output
    return output
