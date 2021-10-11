import json
import re

# Filtering non simple text messages from initial chat history
with open('result.json', encoding='utf8') as f:
    data = json.load(f)

    list_msgs = [x for x in data['messages'] if type(x['text']) == list and len(x['text']) > 2]
    download_msgs = [x for x in list_msgs if len(re.findall(r'\nID[^= ]', x['text'][-1])) > 0]

with open('filtered.json', 'w') as outfile:
    json.dump(download_msgs, outfile)

# Getting file attributes from filtered messages
with open('filtered.json', encoding='utf8') as f:
    data = json.load(f)

    new_list = []
    for i in data:
        list_item = {}
        text_msg = i['text'][2].split('\n')
        size = [x for x in text_msg if 'size:' in x]
        author = [x for x in text_msg if 'author:' in x]

        list_item['name'] = i['text'][1]['text']
        if len(size) > 0:
            list_item['size'] = size[0].split(': ')[-1]
        if len(author) > 0:
            list_item['author'] = author[0].split(': ')[-1]
        list_item['id'] = text_msg[-1][2:]  # Cutting 'ID' substring from id string beginning
        new_list.append(list_item)

with open('short.json', 'w') as outfile:
    json.dump(new_list, outfile)
