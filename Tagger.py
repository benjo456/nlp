import re, os
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
java_path = "C:/Program Files/Java/jre1.8.0_144/bin/java.exe"
os.environ['JAVAHOME'] = java_path
class Tagger:
    def __init__(self,email):
        self.email = email

    def stanford(self,data,typeWanted):
        dir = 'C:/Users/Ben/Documents/NLP/nltk_data/stanford-ner-2018-10-16'
        model = dir + '/classifiers/english.all.3class.distsim.crf.ser.gz'
        jar = dir + '/stanford-ner.jar'
        st = StanfordNERTagger(model, jar, encoding='utf-8')
        tokenisedData = word_tokenize(data)
        classifiedData = st.tag(tokenisedData)
        returnData = []
        counter = 0
        lastTypeWanted = 0
        for entry in classifiedData:
            counter+=1
            if entry[1] == typeWanted:
                #Handles full names
                if counter == lastTypeWanted + 1:
                    lastItem = returnData.pop()
                    returnData.append(lastItem + " " + entry[0])
                else:
                    returnData.append(entry[0])
                lastTypeWanted = counter

        return returnData

    def b_tagger(self):
        pass

    def tagTimes(self, header):
        timeInfoPattern = re.compile(r'[Tt][Ii][Mm][Ee][:]([\W\w].*)')
        timeInfo = re.findall(timeInfoPattern,header)
        if timeInfo:
            print("Time found")
            timeSinglePattern = re.compile(r'([0-9]{1,2}\:?([0-9]{2}[ ]{0,1})?([AaPp][Mm])?)')
            times = re.findall(timeSinglePattern,timeInfo[0])
            if len(times) == 1:
                stime = times[0][0]
                print(stime)
                self.email.stime = stime
            elif len(times) == 2:
                stime = times[0][0]
                etime = times[1][0]
                print(stime,etime)
                self.email.stime = stime
                self.email.etime = etime
            else:
                print("No time found")

    def tagSpeaker(self):
        speakerLinePattern = re.compile(r'(?:Who|Host|Speaker):\s(.*)',flags=re.IGNORECASE)
        speakerLine = re.findall(speakerLinePattern,self.email.header+self.email.body)
        print(speakerLine)
        '''taggedHeader = self.stanford(self.email.header, 'PERSON')
        taggedBody = self.stanford(self.email.body, 'PERSON')
        print(taggedHeader)
        print(taggedBody)'''



    def tagLocation(self):
        pass

    def tagSent(self):
        pass

    def tagPara(self):
        pass

    def tagWholeEmails(self):
        pass