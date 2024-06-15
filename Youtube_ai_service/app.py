import os
import re
import streamlit as st
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import requests
from urllib.parse import urlparse, parse_qs

# API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']['OPENAI_API_KEY']
os.environ["YOUTUBE_API_KEY"] = st.secrets['YOUTUBE_API_KEY']['YOUTUBE_API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title('슈퍼 시나리오 봇🥸')

video_url = st.text_input("YouTube 영상 URL을 입력하세요")
user_name = st.text_input("사용자 이름을 입력하세요")
video_topic = st.text_input("숏폼 영상의 주제를 입력하세요")
user_idea = st.text_input("당신의 아이디어를 입력하세요")

target_audience = st.radio("타겟층을 선택하세요", ('20대', '30대', '40대'))

def get_video_id(url):
    # URL에서 비디오 ID를 추출하는 함수
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        video_id = parse_qs(parsed_url.query).get('v')
        if video_id:
            return video_id[0]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
        return transcript
    except NoTranscriptFound as e:
        st.error(f"대본을 가져오는 데 실패했습니다: {e}")
        return None
    except Exception as e:
        st.error(f"대본을 가져오는 데 실패했습니다: {e}")
        return None

def get_video_details(video_id):
    # YouTube API를 사용하여 영상의 제목과 설명을 가져옵니다.
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        video_info = response.json()
        if 'items' in video_info and len(video_info['items']) > 0:
            title = video_info['items'][0]['snippet']['title']
            description = video_info['items'][0]['snippet']['description']
            return title, description
    return None, None

def format_transcript(transcript):
    transcript_text = ""
    for item in transcript:
        start_time = item['start']
        duration = item['duration']
        text = item['text']
        transcript_text += f"[{start_time} - {start_time + duration}] {text}\n"
    return transcript_text

def truncate_text(text, max_length=4000):  # 대본의 길이를 4000자로 제한합니다.
    if len(text) > max_length:
        return text[:max_length]
    return text

if st.button('분석하기'):
    with st.spinner('분석 중입니다...'):
        video_id = get_video_id(video_url)
        if video_id:
            title, description = get_video_details(video_id)
            transcript = get_transcript(video_id)
            if transcript:
                formatted_transcript = format_transcript(transcript)
                truncated_transcript = truncate_text(formatted_transcript, max_length=4000)
                transcript_text = f"Title: {title}\n\nDescription: {description}\n\nTranscript: {truncated_transcript}"
                
                analysis_prompt = f"""
                Title: {title}
                Description: {description}
                Transcript: {truncated_transcript}

                Analyze the following aspects of the video:
                1. Content
                2. Reasons for success
                3. Future video topics based on this content
                4. Write a short-form script based on the topic: {video_topic}

                사용자 이름: {user_name}
                사용자의 아이디어: {user_idea}
                타겟층: {target_audience}

                Based on the above analysis, create a benchmarking short-form video script using the user's name and idea, tailored to the given topic and target audience.
                """

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": analysis_prompt,
                        },
                        {
                            "role": "system",
                            "content": "위 정보를 바탕으로 1분 길이의 숏폼 영상의 전체 내용, 영상이 성공한 이유, 이 내용을 바탕으로 추가로 다룰 수 있는 주제, 사용자의 이름과 아이디어를 반영하여 주어진 주제를 기반으로 한 타겟층에 맞춘 숏폼 대본을 작성해줘. 답변은 한국어로 작성해줘.",
                        }
                    ],
                    model="gpt-4",
                    max_tokens=4000  # 최대 4000 토큰을 응답에 사용합니다.
                )

                result = chat_completion.choices[0].message.content
                st.write(result)
            else:
                st.error('대본을 가져오는 데 실패했습니다.')
        else:
            st.error('유효한 YouTube 영상 URL을 입력하세요.')



