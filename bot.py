import requests

def info(arg=None):
    if arg is None:
        return commands['!помощь']['desc']
    else:
        arg = f"!{arg}"
        return commands[arg]['desc'] if arg in commands else "Такой комманды нет"

def weather(arg=None):
    return 'Да да'

def get_status(arg=None, url='http://127.0.0.1:5000'):
    response = requests.get(url + '/status')
    return f'Текущее время на сервере: {response.json()["server_current_time"]} \
    \nКол-во сообщений: {response.json()["current_messages"]} \nВремя запуска сервера:\
    {response.json()["server_start_time"]}'
    

commands = {
    "!погода":{
        "desc": "Выводит информацию о погоде",
        "action": weather
    },
    "!помощь":{
        "desc": "Выводит информацию о нужной команде",
        "action": info
    },
    "!статус":{
        "desc": "Возвращает статус сервера",
        "action": get_status
    },
}

while True:
    inp = input().replace('\t', '').replace('\n', '').split(' ')
    inp = [ch for ch in inp if ch]
    if inp == []:
        break
    name = None
    arg = None
    try:
        name, arg = inp[0].lower(), inp[1].lower()
    except:
        name = inp[0].lower()
    if len(inp) <= 2:
        arg = None if arg == "" else arg
        if name == "выход":
            break
        if name in commands:
            if arg is not None:
                print(commands[name]['action'](arg))
            else:
                print(commands[name]['action']())
        else:
            print("Такой команды нет")
    else:
        print("Слишком много аргументов")
