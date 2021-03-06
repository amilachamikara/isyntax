from operator import itemgetter
import xml.etree.ElementTree as ET
import nltk
from nltk.corpus import wordnet
from nltk.metrics import *
from wordquery.preprocessor import *

__author__ = 'ChaminiKD'

rootPath = 'wordquery/out/'

# xml_file = 'company_new.xml'
expression_list = [("equals", "="), ("greater than", ">"), ("less than", "<"), ("greater than or equal", ">="),
                   ("less than or equal", "<="),
                   ("notequal", "<>"), ("greaterthan", ">"), ("lessthan", "<"), ("greater than or equal to", ">="),
                   ("less than or equal to", "<="), ("like", "like"), ("equal", "="), ("order by", "order by"),
                   ("equal to", "=")]

operator_list = ["AND", "OR", "and", "or"]


def identify_expressions(remaining_sentence):
    temp = []
    symbol = []
    indx = 0

    for word in remaining_sentence:
        for elm in expression_list:
            if elm[0] == word:
                temp.append([word, indx, elm[1]])
                symbol.append([elm[1], indx])
        indx = indx + 1

    return temp, symbol


# identify the condition attribute in the user input
def get_codition_attribute(i, tokens_of_remaining):
    exp_index = i[1]
    previous_token = []
    previous_token.append([tokens_of_remaining[exp_index - 1], i[0]])
    return previous_token


def find_operators(token):
    ilist = []
    index = 0
    while index < len(token):
        index = token.find("'", index)
        if index == -1:
            break
        ilist.append(index)
        index += 1

    len_ilist = len(ilist)
    substring = token[ilist[0]:ilist[len_ilist - 1]]

    tokens_of_substring = getTokenz(substring)
    result = [word for word in tokens_of_substring if word.lower() in operator_list]
    return result


def find_condition_elements(tokens_of_remaining, att, noun_list, userInput, xml_file):
    identified_expression, symbol = identify_expressions(tokens_of_remaining)
    print("identified expression in the user input =", identified_expression)
    print("identified symbols in the user input =", symbol)
    condition_att_list = []
    privious_token_list = []
    for i in identified_expression:
        # prv_token = []
        prv_token = get_codition_attribute(i, tokens_of_remaining)
        print("previous token =", prv_token)
        privious_token_list.append(prv_token[0][0])
        # prv_attribute = []
        prv_attribute = attributeIdentifier(att, prv_token[0], xml_file)
        print("previous attribute = ", prv_attribute)
        condition_att_list.append([prv_attribute[0], i[2]])
    print("condition attribute list", condition_att_list)

    # remove condition attribute from noun list
    list_of_nouns = [word for word in noun_list if word.lower() not in privious_token_list]
    print("after removing the condition attributes **", list_of_nouns)

    operator = find_operators(userInput)  # find AND , OR operetors
    print("operators found :", operator)

    print("..........................................................")
    return symbol, prv_attribute, list_of_nouns, operator, condition_att_list


def getContentFromFile(filename):
    with open(filename) as f:
        content = f.readlines()
    return str(''.join(content)).replace('\n', ' ')


def extract_np(psent):
    for subtree in psent.subtrees():
        if subtree.label() == 'NP':
            yield ' '.join(word for word, tag in subtree.leaves())


def chunk_nouns(tags):
    # grammar = "NP: {(<JJ.*>|<RB.*>|<NN.*>)*<NN.*>}"
    # grammar = "NP: {<NNS>*<NN>*}"
    # cp = nltk.RegexpParser(grammar)
    # result = cp.parse(tags)
    # extract_gen = extract_np(result)
    # return [x for x in extract_gen]

    tlist = []
    for t in tags:
        if t[1] == 'NN' or t[1] == 'NNS':
            tlist.append(t[0])
    return tlist


# fetch table names from xml file
def get_Table_names(xml_file):
    tree = ET.parse(xml_file)
    tables = [el.attrib.get('tbname') for el in tree.findall('.//table')]
    return tables


# fetch attribute names from xml file
def get_attribute_names(xmlfile):
    tree = ET.parse(xmlfile)
    attributes = [el.attrib.get('attname') for el in tree.findall('.//attribute')]
    return attributes


# calculate edit distance
def extract_tables(nouns, xml_file):
    table_file = open(rootPath + 'table_editDistance.txt', 'w')
    table_list = get_Table_names(xml_file)
    list1 = []
    for n in nouns:
        count = []
        temp = []
        for y in table_list:
            dist = edit_distance(n.lower(), y.lower())
            count.append([n, y, dist])

        temp = sorted(count, key=itemgetter(2))
        list1.append(temp)
        table_file.write(str(temp))
        table_file.write("\n")
    return list1


# calculate edit distance
def extract_attributes(nouns, xml_file):
    att_file = open(rootPath + 'attribute_editDistance.txt', 'w')
    attribute_list = get_attribute_names(xml_file)
    list2 = []
    for n in nouns:
        count = []
        temp = []
        for y in attribute_list:
            dist = edit_distance(n.lower(), y.lower())
            count.append([n, y, dist])

        temp = sorted(count, key=itemgetter(2))
        list2.append(temp)
        att_file.write(str(temp))
        att_file.write("\n")
    return list2


# check with edit distance threshold
def find_tables(noun_list, xml_file):
    list = extract_tables(noun_list, xml_file)
    tabList = []
    n_list = []
    for a in list:
        for l in a:
            if l[2] <= 3:
                tabList.append(l[1])
                n_list.append(l[0])
    return set(tabList), n_list


# check with edit distance threshold
def find_attributes(noun_list, xml_file):
    list = extract_attributes(noun_list, xml_file)
    attList = []
    for a in list:
        for l in a:
            if l[2] <= 3:
                attList.append(l[1])
    return set(attList)


table_synset_file = open(rootPath+ 'table_synset.txt', 'w')


def tableIdentifier(knowledgeBase, nounList, xml_file):
    # print("mmmmmmmmm")
    try:
        list = []
        temp = []
        n_list = []
        for n in nounList:
            syn = wordnet.synsets(n, pos='n')
            for a in knowledgeBase:
                for x in a[1]:
                    sim = x.wup_similarity(syn[0])
                    table_synset_file.write(str([n, syn[0], ':', x, '=', sim]))
                    table_synset_file.write("\n")
                    # temp.append([n, syn[0], ":", x, "=", sim])
                    if sim >= 0.75:
                        # print("table found:", a[0])
                        list.append(a[0])
                        n_list.append(n)
                        return list, n_list
                    else:
                         # print("lllllll")
                         tab, n_list = find_tables(nounList, xml_file)
                         return tab, n_list

    except:
        # print("hhhhhhhhhhhhhhh")
        tab, n_list = find_tables(nounList, xml_file)
        return tab, n_list


att_synset_file = open(rootPath + 'attribute_synset.txt', 'w')


def attributeIdentifier(knowledgeBase, nounList, xml_file):
    list2 = []
    new_list = []
    for n in nounList:
        try:
            syn = wordnet.synsets(n, pos='n')
            for a in knowledgeBase:
                for x in a[1]:
                    sim = x.wup_similarity(syn[0])
                    att_synset_file.write(str([n, syn[0], ':', x, '=', sim]))
                    att_synset_file.write("\n")

                    if sim >= 0.75:
                        list2.append(a[0])
        except:
            new_list = []
            new_list.append(n)
            att = find_attributes(new_list, xml_file)
            list2.extend(att)

    return list2
