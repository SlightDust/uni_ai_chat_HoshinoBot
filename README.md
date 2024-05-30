# uni_ai_chat_HoshinoBot

适用于HoshinoBot的统一AI对话插件，会尽可能多的整合常见的AI问答API。为避免类似openai0.x和1.x的兼容性问题，目标是不依赖SDK，全部通过 HTTP / Restful 接口实现。  
Spark不得不用websocket……



## AI平台适配情况
### 已适配：
- [Azure OpenAI（国际版Azure）](https://portal.azure.com/)   
- [智谱清言（智谱AI）](https://www.zhipuai.cn)
- [ernie-bot（文心一言，百度千帆大模型）](https://console.bce.baidu.com/qianfan/)（免费版和付费版）
- [Spark（讯飞星火）](https://xinghuo.xfyun.cn/sparkapi)  
- [Qwen（通义千问）](https://bailian.console.aliyun.com/) （预留了调qwen-long和qwen-turbo两个命令）

### 适配中
- [便携AI转发的OpenAI](https://api.bianxieai.com/)  ←摸了
- and so on...

## 局限
- 代码很粗糙
- 目前，只做了单次对话，还没搞多轮对话

## 免费资源
目前（2024.05.22），以下大模型API可以免费使用：
- 文心一言的ERNIE-Speed、ERNIE-Lite、ERNIE-Tiny可以免费试用，需要实名认证。详见[公告](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/wlwg8f1i3)，[控制台计费管理](https://console.bce.baidu.com/qianfan/chargemanage/list)
- 讯飞星火的Spark Lite宣布永久免费，API需要实名认证，可以用非大陆手机号注册。[新闻](https://finance.eastmoney.com/a/202405223084395895.html)，[官网](https://xinghuo.xfyun.cn/sparkapi)

