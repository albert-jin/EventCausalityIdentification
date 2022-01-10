import os
from lxml import etree

base_dir = os.path.abspath('.')
annotations_path = os.path.join(base_dir, 'annotations')
ECB_plus_path = os.path.join(base_dir, 'ECB+')
evaluations_path = os.path.join(base_dir, 'evaluations')

assert os.path.isdir(annotations_path) and os.path.isdir(ECB_plus_path) \
       and os.path.isdir(evaluations_path), '请阅读README下载对应的文件解压到本目录下.'

if __name__ == '__main__':
    # preprocess
    # 删除annotations目录的非xml文件 & 重命名xml文件
    for dirname in os.listdir(annotations_path):
        dir_ = os.path.join(annotations_path, dirname)
        if not os.path.isdir(dir_):
            continue
        for filename in os.listdir(dir_):
            if filename.endswith('.xml.xml'):
                os.rename(os.path.join(dir_, filename), os.path.join(dir_, filename.replace('.xml.xml', '.xml')))
            elif not filename.endswith('.xml'):
                os.remove(os.path.join(dir_, filename))

    # 删除ECB+目录下所有的没有plus的文件(与事件因果无关的数据)
    for dirname in os.listdir(ECB_plus_path):
        dir_path = os.path.join(ECB_plus_path, dirname)
        if os.path.isdir(dir_path):
            for filename in os.listdir(dir_path):
                if 'plus.xml' not in filename:
                    os.remove(os.path.join(dir_path, filename))

#  开始收集数据集
'''
Rules:
    1. 对文章分段：对于一对出现在语料中的因果事件，通过找前事件之前的分句符 & 事件之后的分句符来确定该句子 (., !, ?, 。,等).
    2. 对于超出长度的句子，事件之前50 &  之后50 个字符进行截断 50 + A...B + 50
    3. 舍弃掉因果事件距离超过100单词（indexs）的句子
    4. 因事件的首尾位置用 <CAUSE></CAUSE> 标记; 果事件的首尾位置用 <EFFECT></EFFECT> 标记;
'''


def extract_tokens(etree_root):
    """
    输出下标 与 字符 的映射关系
    :param etree_root:
    :return: 字典 token_index → token
    """
    mapped_tokens = {}
    for element in etree_root.findall('token'):
        token_index = element.get('t_id')
        token = element.text
        mapped_tokens[token_index] = token
    return mapped_tokens


def extract_events(etree_root):
    """
    抽取xml文档中事件编号 与 事件下标 映射关系
    :param etree_root:
    :return: 字典 event_id str → event_indexs list
    """
    mapped_events = {}
    for element in etree_root.findall('Markables/'):
        if element.tag.startswith("ACTION") or element.tag.startswith("NEG_ACTION"):
            event_id = element.get('m_id')
            event_indexs = []
            for token_anchor in element.findall('token_anchor'):
                event_indexs.append(token_anchor.get('t_id'))
            mapped_events[event_id] = event_indexs
    return mapped_events


def extract_causality(etree_root):
    """
    抽取因果事件对 事件用event_id表示
    :param etree_root:
    :return: [(event_id1, event_id2),...]
    """
    all_causalities = []
    for element in etree_root.findall('Relations/'):
        if element.tag == 'PLOT_LINK':
            cause_event_id = element.find('source').get('m_id')
            effect_event_id = element.find('target').get('m_id')
            all_causalities.append((cause_event_id, effect_event_id, element.get('relType')))
    return all_causalities


if __name__ == '__main__':
    # 单元测试
    test_file = os.path.join(annotations_path, '1', '1_1ecbplus.xml')
    etree_root = etree.parse(test_file, etree.XMLParser(remove_blank_text=True)).getroot()
    all_causalities = extract_causality(etree_root)
    mapped_events = extract_events(etree_root)
    mapped_tokens = extract_tokens(etree_root)
    pass


