import re,os

class Evaluator:
    def __init__(self):
        self.filename = ""
        self.truePos = {}
        self.classified = {}
        self.trueCount = {}
        self.evalDicts = [self.truePos,self.classified,self.trueCount]
        self.evalAttr = ["location", "speaker","stime","etime","paragraph","sentence"]
        self.unTagged = ""
        self.speakers, self.location, self.stime, self.etime, self.para, self.sent = "","","","","",""

        self.originalValues = {}
        self.newValues = {}

        #Initialise dictionaries
        for i in self.evalDicts:
            for x in self.evalAttr:
                i[x] = 0

    def getFromTagged(self,email=None):

        if email:
            contents = email
        else:
            with open(self.filename,'r') as f:
                contents = f.read()

        speakers = self.extract("speaker",contents)
        location = self.extract("location",contents)
        stime = self.extract("stime",contents)
        etime = self.extract("etime",contents)
        para = self.extract("paragraph",contents)
        sent = self.extract("sentence",contents)

        allTags = re.compile(r'<([a-z/>]*)>')

        self.unTagged = re.sub(allTags,"",contents)

        return speakers,location,stime,etime,para,sent

    def extract(self,type,data,optReg=None):
        if optReg:
            regex = re.compile(optReg)
        else:
            regexString = r'<{}>([\d\D]*?)<\/{}>'.format(type,type)
            regex = re.compile(regexString)
        regexResults = re.findall(regex,data)

        return regexResults

    def truePositives(self,type, correctVals, testVals):
        self.classified[type] += len(testVals)
        self.trueCount[type] += len(correctVals)

        if any(isinstance(x, (tuple)) for x in correctVals):
            correctVals = [x[0] for x in correctVals]
        else:
            correctVals = [x.strip(' ') for x in correctVals]

        if any(isinstance(x, (tuple)) for x in testVals):
            testVals = [x[0] for x in testVals]
        else:
            testVals = [x.strip(' ') for x in testVals]

        counter = 0


        if type == "sentence":
            allTags = re.compile(r'<([a-z/>]*)>')
            correctVals = [re.sub(allTags, "", x.rstrip('\n')) for x in correctVals]
            testVals = [re.sub(allTags, "",  x.rstrip('\n')[:-1]) for x in testVals]

        if type == "paragraph":
            allTags = re.compile(r'<([a-z/>]*)>')
            correctVals = [re.sub(allTags, "", x.rstrip('\n')) for x in correctVals]
            testVals = [re.sub(allTags, "", x.rstrip('\n')) for x in testVals]

        #print("Test vals: " + str(testVals))
        #print("Correct vals : " + str(correctVals))

        if correctVals:
            for i in testVals:
                if i == correctVals[counter] or i in correctVals or i in correctVals[counter]:
                    self.truePos[type] += 1
                    counter+=1
                if len(correctVals) == counter:
                    break
        else:
            if testVals == correctVals:
                self.truePos[type] += 1
                self.classified[type] += 1
                self.trueCount[type] += 1

    def precision(self,type):
        truePosNumber = self.truePos[type]
        classifiedNum = self.classified[type]
        if classifiedNum > 0:
            return round(truePosNumber/classifiedNum,2)
        else:
            return 0

    def recall(self,type):
        truePosNumber = self.truePos[type]
        trueCountNumber = self.trueCount[type]
        if trueCountNumber > 0:
            return round(truePosNumber/trueCountNumber,2)
        else:
            return 0

    def fMeasure(self,type):
        precis = self.precision(type)
        recall = self.recall(type)
        if (precis+recall) > 0:
            divSum = round((precis * recall) / (precis + recall),2)
        else:
            divSum = 0
        return divSum * 2

    def evaluate(self,email):

        newEmail = email.newHeader + email.newBody
        Nspeakers, Nlocation, Nstime, Netime, Npara, Nsent = self.getFromTagged(newEmail)

        self.newValues["location"] = Nlocation
        self.newValues["speaker"] = Nspeakers
        self.newValues["stime"] = Nstime
        self.newValues["etime"] = Netime
        self.newValues["paragraph"] = Npara
        self.newValues["sentence"] = Nsent

        for i in self.evalAttr:
            originalVal = self.originalValues[i]
            generatedVal = self.newValues[i]
            self.truePositives(i,originalVal,generatedVal)

    def evalResults(self):
        for i in self.evalAttr:
            print("----" + str(i) + "----")
            print("Recall" + ": " + str(self.recall(i)))
            print("Precision"  + ": " + str(self.precision(i)))
            print("F measure" + ": " + str(self.fMeasure(i)))
            print()

    def getFileToTag(self,filename):
        self.filename = filename
        self.speakers, self.location, self.stime, self.etime, self.para, self.sent = self.getFromTagged()
        self.originalValues["location"] = self.location
        self.originalValues["speaker"] = self.speakers
        self.originalValues["stime"] = self.stime
        self.originalValues["etime"] = self.etime
        self.originalValues["paragraph"] = self.para
        self.originalValues["sentence"] = self.sent
        folder = os.path.dirname(self.filename)
        filename = (os.path.basename(os.path.splitext(filename)[0]))
        newFolder = folder + "\\untagged\\"
        if not os.path.exists(newFolder):
            os.makedirs(newFolder)
        newFileName = newFolder + filename + "-untagged.txt"
        file = open(newFileName, 'w')
        file.write(self.unTagged)
        file.close()
        return newFileName
