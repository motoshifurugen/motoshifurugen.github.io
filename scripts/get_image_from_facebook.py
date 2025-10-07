#!/usr/bin/env python3
"""
Seleniumを使用してFacebookの写真ページから画像を取得するスクリプト
"""

import os
import time
import requests
import hashlib
from datetime import datetime
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
        
        # 既存ファイルのハッシュ値をチェック
        existing_hashes = set()
        for file_path in save_dir.glob("*.jpg"):
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    existing_hashes.add(file_hash)
            except:
                continue
        
        # 画像をダウンロード
        downloaded_count = 0
        for i, img in enumerate(photos):
            img_src = img.get_attribute('src')
            if not img_src:
                continue
                
            # 高解像度に変換
            if 's720x720' in img_src:
                img_src = img_src.replace('s720x720', 's2048x2048')
            
            # 画像をダウンロードしてハッシュ値を計算
            try:
                response = requests.get(img_src)
                response.raise_for_status()
                image_data = response.content
                
                # ハッシュ値を計算
                image_hash = hashlib.md5(image_data).hexdigest()
                
                # 重複チェック
                if image_hash in existing_hashes:
                    print(f"スキップ: 既存の画像 (ハッシュ: {image_hash[:8]}...)")
                    continue
                
                # ファイル名を生成（タイムスタンプ + ハッシュ）
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"photo_{timestamp}_{image_hash[:8]}.jpg"
                
                # 保存
                with open(save_dir / filename, 'wb') as f:
                    f.write(image_data)
                print(f"保存: {filename}")
                downloaded_count += 1
                
            except Exception as e:
                print(f"画像 {i+1} のダウンロードに失敗: {e}")
                continue
        
        print(f"新規ダウンロード: {downloaded_count}件")
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1
    
    finally:
        driver.quit()
    
    return 0

if __name__ == "__main__":
    exit(main())