# uni_ai_chat_HoshinoBot

适用于HoshinoBot的统一AI对话插件，会尽可能多的整合常见的AI问答API。为避免类似openai0.x和1.x的兼容性问题，目标是不依赖SDK，全部通过 HTTP / Restful 接口实现。



## 平台适配情况
### 已适配：
- [Azure OpenAI（国际版Azure）](https://portal.azure.com/)   
- [智谱清言（智谱AI）](https://www.zhipuai.cn)
- [ernie-bot（文心一言，百度千帆大模型）](https://console.bce.baidu.com/qianfan/)（免费版和付费版）

### 适配中
- [便携AI转发的OpenAI](https://api.bianxieai.com/)
- [SparkDesk（讯飞星火）](https://xinghuo.xfyun.cn/sparkapi)  
- and so on...

## 免费资源
目前（2024.05.22），以下大模型API可以免费使用：
- 文心一言的ERNIE-Speed、ERNIE-Lite、ERNIE-Tiny可以免费试用，无需付费，详见[公告](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/wlwg8f1i3)，[控制台计费管理](https://console.bce.baidu.com/qianfan/chargemanage/list)
- 讯飞星火的Spark Lite宣布永久免费，[新闻](https://finance.eastmoney.com/a/202405223084395895.html)，[官网](https://xinghuo.xfyun.cn/sparkapi)