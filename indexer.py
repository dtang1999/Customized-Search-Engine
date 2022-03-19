from collections import defaultdict
import json
import math
import re

import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))


class Indexer:
    def __init__(self, corpus) -> None:
        self.corpus_dir = corpus
        self.total_docs = 0
        self.inverted_index = defaultdict(dict)
        self.doc_length = {}


    def storeToFile(self):
        """
        Store the index to the .txt files for searching
        """
        # Visualize the stored self.inverted_index
        with open('inverted_index.txt', 'w', encoding='utf-8') as file:
            for k, v in self.inverted_index.items():
                file.write(str(k) + ":\t" + str(v)+"\n")

        # Stored index dictionary self.inverted_index into inverted_dict.txt for future searching
        with open('inverted_dict.txt', 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.inverted_index))

        # Stored each document's length for computing cosince similarity
        with open('doc_length.txt', 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.doc_length))


    def store_doc(self):
        """
        Stored each document's length for computing cosine similarity
        """
        with open('doc_length.txt', 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.doc_length))

    
    def loadFileToDict(self):
        """
        Load index dictionary from inverted_dict.txt to the 
        variable self.inverted_index
        """
        with open("inverted_dict.txt", 'r') as file:
            self.inverted_index = json.loads(file.read())
    

    def count_doc_length(self):
        """
        Compute the document (doc) length for computing cosine similarity
        score in run time
        """
        corpus_data = json.load(open(self.corpus_dir))
        for doc_id, url in corpus_data.items():
            # if self.total_docs >= 1000:
            #     break
            html = doc_id.split('/')
            file_name = "{}/{}/{}".format("webpages/WEBPAGES_RAW",
                                          html[0], html[1])
            html_file = open(file_name, 'r', encoding='utf-8')
            theSoup = BeautifulSoup(html_file, 'lxml')
            
            tokens_dict = {}
            tokens_dict = self.parse_html(theSoup.get_text(), tokens_dict)

            self.doc_length[doc_id] = math.sqrt(sum([(1+math.log10(i))**2 for i in tokens_dict.values()]))

            self.total_docs += 1
        print(self.total_docs)
        self.store_doc()


    def update_tfidf(self):
        """
        Update the inverse document frequency (idf) for every
        words in the corpus
        """
        for token, docs in self.inverted_index.items():
            # for doc_info in token["Doc_info"].values():
            #     N = len(token["Doc_info"])
            #     doc_info["idf"] = math.log10(self.total_docs / N)
            #     doc_info["tf-idf"] = 1+math.log10(doc_info["tf"]) * doc_info["idf"]
            df = len(docs["Doc_info"].values())
            idf = math.log10(self.total_docs / df)
            self.inverted_index[token]["idf"] = idf


    def parse_html(self, text, tokens_dict):
        """
        Read the html page as string and tokenize each 
        entry in the text string. Return a dictionary
        with token as key and frequency of the token as value
        """
        tokens_dict = defaultdict(int)
        for token in re.findall(re.compile(r"[A-Za-z0-9]+"), text):
            if (token in stop_words):
                continue
            tokens_dict[token.lower()] += 1
        return tokens_dict


    def build_index(self):
        """
        Initiated the index building process
        """
        corpus_data = json.load(open(self.corpus_dir))
        for doc_id, url in corpus_data.items():
            # if self.total_docs >= 1000:
            #     break
            html = doc_id.split('/')
            file_name = "{}/{}/{}".format("webpages/WEBPAGES_RAW",
                                          html[0], html[1])
            html_file = open(file_name, 'r', encoding='utf-8')
            theSoup = BeautifulSoup(html_file, 'lxml')

            tokens_dict = {}
            tokens_dict = self.parse_html(theSoup.get_text(), tokens_dict)
            self.doc_length[doc_id] = math.sqrt(sum([(1+math.log10(i))**2 for i in tokens_dict.values()]))
            self.total_docs += 1

            for token, freq in tokens_dict.items():
                if (token not in self.inverted_index):
                    # self.inverted_index[token] = {"_id": token, "Doc_info": defaultdict(dict)}
                    self.inverted_index[token] = {"Doc_info": defaultdict(dict)}
                self.inverted_index[token]["Doc_info"][doc_id]["tf"] = freq
        self.update_tfidf()
        self.storeToFile()
        # self.analysis()


    def analysis(self):
        """
        Helper function for M1 to record unique doc ids and unique words
        """
        docIdSet = set()
        for k, v in self.inverted_index.items():
            for ele in v["Doc_info"]:
                docIdSet.add(ele)
        print("unique docIds: ", len(docIdSet))
        print("unique words: ", len(self.inverted_index))


if __name__ == "__main__":
    index = Indexer("webpages/WEBPAGES_RAW/bookkeeping.json")
    index.build_index()
    # index.count_doc_length()

    # index.update_tfidf()