def extract_from_three_factors(causalities, events, tokens):
    """
    利用三个参数抽取数据集
    :param causalities:
    :param events:
    :param tokens:
    :return:
    """
    results = []
    STOP_TOKENS = ['.', '?', '!', '。']
    s_cause, e_cause, s_effect, e_effect = '<CAUSE>', '</CAUSE>', '<EFFECT>', '</EFFECT>'
    # 抽取
    wrong_num, ok_num = 0, 0
    for causality in causalities:
        try:
            s_event_id, e_event_id, rel_type = causality
            s_event_indexs, e_event_indexs = events[s_event_id], events[e_event_id]
            if int(e_event_indexs[-1]) - int(s_event_indexs[0]) > 100:  # Rule3
                continue
            # 寻找开始事件前倒序第一个的句子截断符号
            sent_start_idx = int(s_event_indexs[0])
            while sent_start_idx > 0:  # 循环结束，sent_start_idx 为句子开始的下标
                if tokens[str(sent_start_idx)] in STOP_TOKENS:
                    break
                sent_start_idx -= 1
            sent_start_idx += 1  # 保证sent_start_idx为句子起始下标
            if sent_start_idx - int(s_event_indexs[-1]) > 50:  # Rule2
                sent_start_idx = int(s_event_indexs[-1]) + 50

            # 寻找结束事件后正序第一个的句子截断符号
            sent_end_idx = int(e_event_indexs[-1])
            while str(sent_end_idx) in tokens:  # 循环结束，sent_end_idx 为句子结束的下标+1
                if tokens[str(sent_end_idx)] in STOP_TOKENS:
                    sent_end_idx += 1
                    break
                sent_end_idx += 1
            if sent_end_idx - int(e_event_indexs[-1]) > 50:  # Rule2
                sent_end_idx = int(e_event_indexs[-1]) + 50

            # 利用句子开始位置,句子结束位置, 头尾实体下标, 获取整理的语句
            sentence = []
            for token_idx in range(sent_start_idx, sent_end_idx):
                token_idx = str(token_idx)
                if token_idx == s_event_indexs[0] and len(s_event_indexs) == 1:
                    sentence.append(s_cause)
                    sentence.append(tokens[token_idx])
                    sentence.append(e_cause)
                elif token_idx == s_event_indexs[0]:
                    sentence.append(s_cause)
                    sentence.append(tokens[token_idx])
                elif token_idx == s_event_indexs[-1]:
                    sentence.append(tokens[token_idx])
                    sentence.append(e_cause)
                elif token_idx == e_event_indexs[0] and len(e_event_indexs) == 1:
                    sentence.append(s_effect)
                    sentence.append(tokens[token_idx])
                    sentence.append(e_effect)
                elif token_idx == e_event_indexs[0]:
                    sentence.append(s_effect)
                    sentence.append(tokens[token_idx])
                elif token_idx == e_event_indexs[-1]:
                    sentence.append(tokens[token_idx])
                    sentence.append(e_effect)
                else:  # 不需要加标记
                    sentence.append(tokens[token_idx])
            sentence = ' '.join(sentence)
            results.append((sentence, rel_type))

            ok_num += 1
        except:  # 对于所有异常error, 忽略此对因果事件的标注
            wrong_num += 1
            continue
    return results, ok_num, wrong_num


def extract_from_single_file(annotation_file):
    """
    适用于annotations文件夹下的文件标注
    :param annotation_file: annotations文件夹下以.xml结尾的文件
    :return: 标注数据对象 [(sentence, tag)]  sentence 服从Rules规则
    """

    root = etree.parse(annotation_file, etree.XMLParser(remove_blank_text=True)).getroot()
    causalities = extract_causality(root)
    events = extract_events(root)
    tokens = extract_tokens(root)
    return extract_from_three_factors(causalities, events, tokens)


if __name__ == '__main__':
    # 单元测试
    test_file = os.path.join(annotations_path, '1', '1_1ecbplus.xml')
    extract_from_single_file(test_file)


