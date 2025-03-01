import configparser
import os

current_path = os.path.dirname(__file__)
if not os.path.exists(os.path.join(current_path, 'config.ini')):
    with open(os.path.join(current_path, 'config_example.ini'), "rb") as source_file:
        with open(os.path.join(current_path, 'config.ini'), "wb") as target_file:
            target_file.write(source_file.read())

class Config:
    _config = configparser.ConfigParser()
    api_base: str
    api_key: str
    model: str
    max_tokens: int
    temperature: float
    top_p: float  
    use_web_search: bool
    system: str  # 系统设定
    _current_path = os.path.dirname(__file__)
    _token_cost_path = os.path.join(_current_path, 'token_cost.json')
    
    def __init__(self):
        self.load_config()

    def load_config(self):
        self._config.read(os.path.join(self._current_path, 'config.ini'), encoding='utf-8')
    
    def _float(self, value):
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    def _int(self, value):
        try:
            return int(value)
        except ValueError:  
            return 0

class global_Config(Config):
    def __init__(self):
        super().__init__()
        self.history_limit = self._int(self._config.get('global', 'history_limit', fallback=10))

class zhipu_Config(Config):
    def __init__(self):
        super().__init__()
        self.api_key = self._config.get('zhipu', 'api_key')
        self.model = self._config.get('zhipu','model')
        self.max_tokens = self._int(self._config.get('zhipu','max_tokens'))
        self.temperature = self._float(self._config.get('zhipu', 'temperature', fallback=0.9))
        self.top_p = self._float(self._config.get('zhipu', 'top_p', fallback=0.7))
        self.system = self._config.get('zhipu','system')
        self.use_web_search = self._config.getboolean('zhipu', 'use_web_search', fallback=True)

class zhipuV_Config(Config):    
    def __init__(self):
        super().__init__()
        self.api_key = self._config.get('zhipuV', 'api_key')
        self.model = self._config.get('zhipuV','model')
        self.max_tokens = self._int(self._config.get('zhipuV','max_tokens'))
        self.temperature = self._float(self._config.get('zhipuV', 'temperature', fallback=0.9))
        self.top_p = self._float(self._config.get('zhipuV', 'top_p', fallback=0.7))
        self.system = self._config.get('zhipuV','system')

class azure_openai_Config(Config):
    def __init__(self):
        super().__init__()
        self.api_end_point = self._config.get('azure_openai', 'api_end_point')
        self.deply_name = self._config.get('azure_openai', 'deply_name')
        self.api_version = self._config.get('azure_openai', 'api_version')
        self.api_key = self._config.get('azure_openai', 'api_key')
        self.max_tokens = self._int(self._config.get('azure_openai','max_tokens'))
        self.temperature = self._float(self._config.get('azure_openai', 'temperature', fallback=0.9))
        self.top_p = self._float(self._config.get('azure_openai', 'top_p', fallback=0.7))
        self.system = self._config.get('azure_openai','system')


class bianxieai_openai_Config(Config):
    def __init__(self):
        super().__init__()
        self.api_base = self._config.get('bianxieai_openai', 'api_base')
        self.api_key = self._config.get('bianxieai_openai', 'api_key')


class ernie_Config(Config):
    def __init__(self):
        super().__init__()
        self.free_model = self._config.get('ernie','free_model')
        self.model = self._config.get('ernie','model')
        self.api_key = self._config.get('ernie', 'api_key')
        self.secret_key = self._config.get('ernie','secret_key')
        self.auth_method = self._config.get('ernie', 'auth_method')
        self.client_id = self.api_key
        self.client_secret = self.secret_key
        self.temperature = self._float(self._config.get('ernie', 'temperature', fallback=0.95))
        self.top_p = self._float(self._config.get('ernie', 'top_p', fallback=0.7))
        self.penalty_score = self._float(self._config.get('ernie', 'penalty_score', fallback=1))
        self.max_tokens = self._int(self._config.get('ernie','max_output_tokens'))
        self.max_output_tokens = self.max_tokens
        self.system = self._config.get('ernie','system')
        self.enable_citation = self._config.getboolean('ernie', 'enable_citation')
        self.enable_trace = self._config.getboolean('ernie', 'enable_trace')


class spark_Config(Config):
    def __init__(self):
        super().__init__()
        self.api_base = self._config.get('spark', 'url')
        self.url = self.api_base
        self.domain = self._config.get('spark', 'domain')
        self.appid = self._config.get('spark', 'appid')
        self.api_secret = self._config.get('spark', 'api_secret')
        self.api_key = self._config.get('spark', 'api_key')
        self.temperature = self._float(self._config.get('spark', 'temperature', fallback=0.9))
        self.max_tokens = self._int(self._config.get('spark','max_tokens'))
        self.top_k = self._int(self._config.get('spark', 'top_k'))
        self.system = self._config.get('spark','system')

class qwen_Config(Config):
    def __init__(self):
        super().__init__()
        self.api_key = self._config.get('qwen', 'api_key')
        self.model = self._config.get('qwen','model')
        self.model_search = self._config.get('qwen','model_search')
        self.max_tokens = self._int(self._config.get('qwen','max_tokens'))
        self.url = self._config.get('qwen', 'url')
        self.top_p = self._float(self._config.get('qwen', 'top_p'))
        self.temperature = self._float(self._config.get('qwen', 'temperature'))
        self.system = self._config.get('qwen','system')

class deepseek_Config(Config):
    def __init__(self):
        super().__init__()
        self.api_key = self._config.get('deepseek', 'api_key')
        self.model = self._config.get('deepseek','model')
        self.model_reasoner = self._config.get('deepseek','model_reasoner')
        self.url = self._config.get('deepseek', 'url')
        self.temperature = self._float(self._config.get('deepseek', 'temperature'))
        self.top_p = self._float(self._config.get('deepseek', 'top_p'))
        self.frequency_penalty = self._float(self._config.get('deepseek', 'frequency_penalty'))
        self.presence_penalty = self._float(self._config.get('deepseek', 'presence_penalty'))
        self.stream = self._config.getboolean('deepseek','stream')
        self.system = self._config.get('deepseek','system')
        self.max_tokens = self._int(self._config.get('deepseek','max_tokens'))
        



if __name__ == '__main__':
    config = spark_Config()
    print(bool(config.system))