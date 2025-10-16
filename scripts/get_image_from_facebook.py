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
        
        # より多くの画像を表示するためにスクロール（段階的に実行）
        print("ページをスクロールして画像を読み込み中...")
        for i in range(15):  # 15回スクロール
            # より積極的にスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)  # 待機時間を短縮
            
            # 追加のスクロール（ページの中央部分もスクロール）
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.5)
            
            print(f"スクロール {i + 1}/15 完了")
            
            # 2回ごとに要素数をチェック
            if i % 2 == 1:
                current_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
                print(f"現在の要素数: {len(current_elements)}")
                
                # 15個以上見つかったら早期終了
                if len(current_elements) >= 15:
                    print("十分な要素が見つかりました")
                    break
        
        # 画像要素を検出（動作しているa[role='link']方法のみを使用）
        thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
        print(f"見つかった要素数: {len(thumbnail_elements)}")
        
        # 初期検証は最小限に（後で詳細にチェック）
        print(f"初期要素数: {len(thumbnail_elements)}")
        
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
        
        # 1枚目、4枚目、7枚目、10枚目、13枚目を取得
        TARGET_COUNT = 5
        target_positions = [0, 3, 6, 9, 12]  # 0ベースのインデックス
        downloaded_count = 0
        processed_count = 0
        
        print(f"目標: {TARGET_COUNT}枚の画像を取得")
        print(f"取得対象の位置: {[pos + 1 for pos in target_positions]}枚目")
        
        for position in target_positions:
            if downloaded_count >= TARGET_COUNT:
                break
                
            try:
                processed_count += 1
                print(f"画像 {position + 1} を処理中... (新規取得: {downloaded_count}枚)")
                
                # 要素を再取得（複数のセレクターを試す）
                try:
                    current_elements = []
                    
                    # 方法1: 通常のセレクター
                    elements1 = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
                    if elements1:
                        current_elements = elements1
                        print(f"方法1で{len(elements1)}個の要素を発見")
                    
                    # 方法2: より広範囲なセレクター
                    if len(current_elements) < 10:
                        elements2 = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
                        if len(elements2) > len(current_elements):
                            current_elements = elements2
                            print(f"方法2で{len(elements2)}個の要素を発見")
                    
                    if position >= len(current_elements):
                        print(f"画像 {position + 1}: 要素が見つかりません（利用可能: {len(current_elements)}個）")
                        continue
                    
                    thumbnail_element = current_elements[position]
                    
                    # 要素が有効かチェック
                    if not thumbnail_element.is_displayed():
                        print(f"画像 {position + 1}: 要素が表示されていません")
                        continue
                    
                    if not thumbnail_element.is_enabled():
                        print(f"画像 {position + 1}: 要素が無効です")
                        continue
                    
                except Exception as e:
                    print(f"画像 {position + 1}: 要素再取得エラー: {e}")
                    continue
                
                # サムネ画像をクリックして高画質画像を表示
                try:
                    driver.execute_script("arguments[0].click();", thumbnail_element)
                    time.sleep(3)  # モーダルが開くまで待機
                    
                except Exception as e:
                    print(f"画像 {current_position + 1}: クリックエラー: {e}")
                    current_position += 1
                    continue
                
                # 高画質画像の要素を待機して取得（複数の方法を試す）
                try:
                    high_res_img = None
                    img_src = None
                    
                    # 方法1: MediaViewerPhotoの配下から高画質画像を取得
                    try:
                        high_res_img = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']"))
                        )
                        img_src = high_res_img.get_attribute('src')
                    except TimeoutException:
                        pass
                    
                    # 方法2: より広範囲なセレクターで画像を探す
                    if not img_src:
                        try:
                            high_res_img = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] img[src*='scontent']"))
                            )
                            img_src = high_res_img.get_attribute('src')
                        except TimeoutException:
                            pass
                    
                    # 方法3: モーダル内の画像を探す
                    if not img_src:
                        try:
                            high_res_img = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='dialog'] img"))
                            )
                            img_src = high_res_img.get_attribute('src')
                        except TimeoutException:
                            pass
                    
                    if not img_src:
                        print(f"画像 {current_position + 1}: 高画質画像のURLが見つかりません")
                        close_modal_safely(driver)
                        current_position += 1
                        continue
                    
                    # 画像の読み込み完了を待つ
                    if high_res_img:
                        try:
                            WebDriverWait(driver, 10).until(lambda driver: high_res_img.get_attribute('complete') == 'true')
                        except TimeoutException:
                            print(f"画像 {current_position + 1}: 画像読み込みタイムアウト（続行）")
                    
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
                    
                except Exception as e:
                    print(f"画像 {position + 1}: 画像処理エラー: {e}")
                    close_modal_safely(driver)
                    continue
                
            except Exception as e:
                print(f"画像 {position + 1} の処理に失敗: {e}")
                close_modal_safely(driver)
                continue
        
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