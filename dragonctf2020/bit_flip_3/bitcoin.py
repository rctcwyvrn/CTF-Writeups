import requests
import hashlib


def as_le(x):
    return bytes.fromhex(x)[::-1]

def as_le_int(x, sz=4):
    return x.to_bytes(sz, 'little')

def get_val(bid):
    r = requests.get('https://chain.api.btc.com/v3/block/%s' % bid, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:83.0) Gecko/20100101 Firefox/83.0'})
    #print(r.text)
    r.raise_for_status()
    data = r.json()['data']

    tohash = as_le_int(data['version']) + as_le(data['prev_block_hash']) + as_le(data['mrkl_root']) + as_le_int(data['timestamp']) + as_le_int(data['bits']) + as_le_int(data['nonce'])
    return hashlib.sha256(tohash).hexdigest()
    #  print(hashlib.sha256(tohash).hexdigest())
    # print(hashlib.sha256(hashlib.sha256(tohash).digest()).hexdigest())
