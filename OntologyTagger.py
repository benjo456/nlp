import re
from nltk.tokenize import *
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter
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
        topic = self.findTopicHeader()
        if topic:
            data = self.email.header + self.email.body
            tokenisedData = word_tokenize(data)
            lemmatizer = WordNetLemmatizer()
            stopwordInTopic = stopwords.words('english')
            tokenisedData = [lemmatizer.lemmatize(token) for token in tokenisedData]
            tokenisedData = [token for token in tokenisedData if token not in stopwordInTopic and token.isalpha()]
            #print(tokenisedData)
            frequencies = Counter(tokenisedData)
            print(frequencies.most_common())
            tokenisedHeader = word_tokenize(self.email.header)
            headerKeywords = [word for word in tokenisedHeader if word in tokenisedData]
            likelyTopics = []
            for i in frequencies.most_common():
                if i[0] in headerKeywords and len(likelyTopics) < 4:
                    likelyTopics.append(i)
            print(likelyTopics)


