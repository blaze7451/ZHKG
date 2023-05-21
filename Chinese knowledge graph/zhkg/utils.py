import json

class util:
    @ staticmethod
    def  make_entity_relation_dict(triplets:list):
        entity_to_idx = {}
        idx_to_entity = {}
        relation_to_idx = {}
        idx_to_relation = {}
        entities = []
        relations = []

        for triplet in triplets:
            head = triplet[0]
            relation = triplet[1]
            tail = triplet[2]
            entities.append(head)
            entities.append(tail)
            relations.append(relation)

        idx1 = 1
        for entity in entities:
            
            if entity not in entity_to_idx:
                entity_to_idx[entity] = idx1
                idx_to_entity[idx1] = entity
                idx1 += 1
            
        idx2 = 1
        for relation in relations:
            if relation not in relation_to_idx:
                relation_to_idx[relation] = idx2
                idx_to_relation[idx2] = relation
                idx2 += 1

        return entity_to_idx, idx_to_entity, relation_to_idx, idx_to_relation
    
    @staticmethod
    def save_dict(dic:dict, path:str):
        result = json.dumps(dic, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as outfile:
            outfile.write(result)
            outfile.close()



if __name__ == "__main__":
    triplets = [['資本者', '入境', '計劃'], ['意願', '發出', '一個重要信號'], ['香港特區', '銳意擴展', '其人才庫'], ['香港特區', '推動', '高技術領域'], ['香港政府事', '推出', '資本者入境計劃'], ['香港政府事', '相信有', '力'], ['特區政府', '發表', '《有關香港發展家族辦公室業務的政策宣言》'], ['將新版', '投資', '移民'], ['將新版', '列為', '相關政策'], ['這結果', '為', '「重磅消息」'], ['這結果', '自', '移民中介'], ['「香港投資移民即將重啟」呼聲', '響', '徹雲霄'], ['「4月1日」', '成', '一個指標'], ['特區政府', '沒有', '任何公布'], ['不少人', '催', '促特區政府'], ['不少人', '公布', '政策細節'], ['中國中央政府', '駐', '香港'], ['中國中央政府', '引述', '《大公報》'], ['萬方家族室集團首席', '執行', '官關志敏'], ['香港', '作為', '力'], ['政府', '公布', '實施細節']]
    entity_to_idx, idx_to_entity, relation_to_idx, idx_to_relation = util.make_entity_relation_dict(triplets)
    path1 = "Knowledge graph\\Chinese knowledge graph\\zhkg\\data\\ent_to_idx.json"
    path2 = "Knowledge graph\\Chinese knowledge graph\\zhkg\\data\\idx_to_ent.json"
    path3 = "Knowledge graph\\Chinese knowledge graph\\zhkg\\data\\relation_to_idx.json"
    path4 = "Knowledge graph\\Chinese knowledge graph\\zhkg\\data\\idx_to_relation.json"
    util.save_dict(entity_to_idx, path1)
    util.save_dict(idx_to_entity, path2)
    util.save_dict(relation_to_idx, path3)
    util.save_dict(idx_to_relation, path4)
