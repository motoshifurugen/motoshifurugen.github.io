import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path

URL = "https://e-roomjp.com/experiences/"
page = requests.get(URL)

persons = []

soup = BeautifulSoup(page.content, "html.parser")
contents = soup.find(id = "content")
if contents: 
    posts = contents.find_all("article", class_= "post")
    for i in range(4):
        url = posts[i].find("a").get('href')
        perPage = requests.get(url)
        mainImg = posts[i].find("img").get('src')

        food = BeautifulSoup(perPage.content, "html.parser")
        title = food.find(class_="pageTitle").find("h1").text.strip()
        name = title.split('（')[0]
        gender = title.split('（')[1].split('）')[0] 
        age = title.split('年齢：')[1].split('留学期間')[0].strip() 
        period = title.split('留学期間：')[1]
        personPage = requests.get(url)

        exp = BeautifulSoup(personPage.content, "html.parser")
        experience = exp.find("article")
        if experience:
            def contains_advice(t):
                if t and "卒業生からのアドバイス"in t:
                    return True
                return False
            span = exp.find("span", string=contains_advice)
            advice = span.find_next("p").text
            if len(advice) > 100:
                advice_short = advice[:100] + '...'
            else:
                advice_short = advice
        person_data = {
            "name": name,
            "gender": gender,
            "age": age,
            "period": period,
            "img": mainImg,
            "url": url,
            "advice": advice_short
        }
        persons.append(person_data)
        
    output_path = Path(__file__).parent.parent/"contents"/"person.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(persons, f, ensure_ascii=False, indent=2)

