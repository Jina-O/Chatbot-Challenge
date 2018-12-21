from slacker import Slacker
import random

# 슬랙 토큰으로 객체 생성
token = '토큰 값'
slack = Slacker(token)

# 메시지 전송 (#채널명, 내용)
slack.chat.post_message('#day4', 'Slacker 파일 업로드 테스트')



#기온에 따른 옷 추천
def choose_clothes(temperature):
    photo_num = random.randrange(1, 11)
    photo_name = ".png"
    if(temperature > 23):
        photo_name = "summer" + str(photo_num) + photo_name
    elif(temperature > 10):
        photo_name = "middle" + str(photo_num) + photo_name
    else:
        photo_name = "winter" + str(photo_num) + photo_name

    slack.files.upload(photo_name, channels="#day4")

# 파일 업로드 (파일 경로, 채널명)
slack.files.upload('dog.png', channels="#day4")

# 사용자 리스트 반환
response = slack.users.list()
users = response.body['members']
print(users)