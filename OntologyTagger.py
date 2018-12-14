import calendar
import re
from nltk.tokenize import *
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter
import pickle
import string

class OntologyTagger:
    def __init__(self,email):
        self.email = email

    def findTopicHeader(self):
        email = self.email
        header = self.email.header
        topicPattern = re.compile(r'Topic[:]([\W\w].*)',flags=re.IGNORECASE)
        topicLine = re.findall(topicPattern,(email.header))
        if topicLine:
            topic = topicLine[0]
            return topic
        else:
            return None

    def keyWordsInTopic(self):
        try:
            with open("nameList.pkl", 'rb') as f:
                # print("Loading pickle")
                names = pickle.load(f)
                #(names)
        except:
            with open("nameList.pkl", 'wb') as f:
                names = ['Type','Topic','Fwd','Lecture','Talk',"Series","Seminar","Seminars","Presentation"] + [x for x in calendar.month_name][1::]
                pickle.dump(names, f)
        newNames = []

        topic = self.findTopicHeader()
        if topic:
            toReturn = self.keyWordBody(names, newNames,self.email.body,topic)
            if toReturn:
                return toReturn
            #return self.keyWordBody(names, newNames,self.email.header + self.email.body)
        return self.keyWordBody(names, newNames, self.email.header + self.email.body, None)

    def keyWordBody(self, names, newNames, data, topicSent):
        #data = self.email.header + self.email.body
        tokenisedData = word_tokenize(data)
        lemmatizer = WordNetLemmatizer()
        stopwordInTopic = stopwords.words('english')
        tokenisedData = [lemmatizer.lemmatize(token) for token in tokenisedData]
        tokenisedData = [token for token in tokenisedData if token not in stopwordInTopic and token.isalpha()]
        picklePath = "C:/Users/Ben/Documents/NLP/nltk_data/pickled/"
        pickleFileName = picklePath + str(self.email.fileID) + ".pickle"

        try:
            with open(pickleFileName, 'rb') as f:
                # print("Loading pickle")
                classifiedData = pickle.load(f)
                for i in classifiedData:
                    for entry in i:
                        if entry[1] in ['PERSON', 'LOCATION']:
                            if entry[0] in tokenisedData:
                                newNames.append(entry[0])
                                # print(entry[0] in tokenisedData)
                # print("######### Ending stanford #################")
        except:
            pass
        names = names + newNames
        # print(frequencies.most_common())
        if topicSent:
            tokenisedHeader = word_tokenize(topicSent)
        else:
            tokenisedHeader = None

        ''' for i in names:
                        tokenisedHeader = [x for x in tokenisedHeader if x.lower() != i.lower()]
                        tokenisedData = [x for x in tokenisedData if x.lower() != i.lower()'''
        for i in names:
            if tokenisedHeader:
                for x in tokenisedHeader:
                    if i.lower() == x.lower():
                        tokenisedHeader.remove(x)
            for y in tokenisedData:
                if i.lower() == y.lower():
                    tokenisedData.remove(y)

        frequencies = Counter(tokenisedData)
        likelyTopics = []

        if tokenisedHeader:
            headerKeywords = [word for word in tokenisedHeader if word in tokenisedData]
            for i in frequencies.most_common():
                if i[0] in headerKeywords and len(likelyTopics) < 4:
                    likelyTopics.append(i)
        else:
            likelyTopics = frequencies.most_common(4)

        with open("nameList.pkl", 'wb') as f:
            pickle.dump(names, f)
        return likelyTopics

