""" docstring! """

def string2float(cell):
    if cell == "":
        ret = None # Save to DB as null -- passing "" to DB would raise exception
    else:
        ret = float(cell)
    return ret