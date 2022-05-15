# Booker

某施設の利用予約と slack 通知を自動でやってくれる。

## 使い方（ローカル環境）

### 1. `.env` ファイルを置く
```
USERS_FILE_PATH=s3://path/to/users.jsonl
SELENIUM_REMOTE_URL=http://local.selenium:4444/wd/hub
RESERVATION_URL=https://...
SLACK_TOKEN=xoxb-...
SLACK_CHANNEL=C0000000000
```
| 環境変数 | 意味 |
| --- | --- |
| USERS_FILE_PATH | S3 上のユーザーデータの URI |
| SELENIUM_REMOTE_URL | 動作状況を見るために必要 |
| RESERVATION_URL | 某施設の予約ページ URL |
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
AWS_ACCESS_KEY_ID と AWS_SECRET_ACCESS_KEY は S3 からユーザーデータを読み込むために必要。

```
$ docker exec -it -e AWS_ACCESS_KEY_ID=[...] -e AWS_SECRET_ACCESS_KEY=[...] [app のコンテナ名] booker
```


## テスト

### ユニットテスト
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -e ."[dev]"
$ pytest
```

