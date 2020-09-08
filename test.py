def removeSpaces( string):
        '''
        Удаляет все пустые символы в строке
        '''
        for n in string:
            string = string.lstrip(' ')
            string = string.rstrip(' ')
            string = string.lstrip('\n')
            string = string.rstrip('\n')
        return string

print(removeSpaces('''


        f''' ))