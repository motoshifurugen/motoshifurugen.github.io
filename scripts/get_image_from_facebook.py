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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def cleanup_old_images(save_dir, max_files=5):
    """古い画像を削除して最大ファイル数を維持する"""
    image_files = list(save_dir.glob("*.jpg"))
    if len(image_files) > max_files:
        image_files.sort(key=lambda x: x.name, reverse=True)
        for file_path in image_files[max_files:]:
            try:
                file_path.unlink()
                print(f"古い画像を削除: {file_path.name}")
            except Exception as e:
                print(f"ファイル削除エラー: {e}")

def close_modal_safely(driver):
    """モーダルを安全に閉じる"""
    try:
        close_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='閉じる'][role='button']")
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(1)
        return True
    except:
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
            return True
        except:
            return False

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
    wait = WebDriverWait(driver, 15)
    
    try:
        # Facebookにログイン
        driver.get("https://www.facebook.com/login")
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)
        
        # 写真ページにアクセス
        driver.get("https://www.facebook.com/bacoloderoom/photos_by")
        time.sleep(8)
        
        # ページが完全に読み込まれるまで待機
        WebDriverWait(driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # 要素を取得
        elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
        if not elements:
            elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
        
        print(f"見つかった要素数: {len(elements)}")
        
        # 既存の画像数を確認
        existing_count = len(list(save_dir.glob("*.jpg")))
        if existing_count >= 5:
            print("既に5枚の画像が存在します。処理をスキップします。")
            return 0
        
        # 指定された間隔で画像を取得（1枚目、3枚目、5枚目、7枚目、9枚目、11枚目）
        target_positions = [0, 2, 4, 6, 8]  # 1枚目、3枚目、5枚目、7枚目、9枚目
        if len(elements) >= 11:
            target_positions.append(10)  # 11枚目
        
        print(f"取得対象: {[pos + 1 for pos in target_positions]}枚目")
        
        downloaded_count = 0
        
        for target_pos in target_positions:
            if downloaded_count >= len(target_positions):
                break
                
            try:
                print(f"画像 {target_pos + 1} を処理中...")
                
                if target_pos >= len(elements):
                    print(f"画像 {target_pos + 1}: 要素が見つかりません")
                    continue
                
                element = elements[target_pos]
                
                # サムネ画像をクリック
                driver.execute_script("arguments[0].click();", element)
                time.sleep(3)
                
                # 高画質画像を取得
                img_src = None
                selectors = [
                    "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']",
                    "div[role='dialog'] img[src*='scontent']",
                    "[role='dialog'] img",
                    "img[src*='scontent']"
                ]
                
                for selector in selectors:
                    try:
                        img = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        img_src = img.get_attribute('src')
                        break
                    except TimeoutException:
                        continue
                
                if not img_src:
                    print(f"画像 {target_pos + 1}: 高画質画像のURLが見つかりません")
                    close_modal_safely(driver)
                    continue
                    
                # 画像をダウンロード
                response = requests.get(img_src)
                response.raise_for_status()
                image_data = response.content
                
                # 重複チェック
                image_hash = hashlib.md5(image_data).hexdigest()
                existing_hashes = set()
                for file_path in save_dir.glob("*.jpg"):
                    try:
                        with open(file_path, 'rb') as f:
                            existing_hashes.add(hashlib.md5(f.read()).hexdigest())
                    except:
                        continue
                
                if image_hash in existing_hashes:
                    print(f"スキップ: 既存の画像")
                    close_modal_safely(driver)
                    continue
                
                # ファイル名を生成して保存
                filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_hash[:8]}.jpg"
                with open(save_dir / filename, 'wb') as f:
                    f.write(image_data)
                print(f"保存: {filename}")
                downloaded_count += 1
                
                # 古い画像を削除（5枚を超える場合）
                cleanup_old_images(save_dir, 5)
                
                # モーダルを閉じる
                close_modal_safely(driver)
                    
            except Exception as e:
                print(f"画像 {target_pos + 1} の処理に失敗: {e}")
                close_modal_safely(driver)
                continue
        
        print(f"完了: {downloaded_count}枚の画像を取得しました")
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1
    
    finally:
        driver.quit()
    
    return 0

if __name__ == "__main__":
    exit(main())