import re

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
            #print("Contents:")
            #print(contents)
        else:
            with open(self.filename,'r') as f:
                contents = f.read()
                #print(contents)
        '''print()
        print()
        print(contents)
        print()
        print()'''
        speakers = self.extract("speaker",contents)
        location = self.extract("location",contents)
        stime = self.extract("stime",contents)
        etime = self.extract("etime",contents)
       # para = self.extract("paragraph",contents,r'<paragraph>((.|\s)+?)<\/paragraph>')
       # sent = self.extract("sentence",contents,r'<sentence>((.|\s)+?)<\/sentence>')
        para = self.extract("paragraph",contents)
        sent = self.extract("sentence",contents)

        allTags = re.compile(r'<([a-z/>]*)>')

        self.unTagged = re.sub(allTags,"",contents)

        '''for i in sent:
            re.sub(allTags,'',i)
            print(i)'''

        return speakers,location,stime,etime,para,sent

    def extract(self,type,data,optReg=None):
        if optReg:
            regex = re.compile(optReg)
        else:
            #regexString2 = r'<{}>((.|\s)+?)<\/{}>'.format(type, type)
            #regexString = r'<{}\>(.*)\<\/{}>'.format(type,type)
            regexString = r'<{}>([\d\D]*?)<\/{}>'.format(type,type)
            regex = re.compile(regexString)
        regexResults = re.findall(regex,data)
        #print("Results: " + str(regexResults))

        return regexResults

    def truePositives(self,type, correctVals, testVals):
        self.classified[type] += len(testVals)
        self.trueCount[type] += len(correctVals)

        if any(isinstance(x, (tuple)) for x in correctVals):
            #correctVals = correctVals[0]
            correctVals = [x[0] for x in correctVals]
        else:
            correctVals = [x.strip(' ') for x in correctVals]

        if any(isinstance(x, (tuple)) for x in testVals):
            #testVals = testVals[0]
            testVals = [x[0] for x in testVals]
        else:
            testVals = [x.strip(' ') for x in testVals]

        counter = 0
        #print("Type : " + type)


        if type == "sentence":
            allTags = re.compile(r'<([a-z/>]*)>')
            correctVals = [re.sub(allTags, "", x.rstrip('\n')) for x in correctVals]
            testVals = [re.sub(allTags, "",  x.rstrip('\n')[:-1]) for x in testVals]

        if type == "paragraph":
            allTags = re.compile(r'<([a-z/>]*)>')
            correctVals = [re.sub(allTags, "", x.rstrip('\n')) for x in correctVals]
            testVals = [re.sub(allTags, "", x.rstrip('\n')) for x in testVals]

        print("Test vals: " + str(testVals))
        print("Correct vals : " + str(correctVals))

        if correctVals:
            for i in testVals:
                #print(counter)
                if i == correctVals[counter] or i in correctVals or i in correctVals[counter]:
                    self.truePos[type] += 1
                    counter+=1
                '''elif (type != "sentence" ) and (type != "paragraph"):
                    print("Type: " + type)
                    print("My value: " + str(i))
                    print("Correct value: " + correctVals[counter])'''
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
        #speakers, location, stime, etime, para, sent = self.getFromTagged(oldFile)
        #self.genNewValues(email)
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
            #print("Originals")
            #print(originalVal)
            #print("Generated")
            #print(generatedVal)
            self.truePositives(i,originalVal,generatedVal)

    def evalResults(self):
        for i in self.evalAttr:
            print("----" + str(i) + "----")
            print("Recall" + ": " + str(self.recall(i)))
            print("Precision"  + ": " + str(self.precision(i)))
            print("F measure" + ": " + str(self.fMeasure(i)))


            print()

    def genNewValues(self):
        pass

    def getFileToTag(self,filename):
        self.filename = filename
        self.speakers, self.location, self.stime, self.etime, self.para, self.sent = self.getFromTagged()
        self.originalValues["location"] = self.location
        self.originalValues["speaker"] = self.speakers
        self.originalValues["stime"] = self.stime
        self.originalValues["etime"] = self.etime
        self.originalValues["paragraph"] = self.para
        self.originalValues["sentence"] = self.sent
        file = open(self.filename + "-untagged.txt", 'w')
        file.write(self.unTagged)
        file.close()
        return self.filename + "-untagged.txt"
