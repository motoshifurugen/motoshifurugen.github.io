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
    """固定ファイル名以外の古い画像を削除"""
    # 固定ファイル名以外の画像ファイルを削除
    all_files = list(save_dir.glob("*.jpg"))
    fixed_files = {f"slide_{i}.jpg" for i in range(1, max_files + 1)}
    
    for file_path in all_files:
        if file_path.name not in fixed_files:
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
        
        # ProfileAppSection_0の配下にある画像要素のみを取得
        elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
        if not elements:
            elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
        
        # 画像要素のみに絞り込み
        image_elements = []
        for element in elements:
            try:
                # 画像を含む要素かチェック
                img_tag = element.find_element(By.TAG_NAME, "img")
                if img_tag:
                    image_elements.append(element)
            except:
                continue
        
        print(f"見つかった画像要素数: {len(image_elements)}")
        
        # 固定ファイル名の画像数を確認
        existing_count = 0
        existing_files = []
        for i in range(1, 6):
            if (save_dir / f"slide_{i}.jpg").exists():
                existing_count += 1
                existing_files.append(f"slide_{i}.jpg")
        
        print(f"既存の固定画像: {existing_count}枚 ({', '.join(existing_files)})")
        
        if existing_count >= 5:
            print("既に5枚の固定画像が存在します。処理をスキップします。")
            return 0
        
        # 利用可能な要素数に応じて間隔を調整
        available_count = len(image_elements)
        if available_count >= 9:
            target_positions = [0, 2, 4, 6, 8]  # 1枚目、3枚目、5枚目、7枚目、9枚目
        elif available_count >= 7:
            target_positions = [0, 2, 4, 6]  # 1枚目、3枚目、5枚目、7枚目
        elif available_count >= 5:
            target_positions = [0, 2, 4]  # 1枚目、3枚目、5枚目
        elif available_count >= 3:
            target_positions = [0, 2]  # 1枚目、3枚目
        else:
            target_positions = [0]  # 1枚目のみ
        
        print(f"利用可能な要素数: {available_count}個")
        print(f"取得対象: {[pos + 1 for pos in target_positions]}枚目")
        
        downloaded_count = 0
        
        for target_pos in target_positions:
            if downloaded_count >= len(target_positions):
                break
                
            try:
                print(f"画像 {target_pos + 1} を処理中...")
                
                # 画像要素を再取得（stale element reference対策）
                current_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
                if not current_elements:
                    current_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
                
                # 画像要素のみに絞り込み
                current_image_elements = []
                for element in current_elements:
                    try:
                        img_tag = element.find_element(By.TAG_NAME, "img")
                        if img_tag:
                            current_image_elements.append(element)
                    except:
                        continue
                
                if target_pos >= len(current_image_elements):
                    print(f"画像 {target_pos + 1}: 画像要素が見つかりません")
                    continue
                
                element = current_image_elements[target_pos]
                
                # サムネ画像をクリック
                driver.execute_script("arguments[0].click();", element)
                time.sleep(5)  # モーダルが完全に開くまで待機
                
                # 高画質画像を取得（より確実な方法）
                img_src = None
                
                # 方法1: MediaViewerPhotoの高画質画像を待機
                try:
                    high_res_img = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']"))
                    )
                    # 画像の読み込み完了を待つ
                    WebDriverWait(driver, 10).until(
                        lambda driver: high_res_img.get_attribute('complete') == 'true'
                    )
                    img_src = high_res_img.get_attribute('src')
                    print(f"画像 {target_pos + 1}: MediaViewerPhotoで高画質画像を取得")
                except TimeoutException:
                    pass
                
                # 方法2: モーダル内の高画質画像を探す
                if not img_src:
                    try:
                        high_res_img = WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] img[src*='scontent']"))
                        )
                        WebDriverWait(driver, 8).until(
                            lambda driver: high_res_img.get_attribute('complete') == 'true'
                        )
                        img_src = high_res_img.get_attribute('src')
                        print(f"画像 {target_pos + 1}: モーダル内で高画質画像を取得")
                    except TimeoutException:
                        pass
                
                # 方法3: より一般的なセレクターで高画質画像を探す
                if not img_src:
                    try:
                        high_res_img = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='scontent'][src*='_n.jpg']"))
                        )
                        WebDriverWait(driver, 5).until(
                            lambda driver: high_res_img.get_attribute('complete') == 'true'
                        )
                        img_src = high_res_img.get_attribute('src')
                        print(f"画像 {target_pos + 1}: 一般的なセレクターで高画質画像を取得")
                    except TimeoutException:
                        pass
                
                if not img_src:
                    print(f"画像 {target_pos + 1}: 高画質画像のURLが見つかりません")
                    close_modal_safely(driver)
                    time.sleep(2)
                    continue
                    
                # 画像をダウンロード
                response = requests.get(img_src)
                response.raise_for_status()
                image_data = response.content
                
                # 重複チェック（固定ファイル名の既存画像と比較）
                image_hash = hashlib.md5(image_data).hexdigest()
                is_duplicate = False
                
                for i in range(1, 6):
                    existing_file = save_dir / f"slide_{i}.jpg"
                    if existing_file.exists():
                        try:
                            with open(existing_file, 'rb') as f:
                                existing_hash = hashlib.md5(f.read()).hexdigest()
                                if image_hash == existing_hash:
                                    print(f"スキップ: slide_{i}.jpg と同じ画像")
                                    is_duplicate = True
                                    break
                        except:
                            continue
                
                if is_duplicate:
                    close_modal_safely(driver)
                    time.sleep(2)
                    continue
                
                # 固定ファイル名で保存（スライドショー用）
                filename = f"slide_{downloaded_count + 1}.jpg"
                with open(save_dir / filename, 'wb') as f:
                    f.write(image_data)
                print(f"保存: {filename}")
                downloaded_count += 1
                
                # 古い画像を削除（5枚を超える場合）
                cleanup_old_images(save_dir, 5)
                
                # モーダルを閉じる
                close_modal_safely(driver)
                time.sleep(3)  # ページが安定するまで待機
                    
            except Exception as e:
                print(f"画像 {target_pos + 1} の処理に失敗: {e}")
                close_modal_safely(driver)
                time.sleep(3)  # エラー後もページが安定するまで待機
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