import os
import datetime
import google.generativeai as genai
from googleapiclient.discovery import build

# 設定
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_youtube_data():
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q="AI 副業 不労所得",
            part="snippet",
            maxResults=1,
            order="viewCount",
            type="video"
        )
        res = request.execute()
        item = res['items']
        return item['snippet']['title'], item['id']['videoId']
    except:
        return "2026年最新のAI副業術", "dQw4w9WgXcQ"

def generate_article(topic, video_id):
    genai.configure(api_key=GEMINI_API_KEY)
    # 応答が安定している gemini-1.5-flash を使用
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"トピック「{topic}」についてSEOに強いブログ記事をHTML形式で書いてください。出力はHTMLコードのみ（<body>の中身）にしてください。Markdownの枠（```）は不要です。"
    
    try:
        response = model.generate_content(prompt)
        # AIの返答が空でないかチェック
        if response and response.text:
            article_content = response.text.replace("```html", "").replace("```", "").strip()
            youtube_embed = f'<div style="margin-top:30px;"><h2>解説動画</h2><iframe width="100%" height="315" src="[https://www.youtube.com/embed/](https://www.youtube.com/embed/){video_id}" frameborder="0" allowfullscreen></iframe></div>'
            return f"<html><head><meta charset='utf-8'><title>{topic}</title></head><body style='font-family:sans-serif; line-height:1.6; max-width:800px; margin:auto; padding:20px;'><h1>{topic}</h1>{article_content}{youtube_embed}</body></html>"
    except Exception as e:
        print(f"Gemini Error: {e}")
    
    # 失敗した場合の最小限のHTML
    return f"<html><body><h1>{topic}</h1><p>現在AIが記事を執筆中です。しばらくしてから再読み込みしてください。</p></body></html>"

def main():
    title, v_id = get_youtube_data()
    html_article = generate_article(title, v_id)
    
    post_dir = "posts"
    os.makedirs(post_dir, exist_ok=True)
    file_name = f"{post_dir}/{datetime.date.today()}_{v_id}.html"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_article)
    
    # index.htmlの更新
    link = f'<li><a href="{file_name}">{datetime.date.today()} : {title}</a></li>\n'
    if not os.path.exists("index.html"):
        with open("index.html", "w", encoding="utf-8") as f: f.write("<html><body><h1>記事一覧</h1><ul></ul></body></html>")
    
    with open("index.html", "r+", encoding="utf-8") as f:
        content = f.read()
        if "<ul>" in content:
            new_content = content.replace("<ul>", f"<ul>\n{link}")
            f.seek(0)
            f.write(new_content)
            f.truncate()

if __name__ == "__main__":
    main()
