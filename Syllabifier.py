#!/usr/bin/python
# -*- coding: utf-8 -*-
# =============================================================================
#  Version: 1.0 (Decembre 15, 2015)
#  Author: Wassim Swaileh (wassim.swaileh2@univ-rouen.fr), Normandie University
#  LITIS lab EA 4108, Campus du Madrillet, 76800 Saint-Étienne-du-Rouvray
#
#  Contributors:
#        Julien Lerouge (Julien.Lerouge@litislab.fr)
# =============================================================================
#
#  Syllabifier is distributed in the hope that it will be useful, 
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

import os, glob, math
import sys
import getopt
import time
import codecs
import collections
import mmap
import optparse
import operator
import random
import threading
from threading import Thread
import time

reload(sys)
sys.setdefaultencoding('utf-8')

Words_List=[]
Syllabes_List=[]
Charc_List=[]
Label_List=[]
DictSyllabique=[]
Dict=[]

Corpus_codage_caracters=[]
Corpus_codage_mots=[]
Corpus_text=[]
Corpus_codage_Syllabes=[]
Corpus_Syllabes=[]

symbolsList=[":", "%", "_", "2", "5", "6", "7", "¤", "(", "=", "0", "8", "+", "€", "3", ";", ".", "!", ")", "}", "²", "1", "9", ",", "4", "{", "/", "°", '"', "?", "*", "-", "'", "#", "&"]
vowels=["a", "e", "i", "o", "u", "y"]
   
def findIndex(ltr, elmLst):
    indx=-1
    for i in range(len(elmLst)):
        if ltr == elmLst[i].decode('utf-8'):
            indx=i
    return indx 

def extractDatasetSymbols(str4, Charc_List, Label_List):
    txt = ""
    Cline = ""
    Cline = "<s> "
    
    for dx in range(len(str4)):
        ltr=str4[dx]
        if len(Charc_List) == len(Label_List):
            indx=findIndex(ltr, Charc_List)            
            if indx != -1:
                Cline = Cline+Label_List[indx]+" "
    Cline = Cline+"</s>"
    txt = str4
    if txt == "":
        print str4
    return (Cline, txt)
    
def separMotsSyllabique(motsy):
    Mots_liste=[]
    stockage=""
    for m in motsy:
        if m in symbolsList:
            if stockage != "":
                Mots_liste.append(stockage)
            stockage=""
            Mots_liste.append(m)
        else:
            stockage=stockage+m
    if motsy[-1] not in symbolsList:
            Mots_liste.append(stockage)
    return Mots_liste

def isWord(wrd):
    ndx=-1
    for w in wrd:
        ndx = findIndex(w, symbolsList)
        if ndx != -1:
            ndx = findIndex(w, symbolsList)
            break
    return ndx

def singleWordCoding(str4, Charc_List, Label_List):
    wrd=""
    hmm=""
    for dx in range(len(str4)):
        indx=findIndex(str4[dx], Charc_List)            
        if indx != -1:
            wrd = wrd+Label_List[indx]
            hmm = hmm+Label_List[indx]+" "
    Dict=wrd+" "+hmm    
    return (wrd, Dict)

def wordsLineCoding(str4, Charc_List, Label_List, output_path, Dict):
    WLine="<s> s6 "
    mots=str4.split()
    for m in mots:
        if isWord(m)==-1: 
            (W, D) = singleWordCoding(m, Charc_List, Label_List)
            WLine = WLine+W+" s6 "
            Dict.append(D)
        else:
            mot = separMotsSyllabique(m)
            for x in mot:
                (W, D) = singleWordCoding(x, Charc_List, Label_List)
                WLine = WLine+W+" "
                Dict.append(D)
            WLine = WLine+"s6 "
    WLine = WLine+"</s>"
    return WLine

#'''********************* la syllabification ***************'''
def trouverListEnLexique(mots, Words_List, Syllabes_List):
    sortie = ""
    for m in mots:
        if m in symbolsList:
            sortie = sortie+m+" "
        elif m in Words_List:
            dx=Words_List.index(m)
            Rec=m+'\t'+Syllabes_List[dx]
            if Syllabes_List[dx] != "":
                sortie = sortie+Syllabes_List[dx]+" "
            else:
                mot = generateurSyllabique(m, Words_List, Syllabes_List)
                sortie = sortie+mot+" "    
        else:
            mot = generateurSyllabique(m, Words_List, Syllabes_List)
            sortie = sortie+mot+" "    
    return sortie

