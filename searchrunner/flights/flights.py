import json
import requests
import threading

from util.error import ProviderError
from util.multimerge import simple_merge
from util.safestack import SafeStack
from util.selectors import get_agony

class ProviderAPI(object):
    def __init__(self, host, providers):
        self.host = host.strip(r'/')
        self.url_template = self.host + '/scrapers/{}'
        self.providers = providers
        self.results = SafeStack()

    def query_provider(self, provider):
        try:
            response = requests.get(self.url_template.format(provider))
        except requests.exceptions.ConnectionError:
            raise ProviderError('Provider {} unavailable'.format(provider))

        try:
            data = response.json()
        except ValueError:
            raise ProviderError('Could not parse response JSON from {}'.format(provider))

        try:
            results = data['results']
        except KeyError:
            raise ProviderError('No results in JSON response from {}'.format(provider))

        self.results.push(results)

    def query(self):
        for provider in self.providers:
            t = threading.Thread(target=self.query_provider,
                                 name=provider,
                                 kwargs={'provider': provider})
            t.start()

        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

        self.results.lock.acquire()
        results = simple_merge(get_agony, *self.results.stack)
        self.results.lock.release()
        return results

if __name__ == '__main__':
    url = 'http://localhost:9000'
    providers = ['Expedia',
                 'Orbitz',
                 'Priceline',
                 'Travelocity',
                 'United']
    api = ProviderAPI(url, providers)
    print(list((api.query())))
