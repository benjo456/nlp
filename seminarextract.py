import nltk
from os import listdir
from os.path import isfile, join
import Emails, Tagger, os, Evaluator, OntologyTagger

from nltk.tag import StanfordNERTagger
#global email
'''
This program takes in a file, processes it and tags it, and then returns the extracted information to file
'''
'''
#This ideally needs to be done in a different file
def readIn(mypath, corpus_root):
    #Read in files
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    corpus = nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpus_root, onlyfiles)
    #Create email object, with header and body
    preProcess(corpus)
'''

dir = 'C:/Users/Ben/Documents/NLP/nltk_data/stanford-ner-2018-10-16'
model = dir + '/classifiers/english.all.3class.distsim.crf.ser.gz'
jar = dir + '/stanford-ner.jar'
st = StanfordNERTagger(model, jar, encoding='utf-8')

def splitCorpus(content,id):
    #Split file into header and body
        splitWord = "Abstract"
        abstractLocation = content.index(splitWord)
        endAbstract = abstractLocation + len(splitWord)
        header = content[0:endAbstract].replace("\t",'')
        body = content[endAbstract+1::].replace("\t",'')
        email = Emails.Email(body, header,id)
        return email


def tagTheEmail(email):
    tagger = Tagger.Tagger(email,st)
    tagger.tagTimes(email)
    tagger.tagSpeaker()
    tagger.tagSent()
    tagger.tagLocation()
    tagger.tagPara()
    email.combineTogether()

def tagTopics():
    #tag topics, will come in helpful later
    pass

def writeNewFile(filename,email):
    filename = os.path.splitext(filename)[0]
    newEmail = email.newHeader + email.newBody
    file = open(filename + "tagged.txt", 'w')
    file.write(newEmail)
    file.close()

def loadInFile(filename,id):
    file = open(filename, 'r')
    wholeEmail = file.read()
    email = splitCorpus(wholeEmail,id)
    tagTheEmail(email)
    writeNewFile(filename,email)
    return email

def evaluateMeasure(filename,e,id):
    file = e.getFileToTag(filename)
    email = loadInFile(file,id)
    #e.getFromTagged("C:/Users/Ben/Documents/NLP/nltk_data/seminars_training/training/34.txt")
    e.evaluate(email)
    return e

#loadInFile("C:/Users/Ben/Documents/NLP/nltk_data/Test/333.txt")
#evaluateMeasure("C:\\Users\\Ben\\Documents\\NLP\\nltk_data\\seminars_training\\training\\3.txt")

def evaluate():
    ev = Evaluator.Evaluator()
    for i in range(0,300):
        print("File " + str(i))
        e = evaluateMeasure("C:\\Users\\Ben\\Documents\\NLP\\nltk_data\\seminars_training\\training\\{}.txt".format(i),ev,i)
    e.evalResults()

def runOnto():
    id = 100
    filename = "C:\\Users\\Ben\\Documents\\NLP\\nltk_data\\seminars_training\\training\\{}.txt".format(id)
    ev = Evaluator.Evaluator()
    file = ev.getFileToTag(filename)
    email = loadInFile(file,id)
    ont = OntologyTagger.OntologyTagger(email)
    ont.keyWordsInTopic()


#evaluate()
runOnto()