# src/utils.py
def pretty_print_ast(node, indent=0):
    prefix = "  " * indent
    
    output = ""

    if isinstance(node, tuple):
        node_type = node[0]
        children = node[1:]

        output += f"{prefix}{node_type}:\n"

        for i, child in enumerate(children):
            output += f"{prefix}  [{i}] "

            if isinstance(child, (str, int, float, bool)) or child is None:
                output += repr(child)
                output += "\n"
            else:
                output += "\n"
                output += pretty_print_ast(child, indent + 2)

    elif isinstance(node, list):
        output += f"{prefix}list:\n"
        for i, item in enumerate(node):
            output += f"{prefix}  [{i}]\n"
            output += pretty_print_ast(item, indent + 2)

    else:
        output += f"{prefix}{repr(node)}\n"
    return output