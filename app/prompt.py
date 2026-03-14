import openai
import pandas as pd
from config import OPENAI_API_KEY
from db import fetch_all_data

openai.api_key = OPENAI_API_KEY

SYSTEM_MESSAGE = "You are an assistant who summarizes user reviews."

SUMMARY_INSTRUCTION = (
    "다양한 리뷰에서 나타난 내용을 종합하여 다음 카테고리 형식으로 출력해 주세요. "
    "각 항목에서 해당 항목에 해당하는 내용이 없을 경우, 그 카테고리 항목은 출력에 포함하지 마세요. "
    "카테고리 항목에 알맞는 내용만 포함되어야 합니다. 가격대는 가능하다면 대표메뉴를 참고해 주세요. "
    "카테고리: 1) 분위기 2) 서비스 3) 손님 나이대 4) 음식의 가격대 5) 대표 메뉴 6) 주차 7) 위생. "
    "이 카테고리는 반드시 모두 포함될 필요는 없습니다. "
    "구체적인 정보가 없는 카테고리는 해당 카테고리를 포함한 모든 출력을 생략해 주세요. "
    "또한, 요약은 반드시 포함되어야 하며 1~2문장 정도로 간단하게 요약해 주세요. "
    "모두 한국어로 출력해 주세요. 출력은 반드시 리뷰의 내용을 근거로 출력해야 합니다. "
    "대답의 말투는 '요'로 끝나는 말로 해서 친근함이 느껴지게 해주세요."
)

EXAMPLE_OUTPUT_1 = """
{"요약": "황금돼지집은 신선한 생고기와 소고기 육회로 인기 있는 합정역 맛집이에요.",
"상세 정보": {
    "분위기": "깔끔하고 현대적인 인테리어로 편안한 분위기를 제공해요.",
    "서비스": "직접 구워주는 서비스가 있어 초보자도 걱정 없이 즐길 수 있어요.",
    "가격대": "1인당 30000원대의 프리미엄 고기 집으로 가격대가 다소 있어요.",
    "대표 메뉴": ["육회 비빔밥", "생고기 모듬"],
    "주차": "매장 앞 전용 주차 공간이 마련되어 있어 편리해요."}
"""

EXAMPLE_OUTPUT_2 = """
{"요약": "원조소금구이는 양념고기와 껍대기로 유명한 목동역 핫플입니다.",
"상세 정보": {
    "분위기": "넓고 탁 트인 매장으로, 쾌적한 식사 환경을 제공합니다.",
    "서비스": "라면이 무제한으로 제공해요!",
    "가격대": "20000원대의 합리적인 가격으로 즐길 수 있어요.",
    "대표 메뉴": ["소금 구이 모듬"],
    "주차": "주차 공간이 협소하니 방문 전 전화 예약을 추천드려요."}
"""


def find_restaurant_name(whatres, df):
    """사용자 입력을 실제 DB의 식당 이름으로 매칭"""
    res_list = list(df['restaurant_name'].unique())

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": f"다음 중에서 '타오 마라탕'에 해당하는 식당 이름을 찾아주세요. {res_list}. 리스트의 이름 중 정확한 이름만을 입력하고, 다른것은 입력하지 마세요."},
            {"role": "assistant", "content": "타오 마라탕 신촌"},
            {"role": "user", "content": f"다음 중에서 '요이스시'에 해당하는 식당 이름을 찾아주세요. {res_list}"},
            {"role": "assistant", "content": "신촌요이스시 이전한곳"},
            {"role": "user", "content": f"다음 중에서 {whatres}에 해당하는 식당 이름을 찾아주세요. {res_list}"},
        ],
    )

    return response.choices[0].message.content


def build_review_text(reviews_df, names_df, res_name):
    """리뷰 데이터를 텍스트로 변환하고, 광고 비율과 구글 정보를 반환"""
    filtered = reviews_df[reviews_df['restaurant_name'] == res_name]
    google_info = names_df[names_df['restaurant_name'] == res_name][
        ['address', 'rating', 'category', 'image']
    ].values.tolist()

    ad_ratio = round((filtered['광고'] == 'O').mean() * 100, 2)
    clean_reviews = filtered[filtered['광고'] != 'O']

    reviews_text = "다음은 다양한 리뷰 데이터입니다. 각 리뷰는 넘버링으로 구별되어 있습니다.:"
    for i in range(clean_reviews.shape[0]):
        row = clean_reviews.iloc[i]
        reviews_text += f" {i+1}. 제목: {row['title']}, 내용: {row['content']}, 태그: {row['tags']}"

    return ad_ratio, reviews_text, google_info


def prompt(whatres):
    """음식점 이름을 입력받아 클린 리뷰 요약 결과를 반환"""
    reviews_df = pd.DataFrame(fetch_all_data("SELECT * FROM restaurant_reviews"))
    names_df = pd.DataFrame(fetch_all_data("SELECT * FROM restaurant_name"))

    # 전처리: 빈 값 제거
    for col in ['title', 'content']:
        reviews_df = reviews_df[(reviews_df[col].notna()) & (reviews_df[col] != 'unknown')]

    # 사용자 입력을 실제 식당 이름으로 매칭
    matched_name = find_restaurant_name(whatres, reviews_df)
    ratio, review_text, google_info = build_review_text(reviews_df, names_df, matched_name)

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": SUMMARY_INSTRUCTION},
            {"role": "assistant", "content": EXAMPLE_OUTPUT_1},
            {"role": "assistant", "content": EXAMPLE_OUTPUT_2},
            {"role": "user", "content": review_text},
        ],
    )

    return ratio, response.choices[0].message.content, google_info