def extract_from_two_files(raw_file, evaluations_file):
    """
    适用于ECB+ 和 evaluations文件夹下的文件的配合标注
    :param raw_file: ECB+下的.xml 文件
    :param evaluations_file: evaluations文件夹下以.xml结尾的文件
    :return: 标注数据对象 [(sentence, tag)]  sentence 服从Rules规则
    """
    # 读取evaluations文件 并生成causalities, events
    causalities, events = [], {}
    all_event_idxs = {}
    event_id = 1
    with open(evaluations_file, mode='rt', encoding='utf-8') as reader:
        for line in reader.readlines():
            s_event_idxs, e_event_idxs, rel_type = line.strip().split('\t')
            causalities.append([s_event_idxs, e_event_idxs, rel_type])
            if s_event_idxs not in all_event_idxs:
                all_event_idxs[s_event_idxs] = str(event_id)
                event_id += 1
            if e_event_idxs not in all_event_idxs:
                all_event_idxs[e_event_idxs] = str(event_id)
                event_id += 1
    for event_idxs in all_event_idxs:
        events[all_event_idxs[event_idxs]] = event_idxs.split('_')
    for causality in causalities:
        causality[0] = all_event_idxs[causality[0]]
        causality[1] = all_event_idxs[causality[1]]
    # print(causalities, events)

    # 抽取ECB+里的tokens
    root = etree.parse(raw_file, etree.XMLParser(remove_blank_text=True)).getroot()
    tokens = extract_tokens(root)
    # 进行数据集抽取

    return extract_from_three_factors(causalities, events, tokens)


if __name__ == '__main__':
    # 单元测试
    test_ecb_plus = os.path.join(ECB_plus_path, '1', '1_1ecbplus.xml')
    test_evaluations = os.path.join(evaluations_path, '1', '1_1ecbplus.xml')
    results, ok_num, wrong_num = extract_from_two_files(test_ecb_plus, test_evaluations)


# 数据集抽取并生成.txt 保存

# 抽取annotations文件夹的标注数据
all_data = []
ok_count, wrong_count = 0, 0
for dirname in os.listdir(annotations_path):
    dir_ = os.path.join(annotations_path, dirname)
    if not os.path.isdir(dir_):
        continue
    for filename in os.listdir(dir_):
        if filename.endswith('.xml'):
            results, ok_num, wrong_num = extract_from_single_file(os.path.join(dir_, filename))
            all_data.extend(results)
            ok_count += ok_num
            wrong_count += wrong_num

# 联合抽取ECB+ 和 evaluations文件夹的标注数据
wrong_file_num = 0  # ECB+ 和 evaluations文件 不匹配情况数
for dirname in os.listdir(evaluations_path):
    dir_ = os.path.join(evaluations_path, dirname)
    if not os.path.isdir(dir_):
        continue
    for filename in os.listdir(dir_):
        if filename.endswith('.xml'):
            ecb_plus_file = os.path.join(ECB_plus_path, dirname, filename)
            if not os.path.isfile(ecb_plus_file):
                wrong_file_num += 1
                continue
            evaluations_file = os.path.join(dir_, filename)
            results, ok_num, wrong_num = extract_from_two_files(ecb_plus_file, evaluations_file)
            all_data.extend(results)
            ok_count += ok_num
            wrong_count += wrong_num

print(f'all_data 共有 {len(all_data)} 条, 示例:{all_data[0]}')

relations = {}
with open(os.path.join('.', 'eventStoryLine_dataset.txt'), mode='wt', encoding='utf-8') as writer:
    for sentence, rel_type in all_data:
        rel_type = str(rel_type)
        if rel_type not in relations:
            relations[rel_type] = 0
        else:
            relations[rel_type] += 1
        writer.write(sentence+'\n'+rel_type+'\n\n')

print(f'ok_count: {ok_count}, wrong_count: {wrong_count}')
