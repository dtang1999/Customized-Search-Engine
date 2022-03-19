from collections import defaultdict
import json
import math
import re
from unittest import result
from bs4 import BeautifulSoup
# import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import numpy as np

corpus_size = 37497
stop_words = set(stopwords.words('english'))

def get_tfidf(key_value_tuple):
    return key_value_tuple[1]["tf-idf"]

class Improved_query:
    
    def __init__(self) -> None:
        self.inverted_dict = {}
        self.json_data = json.load(open("webpages/WEBPAGES_RAW/bookkeeping.json"))
        self.loadFileToDict()
        self.load_doc_length()

    def loadFileToDict(self):
        """Load stored inverted_dict.txt into dictionary in python"""
        with open("inverted_dict.txt", 'r') as file:
            self.inverted_dict = json.loads(file.read())
            self.N = len(self.inverted_dict)

    def load_doc_length(self):
        """Load stored doc_length.txt into dictionary in python"""
        with open('doc_length.txt', 'r', encoding='utf-8') as file:
            self.doc_length = json.loads(file.read())

    def handle_input(self, input_str):
        """Removed the stop words in the input and split the input into a list"""
        return [word for word in word_tokenize(input_str) if word not in stop_words]


    def normalize(self, matrix):
        """Normalize the query matrix for cosine comparison"""
        length = 0
        length = math.sqrt(sum([i**2 for i in matrix.values()]))
        for k in matrix:
            matrix[k] /= length
        return matrix


    def query_matrix(self, terms):
        """Retrieved the idf weight stored in the created index"""
        res = {}
        for t in terms:
            if t  not in res:
                res[t] = 1
            else:
                res[t] += 1
        # print(res)
        for term, v in res.items():
            # df = len(self.inverted_dict[term]["Doc_info"])
            # idf = math.log10(corpus_size/df)
            idf = self.inverted_dict[term]["idf"]
            res[term] *= idf
        
        return res


    def doc_matrix(self, doc_id, terms):
        """Normalize the a single document(doc) matrix for cosine comparison"""
        res = {}
        for term in terms:
            if doc_id in self.inverted_dict[term]["Doc_info"]:
                tf = self.inverted_dict[term]["Doc_info"][doc_id]["tf"]
                res[term] = tf/self.doc_length[doc_id]
        # print(res)
        return res


    # def parse_html(self, text, doc_id):
    #     res = {}
    #     stop_words = set(stopwords.words('english'))
    #     for token in set(re.findall(re.compile(r"[A-Za-z0-9]+"), text)):
    #         if (token in stop_words):
    #             continue
    #         token = token.lower()
    #         res[token] = self.inverted_dict[token]["Doc_info"][doc_id]["tf"]
    #     return res


    def cosine_simi(self, terms):
        """
        Performing cosine similarity comparison between
        the query and each of the query relevent file.
        Return a dictionary with doc_id and its corresponding
        cosince similarity score.
        """
        res = defaultdict(int)
        score = 0
        q_matrix = self.normalize(self.query_matrix(terms))
        # d_matrix = self.normalize(self.doc_matrix())

        docs = set()
        for term in terms:
            for doc in self.inverted_dict[term]['Doc_info']:
                docs.add(doc)

        for doc_id in docs:
            # d_matrix = self.normalize(self.doc_matrix(doc_id))
            d_matrix = self.doc_matrix(doc_id, terms)

            for k, v in q_matrix.items():
                if k in d_matrix:
                    res[doc_id] += v * d_matrix[k]
        # print(d_matrix)
        # print(q_matrix)
        # print(res)
        return res


    def topK_result(self, k, ranking):
        """
        Returned the top K result with the cosine 
        ranking sorted from highest to lowest
        """
        result_list = []
        score_list = []
        for doc_id,score in sorted(ranking.items(), key=lambda x:x[1], reverse=True):
            if k == 0:
                break
            result_list.append(self.json_data[doc_id])
            score_list.append((self.json_data[doc_id], score))
            k -= 1
        return result_list, score_list


    def start_query(self, search_str):
        """Initiated the query process"""
        res = self.cosine_simi(self.handle_input(search_str))
        web_list, scores = self.topK_result(10, res)
        return web_list, scores




    # def start_query(self, input):
    #     url_dict = {} #stores data of end urls                
    #     urls_tf_idf_total = {}#used to keep track of tf.idf for the queries
    #     result_list = [] #used to store the results
    #     json_data = json.load(open("webpages/WEBPAGES_RAW/bookkeeping.json"))
    #     split_query = input.split()
    #     counter = 0

    #     for query in split_query:
    #         try:
    #             docs_dict = self.inverted_dict[query]["Doc_info"]
    #             result_count = 0
    #             for doc_id, attr in sorted(docs_dict.items(), key=get_tfidf, reverse=True):
    #                 if(json_data[doc_id] in urls_tf_idf_total):
    #                     urls_tf_idf_total[json_data[doc_id]][0] += 1
    #                     urls_tf_idf_total[json_data[doc_id]][1] += docs_dict[doc_id]["tf-idf"]
    #                 else:
    #                     urls_tf_idf_total[json_data[doc_id]] = [1,docs_dict[doc_id]["tf-idf"]]
    #                 result_count += 1
    #                 if (result_count == 10):
    #                     break

    #             print(urls_tf_idf_total)
    #         except:
    #             pass
        
        
    #     counter = len(split_query)
    #     while(1):
    #             if(len(url_dict) >= 10 or counter == 0): 
    #                     break
    #             for url,tf_idf in list(urls_tf_idf_total.items()):#list part necessary in python3
    #                 if( tf_idf[0] == counter): #iterates through ALL the words matching. Stopping prematurely
    #                         #will result in queries being missed before moving to the next best match.
    #                     url_dict[url] = tf_idf
    #             counter -= 1 #used to keep track of how many queries are matching.
    #             #higher priority towards queries with more words matching
    #     #return urls sorted by tf_idf
    #     sorted_values = sorted(url_dict.items(),  key=lambda x: (x[1][0],x[1][1]), reverse = True)
    #     #return 10 top urls from sorted_values
    #     tf_idf_score = []
    #     for url,tf_idf in sorted_values:
    #             if(len(result_list) < 10):
    #                     # result_list.append((url,tf_idf))
    #                     result_list.append(url)
    #                     tf_idf_score.append((url,tf_idf))
    #             else:
    #                     break
    #     # return result_list
    #     return result_list, tf_idf_score


if __name__ == "__main__":
    query = Improved_query()

    terms = query.handle_input("computer science")
    # qm = query.query_matrix(terms)
    # print(query.normalize(qm))
    # print(terms)
    res = query.cosine_simi(terms)
    doc, score = query.topK_result(10, res)
    print(doc)
    print(score)
    # print(query.doc_matrix("44/424"))
