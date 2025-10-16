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
        
        # 写真ページにアクセス（photos_byのみ）
        target_url = "https://www.facebook.com/bacoloderoom/photos_by"
        print(f"アクセス中: {target_url}")
        driver.get(target_url)
        time.sleep(8)  # 待機時間を延長
        
        # ページが完全に読み込まれるまで待機
        WebDriverWait(driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # 初期の要素数をチェック
        initial_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
        if not initial_elements:
            initial_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
        
        print(f"初期要素数: {len(initial_elements)}")
        
        # 要素数が少ない場合は追加の待機
        if len(initial_elements) < 5:
            print("要素数が少ないため、追加の待機時間を設けます...")
            time.sleep(10)
            
            # 再確認
            initial_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
            if not initial_elements:
                initial_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
            print(f"追加待機後の要素数: {len(initial_elements)}")
        
        # photos_byページに特化したスクロール戦略
        print("photos_byページをスクロールして画像を読み込み中...")
        max_scroll_attempts = 40  # スクロール回数を増加
        elements_found = len(initial_elements)
        no_change_count = 0
        last_scroll_height = 0
        
        print(f"スクロール開始時の要素数: {elements_found}")
        
        for i in range(max_scroll_attempts):
            # 現在のスクロール位置を記録
            current_scroll_height = driver.execute_script("return document.body.scrollHeight")
            
            # photos_byページに特化したスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4.0)  # より長い待機時間
            
            # 追加のスクロール（Facebookの遅延読み込みに対応）
            driver.execute_script("window.scrollBy(0, 3000);")
            time.sleep(2.0)
            
            # さらに追加スクロール
            driver.execute_script("window.scrollBy(0, -1000);")
            time.sleep(1.5)
            
            # 要素数をチェック（複数のセレクターで確認）
            current_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
            if not current_elements:
                current_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
            
            print(f"スクロール {i + 1}/{max_scroll_attempts} 完了 - 要素数: {len(current_elements)} (スクロール高: {current_scroll_height})")
            
            # 要素数が増加しなくなったら終了
            if len(current_elements) == elements_found and current_scroll_height == last_scroll_height:
                no_change_count += 1
                if no_change_count >= 3:  # 3回連続で変化なし
                    print("要素数とスクロール高が変化しなくなりました")
                    break
            else:
                no_change_count = 0
            
            elements_found = len(current_elements)
            last_scroll_height = current_scroll_height
            
            # 25個以上見つかったら早期終了
            if len(current_elements) >= 25:
                print("十分な要素が見つかりました")
                break
            
            # 追加の待機時間でコンテンツの読み込みを確実にする
            if i % 4 == 3:  # 4回ごとに追加待機
                print("追加の待機時間...")
                time.sleep(5)
        
        # 画像要素を検出（複数のセレクターで確認）
        thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a[role='link']")
        if not thumbnail_elements:
            thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet='ProfileAppSection_0'] a")
        print(f"見つかった要素数: {len(thumbnail_elements)}")
        
        # 要素が見つからない場合は、より広範囲なセレクターを試す
        if len(thumbnail_elements) < 5:
            print("要素数が少ないため、より広範囲なセレクターを試します...")
            alternative_selectors = [
                "div[data-pagelet*='ProfileApp'] a[role='link']",
                "div[data-pagelet*='ProfileApp'] a",
                "a[href*='/photos/']",
                "a[href*='photo.php']"
            ]
            
            for selector in alternative_selectors:
                try:
                    alt_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"セレクター '{selector}' で {len(alt_elements)} 個の要素を発見")
                    if len(alt_elements) > len(thumbnail_elements):
                        thumbnail_elements = alt_elements
                        print(f"より多くの要素が見つかりました: {len(thumbnail_elements)}個")
                except Exception as e:
                    print(f"セレクター '{selector}' でエラー: {e}")
        
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
        
        # 既に5枚以上ある場合は処理をスキップ
        if existing_image_count >= 5:
            print("既に5枚の画像が存在します。処理をスキップします。")
            return 0
        
        # 既存画像が少ない場合は、より積極的に取得を試みる
        if existing_image_count < 3:
            print("既存画像が少ないため、より積極的に取得を試みます。")
            TARGET_COUNT = 5  # 目標を5枚に設定
        else:
            TARGET_COUNT = 5 - existing_image_count  # 不足分のみ取得
        
        downloaded_count = 0
        processed_count = 0
        current_position = 0
        
        print(f"目標: {TARGET_COUNT}枚の画像を取得")
        
        # 利用可能な要素を取得
        def get_available_elements():
            """利用可能な要素を取得（複数のセレクターを試行）"""
            elements = []
            
            # 複数のセレクターを試行
            selectors = [
                ("div[data-pagelet='ProfileAppSection_0'] a[role='link']", "正確なセレクター"),
                ("div[data-pagelet='ProfileAppSection_0'] a", "広範囲セレクター1"),
                ("div[data-pagelet='ProfileAppSection_0'] [role='link']", "広範囲セレクター2"),
                ("div[data-pagelet*='ProfileApp'] a[role='link']", "ProfileAppセレクター"),
                ("div[data-pagelet*='ProfileApp'] a", "ProfileApp広範囲"),
                ("a[href*='/photos/']", "写真リンクセレクター"),
                ("a[href*='photo.php']", "photo.phpセレクター")
            ]
            
            for selector, description in selectors:
                try:
                    found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(found_elements) > len(elements):
                        elements = found_elements
                        print(f"{description}で{len(found_elements)}個の要素を発見")
                        # 十分な要素が見つかったら早期終了
                        if len(found_elements) >= 10:
                            break
                except Exception as e:
                    print(f"{description}でエラー: {e}")
            
            return elements
        
        # スクロール完了後に最終的な要素数を確認
        print("スクロール完了後の最終確認...")
        time.sleep(2)  # 追加の待機時間
        
        # 利用可能な要素数を確認してから適切な間隔を決定
        current_elements = get_available_elements()
        available_count = len(current_elements)
        print(f"最終的な利用可能な要素数: {available_count}個")
        
        # photos_byページで要素数が少ない場合は追加のスクロールを試行
        if available_count < 15:
            print("photos_byページで要素数が少ないため、追加のスクロールを実行します...")
            for i in range(15):  # スクロール回数を増加
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # 待機時間を延長
                driver.execute_script("window.scrollBy(0, 2000);")
                time.sleep(2)
                
                # 要素数を再確認
                current_elements = get_available_elements()
                new_count = len(current_elements)
                print(f"追加スクロール {i + 1}/15 - 要素数: {new_count}")
                
                if new_count > available_count:
                    available_count = new_count
                    current_elements = get_available_elements()
                
                if available_count >= 20:
                    print("十分な要素が見つかりました")
                    break
                
                # 5回ごとに追加の待機
                if i % 5 == 4:
                    print("追加の待機時間...")
                    time.sleep(5)
        
        # 利用可能な要素数に応じて間隔を調整
        if available_count >= 23:
            target_positions = [0, 4, 9, 15, 22]  # 1枚目、5枚目、10枚目、16枚目、23枚目
        elif available_count >= 16:
            target_positions = [0, 4, 9, 15]  # 1枚目、5枚目、10枚目、16枚目
        elif available_count >= 10:
            target_positions = [0, 4, 9]  # 1枚目、5枚目、10枚目
        elif available_count >= 5:
            target_positions = [0, 4]  # 1枚目、5枚目
        else:
            # 要素が少ない場合は、利用可能なすべての要素を取得
            target_positions = list(range(min(available_count, 5)))
            print(f"要素数が少ないため、利用可能なすべての要素を取得します: {[pos + 1 for pos in target_positions]}枚目")
        
        print(f"選択された間隔: {[pos + 1 for pos in target_positions]}枚目")
        
        # デバッグ情報: 見つかった要素の詳細を表示
        if available_count > 0:
            print("見つかった要素の詳細:")
            for i, element in enumerate(current_elements[:5]):  # 最初の5個の要素の詳細を表示
                try:
                    href = element.get_attribute('href')
                    print(f"  要素 {i + 1}: href={href[:50]}..." if href else f"  要素 {i + 1}: hrefなし")
                except:
                    print(f"  要素 {i + 1}: 詳細取得エラー")
        
        max_attempts = len(target_positions) * 2  # 各位置で最大2回試行
        attempt_count = 0
        
        for target_pos in target_positions:
            if downloaded_count >= TARGET_COUNT:
                break
                
            try:
                attempt_count += 1
                processed_count += 1
                print(f"画像 {target_pos + 1} を処理中... (新規取得: {downloaded_count}枚) [試行: {attempt_count}/{max_attempts}]")
                
                # 要素を再取得
                current_elements = get_available_elements()
                
                if target_pos >= len(current_elements):
                    print(f"画像 {target_pos + 1}: 要素が見つかりません（利用可能: {len(current_elements)}個）")
                    continue
                
                thumbnail_element = current_elements[target_pos]
                
                # 要素が有効かチェック
                if not thumbnail_element.is_displayed():
                    print(f"画像 {target_pos + 1}: 要素が表示されていません")
                    continue
                
                if not thumbnail_element.is_enabled():
                    print(f"画像 {target_pos + 1}: 要素が無効です")
                    continue
                
                # サムネ画像をクリックして高画質画像を表示
                try:
                    driver.execute_script("arguments[0].click();", thumbnail_element)
                    time.sleep(3)  # モーダルが開くまで待機
                    
                except Exception as e:
                    print(f"画像 {target_pos + 1}: クリックエラー: {e}")
                    continue
                
                # 高画質画像の要素を待機して取得（複数の方法を試す）
                try:
                    high_res_img = None
                    img_src = None
                    
                    # 方法1: MediaViewerPhotoの配下から高画質画像を取得
                    try:
                        high_res_img = WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-pagelet='MediaViewerPhoto'] img[src*='scontent']"))
                        )
                        img_src = high_res_img.get_attribute('src')
                        print(f"方法1で画像URLを取得: {img_src[:50]}...")
                    except TimeoutException:
                        pass
                    
                    # 方法2: より広範囲なセレクターで画像を探す
                    if not img_src:
                        try:
                            high_res_img = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] img[src*='scontent']"))
                            )
                            img_src = high_res_img.get_attribute('src')
                            print(f"方法2で画像URLを取得: {img_src[:50]}...")
                        except TimeoutException:
                            pass
                    
                    # 方法3: モーダル内の画像を探す
                    if not img_src:
                        try:
                            high_res_img = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='dialog'] img"))
                            )
                            img_src = high_res_img.get_attribute('src')
                            print(f"方法3で画像URLを取得: {img_src[:50]}...")
                        except TimeoutException:
                            pass
                    
                    # 方法4: より一般的なセレクターで画像を探す
                    if not img_src:
                        try:
                            high_res_img = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='scontent']"))
                            )
                            img_src = high_res_img.get_attribute('src')
                            print(f"方法4で画像URLを取得: {img_src[:50]}...")
                        except TimeoutException:
                            pass
                    
                    if not img_src:
                        print(f"画像 {target_pos + 1}: 高画質画像のURLが見つかりません")
                        close_modal_safely(driver)
                        continue
                    
                    # 画像の読み込み完了を待つ
                    if high_res_img:
                        try:
                            WebDriverWait(driver, 10).until(lambda driver: high_res_img.get_attribute('complete') == 'true')
                        except TimeoutException:
                            print(f"画像 {target_pos + 1}: 画像読み込みタイムアウト（続行）")
                    
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
                    
                except Exception as e:
                    print(f"画像 {target_pos + 1}: 画像処理エラー: {e}")
                    close_modal_safely(driver)
                    continue
                
            except Exception as e:
                print(f"画像 {target_pos + 1} の処理に失敗: {e}")
                close_modal_safely(driver)
                continue
        
        # 処理完了の表示
        print(f"指定された間隔での画像取得が完了しました")
        
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