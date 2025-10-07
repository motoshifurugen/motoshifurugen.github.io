#!/usr/bin/env python3
"""
Seleniumを使用してFacebookの写真ページから画像を取得するスクリプト
"""

import os
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def main():
    # 環境変数から認証情報を取得
    email = os.getenv('FACEBOOK_EMAIL')
    password = os.getenv('FACEBOOK_PASSWORD')
    
    if not email or not password:
        print("環境変数が設定されていません")
        return 1
    
    # 保存先ディレクトリを作成
    save_dir = Path('images/facebook')
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Chrome WebDriverを設定
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Facebookにログイン
        driver.get("https://www.facebook.com/login")
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)
        
        # 写真ページにアクセス
        driver.get("https://www.facebook.com/profile.php?id=100054664260008&sk=photos")
        time.sleep(5)
        
        # 写真要素を取得
        photos = driver.find_elements(By.CSS_SELECTOR, "img[src*='scontent']")[:5]
        
        # 既存ファイルをチェック
        existing = {f.name for f in save_dir.glob("photo_*.jpg")}
        
        # 画像をダウンロード
        for i, img in enumerate(photos):
            filename = f"photo_{i+1}.jpg"
            if filename in existing:
                print(f"スキップ: {filename}")
                continue
                
            img_src = img.get_attribute('src')
            if img_src:
                # 高解像度に変換
                if 's720x720' in img_src:
                    img_src = img_src.replace('s720x720', 's2048x2048')
                
                # ダウンロード
                response = requests.get(img_src)
                with open(save_dir / filename, 'wb') as f:
                    f.write(response.content)
                print(f"保存: {filename}")
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1
    
    finally:
        driver.quit()
    
    return 0

if __name__ == "__main__":
    exit(main())