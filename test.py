import hashlib

result = hashlib.md5('Игорь пидор'.encode()) 
print(result.hexdigest())
result
new = input()
new_result = hashlib.md5(new.encode())
print(new_result.digest() == result.digest())