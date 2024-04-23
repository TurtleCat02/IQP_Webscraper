import os
import re

import pandas as pd
import pytesseract as pt
import requests
from bs4 import BeautifulSoup

with open("websites.txt", "r") as f:
    websites = f.readlines()

for website in websites:
    site_name = re.search(r'https://([\w.-]+)', website).group(1)
    response = requests.get(website.strip())
    soup = BeautifulSoup(response.content, "lxml")

    img_tags = soup.find_all('img')

    urls: list[str] = list()
    for img in img_tags:
        try:
            urls.append(img['src'])
        except KeyError:
            print(f"Oops: {img}")

    with open(f"./output/{site_name}.txt", "wb") as f:
        f.write(
            "\n".join([line.strip() for line in soup.get_text().splitlines() if (not line.isspace() and line)]).encode(
                "utf-8"))
        f.write("\n\n---IMAGE TEXT----\n".encode("utf-8"))

        for url in urls:
            filename = re.search(r'/([\w%.@_-]+[.](jpg|JPG|gif|png|PNG))', url)
            if not filename:
                print("Regex didn't match with the url: {}".format(url))
                continue
            os.makedirs(f"./images/{site_name}/", exist_ok=True)
            filename = f"./images/{site_name}/{filename.group(1)}"
            if not os.path.exists(filename):
                with open(filename, 'wb') as f2:
                    if 'http' not in url:
                        if url.startswith("//"):
                            url = 'http:{}'.format(url)
                        else:
                            url = '{}{}'.format(website.strip(), url)

                    print(f"URL: {url}")
                    response = requests.get(url)
                    f2.write(response.content)
            else:
                print(f"File exists: {filename}")
            try:
                data = pt.image_to_data(filename, lang="eng+chi_tra", config="--psm 11", output_type=pt.Output.DATAFRAME, timeout=4)
                text: pd.Series = data.text[data.conf > 75]
                print(f"Text: {text.values}")
                # print(f"Data: {data}")
            except pt.TesseractError as error:
                text = pd.Series()
                print(error.message)
            if text is not None and not text.empty:
                f.write("\n".join([line.strip() for line in text if (not line.isspace() and line)]).encode("utf-8"))
                f.write("\n".encode("utf-8"))
