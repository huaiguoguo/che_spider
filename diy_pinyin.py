#!/usr/bin/env python
# coding=utf-8
def get_Mutil_CnFirstLetter(str):
    index = 0;
    strReturnCn = ""
    print
    "len(str)=%s" % len(str)
    while index < (len(str) - 1):
        # print "strReturnCn=%s" % strReturnCn
        # print get_cn_first_letter(str[index:index+2],"GBK")
        # print str[index:index+2]
        strReturnCn += get_cn_first_letter(str[index:index + 2], "GBK")
        index += 2;
    return strReturnCn;


def get_cn_first_letter(str, codec="UTF8"):
    if codec != "GBK":
        if codec != "unicode":
            str = str.decode(codec)
        str = str.encode("GBK")
    if str < "/xb0/xa1" or str > "/xd7/xf9":
        return ""
    if str < "/xb0/xc4":
        return "a"
    if str < "/xb2/xc0":
        return "b"
    if str < "/xb4/xed":
        return "c"
    if str < "/xb6/xe9":
        return "d"
    if str < "/xb7/xa1":
        return "e"
    if str < "/xb8/xc0":
        return "f"
    if str < "/xb9/xfd":
        return "g"
    if str < "/xbb/xf6":
        return "h"
    if str < "/xbf/xa5":
        return "j"
    if str < "/xc0/xab":
        return "k"
    if str < "/xc2/xe7":
        return "l"
    if str < "/xc4/xc2":
        return "m"
    if str < "/xc5/xb5":
        return "n"
    if str < "/xc5/xbd":
        return "o"
    if str < "/xc6/xd9":
        return "p"
    if str < "/xc8/xba":
        return "q"
    if str < "/xc8/xf5":
        return "r"
    if str < "/xcb/xf9":
        return "s"
    if str < "/xcd/xd9":
        return "t"
    if str < "/xce/xf3":
        return "w"
    if str < "/xd1/x88":
        return "x"
    if str < "/xd4/xd0":
        return "y"
    if str < "/xd7/xf9":
        return "z"


if __name__ == '__main__':
    s = "人"
    print(s.encode("utf-8"))
    # print( get_Mutil_CnFirstLetter("大埔的d") )
    # print
    # get_cn_first_letter("们", "GBK")
    # print
    # get_cn_first_letter("他", "GBK")
    # print
    # get_cn_first_letter("是", "GBK")
    # print
    # get_cn_first_letter("大", "GBK")
    # print
    # get_Mutil_CnFirstLetter("大埔的d")