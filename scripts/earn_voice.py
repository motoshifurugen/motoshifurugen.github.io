import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
import re

URL = "https://e-roomjp.com/experiences/"
page = requests.get(URL)

slideImg = []
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
        experience = exp.find(class_="sentry")
        
        if experience:
            # アドバイスを回収
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

            img_data =[]
            mainImg_src = []
            for img_tag in experience.find_all("img"):
                src = img_tag.get('src')
                if src:
                    original_src = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', src)
                    res = requests.get(original_src)
                    img = Image.open(BytesIO(res.content))
                    w,h = img.size
                    img_data.append({"src":original_src, "width":w, "height": h, "file_size": len(res.content)})
            img_data.sort(key=lambda x: x["width"])
            mainImg_src = img_data[0]["src"]
            img_data.sort(key=lambda x: (x["width"],x["file_size"] / (x["width"] * x["height"])), reverse=True)
            slideImg_src = [item["src"] for item in img_data[:2]]
            slideImg.extend(slideImg_src)

        person_data = {
            "name": name,
            "gender": gender,
            "age": age,
            "period": period,
            "mainImg_src":mainImg_src, 
            "url": url,
            "advice": advice_short
        }
        persons.append(person_data)
        
    output_data = {"persons": persons, "slideImg": slideImg}
    output_path = Path(__file__).parent.parent/"contents"/"person.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

