
def RC(value, tolerance=5.0, power=None, package="0603",pkgcode="07"):
    res = {"manufacturer": "Yageo"}
    suffix = ['R', 'K', 'M']
    digits = 3 if tolerance < 5 else 2
    while value >= 1000:
        value = value/1000.
        suffix.pop(0)
    suffix = suffix[0]
    whole = str(int(value))
    decimal = str(round((value-int(value)) * 10**(digits-len(whole))))
    v_str = (whole+suffix+decimal).strip("0")
    if v_str == "R": v_str = "0R"
    if tolerance == 0.5:
        t_str = 'D'
    elif tolerance == 1.0:
        t_str = 'F'
    else:
        t_str = 'J'
    res["MPN"] = "RC{}{}R-{}{}L".format(package, t_str, pkgcode, v_str)
    return res

_cc_voltages = {6300: '5', 10000: '6', 16000: '7', 25000: '8', 50000: '9'}


def CC_X7R(value, tolerance=10, voltage=16, package='0603', pkgcode='R'):
    res = {"manufacturer": "Yageo"}
    c_pf = int(value * 1e12)
    exp = 0
    while c_pf >= 100:
        exp += 1
        c_pf /= 10
    c_str = str(int(c_pf))+str(exp)
    v_mv = round(voltage*1e3)
    v_str = _cc_voltages.get(v_mv, '9')
    t_str = 'K'
    res["MPN"] = "CC{}{}{}X7R{}BB{}".format(package, t_str, pkgcode, v_str, c_str)
    return res
