class Email:
    def __init__(self,body,header,id):
        self.body = body
        self.header = header
        self.stime = None
        self.etime = None
        self.speaker = None
        self.location = None
        self.topic = None
        self.newHeader = header
        self.newBody = body
        self.sentences = []
        self.paragraphs = []
        self.fileID = id


    def replace(self,label,data):
        data = str(data)
        newStartTag = "<" + label + ">"
        newEndTag = "</" + label + ">"
        newWholeTag = newStartTag + data + newEndTag
        self.newHeader = self.newHeader.replace(data,newWholeTag)
        self.newBody = self.newBody.replace(data,newWholeTag)

    def combineTogether(self):
        for i in self.paragraphs:
            self.newBody = self.newBody.replace(i, "<paragraph>" + i + "</paragraph>")
        for i in self.sentences:
            self.newBody = self.newBody.replace(i, "<sentence>" + i + "</sentence>")

        self.replace("stime",self.stime)
        self.replace("etime", self.etime)
        self.replace("speaker", self.speaker)
        self.replace("location", self.location)

