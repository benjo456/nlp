import calendar
import re
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from os.path import expanduser, join
from nltk.tokenize import *
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet, brown
from collections import Counter
import pickle, OntologyTree, pprint, json


import gensim
import string


class OntologyTagger:
    def __init__(self,email,model,tree):
        self.email = email
        self.model = model
        self.tree = tree
        self.categ = []
        self.loadTree()
        print(self.tree)

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
                names = ['Type','Topic','Fwd','Lecture','Talk',"Series","Seminar","Seminars","Presentation","The"] + [x for x in calendar.month_name][1::]
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
                if i[0] in headerKeywords and len(likelyTopics) < 5:
                    likelyTopics.append(i)
        else:
            likelyTopics = frequencies.most_common(4)

        with open("nameList.pkl", 'wb') as f:
            pickle.dump(names, f)
        return likelyTopics


    def findOntTreeMatch(self,keywords):
        self.loadTree()
        #tree = OntologyTree.tree
        #tree = self.tree
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(tree)
        #print(json.dumps(tree,indent=4))
        matches = {}
        maxSimilarity = 0
        maxTopic = 0
        maxKeyword = ""
        self.categ = []
        self.traverseTree(self.tree)
        print(self.categ)
        for i in keywords:
            print(self.tree.keys())
            for x in self.categ:
                print(i[0],x)
                #s = keyword[0].path_similarity(treeWord[0])
                s = self.model.similarity(str(i[0]),str(x))
                print(s)
                if s > maxSimilarity:
                    maxSimilarity = s
                    maxTopic = x
                    maxKeyword = i[0]
        print("Results:")
        print(maxKeyword, maxTopic)
        print()
        self.addFileToTreeCat(self.tree,maxTopic)
        with open("tree.pkl",'wb') as f:
            pickle.dump(self.tree, f)
            self.categ = []
        return self.tree

    def traverseTree(self,tr):
        for k, v in tr.items():
            ''' print()
            print("K: " + str(k))
            print("V: " + str(v))'''
            if isinstance(v,list):
                self.categ.append(k)
            if isinstance(v, dict):
                #print("Is dict, going deeper")
                self.traverseTree(v)
            else:
                #print("Not dict, continuing)")
                continue

    def addFileToTreeCat(self,t,cat):
        id = self.email.fileID
        if isinstance(t,list):
            t.append(cat)
            return
        for k, v in t.items():
            if k == cat:
                v.append(id)
                return
            elif not v:
                continue
            else:
                self.addFileToTreeCat(v, cat)

    def loadTree(self):
        try:
            with open("tree.pkl", 'rb') as f:
                # print("Loading pickle")
                self.tree = pickle.load(f)
                #(names)
        except:
            with open("tree.pkl", 'wb') as f:
                self.tree = OntologyTree.tree
                pickle.dump(self.tree, f)