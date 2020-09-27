import hashlib

users = {
    'Jack': {
        'password': hashlib.md5('1234'.encode()).hexdigest(),
        'online': False
        },
    'Jack2': {
        'password': hashlib.md5('5678'.encode()).hexdigest(),
        'online': False
    },
    'Jack3': {
        'password': hashlib.md5('1234'.encode()).hexdigest(),
        'online': False
        },
    'Jack4': {
        'password': hashlib.md5('5678'.encode()).hexdigest(),
        'online': False
    }
}

print(
        
)