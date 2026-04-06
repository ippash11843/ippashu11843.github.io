import os
import datetime
import google.generativeai as genai
from googleapiclient.discovery import build

# 設定（GitHub Secretsから取得）
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_youtube_data():
    """YouTubeから動画を取得。失敗した場合はデフォルトのトピックを返す"""
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q="不労所得 AI 副業",
            part="snippet",
            maxResults=1,
            order="viewCount",
            type="video"
        )
        res = request.execute()
        if 'items' in res and len(res['items']) > 0:
            item = res['items']
            return item['snippet']['title'], item['id']['videoId']
    except Exception as e:
        print(f"YouTube API Error: {e}")
    
    # 動画が取れなかった時の予備ネタ
    return "2026年最新のAI副業術", "dQw4w9WgXcQ" # 予備の動画ID

def generate_article(topic, video_id):
    """Geminiで記事生成"""
    genai.configure(api_key=GEMINI_API_KEY)
    # モデル名を安定版に変更
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    ad_code = '<div style="text-align:center; margin:20px 0;">[スポンサーリンク]<br></div>'
    
    prompt = f"トピック「{topic}」についてSEO記事をHTMLで作成。{ad_code}を含め、出力はHTMLコードのみにすること。"
    
    try:
        response = model.generate_content(prompt)
        article_body = response.text.strip()
        # Markdown装飾の除去
        if article_body.startswith("```"):
            article_body = article_body.split("```")
            if article_body.startswith("html"): article_body = article_body[4:]
        
        youtube_embed = f'<div style="margin-top:40px;"><h2>関連動画</h2><iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe></div>'
        return article_body + youtube_embed
    except Exception as e:
        return f"<html><body><h1>{topic}</h1><p>記事の自動生成中にエラーが発生しました。</p></body></html>"

def main():
    title, v_id = get_youtube_data()
    html_article = generate_article(title, v_id)
    
    # 保存処理
    post_dir = "posts"
    os.makedirs(post_dir, exist_ok=True)
    file_name = f"{post_dir}/{datetime.date.today()}_{v_id}.html"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_article)
        
    # index.htmlの更新
    link = f'<li><a href="{file_name}">{datetime.date.today()} : {title}</a></li>\n'
    if not os.path.exists("index.html"):
        with open("index.html", "w") as f: f.write("<ul></ul>")
    
    with open("index.html", "r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        f.write(content.replace("<ul>", f"<ul>\n{link}"))

if __name__ == "__main__":
    main()
