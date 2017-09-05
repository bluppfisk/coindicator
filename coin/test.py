import grequests

urls = ['https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD']

def print_url(r, **kwargs):
    print(r.url)

def async(url_list):
    sites = []
    for u in url_list:
        rs = grequests.get(u, hooks=dict(response=print_url))
        sites.append(rs)
    return grequests.map(sites)

async(urls)