def trouverMotEnLexique(w, Words_List, Syllabes_List):
    sortie = ""
    if w in Words_List:
        dx=Words_List.index(w)
        Rec=w+'\t'+Syllabes_List[dx]
        if Syllabes_List[dx] != "":
            sortie = Syllabes_List[dx]+" "
        else:
            mot = generateurSyllabique(w, Words_List, Syllabes_List)
            sortie = mot
    else:
        mot = generateurSyllabique(w, Words_List, Syllabes_List)
        sortie = mot    
    return sortie

def majVerfication(mot):
    x = False
    for m in mot:
        if m.isupper():
            x = True
            return x
    return x

def generateurSyllabique(mot, Words_List, Syllabes_List):
    output = []
    prev = 0
    i=0
    outSyl = ""
    M=mot
    if mot in symbolsList:
        return mot
    if len(mot) <= 2:
        return mot
    if majVerfication(mot) == True:
        
        mot=mot.lower()
        if mot in Words_List: 
            dx = Words_List.index(mot)
            sy = Syllabes_List[dx]
            l = dict(zip(set(sy), map(lambda y: [i for i, z in enumerate(sy) if z is y ], set(sy))))
            if " " in l:
                indexes = l[" "]
                for index in indexes:
                    index = index-i
                    output.append(M[prev:index])
                    outSyl = outSyl +" "+ M[prev:index]
                    prev = index
                    i=i+1
                i=i-1
                output.append(M[indexes[-1]-i:])
                outSyl = outSyl +" "+ M[indexes[-1]-i:]
                outSyl = outSyl.strip()
            else: 
                outSyl = M
        else:
            mwrd = mesureDesSimilarites(M, Words_List, Syllabes_List)
            if mwrd != M:
                return mwrd
            else:
                return mwrd
    else:
        mwrd = mesureDesSimilarites(M, Words_List, Syllabes_List)
        if mwrd != M:
            return mwrd
        else:
            return mwrd
    return outSyl

def phonesStructs(wrd, vowels):
    phone = ""
    for w in wrd:
        if w in vowels:
            phone = phone + w
        else:
            phone = phone + "C"
    return phone

def jaccard_similarity(a, b, vowels):
    ph1 = phonesStructs(a, vowels)
    ph2 = phonesStructs(b, vowels)

    intersection1 = map(operator.eq, a, b).count(True)
    intersection2 = map(operator.eq, ph1, ph2).count(True)
    if len(a) > len(b):
        union = len(a)
    else:
        union = len(b)
    v = float(intersection1 + intersection2)
    w = float(2 *union)  
    r = float(v)/float(w)
    return r



class Destination:
    def run(self,  mot, chunkWRD, chunkSYL, wrds_scores_dict, vowels):
        self.Mn = mot.lower()
        self.vwl= vowels
        self.scr_lst = []
        self.wrd_lst = chunkWRD
        self.syl_lst = chunkSYL
        self.s = 0
        self.Max_score = 0
        for m in self.wrd_lst:
            self.Mx = m.lower()
            self.s = jaccard_similarity(self.Mn, self.Mx, self.vwl) 
            self.scr_lst.append(self.s)
            if self.Max_score < self.s:
                self.Max_score = self.s
        dx_score = self.scr_lst.index(self.Max_score)
        candidat = self.wrd_lst[dx_score]
        candidatSyl = self.syl_lst[dx_score]
        while candidatSyl == "":
            self.scr_lst[dx_score]=0
            self.Max_score = max(self.scr_lst)
            dx_score = self.scr_lst.index(self.Max_score)
            candidat = self.wrd_lst[dx_score]
            candidatSyl = self.syl_lst[dx_score]
        wrds_scores_dict[candidat] = self.Max_score


def threading_search(mot, Words_List, Syllabes_List, n_threads=8):
    threadList = [] # theards list
    list_scores=[]
    wrds_scores_dict={}
    Max_score = 0
    candidat = ""
    candidatSy = ""
    for i in range(0, len(Words_List), int(len(Words_List)/n_threads)):
        chunkWRD = Words_List[i:i + int(len(Words_List)/n_threads)]
        chunkSYL = Syllabes_List[i:i + int(len(Words_List)/n_threads)]
        destination = Destination()
        thread = threading.Thread(target=destination.run, args=(mot, chunkWRD, chunkSYL, wrds_scores_dict, vowels))
        threadList.append(thread)
    for thread in threadList:
        thread.start()
    for thread in threadList:
        thread.join()
    maxx = max(wrds_scores_dict.values())
    Max_wrd = max(wrds_scores_dict, key=wrds_scores_dict.get)
    return Max_wrd, maxx

