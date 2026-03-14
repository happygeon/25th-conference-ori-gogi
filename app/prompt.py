import openai
import pandas as pd
import mysql.connector

def get_connection():
    """MySQL 데이터베이스 연결 반환 함수"""
    return mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password="1234",
        database="crawling_db"
    )

def fetch_all_data(query):
    """SQL 쿼리를 실행하고 결과를 반환하는 함수"""
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        return results
    finally:
        conn.close()

def find_restaurant_name(whatres, df, key):
    openai.api_key = key
    
    df = df['restaurant_name'].unique()
    res_list = list(df)
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant who summarizes user reviews."},
            {"role": "user", "content": f"다음 중에서 '타오 마라탕'에 해당하는 식당 이름을 찾아주세요. {res_list}. 리스트의 이름 중 정확한 이름만을 입력하고, 다른것은 입력하지 마세요."},
            {"role": "assistant", "content": '타오 마라탕 신촌'},
            {"role": "user", "content": f"다음 중에서 '요이스시'에 해당하는 식당 이름을 찾아주세요. {res_list}"},  
            {"role": "assistant", "content": '신촌요이스시 이전한곳'},
            {"role": "user", "content": f"다음 중에서 {whatres}에 해당하는 식당 이름을 찾아주세요. {res_list}"}
        ]
    )
    
    return response.choices[0].message.content

def prompt(whatres):
    openai.api_key = ""

    example_output = """
    {"요약": "황금돼지집은 신선한 생고기와 소고기 육회로 인기 있는 합정역 맛집이에요.",
    "상세 정보": {
        "분위기": "깔끔하고 현대적인 인테리어로 편안한 분위기를 제공해요.",
        "서비스": "직접 구워주는 서비스가 있어 초보자도 걱정 없이 즐길 수 있어요.",
        "가격대": "1인당 30000원대의 프리미엄 고기 집으로 가격대가 다소 있어요.",
        "대표 메뉴": ["육회 비빔밥", "생고기 모듬"],
        "주차": "매장 앞 전용 주차 공간이 마련되어 있어 편리해요."}
    """
    example_output2 = """
    {"요약": "원조소금구이는 양념고기와 껍대기로 유명한 목동역 핫플입니다.",
    "상세 정보": {
        "분위기": "넓고 탁 트인 매장으로, 쾌적한 식사 환경을 제공합니다.",
        "서비스": "라면이 무제한으로 제공해요!",
        "가격대": "20000원대의 합리적인 가격으로 즐길 수 있어요.",
        "대표 메뉴": ["소금 구이 모듬"],
        "주차": "주차 공간이 협소하니 방문 전 전화 예약을 추천드려요."}
    """

    # restaurant_reviews 데이터 가져오기
    query_reviews = "SELECT * FROM restaurant_reviews"
    reviews_data = fetch_all_data(query_reviews)
    reviews_df = pd.DataFrame(reviews_data)

    # restaurant_name 데이터 가져오기
    query_names = "SELECT * FROM restaurant_name"
    names_data = fetch_all_data(query_names)
    names_df = pd.DataFrame(names_data)

    # Preprocess
    columns_to_check = ['title', 'content']
    for col in columns_to_check:
        reviews_df = reviews_df[(reviews_df[col].notna()) & (reviews_df[col] != 'unknown')]

    #입력받은 res_name을 실제 데이터의 res_name으로 변경
    whatres = find_restaurant_name(whatres, reviews_df, openai.api_key)    
    
    def multi_review(res_name):
        # 리뷰글 df
        filtered_reviews = reviews_df[reviews_df['restaurant_name'] == res_name]

        # 구글지도 정보 df
        google_info = names_df[names_df['restaurant_name'] == res_name][['address', 'rating', 'category', 'image']].values.tolist()
        ad_o_ratio = round((filtered_reviews['광고'] == 'O').mean() * 100, 2)
        filtered_reviews = filtered_reviews[filtered_reviews['광고'] != 'O']

        reviews = f"다음은 다양한 리뷰 데이터입니다. 각 리뷰는 넘버링으로 구별되어 있습니다.:"
        for i in range(filtered_reviews.shape[0]):
            title = filtered_reviews.iloc[i]['title']
            content = filtered_reviews.iloc[i]['content']
            tags = filtered_reviews.iloc[i]['tags']
            reviews += f" {i+1}. 제목: {title}, 내용: {content}, 테그: {tags}"

        return ad_o_ratio, reviews, google_info

    ratio, stri, result = multi_review(whatres)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant who summarizes user reviews."},
            {"role": "user", "content": "다양한 리뷰에서 나타난 내용을 종합하여 다음 카테고리 형식으로 출력해 주세요. 각 항목에서 해당 항목에 해당하는 내용이 없을 경우, 그 카테고리 항목은 출력에 포함하지 마세요. 카테고리 항목에 알맞는 내용만 포함되어야 합니다. 가격대는 가능하다면 대표메뉴를 참고해 주세요. 카테고리: 1) 분위기 2) 서비스 3) 손님 나이대 4) 음식의 가격대 5) 대표 메뉴 6) 주차 7) 위생. 이 카테고리는 반드시 모두 포함될 필요는 없습니다. 구체적인 정보가 없는 카테고리는 해당 카테고리를 포함한 모든 출력을 생략해 주세요. 또한, 요약은 반드시 포함되어야 하며 1~2문장 정도로 간단하게 요약해 주세요. 모두 한국어로 출력해 주세요. 출력은 반드시 리뷰의 내용을 근거로 출력해야 합니다. 대답의 말투는 '요'로 끝나는 말로 해서 친근함이 느껴지게 해주세요."},
            {"role": "assistant", "content": example_output},  
            {"role": "assistant", "content": example_output2}, 
            {"role": "user", "content": stri}
        ]
    )

    return ratio, response.choices[0].message.content, result

print(prompt("0"))
