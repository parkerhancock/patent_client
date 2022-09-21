import re
import time
import requests
import threading
from copy import copy
from concurrent.futures import ThreadPoolExecutor


state_re = re.compile(r"state=(?P<session_id>\d{4}:\w+).(?P<query_id>\d+).(?P<record_id>\d+)")

class TessState():    
    def __init__(self, response_body=None):
        if response_body is None:
            self.session_id = self.query_id = self.record_id = ''
        else:
            state = state_re.search(response_body).groupdict()
            self.session_id = state['session_id']
            self.query_id = state['query_id']
            self.record_id = state['record_id']
    
    def __str__(self):
        return f"{self.session_id}.{self.query_id}.{self.record_id}"
    
    @property
    def string(self):
        return str(self)

class ExpiredSessionException(Exception):
    pass

class TessSession(requests.Session):
    heartbeat_interval = 30
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = TessState()
        self.state_lock = threading.Lock()
        self.keep_alive_thread = ThreadPoolExecutor(thread_name_prefix="TESS-Keep-Alive")
        self.headers['user-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        
    def request(self, *args, **kwargs):
        with self.state_lock:
            state = bool(self.state)
        if not state:
            self.login()
        response = super().request(*args, **kwargs)
        if state_re.search(response.text):
            with self.state_lock:
                self.state = TessState(response.text)
        if "This search session has expired." in response.text or "Bad query - no database specified" in response.text:
            raise ExpiredSessionException()

        return response
    
    def get_state(self):
        with self.state_lock:
            return copy(self.state)
        
    def login(self):
        login_response = super().request("get", "https://tmsearch.uspto.gov/bin/gate.exe", params={"f": "login", "p_lang": "english", "p_d": "trmk"})
        with self.state_lock:
            self.state = TessState(login_response.text)
            print(f"Logged in! Current State: {self.state}")
        # Kill the existing keep-alive thread
        self.keep_alive_thread.shutdown(wait=False, cancel_futures=True)
        # Create a new keep-alive thread
        self.keep_alive_thread = ThreadPoolExecutor(thread_name_prefix="TESS-Keep-Alive")
        self.keep_alive_thread.submit(self.keep_alive)
        
    def keep_alive(self):
        while True:
            with self.state_lock:
                response = super().request("get", "https://tmsearch.uspto.gov/bin/gate.exe", params={"f": "tess", "state": str(state)})
            time.sleep(self.heartbeat_interval)
            
    def __del__(self):
        self.keep_alive_thread.shutdown(wait=False, cancel_futures=True)
        super().request("post", "https://tmsearch.uspto.gov/bin/gate.exe", data={"state": str(self.state), "f": "logout", "a_logout": "Logout"})
        print("Logged out!")

session = TessSession()