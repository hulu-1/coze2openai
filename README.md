# 用户手册

## 情况
- coze.cn [目前API免费有限额](https://www.coze.cn/docs/developer_guides/coze_api_overview)
- coze.com [目前每个账号额度100](https://www.coze.com/token)


## 前置条件
- 注册COZE
- [申请API 得到API_KEY ](https://www.coze.cn/open)
- 创建COZE bot
- 发布bot到API

# 项目

## 结构
```textyour_project/
├── Dockerfile
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py
    └── other_module.py
```


## 环境变量
```text
   BOT_ID= xxxxx
   COZE_API_BASE=api.coze.cn
```

## model

```text 
随便填，最终跟是走的你COZE里bot选择的
```

##  效果

### chat

```text
curl --location --request POST 'http://127.0.0.1:3000/v1/chat/completions' \
--header 'Authorization: Bearer api key' \
--header 'Content-Type: application/json' \
--data-raw '{
    "model": "GPT-4o",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "你是谁呢"
                }
            ]
        }
    ],
    "max_tokens": 300,
    "stream":false
}'
```

### LOBE chat
![lobechat.png](doc%2Flobechat.png)

# 部署

## docker

```bash
docker run --name coze2api --restart=always -d -p 3000:3000 -e BOT_ID={{bot_id}}  hulu365/coze2api:latest
```


This project is tested with BrowserStack.
