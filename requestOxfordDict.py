"""
    用于请求牛津字典的事件描述信息
"""

import requests


app_id = 'c2e7b1fe'
app_key = 'b41be5b3b08f91ebe3d849570f15c52a'
path = '/api/v2/search/en-gb'
entry_path = '/api/v2/entries/en-gb/'
language_type = 'en-gb'
urlOxfordApiProxy = 'https://od-api.oxforddictionaries.com'
urlProxy = "https://developer.oxforddictionaries.com/api_docs/proxy"
methodRequestGet = 'GET'


def request_word_explanation(query_word):
    '''
    查询牛津字典对于词汇的解释
    :param query_word: 查询单词
    :return: 返回描述文本 {'status': False} or {'status': True, 'result': final_dict_knowledge}
    '''
    target_headers = {'X-Apidocs-Url': urlOxfordApiProxy,
                      'X-Apidocs-Method': methodRequestGet,
                      'X-Apidocs-Query': 'q=' + query_word,
                      'X-Apidocs-Path': path,
                      'app_id': app_id,
                      'app_key': app_key}
    r = requests.get(urlProxy, headers=target_headers)
    ''' r.text.results[0] 一览
        {
        "id": "pigs_in_clover",
        "label": "pigs in clover",
        "matchString": "sbpigs",
        "matchType": "fuzzy",
        "score": 22.254377,
        "word": "pigs in clover"
        }
    '''  # matchString 与原查询词汇的区别是：大小写统一
    if r.status_code != 200:
        return {'status': False}
    res = eval(r.text)  # matchString = 原词汇, id,word,label =fuzzy 匹配的词汇 , 优先使用word
    if 'results' not in res or len(res['results']) == 0:
        return {'status': False}
    infos = res['results'][0]
    keyRetry = infos['word'] or infos['id'] or infos['label']  # 用于查牛津词典的名词解释的中间单词
    target_entry_headers = {'X-Apidocs-Url': urlOxfordApiProxy,
                            'X-Apidocs-Method': methodRequestGet,
                            'X-Apidocs-Query': '',
                            'X-Apidocs-Path': entry_path + keyRetry,
                            'app_id': app_id,
                            'app_key': app_key}
    r = requests.get(urlProxy, headers=target_entry_headers)
    if r.status_code != 200:
        return {'status': False}
    res = eval(r.text)
    try:
        descriptions = []
        entries = res['results'][0]['lexicalEntries'][0]['entries']
        for entry in entries:  # 一个entry下所有解释
            description = ' [SEP] '.join(['.'.join(describe['definitions']) for describe in entry['senses']])  # 一个senses下所有解释
            descriptions.append(description)
    except KeyError:
        return {'status': False}
    final_dict_knowledge = ' [SEP] '.join(descriptions)
    if final_dict_knowledge:
        return {'status': True, 'result': final_dict_knowledge}
    else:
        return {'status': False}


if __name__ == '__main__':
    word = 'SBpigs'
    request_word_explanation(word)
    # 牛津官网示例，稍作修改
    '''
        import json
        app_id = 'c2e7b1fe'
        app_key = 'b41be5b3b08f91ebe3d849570f15c52a'
        language = 'en-gb'
        url = 'https://od-api.oxforddictionaries.com/api/v2/entries/' + language + '/' + word.lower()
        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
        print("code {}\n".format(r.status_code))
        print("text \n" + r.text)
        print("json \n" + json.dumps(r.json()))
    '''
