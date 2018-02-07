import json
from tornado import httpclient, ioloop

from util.error import ProviderError
from util.selectors import get_agony
from util.multimerge import simple_merge

class ProviderAPI(object):
    def __init__(self, host, providers):
        self.host = host.strip(r'/')
        self.url_template = self.host + '/scrapers/{}'
        self.providers = providers
        self.results = []

    def query_provider(self, provider):
        client = httpclient.HTTPClient()
        try:
            response = client.fetch(self.url_template.format(provider))
        except tornado.httpclient.HTTPError:
            raise ProviderError('Provider {} unavailable'.format(provider))

        try:
            data = json.loads(response.body)
        except ValueError:
            raise ProviderError('Could not parse response JSON from {}'.format(provider))

        try:
            results = data['results']
        except KeyError:
            raise ProviderError('No results in JSON response from {}'.format(provider))

        return results

    def query(self):
        results = []
        for provider in self.providers:
            try:
                results.append(self.query_provider(provider))
            except ProviderError as e:
                print(e)
                continue

        return simple_merge(get_agony, *results)

    def async_query(self):
        client = httpclient.AsyncHTTPClient()
        for provider in self.providers:
            url = self.url_template.format(provider)
            client.fetch(url, self._push_response, method='GET')

        ioloop.IOLoop.instance().start()
        return simple_merge(get_agony, *self.results)

    def _push_response(self, response):
        try:
            data = json.loads(response.body)
            result = data['results']
        except ValueError:
            # Couldn't parse JSON
            result = []
        except KeyError:
            # Results key missing
            result = []

        self.results.append(result)
        if len(self.results) == len(self.providers):
            ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    url = 'http://localhost:9000'
    providers = ['Expedia',
                 'Orbitz',
                 'Priceline',
                 'Travelocity',
                 'United']
    api = ProviderAPI(url, providers)
    print(list((api.query())))
