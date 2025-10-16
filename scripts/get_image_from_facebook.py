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
        # ファイル名でソート（日時順、新しい順）
        image_files.sort(key=lambda x: x.name, reverse=True)
        # 古いファイルを削除（最新のmax_files個以外）
        files_to_delete = image_files[max_files:]
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                print(f"古い画像を削除: {file_path.name}")
            except Exception as e:
                print(f"ファイル削除エラー: {e}")

def close_modal_safely(driver):
    """モーダルを安全に閉じる"""
    try:
        # まず閉じるボタンを試す
        close_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='閉じる'][role='button']")
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(1)
        return True
    except (NoSuchElementException, ElementClickInterceptedException):
        try:
            # ESCキーで閉じる
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
            return True
        except Exception:
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
    
    # 最大5枚まで制限
    MAX_IMAGES = 5
    
    # Chrome WebDriverを設定
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)  # 15秒の待機時間を設定
    
    try:
        # Facebookにログイン
        driver.get("https://www.facebook.com/login")
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)
        
        # 写真ページにアクセス
        # driver.get("https://www.facebook.com/profile.php?id=100054664260008&sk=photos")
        driver.get("https://www.facebook.com/bacoloderoom/photos_by")
        time.sleep(5)
        
        # より多くの画像を表示するためにスクロール（複数回実行）
        print("ページをスクロールして画像を読み込み中...")
        for i in range(5):  # 5回スクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # より長く待機
            print(f"スクロール {i + 1}/5 完了")
        
        # 画像要素を検出（動作しているa[role='link']方法のみを使用）
        thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
        print(f"見つかった要素数: {len(thumbnail_elements)}")
        
        # 要素の検証
        valid_elements = []
        for element in thumbnail_elements:
            try:
                if element.is_displayed() and element.is_enabled():
                    valid_elements.append(element)
            except Exception:
                continue
        
        thumbnail_elements = valid_elements
        print(f"有効な要素数: {len(thumbnail_elements)}")
        
        # 既存ファイルのハッシュ値をチェック
        existing_hashes = set()
        for file_path in save_dir.glob("*.jpg"):
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    existing_hashes.add(file_hash)
            except:
                continue
        
        # 既存の画像数を確認
        existing_image_count = len(list(save_dir.glob("*.jpg")))
        print(f"既存画像: {existing_image_count}枚")
        
        # 5枚の画像が保存されるまで処理を続ける
        TARGET_COUNT = 5
        downloaded_count = 0
        processed_count = 0
        current_position = 0
        
        print(f"利用可能な画像数: {len(thumbnail_elements)}")
        print(f"目標: {TARGET_COUNT}枚の画像を取得")
        
        while downloaded_count < TARGET_COUNT and current_position < len(thumbnail_elements):
            thumbnail_element = thumbnail_elements[current_position]
            try:
                processed_count += 1
                print(f"画像 {current_position + 1} を処理中... (新規取得: {downloaded_count}枚)")
                
                # サムネ画像をクリックして高画質画像を表示
                try:
                    driver.execute_script("arguments[0].click();", thumbnail_element)
                    time.sleep(3)  # モーダルが開くまで待機
                    
                except Exception as e:
                    print(f"画像 {current_position + 1}: クリックエラー: {e}")
                    current_position += 1
                    continue
                
                # 高画質画像の要素を待機して取得
                try:
                    # MediaViewerPhotoの配下から高画質画像を取得
                    high_res_img = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']"))
                    )
                    
                    # 画像の読み込み完了を待つ
                    wait.until(lambda driver: high_res_img.get_attribute('complete') == 'true')
                    img_src = high_res_img.get_attribute('src')
                    
                    if not img_src:
                        print(f"画像 {current_position + 1}: 高画質画像のURLが見つかりません")
                        close_modal_safely(driver)
                        current_position += 1
                        continue
                    
                    # 画像をダウンロード
                    response = requests.get(img_src)
                    response.raise_for_status()
                    original_image_data = response.content
                    
                    # 重複チェック（元画像のハッシュで）
                    original_hash = hashlib.md5(original_image_data).hexdigest()
                    if original_hash in existing_hashes:
                        print(f"スキップ: 既存の画像 (ハッシュ: {original_hash[:8]}...)")
                        close_modal_safely(driver)
                        current_position += 1
                        continue
                    
                    # ファイル名を生成
                    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_hash[:8]}.jpg"
                    
                    # 画像を保存
                    with open(save_dir / filename, 'wb') as f:
                        f.write(original_image_data)
                    print(f"保存: {filename}")
                    downloaded_count += 1
                    
                    # 既存ハッシュに追加（重複チェック用）
                    existing_hashes.add(original_hash)
                    
                    # 新しい画像を保存したので、古い画像を1枚削除
                    if existing_image_count + downloaded_count > MAX_IMAGES:
                        # 最も古い画像を削除
                        image_files = list(save_dir.glob("*.jpg"))
                        image_files.sort(key=lambda x: x.name)  # 古い順にソート
                        oldest_file = image_files[0]
                        try:
                            oldest_file.unlink()
                            print(f"古い画像を削除: {oldest_file.name}")
                        except Exception as e:
                            print(f"古い画像の削除に失敗: {e}")
                    
                    # モーダルを安全に閉じる
                    close_modal_safely(driver)
                    
                except TimeoutException:
                    print(f"画像 {current_position + 1}: 高画質画像の読み込みがタイムアウトしました")
                    close_modal_safely(driver)
                    current_position += 1
                    continue
                except Exception as e:
                    print(f"画像 {current_position + 1}: 画像処理エラー: {e}")
                    close_modal_safely(driver)
                    current_position += 1
                    continue
                
            except Exception as e:
                print(f"画像 {current_position + 1} の処理に失敗: {e}")
                close_modal_safely(driver)
                current_position += 1
                continue
            
            # 次の画像に進む
            current_position += 1
        
        print(f"新規ダウンロード: {downloaded_count}件")
        if downloaded_count >= TARGET_COUNT:
            print(f"目標達成: {TARGET_COUNT}枚の画像を取得しました")
        else:
            print(f"警告: 目標の{TARGET_COUNT}枚に達しませんでした（取得: {downloaded_count}枚）")
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1
    
    finally:
        driver.quit()
    
    return 0

if __name__ == "__main__":
    exit(main())