import requests

from util.selectors import get_agony
from util.multimerge import simple_merge

class ProviderError(Exception):
    """Raise when unable to obtain useful data from provider"""

class ProviderAPI(object):
    def __init__(self, host, providers):
        self.host = host.strip(r'/')
        self.url_template = self.host + '/scrapers/{}'
        self.providers = providers

    def query_provider(self, provider):
        try:
            r = requests.get(self.url_template.format(provider))
        except requests.exceptions.ConnectionError:
            raise ProviderError('Provider {} unavailable'.format(provider))

        try:
            data = r.json()
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

if __name__ == '__main__':
    url = 'http://localhost:9000'
    providers = ['Expedia',
                 'Orbitz',
                 'Priceline',
                 'Travelocity',
                 'United']
    api = ProviderAPI(url, providers)
    print(list((api.query())))
