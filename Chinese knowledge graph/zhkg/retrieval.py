import spacy_stanza
import pandas as pd

nlp = spacy_stanza.load_pipeline("xx", lang='zh-hant')

def find_all(a_str:str, sub:str):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def search_all_idx(a_str:str, sub:str):
    idx = list(find_all(a_str, sub))

    return idx

def remove_part(text:str) -> str:
    split_list = text.split("的")

    return split_list[-1]


class info_retrieval:
    def __init__(self):
        self.left_punct = ['《', "（", "「"]
        self.right_punct = ["》", "）", "」"]

    def get_dict(self, sent:str):
        word_to_class_dict = dict()
        new_sent = sent

        i = 0

        prv_tok_dep = ""
        prv_tok_text = ""
        prv_tok_pos = ""

        noundeps = ["nummod", "mark:clf", "compound:nn", "amod", "nmod", "appos", "dobj", "nsubj"]

        prefix = ""

        for tok in nlp(sent):
            # Get prefix
            if tok.dep_ in noundeps and tok.pos_ != "VERB":
                if prv_tok_dep in noundeps and tok.pos_ != "VERB":
                    prefix = prefix + tok.text
                else:
                    prefix = tok.text
            
            # find all words between left punct and right punct
            if tok.text == self.left_punct[0]: 
                idx1 = search_all_idx(new_sent, self.left_punct[0])[0]
                idx2 = search_all_idx(new_sent, self.right_punct[0])[0]
                term = new_sent[idx1: idx2+1]

                if prv_tok_pos == "NOUN" or prv_tok_pos == "PROPN":                
                    word_to_class_dict[prefix] = term
                    prefix = ""
                    new_sent = new_sent[:idx1] + new_sent[idx2 + 1:]
                else:
                    value = "名詞" + str(i)
                    word_to_class_dict[value] = term 
                    i += 1
                    new_sent = new_sent[:idx1] + value + new_sent[idx2 + 1:]

            if tok.text == self.left_punct[1]:
                idx1 = search_all_idx(new_sent, self.left_punct[1])[0]
                idx2 = search_all_idx(new_sent, self.right_punct[1])[0]
                term = new_sent[idx1+1: idx2]

                if prv_tok_pos == "NOUN" or prv_tok_pos == "PROPN":                
                    word_to_class_dict[prefix] = term
                    prefix = ""
                    new_sent = new_sent[:idx1] + new_sent[idx2 + 1:]
                else:
                    value = "名詞" + str(i)
                    word_to_class_dict[value] = term
                    i += 1
                    new_sent = new_sent[:idx1] + value + new_sent[idx2 + 1:]

            if tok.text == self.left_punct[2]:
                if prv_tok_text != "：":
                    idx1 = search_all_idx(new_sent, self.left_punct[2])[0]
                    idx2 = search_all_idx(new_sent, self.right_punct[2])[0]
                    term = new_sent[idx1: idx2+1]

                    if prv_tok_pos == "NOUN" or prv_tok_pos == "PROPN":                
                        word_to_class_dict[prefix] = term
                        prefix = ""
                        new_sent = new_sent[:idx1] + new_sent[idx2 + 1:]
                    else:
                        value = "名詞" + str(i)
                        word_to_class_dict[value] = term 
                        i += 1
                        new_sent = new_sent[:idx1] + value + new_sent[idx2 + 1:]
                
                else:
                    pass
        
            if tok.dep_ not in noundeps:
                prefix = ""

            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text
            prv_tok_pos = tok.pos_
            
        return word_to_class_dict, new_sent
    
    def get_sent_list(self, text:str):
        sent_list = []
        paragraphs = text.split("\n")

        for i in paragraphs:
            if len(i) > 0:
                sent_dict, replaced_sent = self.get_dict(i)
                sent_list.append((sent_dict, replaced_sent))

        return sent_list
    
    def get_triplets(self, sent: str, sent_dict: dict):
        doc = nlp(sent)
        triplets = []  #list of subject-transitive verbs-object triplet
        internal_features = {}
        ent1 = "" 
        ent2 = ""
        ent3 = ""
        ent4 = ""
        rel1 = ""

        prv_tok_dep = ""
        prv_tok_text = ""
        prv_tok_pos = ""

        prefix = ""
        verbdeps = ["ccomp", "conj", "acl", "xcomp", "parataxis"]
        noundeps = ["nummod", "mark:clf", "compound", "amod", "nmod", "appos", "dep", "name", "clf", "case", "det", "conj", "acl:relcl", "mark:rel"]
        numbers = [str(i) for i in range(100)]

        for tok in doc:
            
            # Get prefix
            if tok.dep_ in noundeps and tok.pos_ != "VERB":
                if prv_tok_dep in noundeps and tok.pos_ != "VERB":
                    prefix = prefix + tok.text
                else:
                    prefix = tok.text
        
            # Get compound verbs or normal verbs
            if tok.pos_ == "VERB" and tok.dep_ != "amod" and tok.dep_ != "compound" and not ent4:
                if ent1:
                    if prv_tok_dep == "auxpass":
                        rel1 = prv_tok_text + tok.text
                    elif prv_tok_pos == "VERB" and prv_tok_dep in verbdeps:
                        rel1 = rel1 + tok.text
                    elif prv_tok_dep == "aux" and prv_tok_pos == "AUX":
                        rel1 = prv_tok_text + tok.text
                    else:
                        rel1 = tok.text
        
            # Get subject
            if tok.dep_ == "nsubj":
                if prv_tok_dep in noundeps and tok.pos_ != "VERB":
                    ent1 = prefix + tok.text
                elif prv_tok_dep == "nsubj":
                    ent1 = prefix + prv_tok_text + tok.text
                else:
                    ent1 = tok.text 
                prefix = ""
                prv_tok_dep = ""
                prv_tok_text = ""

            if tok.text in numbers and prv_tok_dep == "nsubj" and prv_tok_text in "名詞" and ent1:
                ent1 = "名詞" + tok.text
            
            if tok.dep_ == "flat:name" or tok.dep_ == "appos":
                if prv_tok_dep == "nsubj" and ent1:
                    ent1 = ent1 + tok.text
                elif prv_tok_dep == "flat:name" and ent1:
                    ent1 = ent1 + tok.text
                elif prv_tok_dep == "appos" and ent1:
                    ent1 = ent1 + tok.text

            if tok.dep_ == "conj" and prv_tok_dep == "cc" and ent1:
                ent3 = tok.text

            if tok.dep_ == "obj":
                if ent1:
                    if prv_tok_dep in noundeps and tok.pos_ != "VERB":
                        
                        ent4 = prefix  + tok.text
                    else:
                        ent4 = tok.text

                    if doc[-1].text == tok.text:
                        ent2 = prefix + tok.text

                    prefix = ""
                    prv_tok_dep = ""
                    prv_tok_text = ""

            if tok.text in numbers and prv_tok_dep == "obj" and prv_tok_text in "名詞" and ent4:
                ent4 = "名詞"
                ent2 = ent4 + tok.text
                ent4 = None

            if tok.dep_ == "flat:name" and prv_tok_dep == "obj":
                ent4 = ent4 + tok.text
            elif tok.dep_ != "flat:name" and prv_tok_dep == "obj" and ent4:
                ent2 = ent4
                ent4 = None
            elif tok.dep_ == "flat:name" and prv_tok_dep == "flat:name" and ent4:
                ent4 = ent4 + tok.text
            elif prv_tok_dep == "flat:name" and tok.dep_ != "flat:name" and ent4:
                ent2 = ent4
                ent4 = None

            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text
            prv_tok_pos = tok.pos_

            if ent1 and ent2 and ent3 and rel1:            
                if ent1 in sent_dict:
                    if "名詞" not in ent1:
                        internal_features[sent_dict[ent1]] = {"class":[ent1]}
                        ent1 += ":" + sent_dict[ent1]
                    else:
                        internal_features[sent_dict[ent1]] = {"class":[]}
                        ent1 = sent_dict[ent1]
                else:
                    if "名詞" not in ent1:
                        ent1 = remove_part(ent1)
                        internal_features[ent1] = {"class":[]}
                    else:
                        for key in sent_dict.keys():
                            if key in ent1:
                                ent1 = ent1.replace(key, sent_dict[key])

                if ent2 in sent_dict:
                    if "名詞" not in ent2:
                        internal_features[sent_dict[ent2]] = {"class":[ent2]}
                        ent2 += ":" + sent_dict[ent2]
                    else:
                        internal_features[sent_dict[ent2]] = {"class":[]}
                        ent2 = sent_dict[ent2]
                else:
                    if "名詞" not in ent2:
                        ent2 = remove_part(ent2)
                        internal_features[ent2] = {"class":[]}
                    else:
                        for key in sent_dict.keys():
                            if key in ent2:
                                ent2 = ent2.replace(key, sent_dict[key])

                if ent3 in sent_dict:
                    if "名詞" not in ent3:
                        internal_features[sent_dict[ent3]] = {"class":[ent3]}
                        ent3 += ":" + sent_dict[ent3]
                    else:
                        internal_features[sent_dict[ent3]] = {"class":[]}
                        ent3 = sent_dict[ent3]
                else:
                    if "名詞" not in ent3:
                        ent3 = remove_part(ent3)
                        internal_features[ent3] = {"class":[]}
                    else:
                        for key in sent_dict.keys():
                            if key in ent3:
                                ent3 = ent3.replace(key, sent_dict[key])

                if [ent1, rel1, ent2] not in triplets and [ent3, rel1, ent2] not in triplets:
                    triplets.append([ent1, rel1, ent2])
                    triplets.append([ent3, rel1, ent2])
                    ent2 = None
                    ent3 = None
                    rel1 = None

            if ent1 and ent2 and rel1:
                if ent1 in sent_dict:
                    if "名詞" not in ent1:
                        internal_features[sent_dict[ent1]] = {"class":[ent1]}
                        ent1 += ":" + sent_dict[ent1]
                    else:
                        internal_features[sent_dict[ent1]] = {"class":[]}
                        ent1 = sent_dict[ent1]
                else:
                    if "名詞" not in ent1:
                        ent1 = remove_part(ent1)
                        internal_features[ent1] = {"class":[]}
                    else:
                        for key in sent_dict.keys():
                            if key in ent1:
                                ent1 = ent1.replace(key, sent_dict[key])

                if ent2 in sent_dict:
                    if "名詞" not in ent2:
                        internal_features[sent_dict[ent2]] = {"class":[ent2]}
                        ent2 += ":" + sent_dict[ent2]
                    else:
                        internal_features[sent_dict[ent2]] = {"class":[]}
                        ent2 = sent_dict[ent2]
                else:
                    if "名詞" not in ent2:
                        ent2 = remove_part(ent2)
                        internal_features[ent2] = {"class":[]}
                    else:
                        for key in sent_dict.keys():
                            if key in ent2:
                                ent2 = ent2.replace(key, sent_dict[key])

                if [ent1, rel1, ent2] not in triplets:
                    triplets.append([ent1, rel1, ent2])
                    ent2 = None
                    rel1 = None
            
        return triplets, internal_features
    
    def save_triplets(self, triplets:list, result_path:str):
        heads = [i[0] for i in triplets]
        relationships = [i[1] for i in triplets]
        tails = [i[2] for i in triplets]
        kg_dataset = pd.DataFrame({'head':heads, 'edge':relationships, 'tail':tails})
        kg_dataset.to_json(result_path, force_ascii = False)


