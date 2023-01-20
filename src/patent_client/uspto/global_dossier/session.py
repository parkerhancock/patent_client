from patent_client.session import PatentClientSession


class GlobalDossierSession(PatentClientSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["Authorization"] = "OQmPwAN1QD4OXe25jpmMD27zmnM21gIL0lg85G6j"
