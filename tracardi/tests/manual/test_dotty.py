from dotty_dict import dotty

dot = dotty({"a":None})
try:
    print('a.h' in dot)
except TypeError:
    print('er')