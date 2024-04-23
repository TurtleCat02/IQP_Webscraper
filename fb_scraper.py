import json
import os
import re

import facebook_page_scraper as fps
import pandas as pd
import pytesseract as pt
import requests

browser = "firefox"

with open("facebooks.txt", "r") as f:
    facebooks = f.readlines()

for facebook in facebooks:
    name = facebook.strip()
    with open(f"./output/{name}.txt", 'wb') as textfile:
        scraper = fps.Facebook_scraper(name, posts_count=3, browser=browser)
        j = json.loads(scraper.scrap_to_json())
        for _, post in j.items():
            textfile.write(post["content"].encode("utf-8"))
            for image in post["image"]:
                filename = re.search(r'/([\w%.@_-]+[.](jpg|JPG|gif|png|PNG))', image)
                if not filename:
                    print("Regex didn't match with the url: {}".format(image))
                    continue
                os.makedirs(f"./output/{name}/", exist_ok=True)
                imgpath = f"./output/{name}/{filename.group(1)}"
                if not os.path.exists(imgpath):
                    with open(imgpath, 'wb') as f2:
                        print(f"URL: {image}")
                        response = requests.get(image)
                        f2.write(response.content)
                else:
                    print(f"File exists: {imgpath}")
                try:
                    data = pt.image_to_data(imgpath, lang="eng+chi_tra", config="--psm 11",
                                            output_type=pt.Output.DATAFRAME, timeout=4)
                    text: pd.Series = data.text[data.conf > 75]
                    print(f"Text: {text.values}")
                    # print(f"Data: {data}")
                except pt.TesseractError as error:
                    text = pd.Series()
                    print(error.message)
                if text is not None and not text.empty:
                    textfile.write("\n".join([line.strip() for line in text if (not line.isspace() and line)]).encode("utf-8"))
                    textfile.write("\n".encode("utf-8"))
