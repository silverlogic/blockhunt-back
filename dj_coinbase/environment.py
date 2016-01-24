class Environment:
    def __init__(self, name, base_api_uri):
        self.name = name
        self.base_api_uri = base_api_uri

    def __repr__(self):
        return '{}(name={}, base_api_uri={})'.format(self.__class__.__name__,
                                                     self.name,
                                                     self.base_api_uri)


Environment.Production = Environment('Production', 'https://api.coinbase.com')
Environment.Sandbox = Environment('Sandbox', 'https://api.sandbox.coinbase.com')
