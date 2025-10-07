# E-ROOM Private Site

## 概要
E-ROOMについて、口コミや見やすい料金表を掲載した新しいホームページ（非公式）

## Facebook情報取得機能

### 機能概要
- Facebookの指定されたアカウントから最新5件の写真を自動取得
- 取得した画像は`images/facebook`ディレクトリに保存
- 既存ファイルの重複チェック機能付き
- GitHub Actionsによる定期実行（毎日午前9時 JST）

### 技術仕様
- **バックエンド**: Python + Selenium WebDriver
- **フロントエンド**: JavaScript（今後実装予定）
- **自動化**: GitHub Actions
- **対象アカウント**: [Facebook Profile](https://www.facebook.com/profile.php?id=100054664260008&sk=photos)

### セットアップ

#### 1. 環境変数の設定
GitHubリポジトリのSecretsに以下の環境変数を設定してください：

```
FACEBOOK_EMAIL=your_facebook_email@example.com
FACEBOOK_PASSWORD=your_facebook_password
```

#### 2. 必要なライブラリ
```bash
pip install -r scripts/requirements.txt
```

#### 3. 実行方法
- **手動実行**: GitHub Actionsの「Run workflow」ボタン
- **自動実行**: 毎日午前9時（JST）に自動実行

### ファイル構成
```
e-room/
├── scripts/
│   ├── get_image_from_facebook.py  # Facebook画像取得スクリプト
│   └── requirements.txt             # Python依存関係
├── images/
│   └── facebook/                    # 取得した画像の保存先
├── .github/workflows/
│   └── get_image_from_facebook.yml  # GitHub Actions設定
└── README.md
```

### 注意事項
- Facebookの利用規約に従って使用してください
- 取得した画像の著作権にご注意ください
- ログイン情報は適切に管理してください
- レート制限を考慮した実装になっています
