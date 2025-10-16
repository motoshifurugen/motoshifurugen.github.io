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
        
        # 堅牢な画像要素検出システム
        def find_image_elements():
            """複数の方法で画像要素を検出する"""
            methods = [
                # 方法1: 直接的なリンク要素
                ("a[role='link']", "div[data-pagelet='ProfileAppSection_0'] a[role='link']"),
                
                # 方法2: 画像を含むdiv要素内のリンク
                ("div内のa要素", "div[data-pagelet='ProfileAppSection_0'] div[style*='min-width: 168px'] a"),
                
                # 方法3: 画像を含むdiv要素内のクリック可能要素
                ("div内のクリック要素", "div[data-pagelet='ProfileAppSection_0'] div[style*='min-width: 168px'] [role='button']"),
                
                # 方法4: 画像要素自体（親要素を取得）
                ("img要素の親", "div[data-pagelet='ProfileAppSection_0'] img"),
                
                # 方法5: より広範囲なdiv要素
                ("広範囲div", "div[data-pagelet='ProfileAppSection_0'] div[class*='x9f619']"),
                
                # 方法6: 画像を含む可能性のあるdiv要素
                ("画像div", "div[data-pagelet='ProfileAppSection_0'] div[style*='padding: 4px']")
            ]
            
            for method_name, selector in methods:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"{method_name}: {len(elements)}個の要素を発見")
                    
                    if len(elements) >= 5:  # 最低5個は必要
                        # 要素の検証
                        valid_elements = []
                        for i, element in enumerate(elements[:20]):  # 最初の20個をチェック
                            try:
                                # 要素が表示されているかチェック
                                if element.is_displayed() and element.is_enabled():
                                    # 要素内に画像があるかチェック
                                    img_in_element = element.find_elements(By.TAG_NAME, "img")
                                    if img_in_element or method_name == "img要素の親":
                                        valid_elements.append(element)
                                        if len(valid_elements) >= 10:  # 十分な数が見つかったら終了
                                            break
                            except Exception as e:
                                continue
                        
                        if len(valid_elements) >= 5:
                            print(f"{method_name}で有効な要素: {len(valid_elements)}個")
                            return valid_elements, method_name
                            
                except Exception as e:
                    print(f"{method_name}でエラー: {e}")
                    continue
            
            return [], "見つからず"
        
        # 画像要素を検出
        thumbnail_elements, detection_method = find_image_elements()
        print(f"検出方法: {detection_method}")
        print(f"最終的に見つかった要素数: {len(thumbnail_elements)}")
        
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
        
        # 取得する画像の位置を定義（利用可能な画像数に応じて調整）
        available_count = len(thumbnail_elements)
        if available_count >= 40:
            target_positions = [0, 9, 19, 29, 39]  # 1枚目、10枚目、20枚目、30枚目、40枚目
        elif available_count >= 20:
            target_positions = [0, 4, 9, 14, 19]  # 1枚目、5枚目、10枚目、15枚目、20枚目
        elif available_count >= 10:
            target_positions = [0, 2, 4, 6, 8]    # 1枚目、3枚目、5枚目、7枚目、9枚目
        else:
            target_positions = list(range(min(available_count, 5)))  # 利用可能な分だけ取得
        
        print(f"利用可能な画像数: {available_count}")
        print(f"取得対象の位置: {[pos + 1 for pos in target_positions]}枚目")
        
        # 画像をダウンロード - 指定された位置の画像のみを取得
        downloaded_count = 0
        processed_count = 0
        
        for position in target_positions:
            if position >= len(thumbnail_elements):
                print(f"位置 {position + 1} の画像が見つかりません（利用可能な画像数: {len(thumbnail_elements)}）")
                continue
                
            thumbnail_element = thumbnail_elements[position]
            try:
                processed_count += 1
                print(f"画像 {position + 1} を処理中... (新規取得: {downloaded_count}枚)")
                
                # サムネ画像をクリックして高画質画像を表示（検出方法に応じて適応）
                try:
                    if detection_method == "img要素の親":
                        # img要素の場合は、親要素をクリック
                        parent_element = thumbnail_element.find_element(By.XPATH, "./..")
                        driver.execute_script("arguments[0].click();", parent_element)
                    else:
                        # その他の場合は直接クリック
                        driver.execute_script("arguments[0].click();", thumbnail_element)
                    
                    time.sleep(3)  # モーダルが開くまで待機
                    
                except Exception as e:
                    print(f"画像 {position + 1}: クリックエラー: {e}")
                    continue
                
                # 高画質画像の要素を待機して取得（複数の方法を試す）
                try:
                    high_res_img = None
                    img_src = None
                    
                    # 方法1: MediaViewerPhotoの配下から高画質画像を取得
                    try:
                        high_res_img = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']"))
                        )
                        img_src = high_res_img.get_attribute('src')
                    except TimeoutException:
                        pass
                    
                    # 方法2: より広範囲なセレクターで画像を探す
                    if not img_src:
                        try:
                            high_res_img = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] img[src*='scontent']"))
                            )
                            img_src = high_res_img.get_attribute('src')
                        except TimeoutException:
                            pass
                    
                    # 方法3: モーダル内の画像を探す
                    if not img_src:
                        try:
                            high_res_img = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='dialog'] img"))
                            )
                            img_src = high_res_img.get_attribute('src')
                        except TimeoutException:
                            pass
                    
                    if not img_src:
                        print(f"画像 {position + 1}: 高画質画像のURLが見つかりません")
                        close_modal_safely(driver)
                        continue
                    
                    # 画像の読み込み完了を待つ
                    if high_res_img:
                        wait.until(lambda driver: high_res_img.get_attribute('complete') == 'true')
                    
                    # 画像をダウンロード
                    response = requests.get(img_src)
                    response.raise_for_status()
                    original_image_data = response.content
                    
                    # 重複チェック（元画像のハッシュで）
                    original_hash = hashlib.md5(original_image_data).hexdigest()
                    if original_hash in existing_hashes:
                        print(f"スキップ: 既存の画像 (ハッシュ: {original_hash[:8]}...)")
                        close_modal_safely(driver)
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
                    print(f"画像 {position + 1}: 高画質画像の読み込みがタイムアウトしました")
                    close_modal_safely(driver)
                    continue
                except Exception as e:
                    print(f"画像 {position + 1}: 画像処理エラー: {e}")
                    close_modal_safely(driver)
                    continue
                
            except Exception as e:
                print(f"画像 {position + 1} の処理に失敗: {e}")
                close_modal_safely(driver)
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