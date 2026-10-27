# vlookup without linear interpolation
# assumes xlist and ylist are ordered

def extract(v, xlist, ylist):
    value_found = False
    if xlist[0] <= v <= xlist[len(xlist) - 1]:
        for i in range(len(xlist) - 1):
            if xlist[i] <= v <= xlist[i + 1]:
                value_found = True
                break
    else:
        print("Warning: vlookup1 out of bounds")
        if v <= xlist[0]:
            value_found = True
            i = 0
        if v >= xlist[len(xlist) - 1]:
            value_found = True
            i = len(xlist) - 1
    
    if value_found:
        return ylist[i]
    else:
        print("Error: vlookup1")