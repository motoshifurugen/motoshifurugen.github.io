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
from PIL import Image
import io

def resize_image_with_crop(image_data, target_size=(1024, 1024), quality=95):
    """
    画像をクロップして正方形に統一し、余白を最小化する
    """
    try:
        # 画像を開く
        image = Image.open(io.BytesIO(image_data))
        
        # RGBに変換
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 元の画像サイズを取得
        width, height = image.size
        
        # 正方形にクロップしてリサイズ
        crop_size = min(width, height)
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        cropped_image = image.crop((left, top, left + crop_size, top + crop_size))
        resized_image = cropped_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # JPEGとして保存
        output = io.BytesIO()
        resized_image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        print(f"画像リサイズエラー: {e}")
        return image_data

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
        
        # 写真要素を取得（ProfileAppSection_0配下の画像のみ）
        photos = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] img[src*='scontent']")[:5]
        
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
                
            # 画像をダウンロード
            try:
                response = requests.get(img_src)
                response.raise_for_status()
                original_image_data = response.content
                
                # 重複チェック（元画像のハッシュで）
                original_hash = hashlib.md5(original_image_data).hexdigest()
                if original_hash in existing_hashes:
                    print(f"スキップ: 既存の画像 (ハッシュ: {original_hash[:8]}...)")
                    continue
                
                # 画像サイズを統一（1024x1024、画質95%、クロップ方式）
                resized_image_data = resize_image_with_crop(
                    original_image_data, 
                    target_size=(1024, 1024), 
                    quality=95
                )
                
                # ファイル名を生成
                filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_hash[:8]}.jpg"
                
                # 保存
                with open(save_dir / filename, 'wb') as f:
                    f.write(resized_image_data)
                print(f"保存: {filename} (1024x1024, 画質95%, Web用最適化)")
                downloaded_count += 1
                
            except Exception as e:
                print(f"画像 {i+1} の処理に失敗: {e}")
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