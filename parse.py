from bs4 import BeautifulSoup
import requests


req = requests.get("https://ru.indeed.com/Психолог-jobs")
soup = BeautifulSoup(req.text, 'html.parser')
print(soup)
exit()
companies_name = soup.find_all("a", class_="tapItem fs-unmask result job_8a0792b0634de3bc resultWithShelf sponTapItem desktop")
link = list()
print(len(companies_name))
for name in companies_name:
	if "/rc/clk" in name:
		link.append(f"https://ru.indeed.com/viewjob?" + name[0].get('href').split("?")[1].split("&")[0] + "&tk=1" + name[0].get('href').split("?")[1].split("&")[1])
print(link)