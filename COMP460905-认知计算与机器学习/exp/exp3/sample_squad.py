# sample_squad.py
import json
import random

def sample_squad(in_path, out_path, num_samples):
    with open(in_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_qas = []
    for article in data['data']:
        for para in article['paragraphs']:
            for qa in para['qas']:
                all_qas.append({'context': para['context'],
                                'qas': [qa]})
    sampled = random.sample(all_qas, min(num_samples, len(all_qas)))
    # 把它再拼回 SQuAD 格式
    out = {'version': data.get('version', ''),
           'data': [{'title': 'sample', 'paragraphs': sampled}]}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    sample_squad('SQuAD-train-v2.0.json', 'SQuAD-train-small.json', 2000)
    sample_squad('SQuAD-dev-v2.0.json',   'SQuAD-dev-small.json',   500)
