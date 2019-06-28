from local_settings import DEFAULT_CONFIG as default_config

class Config:
    
    def __init__(self):
        self.ES_HOST             =   None
        self.ES_PORT             =   None
        self.MONGO_HOST          =   None
        self.MONGO_PORT          =   None


    async def load_config(self, config=default_config):
        self.ES_HOST                        =   config.get('ES_HOST')
        self.ES_PORT                        =   config.get('ES_PORT')
        self.MONGO_HOST                     =   config.get('MONGO_HOST')
        self.MONGO_PORT                     =   config.get('MONGO_PORT')
