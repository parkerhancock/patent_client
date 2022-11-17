import re
import requests


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = TessState()
        self.headers['user-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        
    def request(self, *args, **kwargs):
        state = bool(self.state)
        if not state:
            self.login()
        response = super().request(*args, **kwargs)
        if state_re.search(response.text):
            self.state = TessState(response.text)
        if "This search session has expired." in response.text or "Bad query - no database specified" in response.text:
            raise ExpiredSessionException()
        return response
    
    def get_state(self):
        return self.state
        
    def login(self):
        login_response = super().request("get", "https://tmsearch.uspto.gov/bin/gate.exe", params={"f": "login", "p_lang": "english", "p_d": "trmk"})
        self.state = TessState(login_response.text)
        print(f"Logged in! Current State: {self.state}")
            
    def __del__(self):
        super().request("post", "https://tmsearch.uspto.gov/bin/gate.exe", data={"state": str(self.state), "f": "logout", "a_logout": "Logout"})
        print("Logged out!")

session = TessSession()