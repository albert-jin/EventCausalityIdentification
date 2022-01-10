"""
    用于请求ConceptNet知识图谱的事件属性信息
"""
import requests

relations = ['CapableOf', 'IsA', 'HasProperty',
             'Causes', 'MannerOf', 'CausesDesire',
             'UsedFor', 'HasSubevent', 'HasPrerequisite',
             'NotDesires', 'PartOf', 'HasA',
             'Entails', 'ReceivesAction', 'UsedFor',
             'CreatedBy', 'MadeOf', 'Desires']


def request_concept_net(query_word: str):
    """
    在ConceptNet中查询该实体相关的图谱节点
    :param query_word:
    :return:返回 {'status': False} or {'status': True, 'result': [(关系类型1，节点标签1),(关系类型2，节点标签2),...]}
    """
    results = requests.get('https://api.conceptnet.io/c/en/%s' % query_word.lower()).json()
    attributes_knowledge = []
    try:
        for edge in results['edges']:
            relation_type = edge['rel']['label']
            if relation_type in relations:
                node = edge['end']['label']
                attributes_knowledge.append((relation_type, node))
        return {'status': True, 'result': attributes_knowledge}  # 返回成功
    except KeyError:
        return {'status': False}  # 返回失败


if __name__ == '__main__':
    query_word = 'Pigs'
    request_concept_net(query_word)
