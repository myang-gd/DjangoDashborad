class Result:
    
    SUCCESS = 'success'
    ERROR = 'error'
    RESPONSE = 'response'
    VALIDATIONRESULT = 'validationResult'
    SUCCESS_Y = 'Y'
    SUCCESS_N = 'N'
    def __init__(self):
        self.success = ''
        self.error = ''
        self.response = ''
        self.request = ''
        self.headers = ''
        self.validationResultMap = {}