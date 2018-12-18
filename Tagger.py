import re, os
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize, punkt
from collections import Counter
from sner import Ner
import pickle
from string import punctuation

java_path = "C:/Program Files/Java/jre1.8.0_144/bin/java.exe"
os.environ['JAVAHOME'] = java_path
classifiedData = ""


class Tagger:
    def __init__(self,email,st,dataDir):
        self.email = email
        self.st = st
        picklePath = dataDir + "/pickled/"
        self.pickleFileName = picklePath + str(self.email.fileID) + ".pickle"

    def stanford(self,data,typeWanted):
        try:
            with open(self.pickleFileName, 'rb') as f:
                classifiedData = pickle.load(f)
        except:
            tokenisedData = [word_tokenize(sent) for sent in sent_tokenize(data)]
            classifiedData = self.st.tag_sents(tokenisedData)
            with open(self.pickleFileName, 'wb') as f:
                pickle.dump(classifiedData, f)

        returnData = []
        counter = 0
        lastTypeWanted = 0
        titleRegex = re.compile(r'(Miss|Mr|Mrs|Dr|Prof|Professor|Doctor|Ms)(.){0,1}')
        lastTitle = ""
        for i in classifiedData:
            for entry in i:
                title = ""
                counter+=1
                if lastTitle:
                    title = lastTitle + " "
                    lastTitle = ""
                if entry[1] == typeWanted:
                    #Check for title
                    #Handles full names
                    if counter == lastTypeWanted + 1 and counter!= 1:
                        lastItem = returnData.pop()
                        returnData.append(title + lastItem + " " + entry[0])
                        lastTypeWanted = counter
                    else:
                        returnData.append(title + entry[0])
                        lastTypeWanted = counter
                elif re.match(titleRegex,entry[0]):
                    lastTitle = entry[0]
        return returnData

    def tagTimes(self, email):
        timeInfoPattern = re.compile(r'[Tt][Ii][Mm][Ee][:]([\W\w].*)')
        timeInfo = re.findall(timeInfoPattern,(email.body + email.header))
        if timeInfo:
            timeSinglePattern = re.compile(r'([0-9]{1,2}\:?([0-9]{2}[ ]{0,1})?([AaPp][Mm])?)')
            times = re.findall(timeSinglePattern,timeInfo[0])
            if len(times) == 1:
                stime = times[0][0]
                self.email.stime = stime
            elif len(times) == 2:
                stime = times[0][0]
                etime = times[1][0]
                self.email.stime = stime
                self.email.etime = etime
            else:
                pass

    def tagSpeaker(self):
        speakerLinePattern = re.compile(r'(?:Who|Host|Speaker):\s(.*)',flags=re.IGNORECASE)
        speakerLine = re.findall(speakerLinePattern,self.email.header+self.email.body)
        speakerLine = [x.lstrip() for x in speakerLine]
        if speakerLine:
            speakerPotential = speakerLine[0]
            if "," in speakerPotential:
                speakerPotential = speakerPotential[0:(speakerPotential.index(","))]
            if len(speakerPotential.split()) > 3:
                speakerPotential = speakerPotential.split()
                newSpeaker = ""
                for i in range(3):
                    newSpeaker = newSpeaker + " " + speakerPotential[i]
                speakerPotential = newSpeaker
            self.email.speaker = speakerPotential

        else:
            taggedBody = self.stanford(self.email.body, 'PERSON')
            c = Counter(taggedBody)
            if taggedBody:
                self.email.speaker = c.most_common(1)[0][0]
                taggedBody.remove(self.email.speaker)
                for i in taggedBody:
                    if self.email.speaker in i:
                        self.email.speaker = i
            else:
                pass

    def tagLocation(self):
        locationLinePattern = re.compile(r'(?:Place|Location|Where):\s(.*)', flags=re.IGNORECASE)
        locationPattern = re.compile(r'\b(Wing|Auditorium|Theatre|Hall|Room|Lab|Building)\b',flags=re.IGNORECASE)
        locationLine = re.findall(locationLinePattern, self.email.header + self.email.body)
        if locationLine:
            self.email.location = locationLine[0]
        else:
            otherLocationMentions = re.findall(locationPattern, self.email.body)
            if otherLocationMentions:
                indexOfMentionRegex = re.compile(r'\b(Wing|Auditorium|Theatre|Hall|Room|Lab|Building)\b',flags=re.IGNORECASE )
                mentionInText = re.findall(indexOfMentionRegex,self.email.body)
                wordList = self.email.body.lower().split()
                wordList = [re.sub(r'[^\w\s]','',x) for x in wordList]
                actualIndex = wordList.index(mentionInText[0].lower())
                wordBefore = wordList[actualIndex-1]
                try:
                    wordAfter = wordList[actualIndex+1]
                except:
                    wordAfter = ""
                if wordBefore in ['in', 'at']:
                    actualLocation = mentionInText[0] + wordAfter
                else:
                    if wordAfter.isdigit():
                        actualLocation = "{} {} {}".format(wordBefore.title(),mentionInText[0].title(),wordAfter.title())
                    else:
                        actualLocation = wordBefore.title() +  " " +  mentionInText[0].title()
                self.email.location = actualLocation
            else:
                self.email.location = self.advancedTagLocation()

    def advancedTagLocation(self):
        self.email.location = "Unknown"
        locations = []
        for i in classifiedData:
            for entry in i:
                title = ""
                if lastTitle:
                    title = lastTitle + " "
                    lastTitle = ""
                if entry[1] == "LOCATION":
                    locations.append(entry[0])
        c = Counter(locations)
        if locations:
            returnLoc = c.most_common(1)[0][0]
            return returnLoc
        else:
            return None

    def tagSent(self):
        text = (sent_tokenize(self.email.body))
        for i in text:
            self.email.sentences.append(i)

    def tagPara(self):
        paraList = self.email.body.split("\n\n")
        #rint(paraList)
        for i in paraList:
            if i != " " and i != '':
                self.email.paragraphs.append(i)
