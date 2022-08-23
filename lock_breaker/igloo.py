import datetime
import random

import pytz
import requests

from lock_breaker import IGLOO_API_URL, PIN, IGLOO_LOCK_IDS
from lock_breaker.gcs import igloo_api_key_reader


def _isodate_with_timezone(date) -> str:
    tz = pytz.timezone("America/Los_Angeles")
    aware_dt = tz.localize(date)
    return aware_dt.isoformat()

def _make_date_api_readable(date) -> str:
    date = date.replace(minute=0)
    date = date.replace(second=0)
    date = date.replace(microsecond=0)
    date= _isodate_with_timezone(date)
    return date

class IglooManager:
    def __init__(self, api_key):
        self.api_key = api_key

    @property
    def header(self):
        return {
            'X-IGLOOCOMPANY-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }


class Lock:
    def __init__(self,
                 manager: IglooManager,
                 lock_id: str):
        self.manager = manager
        self.lock_id = lock_id

    @property
    def _lock_api_url(self):
        return f'{IGLOO_API_URL}/locks/{self.lock_id}/pin'

    def hourly_pin(self):
        try:
            n = random.randint(1, 3)
            start = datetime.datetime.now()
            end = start + datetime.timedelta(hours=2)

            start = _make_date_api_readable(start)
            end = _make_date_api_readable(end)

            data = {
                'startDate': start,
                'endDate': end,
                'variance': n
            }

            res = requests.post(
                f'{self._lock_api_url}/hourly',
                json=data,
                headers=self.manager.header
            )
            return res.json()[PIN]
        except:
            return 'Need to enter API key.'

def fetch_igloo_pin(lock_id):
    api_key = igloo_api_key_reader()
    manager = IglooManager(api_key=api_key)
    lock = Lock(manager=manager,
                lock_id=lock_id)
    return lock.hourly_pin()

def get_igloo_pins():
    answer = {}
    for id in IGLOO_LOCK_IDS:
        answer[id] = fetch_igloo_pin(id)
    return answer
