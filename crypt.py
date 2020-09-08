
eng = 'abcdefghijklmnopqrstuvwxyz'
ENG = eng.upper()

rus = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
RUS = rus.upper()

key = 666

def encrypt(msg, shift):
    res = ''
    for char in msg:
        if char in eng:
            res += eng[(eng.index(char) + shift) % len(eng)]
        elif char in ENG:
            res += ENG[(ENG.index(char) + shift) % len(ENG)]
        elif char in rus:
            res += rus[(rus.index(char) + shift) % len(rus)]
        elif char in RUS:
            res += RUS[(RUS.index(char) + shift) % len(RUS)]
        else:
            res += char
    return res


def decrypt(msg, shift):
    res = ''
    for char in msg:
        if char in eng:
            res += eng[(eng.index(char) - shift) % len(eng)]
        elif char in ENG:
            res += ENG[(ENG.index(char) - shift) % len(ENG)]
        elif char in rus:
            res += rus[(rus.index(char) - shift) % len(rus)]
        elif char in RUS:
            res += RUS[(RUS.index(char) - shift) % len(RUS)]
        else:
            res += char
    return res