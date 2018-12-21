# -*- coding: utf-8 -*
import requests
###
import json
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template, jsonify
import random
from slacker import Slacker

# 슬랙 토큰으로 객체 생성
token = 'xoxb-503818135714-506719126544-4GYbCgOP0WWwiVbeRcu7lMVb'
slack = Slacker(token)

app = Flask(__name__)
slack_token = 'xoxb-503818135714-506719126544-4GYbCgOP0WWwiVbeRcu7lMVb'
slack_client_id = '503818135714.507453486050'
slack_client_secret = '000a42568d8f21b437b7320175dda73f'
slack_verification = 'PR5MTEUUU3wj5ArHBHB8kV8X'
sc = SlackClient(slack_token)

######

temperatureValue = 0


# 기온에 따른 옷 추천
def choose_clothes(temperature):
    # temperature = "30"
    photo_num = random.randrange(1, 11)
    photo_name = ".png"

    if (int(temperature) > 23):
        photo_name = "summer" + str(photo_num) + photo_name
    elif (int(temperature) > 10):
        photo_name = "middle" + str(photo_num) + photo_name
    else:
        photo_name = "winter" + str(photo_num) + photo_name

    photo_name = "./imgs/" + photo_name
    #    print("넘어온 온도값:::::::"+temperature)
    return2hundreds()
    slack.files.upload(photo_name, channels="#day4")

    return "오늘 기온은 " + temperature + "℃ 입니다.\n오늘은 이렇게 입는 걸 추천 드려요!"


def return2hundreds():
    return make_response("끝!", 200, {"X-Slack-No-Retry": 1})


# ######


###
def get_answer(text, user_key):
    if "오늘" in text:
        text = "today"
    elif "내일" in text:
        text = "tomorrow"

    data_send = {
        'query': text,
        'sessionId': user_key,
        'lang': 'ko',
    }
    data_header = {
        'Authorization': 'Bearer 9517c5e431be412790bd1e0a1b23ffcb',
        'Content-Type': 'application/json; charset=utf-8'
    }
    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)
    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'
    data_receive = res.json()
    result = {
        "speech": data_receive['result']['fulfillment']['speech'],
        "intent": data_receive['result']['metadata']['intentName']
    }
    real_result = result['speech']
    # if(real_result == "music"):
    #     return _crawl_naver_keywords(real_result)
    return real_result


###


# 크롤링 함수 구현하기
def _crawl_weather_today(text):
    url = "https://weather.naver.com/rgn/cityWetrCity.nhn?cityRgnCd=CT001013"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []

    if "today1" in text:
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

        response1 = []
        # response1.append("서울의 오늘 날씨 입니다\n" + "1.온도: " + temp + " ℃" + "2.날씨: " + weat + "3.미세먼지: " + dust + "4.강수확률: " + rainfull_prob + " %")
        # print(response1)

        if int(rainfull_prob) > 50:
            response1.append(
                "오늘 서울 날씨 입니다\n" + "1. 온도:" + temp + " ℃" + "  2.날씨: " + weat + "  3.미세먼지: " + dust + "  4.강수확률: " + rainfull_prob + " %" + "우산 꼭 챙겨주세요!")
        else:
            response1.append(
                "오늘 서울 날씨 입니다\n" + "1. 온도:" + temp + " ℃" + "  2.날씨: " + weat + "  3.미세먼지: " + dust + "  4.강수확률: " + rainfull_prob + " %")

        global temperatureValue
        temperatureValue = temp

        # response1 = json.dumps(response1, ensure_ascii=False)
        return u'\n'.join(response1)

    # 내일 날씨
    elif "tomorrow1" in text:
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

        response2 = []
        # response2.append("서울의 내일 날씨 입니다\n" + "1.온도: " + tom_temp_pm + " ℃" + "2.날씨: " + tom_weat_am + "3.강수확률: " + tom_rainfull_prob_am)
        response2.append(
            "내일 서울의 날씨 입니다\n" + "  1.온도: " + tom_temp_pm + " ℃" + "  2.날씨: " + tom_weat_am + "  3.강수확률: " + tom_rainfull_prob_am)

        # response2 = json.dumps(response2, ensure_ascii=False)

        return u'\n'.join(response2)
        print(response2)

        # response2 = json.dumps(response2, ensure_ascii=False)

        return u'\n'.join(response2)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])
    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        keywords = get_answer(text, "session")
        ###
        if "today1" in keywords:
            answer = _crawl_weather_today(keywords)
        elif "tomorrow1" in keywords:
            answer = _crawl_weather_today(keywords)
        elif "clothes" in keywords:
            global temperatureValue
            answer = choose_clothes(temperatureValue)
        else:
            answer = keywords
        ###

        # slack.chat.post_message(channel, answer)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=answer
        )
        return make_response("App mention message has been sent", 200, )
    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })
    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0')