import requests

def info(arg=None):
    if arg is None:
        return commands['Помощь']['desc']
    else:
        return commands[arg]['desc']

def weather(arg=None):
    return 'Да да'

def get_status(arg=None, url='http://127.0.0.1:5000'):
    response = requests.get(url + '/status')
    return f'Текущее время на сервере: {response.json()["server_current_time"]} \
    \nКол-во сообщений: {response.json()["current_messages"]} \nВремя запуска сервера:\
    {response.json()["server_start_time"]}'
    

commands = {
    "!Погода":{
        "desc": "Выводит информацию о погоде",
        "action": weather
    },
    "!Помощь":{
        "desc": "Выводит информацию о нужной команде",
        "action": info
    },
    "!Статус":{
        "desc": "Возвращает статус сервера",
        "action": get_status
    },
}

inp = input()
arg = None
try:
    name, arg = inp.split(' ')
except:
    name = inp
if name in commands:
    if arg is not None:
        print(commands[name]['action'](arg))
    else:
        print(commands[name]['action']())