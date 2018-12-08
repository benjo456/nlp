class Email:
    def __init__(self,body,header):
        self.body = body
        self.header = header
        self.stime = None
        self.etime = None
        self.speaker = None
        self.location = None
        self.topic = None