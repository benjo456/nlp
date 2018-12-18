import calendar
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
warnings.filterwarnings(action='ignore', category=FutureWarning,module='gensim')
from nltk.tokenize import *
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter
import pickle, OntologyTree, pprint, json

class OntologyTagger:
    def __init__(self,email,model,tree,dir):
        self.email = email
        self.model = model
        self.tree = tree
        self.categ = []
        self.dir = dir

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
                names = pickle.load(f)
        except:
            with open("nameList.pkl", 'wb') as f:
                names = ['Type','Topic','Fwd','Lecture','Talk',"Series","Seminar","Seminars","Presentation","The"] + [x for x in calendar.month_name][1::]
                pickle.dump(names, f)
        newNames = []

        topic = self.findTopicHeader()
        if topic:
            toReturn = self.keyWordBody(names, newNames,self.email.body,topic)
            if toReturn:
                return toReturn
        return self.keyWordBody(names, newNames, self.email.header + self.email.body, None)

    def keyWordBody(self, names, newNames, data, topicSent):
        tokenisedData = word_tokenize(data)
        lemmatizer = WordNetLemmatizer()
        stopwordInTopic = stopwords.words('english')
        tokenisedData = [lemmatizer.lemmatize(token) for token in tokenisedData]
        tokenisedData = [token for token in tokenisedData if token not in stopwordInTopic and token.isalpha()]
        picklePath = self.dir + "/pickled/"
        pickleFileName = picklePath + str(self.email.fileID) + ".pickle"

        try:
            with open(pickleFileName, 'rb') as f:
                classifiedData = pickle.load(f)
                for i in classifiedData:
                    for entry in i:
                        if entry[1] in ['PERSON', 'LOCATION']:
                            if entry[0] in tokenisedData:
                                newNames.append(entry[0])
        except:
            pass
        names = names + newNames
        if topicSent:
            tokenisedHeader = word_tokenize(topicSent)
        else:
            tokenisedHeader = None

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
                if i[0] in headerKeywords and len(likelyTopics) < 5:
                    likelyTopics.append(i)
        else:
            likelyTopics = frequencies.most_common(4)

        with open("nameList.pkl", 'wb') as f:
            pickle.dump(names, f)
        return likelyTopics


    def findOntTreeMatch(self,keywords):
        matches = {}
        maxSimilarity = 0
        maxTopic = 0
        maxKeyword = ""
        self.categ = []
        self.traverseTree(self.tree)
        for i in keywords:
            for x in self.categ:
                cate = word_tokenize(x)
                for y in cate:
                    try:
                        s = self.model.similarity(i[0],y)
                    except KeyError:
                        s = 0
                    if s > maxSimilarity:
                        maxSimilarity = s
                        maxTopic = y
                        maxKeyword = i[0]
        self.addFileToTreeCat(self.tree,maxTopic)
        self.categ = []
        return self.tree

    def traverseTree(self,tr):
        for k, v in tr.items():
            if isinstance(v,list):
                self.categ.append(k)
            if isinstance(v, dict):
                self.traverseTree(v)
            else:
                continue

    def addFileToTreeCat(self,t,cat):
        id = self.email.fileID
        for k, v in t.items():
            if k == cat:
                if isinstance(v, list):
                    v.append(id)
            if isinstance(v, dict):
                self.addFileToTreeCat(v, cat)
            else:
                continue

    def printTree(self,tree):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(tree)
        #print(json.dumps(tree,indent=4))