import re
from asyncio import ensure_future, gather, get_event_loop, sleep
from collections import deque
from statistics import mean
from time import time

from aiohttp import ClientSession
import aiohttp
#from aiosocksy import Socks5Auth
#from aiosocksy.connector import ProxyConnector, ProxyClientRequest
#conna = ProxyConnector()
#socks = 'socks5://127.0.0.1:1087'
MIN_DURATION = 7
MAX_DURATION = 30
STABILITY_DELTA = 2
MIN_STABLE_MEASUREMENTS = 6

LOCAL_ADDRESS = "127.0.0.1"
LOCAL_PORT = 1088
proxy = "http://%s:%d" % (LOCAL_ADDRESS,LOCAL_PORT)

total = 0
done = 0
sessions = []

def setProxy(address,port):
    global LOCAL_ADDRESS,LOCAL_PORT,proxy
    LOCAL_PORT = port
    LOCAL_ADDRESS = address
    proxy = "http://%s:%d" % (LOCAL_ADDRESS,LOCAL_PORT)

async def run():
    print('fast.com cli')
    token = await get_token()
    urls = await get_urls(token)
    conns = await warmup(urls)
    future = ensure_future(measure(conns))
    result = await progress(future)
    await cleanup()
    return result


async def get_token():
    async with ClientSession() as s:
        resp = await s.get('https://fast.com/',proxy=proxy)
        text = await resp.text()
        script = re.search(r'<script src="(.*?)">', text).group(1)

        resp = await s.get(f'https://fast.com{script}',proxy=proxy)
        text = await resp.text()
        token = re.search(r'token:"(.*?)"', text).group(1)
    dot()
    return token


async def get_urls(token):
    async with ClientSession() as s:
        params = {'https': 'true', 'token': token, 'urlCount': 5}
        resp = await s.get('https://api.fast.com/netflix/speedtest', params=params,proxy=proxy)
        data = await resp.json()
    dot()
    return [x['url'] for x in data]


async def warmup(urls):
    conns = [get_connection(url) for url in urls]
    return await gather(*conns)


async def get_connection(url):
    s = ClientSession()
    sessions.append(s)
    conn = await s.get(url,proxy=proxy)
    dot()
    return conn


async def measure(conns):
    workers = [measure_speed(conn) for conn in conns]
    await gather(*workers)


async def measure_speed(conn):
    global total, done
    chunk_size = 64 * 2**10
    async for chunk in conn.content.iter_chunked(chunk_size):
        total += len(chunk)
    done += 1


def stabilized(deltas, elapsed):
    return (
        elapsed > MIN_DURATION and
        len(deltas) > MIN_STABLE_MEASUREMENTS and
        max(deltas) < STABILITY_DELTA
    )


async def progress(future):
    start = time()
    measurements = deque(maxlen=10)
    deltas = deque(maxlen=10)

    while True:
        await sleep(0.2)
        elapsed = time() - start
        speed = total / elapsed / 2**17
        measurements.append(speed)

        print(f'\033[2K\r{speed:.3f} mbps', end='', flush=True)

        if len(measurements) == 10:
            delta = abs(speed - mean(measurements)) / speed * 100
            deltas.append(delta)

        if done or elapsed > MAX_DURATION or stabilized(deltas, elapsed):
            future.cancel()
            return total/elapsed


async def cleanup():
    await gather(*[s.close() for s in sessions])
    print()


def dot():
    print('.', end='', flush=True)


def main():
    loop = get_event_loop()
    return loop.run_until_complete(run())


if __name__ == '__main__':
    main()
