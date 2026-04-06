import os
import datetime
import google.generativeai as genai
from googleapiclient.discovery import build

# 設定
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADSENSE_CLIENT_ID = "ca-pub-xxxxxxxxxxxxxxxx" # 審査通過後に書き換え

def get_youtube_data():
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
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # 広告コード（仮）
    ad_code = f'<div style="text-align:center; margin:20px 0;">[スポンサーリンク]<br></div>'
    
    prompt = f"""
    トピック「{topic}」について、SEOに強いブログ記事をHTML形式で作成してください。
    以下の構成を守ってください：
    1. 読者の興味を引くタイトル
    2. 導入文
    3. {ad_code} を記事の途中に挿入
    4. 3つの見出し（h2）とその詳細内容
    5. 結論
    CSSはモダンで清潔感のあるデザイン（白背景に濃いグレーの文字、青のアクセント）にしてください。
    """
    article_body = model.generate_content(prompt).text
    
    # YouTube動画の埋め込みコードを追加
    youtube_embed = f'<h2>関連動画で詳しく学ぶ</h2><iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
    
    return article_body.replace("</body>", f"{youtube_embed}</body>")

def update_index_and_save_post(new_post_path, title):
    # index.htmlに最新記事へのリンクを追記する処理
    link_line = f'<li><a href="{new_post_path}">{datetime.date.today()} : {title}</a></li>\n'
    
    if not os.path.exists("index.html"):
        with open("index.html", "w", encoding="utf-8") as f:
            f.write("<h1>AI自動更新ブログ 記事一覧</h1><ul></ul>")
            
    with open("index.html", "r+", encoding="utf-8") as f:
        content = f.read()
        if "<ul>" in content:
            new_content = content.replace("<ul>", f"<ul>\n{link_line}")
            f.seek(0)
            f.write(new_content)

def main():
    title, v_id = get_youtube_data()
    html_article = generate_article(title, v_id)
    
    # 記事を個別ファイルとして保存
    post_dir = "posts"
    os.makedirs(post_dir, exist_ok=True)
    file_name = f"{post_dir}/{datetime.date.today()}_{v_id}.html"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_article)
    
    # 一覧ページを更新
    update_index_and_save_post(file_name, title)

if __name__ == "__main__":
    main()
