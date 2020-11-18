import requests


def info(arg=None):
    if arg is None:
        return "!помощь - " + commands['!помощь']['desc']
    else:
        arg = f"!{arg}"
        return (arg + " - " + commands[arg]['desc']) if arg in commands else arg + " - Такой команды нет"


def weather(arg=None):
    return 'Да да'


def get_status(arg=None, url='http://127.0.0.1:5000'):
    response = requests.get(url + '/status')
    if response.json()['status'] == "OK":
        return f'Кол-во сообщений: {response.json()["current_messages"]} \
            \nВремя запуска сервера: {response.json()["server_start_time"]}\nКол-во пользователей:{response.json()["current_users"]}'
    else:
        return "Статус сервера на данный момент: " + response.json()["status"]


commands = {
    "!погода": {
        "desc": "Выводит информацию о погоде",
        "action": weather
    },
    "!помощь": {
        "desc": "Выводит информацию о нужной команде",
        "action": info
    },
    "!статус": {
        "desc": "Возвращает статус сервера",
        "action": get_status
    },
}

if __name__ == "__main__":
    print(commands['!статус']['action']())
    exit()
    while True:
        inp = input().replace('\t', '').replace('\n', '')
        inp = [ch for ch in inp.split(' ') if ch]
        if inp == []:
            break
        name, arg = None, None
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
