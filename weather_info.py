from slacker import Slacker
import random
import urllib.request
from bs4 import BeautifulSoup
import re
import json

# 슬랙 토큰으로 객체 생성
token = '토큰 값'
slack = Slacker(token)

#기온에 따른 옷 추천
def choose_clothes(temperature):
    photo_num = random.randrange(1, 21)
    photo_name = ".png"
    if(temperature > 23):
        photo_name = "summer" + str(photo_num) + photo_name
    elif(temperature > 10):
        photo_name = "middle" + str(photo_num) + photo_name
    else:
        photo_name = "winter" + str(photo_num) + photo_name

    slack.files.upload(photo_name, channels="#day4")

#날씨 정보
def weather_information(text):
    url = "https://weather.naver.com/rgn/cityWetrCity.nhn?cityRgnCd=CT001013"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    rainfull = soup.find(class_="w_now2").find("p").find_all("strong")
    text = soup.find(class_="w_now2").find(class_="fl").text
    info = soup.find(class_="w_now2").find("em").text
    info_result = ''.join(info.split())

    temp_ext = re.findall("\d+", info_result)[0]  # 문자열에서 숫자만 추출(온도)
    weat_ext = re.compile("[^0-9]").findall(info_result)  # 문자열에서 숫자를 제외한 문자만 추출해 list에 집어넣음(날씨)

    if "-" in info_result:
        temp = "-" + temp_ext
        del weat_ext[0:3]
        weat = "".join(weat_ext)
    else:
        temp = temp_ext
        del weat_ext[0:2]
        weat = "".join(weat_ext)

    if "미세먼지" in text:
        dust = soup.find(class_="w_now2").find("a").find("em").text  # 미세먼지
    else:
        dust = "정보없음"

    if len(rainfull) == 1:
        rainfull_prob = rainfull[0].text  # 강수확률

    else:
        rainfull_prob = rainfull[1].text  # 강수확률

    response1 = [
        "서울" + "의 오늘 날씨 입니다 "
        + "1.온도:" + temp + "도 "
        + "2.날씨:" + weat
        + "3.미세먼지:" + dust
        + "4.강수확률:" + rainfull_prob + "%"
    ]

    tom_info_am = soup.find_all("tbody")[1].find_all("div")[2]  # 내일 우전날씨 정보
    tom_info_pm = soup.find_all("tbody")[1].find_all("div")[3]  # 내일 오후날씨 정보

    tom_temp_am = tom_info_am.find("span", class_="temp").text  # 내일 오전 온도
    tom_temp_pm = tom_info_pm.find("span", class_="temp").text  # 내일 오후 온도

    tom_weat_am_a = tom_info_am.find_all("li")[1].text
    tom_weat_pm_a = tom_info_pm.find_all("li")[1].text

    tom_weat_am = "".join(re.compile("[^0-9]").findall(tom_weat_am_a)).replace("강수확률", "", 1).replace("%", "",
                                                                                                      1)  # 내일 오전 날씨
    tom_weat_pm = "".join(re.compile("[^0-9]").findall(tom_weat_pm_a)).replace("강수확률", "", 1).replace("%", "",
                                                                                                      1)  # 내일 오후 날씨

    tom_rainfull_prob_am = tom_info_am.find_all("li")[1].find("strong").text  # 내일 오전 강수확률
    tom_rainfull_prob_pm = tom_info_pm.find_all("li")[1].find("strong").text  # 내일 오후 강수확률

    response2 = [
        "서울" + "의 내일 날씨 입니다 "
        + "1.온도:" + tom_temp_pm + "도 "
        + "2.날씨:" + tom_weat_am
        + "3.강수 확률: " + tom_rainfull_prob_am
    ]

    response2 = json.dumps(response2, ensure_ascii=False)

    print(response1)
    print(response2)

