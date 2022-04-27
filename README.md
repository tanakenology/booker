# Booker

某施設の利用予約と slack 通知を自動でやってくれる。

## 使い方（ローカル環境）

### 1. `.env` ファイルを置く
```
SELENIUM_REMOTE_URL=http://local.selenium:4444/wd/hub
RESERVATION_URL=https://...
DATE_PATTERN=（土,（日,祝）
NAME_KANJI=中田混沌
NAME_KANA=ナカタカオス
TELEPHONE=000-000-0000
EMAIL=test@example.com
SLACK_TOKEN=xoxb-...
SLACK_CHANNEL=C0000000000
```
| 環境変数 | 意味 |
| --- | --- |
| SELENIUM_REMOTE_URL | 動作状況を見るために必要 |
| RESERVATION_URL | 某施設の予約ページ URL |
| DATE_PATTERN | 予約したい曜日・祝日 |
| NAME_KANJI | 予約者の氏名（漢字表記） |
| NAME_KANA | 予約者の氏名（カタカナ表記） |
| TELEPHONE | 予約者の電話番号（ 000-000-0000 形式） |
| EMAIL | 予約者のメールアドレス |
| SLACK_TOKEN | slack の Bot トークン |
| SLACK_CHANNEL | slack のチャンネル |

### 2. コンテナ起動
```
$ docker-compose up --build -d
```

実際に画面が動作する様子を見たい場合は、事前に以下のコマンドを実行して chrome コンテナに vnc で接続しておく。パスワードは `secret` 。

```
$ open vnc://localhost:5900
```

### 3. コマンド実行
```
$ docker exec -it [app のコンテナ名 ] booker
```


## テスト

### ユニットテスト

```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -e ."[dev]"
$ pytest
```

