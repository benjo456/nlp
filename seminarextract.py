import nltk
from os import listdir
from os.path import isfile, join
import Emails, Tagger, os, Evaluator, OntologyTagger, pprint, OntologyTree
from gensim.models import KeyedVectors

from nltk.tag import StanfordNERTagger
'''
This program takes in a file, processes it and tags it, and then returns the extracted information to file
'''

dir = 'C:/Users/Ben/Documents/NLP/nltk_data/stanford-ner-2018-10-16'
dataDir = 'C:\\Users\\Ben\\PycharmProjects\\nlp\\nltk_data'
model = dir + '/classifiers/english.all.3class.distsim.crf.ser.gz'
jar = dir + '/stanford-ner.jar'
st = None

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
    tagger = Tagger.Tagger(email,st,dataDir)
    tagger.tagTimes(email)
    tagger.tagSpeaker()
    tagger.tagSent()
    tagger.tagLocation()
    tagger.tagPara()
    email.combineTogether()

def writeNewFile(filename,email):
    filename = os.path.splitext(filename)[0]
    folder = os.path.dirname(os.path.dirname(filename)) +"\\results\\"
    if not os.path.exists(folder):
        os.makedirs(folder)
    newEmail = email.newHeader + email.newBody
    file = open(folder + str(email.fileID) + ".txt", 'w')
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
    e.evaluate(email)
    return e

def evaluate():
    st = StanfordNERTagger(model, jar, encoding='utf-8')
    ev = Evaluator.Evaluator()
    for i in range(1,301):
        print("File " + str(i))
        e = evaluateMeasure(dataDir + "\\seminars_training\\training\\{}.txt".format(i),ev,i)
    e.evalResults()

def runOnto():
    print("Loading model, please wait. (This may take a while)")
    model = KeyedVectors.load_word2vec_format(
        dataDir + "\\GoogleNews-vectors-negative300.bin",
        binary=True)
    print("Model loaded")
    for i in range(0, 485):
        id = i
        print(id)
        filename = dataDir + "\\seminars_training\\training\\{}.txt".format(id)
        ev = Evaluator.Evaluator()
        file = ev.getFileToTag(filename)
        email = loadInFile(file,id)
        tree = OntologyTree.tree
        ont = OntologyTagger.OntologyTagger(email,model,tree,dataDir)
        tree = ont.findOntTreeMatch(ont.keyWordsInTopic())
    ont.printTree(tree)


evaluate()

#runOnto()