if __name__ == "__main__":

    text = """美資國際人力資源管理諮詢企業美世（Mercer）香港財富業務主管陳慧盈對《BBC中文》評論說：「政府重啟『資本投資者入境計劃』的意願發出了一個重要信號，說明香港特區銳意擴展其人才庫，推動高技術領域就業。」

「表明政府承認問題，意識到問題的存在，還有對解決問題的承擔。」

同樣來自美國的萬寶盛華（ManpowerGroup）大中華高級副總裁徐玉珊也對《BBC中文》指出：「香港政府事隔8年重新推出資本投資者入境計劃，相信有一定的吸引力。」

3月，特區政府發表《有關香港發展家族辦公室業務的政策宣言》，再次將新版投資移民計劃列為相關政策。這結果成為了中國大陸社交媒體上的「重磅消息」。從微信、到小紅書來自移民中介、保險、財經類博主的文章、視頻不斷湧現，「香港投資移民即將重啟」呼聲響徹雲霄，「4月1日」更成了一個指標。

但結果，4月1日除了是西方的愚人節之外，特區政府沒有任何公布。

但香港內部也有不少人催促特區政府盡快公布政策細節。例如在家族辦公室政策宣言發表後，直屬中國中央政府駐香港聯絡辦公室（香港中聯辦）的《大公報》便引述萬方家族辦公室集團首席執行官關志敏說，期望該計劃的推出能提升香港作為家族辦公室樞紐的吸引力，希望政府盡快公布實施細節。"""

    result_path = "C:\\Python\\Knowledge graph\\Chinese knowledge graph\\zhkg\\data\\triplets.json"
    retriever = info_retrieval()
    sent_list = retriever.get_sent_list(text)
    total_triplets = []

    for sent in sent_list:
        doc = nlp(sent[1])
        sent_dict = sent[0]
        triplets, internal_features = retriever.get_triplets(doc, sent_dict)
        
        for triplet in triplets:
            total_triplets.append(triplet)

    print(total_triplets)
    retriever.save_triplets(total_triplets, result_path)
