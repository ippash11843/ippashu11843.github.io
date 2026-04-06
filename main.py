import os
import google.generativeai as genai
from googleapiclient.discovery import build

# 1. GitHub SecretsからAPIキーを読み込む
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_youtube_topic():
    """YouTubeで「不労所得 AI」関連の人気動画タイトルを1つ取得"""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q="不労所得 AI",
        part="snippet",
        maxResults=1,
        order="viewCount",
        type="video"
    )
    response = request.execute()
    return response['items']['snippet']['title']

def generate_article(topic):
    """Geminiを使ってHTML形式のブログ記事を生成"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    YouTubeで話題のトピック「{topic}」についてのブログ記事を書いてください。
    出力は必ず「完全な1枚のHTMLファイル形式」にしてください。
    モダンなデザインのCSS（<style>タグ内）を含め、読者がワクワクするような内容にしてください。
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    try:
        # トピック取得
        topic = get_youtube_topic()
        print(f"Topic found: {topic}")
        
        # 記事生成
        html_content = generate_article(topic)
        
        # index.htmlを上書き保存
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Successfully updated index.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
