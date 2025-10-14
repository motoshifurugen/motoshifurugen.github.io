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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
    wait = WebDriverWait(driver, 10)
    
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
        
        # サムネ画像要素を取得（クリック可能な要素）
        thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")[:5]
        
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
        for i, thumbnail_element in enumerate(thumbnail_elements):
            try:
                print(f"画像 {i+1} を処理中...")
                
                # サムネ画像をクリックして高画質画像を表示
                driver.execute_script("arguments[0].click();", thumbnail_element)
                time.sleep(3)  # モーダルが開くまで待機
                
                # 高画質画像の要素を待機して取得
                try:
                    # MediaViewerPhotoの配下から高画質画像を取得
                    high_res_img = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']"))
                    )
                    img_src = high_res_img.get_attribute('src')
                    
                    if not img_src:
                        print(f"画像 {i+1}: 高画質画像のURLが見つかりません")
                        # モーダルを閉じる
                        driver.find_element(By.CSS_SELECTOR, "[aria-label='閉じる'][role='button']").click()
                        time.sleep(1)
                        continue
                    
                    # 画像をダウンロード
                    response = requests.get(img_src)
                    response.raise_for_status()
                    original_image_data = response.content
                    
                    # 重複チェック（元画像のハッシュで）
                    original_hash = hashlib.md5(original_image_data).hexdigest()
                    if original_hash in existing_hashes:
                        print(f"スキップ: 既存の画像 (ハッシュ: {original_hash[:8]}...)")
                        # モーダルを閉じる
                        driver.find_element(By.CSS_SELECTOR, "[aria-label='閉じる'][role='button']").click()
                        time.sleep(1)
                        continue
                    
                    # ファイル名を生成
                    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_hash[:8]}.jpg"
                    
                    # 画像を保存
                    with open(save_dir / filename, 'wb') as f:
                        f.write(original_image_data)
                    print(f"保存: {filename}")
                    downloaded_count += 1
                    
                    # モーダルを閉じる
                    driver.find_element(By.CSS_SELECTOR, "[aria-label='閉じる'][role='button']").click()
                    time.sleep(1)
                    
                except TimeoutException:
                    print(f"画像 {i+1}: 高画質画像の読み込みがタイムアウトしました")
                    # モーダルを閉じる（ESCキーで閉じる）
                    driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')  # ESCキー
                    time.sleep(1)
                    continue
                except NoSuchElementException:
                    print(f"画像 {i+1}: モーダルの閉じるボタンが見つかりません")
                    # ESCキーでモーダルを閉じる
                    driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')  # ESCキー
                    time.sleep(1)
                    continue
                
            except Exception as e:
                print(f"画像 {i+1} の処理に失敗: {e}")
                # エラーが発生した場合もモーダルを閉じる
                try:
                    driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')  # ESCキー
                    time.sleep(1)
                except:
                    pass
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