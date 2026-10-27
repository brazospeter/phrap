# vlookup with linear interpolation
# assumes xlist and ylist are ordered

def extract(v, xlist, ylist):
    value_found = False
    if xlist[0] <= v <= xlist[len(xlist) - 1]:
        for i in range(len(xlist) - 1):
            if xlist[i] <= v <= xlist[i + 1]:
                value_found = True
                break
    else:
        if v <= xlist[0]:
            i = 0
        elif v >= xlist[len(xlist) - 1]:
            i = len(xlist) - 1
    if value_found:
        slope = (ylist[i] - ylist[i + 1]) / (xlist[i] - xlist[i + 1])
        result = ylist[i] + (slope * (v - xlist[i]))
        if result < min(ylist) or max(ylist) < result:
            print("Error: vlookup2")
        return ylist[i] + (slope * (v - xlist[i]))
    else:
        return ylist[i]