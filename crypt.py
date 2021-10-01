# Messenger
# Copyright (C) 2021  ChazGrant (https://github.com/ChazGrant)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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