import requests
import os

print(len("Текущее время на сервере: 13:03:08 13/11/2020 Кол-во сообщений: 18 Время запуска сервера:"))


files = [file for _, _, file in os.walk("static/" + "JUST TALKING")][0]


print(files)


input()
# filename = "testExcel.xlsx"

# with open("Загрузки/" + filename, "rb") as file:

#     content = file.read()

#     res = requests.get("http://127.0.0.1:5000/upload", data=content, params={
#         "name": "fff.xlsx"
#     })

#     if "nameIsTaken" in res.json():
#         print("Cant't upload this file, try to change the name of it")

# # res = requests.get("http://127.0.0.1:5000/download", json={
# #     'filename': 'send.docx'
# # })
# # if res.status_code == 200:
# #     with open("Загрузки/receive.docx", "wb") as out:
# #         out.write(res.content)
# # output.write(res.content)

# # with open(file) as file:
# # 	file.close()
