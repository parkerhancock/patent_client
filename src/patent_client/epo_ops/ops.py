import requests

session = requests.Session()


CLIENT_SETTINGS = SETTINGS['EpoOpenPatentServices']
KEY = CLIENT_SETTINGS['ApiKey']
SECRET = CLIENT_SETTINGS['Secret']
CACHE_DIR = CACHE_BASE / 'epo'
CACHE_DIR.mkdir(exist_ok=True)


class OPSException(Exception):
    pass

class OPSAuthenticationException(OPSException):
    pass

class OpenPatentServices():
     def authenticate(self, key=None, secret=None):
        auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        global KEY, SECRET
        if key:
            KEY=key
            SECRET=secret

        response = session.post(
            auth_url, auth=(KEY, SECRET), data={"grant_type": "client_credentials"}
        )

        if not response.ok:
            raise OPSAuthenticationException()

        access_token = response.json()["access_token"]
        session.headers["Authorization"] = "Bearer " + access_token

    def pdf_request(self, fname, url, params=dict()):
        if os.path.exists(fname):
            return
        else:
            with open(fname, 'wb') as f:
                response = self.request(url, params, stream=True)
                f.write(response.raw.read())
    
    def request(self, url, params=dict(), stream=False):
        retry = 0
        while retry < 3:
            response = session.get(url, params=params, stream=stream)
            if response.ok:
                return response
            elif response.status_code in (400, 403):
                self.authenticate()
            elif not response.ok:
                tree = ET.fromstring(response.text.encode("utf-8"))
                code = tree.find("./ops:code", NS).text
                message = tree.find("./ops:message", NS).text
                details = tree.find('./ops:details', NS)
                if details is not None:
                    details = ''.join(details.itertext())
                else:
                    details = '<None>'
                raise OPSException(f"{response.status_code} - {code} - {message}\nDETAILS: {details} \nURL: {response.request.url}")
            retry += 1
        raise OPSException("Max Retries Exceeded!")

    def xml_request(self, url, params=dict()):
        print(url, params)
        param_hash = md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
        fname = os.path.join(CACHE_DIR, f"{url[37:].replace('/', '_')}{param_hash if params else ''}.xml")
        if os.path.exists(fname):
            return open(fname).read()
        response = self.request(url, params)
        text = response.text
        with open(fname, "w") as f:
            f.write(text)
        return text
    
    def original_to_docdb(self, number, doc_type):
        if 'PCT' in number:
            return self.parser.pct_to_docdb(number)

        country = country_re.search(number)
        if country:
            country = country.group(0)
            number = number[2:]
        else:
            country = "US"
            number = number

        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{country}.({number})/docdb"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.parser.docdb_number(app_ref, doc_type)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.docdb_number(pub_ref, doc_type)
    
    def original_to_epodoc(self, number, doc_type):
        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{number})/epodoc"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.parser.epodoc_number(app_ref)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.epodoc_number(pub_ref)

    def pct_to_docdb(self, number):
        _, country_year, number = number.split("/")
        country, year = country_year[:2], country_year[2:]
        if len(year) == 2:
            if int(year) > 50:
                year = "19" + year
            else:
                year = "20" + year

        # DocDB format changed in 2004:
        # Pre-2003 - CCyynnnnnW
        # Post-2003 - CCccyynnnnnnW
        if int(year) >= 2004:
            case_number = year + number.rjust(6, "0")
        else:
            case_number = year[2:] + number.rjust(5, "0")
        return DocDB(country, case_number, 'W', None, 'application')