def mesureDesSimilarites(mot, Words_List, Syllabes_List, threshold=0.6):
    output = []
    prev = 0
    Max_score = 0
    s = 0
    i=0
    outSyl = ""
    (candidat, Max_score) = threading_search(mot, Words_List, Syllabes_List)
    wrd_indx = Words_List.index(candidat)
    candidatSy = Syllabes_List[wrd_indx]
    if Max_score >= threshold:
        l = dict(zip(set(candidatSy), map(lambda y: [i for i, z in enumerate(candidatSy) if z is y ], set(candidatSy))))
        if " " in l:
            indexes = l[" "]
            for index in indexes:
                index = index-i
                output.append(mot[prev:index])
                outSyl = outSyl +" "+ mot[prev:index]
                prev = index
                i=i+1
            i=i-1
            output.append(mot[indexes[-1]-i:])
            outSyl = outSyl +" "+ mot[indexes[-1]-i:]
            outSyl = outSyl.strip()
        else: 
            outSyl = mot
        return outSyl
    else:
        mot = wordSlicing(mot)
        return mot

def wordSlicing(word):
    output=""
    for w in word:
        output = output+w+" "
    return output

def codageSyllabique(str4, Charc_List, Label_List, output_path, Words_List, Syllabes_List, DictSyllabique):
    wrd = "<s> s6 "
    txt = ""
    mots=str4.split()
    for m in mots:
        if isWord(m)==-1:
            T = trouverMotEnLexique(m, Words_List, Syllabes_List)
            T = T.strip()
            txt = txt+T+" "
            T = T.split()
            for sw in T:
                (W, D) = singleWordCoding(sw, Charc_List, Label_List)
                wrd = wrd+W+" "
                DictSyllabique.append(D)
                
            wrd = wrd+"s6 "
        else:
            mots = separMotsSyllabique(m)
            for w in mots:
                T = trouverMotEnLexique(w, Words_List, Syllabes_List)
                T = T.strip()
                txt = txt+T+" "
                T = T.split()
                for sw in T:
                    (W, D) = singleWordCoding(sw, Charc_List, Label_List)
                    wrd = wrd+W+" "
                    DictSyllabique.append(D)
            wrd=wrd+"s6 "
    wrd=wrd+"</s>"
    return (wrd, txt)

def writeToFile(filename, string):
    with open(filename, 'w') as f:
        f.write("\n".join(map(str, string)))            

def main():
    DictSyllabique=[]
    Dict=[]
    path = sys.argv[1]

    with open("data/chars.txt") as f1:
        Charc_List = f1.read().splitlines()
    with open("data/labels.txt") as f2:
        Label_List = f2.read().splitlines()
    if len(Charc_List) != len(Label_List):
        raise Exception("Chars and Labels must have the same size.");
    
    with codecs.open("data/words.txt", 'r', encoding='utf8') as f1:
        Words_List = f1.read().splitlines()
    with codecs.open("data/syllabs.txt", 'r', encoding='utf8') as f2:
        Syllabes_List = f2.read().splitlines()
    if len(Words_List) != len(Syllabes_List):
        raise Exception("Words and Syllabs must have the same size.");

    str1=path
    str2=str1.find(".txt");
    strw=str1[0:str2]
    output_path = strw+"/"
    os.system("mkdir "+output_path)

    IN_FILE_txt = codecs.open(path, 'r', encoding='utf-8') 
    for line in IN_FILE_txt:
        str4=" "+line.rstrip()+" "
        (Carc, txt1) = extractDatasetSymbols(str4, Charc_List, Label_List)        
        Word = wordsLineCoding(str4, Charc_List, Label_List, output_path, Dict)
        (Syll, txt3) = codageSyllabique(str4, Charc_List, Label_List, output_path, Words_List, Syllabes_List, DictSyllabique)
        Corpus_codage_caracters.append(Carc)
        Corpus_codage_mots.append(Word)
        Corpus_text.append(txt1)
        Corpus_codage_Syllabes.append(Syll)
        Corpus_Syllabes.append(txt3)

    writeToFile(output_path+"Corpus_codage_caracters.txt", Corpus_codage_caracters)
    writeToFile(output_path+"Corpus_codage_mots.txt", Corpus_codage_mots)
    writeToFile(output_path+"Corpus_text.txt", Corpus_text)
    writeToFile(output_path+"Corpus_codage_Syllabes.txt", Corpus_codage_Syllabes)
    writeToFile(output_path+"Corpus_Syllabes.txt", Corpus_Syllabes)
    
    DictSyllabique = list(set(DictSyllabique))
    writeToFile(output_path+"Words_Dict.txt", Dict)
    Dict = list(set(Dict))
    writeToFile(output_path+"Dictionair_des_syllabes.txt", DictSyllabique)

if __name__ == "__main__":
    main()
