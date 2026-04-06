import os
import datetime
import google.generativeai as genai
from googleapiclient.discovery import build

# 設定（GitHub Secretsから自動取得）
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_youtube_data():
    """YouTubeから「不労所得 AI 副業」関連の人気動画を取得"""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q="不労所得 AI 副業",
        part="snippet",
        maxResults=1,
        order="viewCount",
        type="video"
    )
    res = request.execute()['items']
    return res['snippet']['title'], res['id']['videoId']

def generate_article(topic, video_id):
    """Geminiを使ってSEOに強いHTML記事を生成（HTMLのみを出力）"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # 広告コード（審査通過後に ca-pub-... を書き換え）
    ad_code = '<div style="text-align:center; margin:20px 0;">[スポンサーリンク]<br></div>'
    
    prompt = f"""
    トピック「{topic}」について、SEOに強いブログ記事をHTML形式で作成してください。
    
    【構成ルール】
    1. 読者の興味を引くタイトル、導入文、3つの見出し（h2）、結論を含める。
    2. {ad_code} を記事の途中に必ず挿入する。
    3. モダンで清潔感のあるCSS（<style>タグ）を内部に含める。
    
    【重要：出力ルール】
    - 出力は必ず「<!DOCTYPE html>」から始まるHTMLコードのみにしてください。
    - 「はい、作成しました」等の説明文は一切不要です。
    - Markdownのバッククォート（```html ）も絶対に含めないでください。
    """
    
    response = model.generate_content(prompt)
    article_body = response.text.strip()
    
    # 万が一Markdownの枠が含まれた場合の除去処理
    if article_body.startswith("```"):
        article_body = article_body.replace("```html", "").replace("```", "").strip()
    
    # YouTube動画の埋め込みを追加
    youtube_embed = f'<div style="margin-top:40px;"><h2>関連動画で詳しく学ぶ</h2><iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe></div>'
    
    if "</body>" in article_body:
        return article_body.replace("</body>", f"{youtube_embed}</body>")
    else:
        return article_body + youtube_embed

def update_index_and_save_post(new_post_path, title):
    """index.htmlに最新記事のリンクを追記"""
    link_line = f'<li><a href="{new_post_path}">{datetime.date.today()} : {title}</a></li>\n'
    
    if not os.path.exists("index.html"):
        with open("index.html", "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>AI Blog</title></head><body><h1>記事一覧</h1><ul></ul></body></html>")
            
    with open("index.html", "r+", encoding="utf-8") as f:
        content = f.read()
        if "<ul>" in content:
            new_content = content.replace("<ul>", f"<ul>\n{link_line}")
            f.seek(0)
            f.write(new_content)
            f.truncate()

def main():
    try:
        title, v_id = get_youtube_data()
        print(f"Target Topic: {title}")
        
        html_article = generate_article(title, v_id)
        
        # 個別記事の保存
        post_dir = "posts"
        os.makedirs(post_dir, exist_ok=True)
        # ファイル名に日付と動画IDを入れて重複回避
        file_name = f"{post_dir}/{datetime.date.today()}_{v_id}.html"
        
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_article)
        
        # 一覧ページの更新
        update_index_and_save_post(file_name, title)
        print("Success: New post generated and index.html updated.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
