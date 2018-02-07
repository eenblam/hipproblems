from flask import Flask, jsonify

from flights.flights import ProviderAPI

app = Flask(__name__)

@app.route('/flights/search')
def search():
    """Aggregate search results across all providers"""
    url = 'http://localhost:9000'
    providers = ['Expedia',
                 'Orbitz',
                 'Priceline',
                 'Travelocity',
                 'United']
    api = ProviderAPI(url, providers)

    return jsonify(results=list(api.query()))

if __name__ == '__main__':
    app.run(port=8000)
