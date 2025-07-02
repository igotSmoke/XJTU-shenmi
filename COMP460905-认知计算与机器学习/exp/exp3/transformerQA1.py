# transformerQA1.py
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
import argparse
import os
from tqdm import tqdm
from transformers import BertTokenizerFast


def compute_em(pred_starts, pred_ends, gold_starts, gold_ends):
    """Compute exact match: both start and end must match."""
    matches = [(p_s == g_s and p_e == g_e) for p_s, p_e, g_s, g_e in zip(pred_starts, pred_ends, gold_starts, gold_ends)]
    return sum(matches) / len(matches) if matches else 0.0

class Config:
    def __init__(self):
        self.batch_size = 8
        self.learning_rate = 3e-6
        self.epochs = 10
        self.max_length = 256
        self.model_dir = "./model_qa1"
        self.train_path = "SQuAD-train-small.json"
        self.dev_path = "SQuAD-dev-small.json"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.d_model = 32
        self.nhead = 2
        self.dim_feedforward = 512
        self.dropout = 0.1
        self.num_layers = 2

class SQuADProcessor:
    def __init__(self, config):
        self.config = config
        self.tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    
    def load_data(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)['data']
    
    def process(self, data):
        examples = []
        for article in data:
            for para in article['paragraphs']:
                context = para['context']
                for qa in para['qas']:
                    # 检查answers是否存在且非空
                    if not qa.get('answers') or len(qa['answers']) == 0:
                        continue  # 跳过没有答案的问题
                
                    # 创建有效样本
                    example = {
                        'context': context,
                        'question': qa['question'],
                        'answer': qa['answers'][0]  # 确保此处不会越界
                    }
                    examples.append(example)
    
        return examples
    
    def create_features(self, examples):
        input_ids, masks = [], []
        start_pos, end_pos = [], []
        
        for ex in examples:
            encoding = self.tokenizer(
                ex['question'],
                ex['context'],
                max_length=self.config.max_length,
                truncation=True,
                padding='max_length',
                return_offsets_mapping=True
            )
            
            ans_start = ex['answer']['answer_start']
            ans_end = ans_start + len(ex['answer']['text'])
            
            sequence_ids = encoding.sequence_ids()
            start_token, end_token = -1, -1
            for i, (seq_id, (s, e)) in enumerate(zip(sequence_ids, encoding['offset_mapping'])):
                if seq_id != 1:
                    continue
                if s <= ans_start and ans_start < e:
                    start_token = i
                if s < ans_end and ans_end <= e:
                    end_token = i

            
            if start_token >= 0 and end_token >= 0:
                input_ids.append(encoding['input_ids'])
                masks.append(encoding['attention_mask'])
                start_pos.append(start_token)
                end_pos.append(end_token)
        
        return {
            'input_ids': torch.tensor(input_ids),
            'attention_mask': torch.tensor(masks),
            'start_pos': torch.tensor(start_pos),
            'end_pos': torch.tensor(end_pos)
        }

class SQuADDataset(Dataset):
    def __init__(self, features):
        self.features = features
    
    def __len__(self):
        return len(self.features['input_ids'])
    
    def __getitem__(self, idx):
        return {k: v[idx] for k, v in self.features.items()}

class TransformerQA(nn.Module):
    def __init__(self, config, tokenizer):
        super().__init__()
        self.tokenizer = tokenizer
        self.embedding = nn.Embedding(self.tokenizer.vocab_size, config.d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(config.max_length, config.d_model))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, config.num_layers)
        self.start_fc = nn.Linear(config.d_model, 1)
        self.end_fc = nn.Linear(config.d_model, 1)
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, input_ids, attention_mask):
        x = self.embedding(input_ids) + self.pos_encoder[:input_ids.size(1)]
        x = self.dropout(x)
        x = x.permute(1, 0, 2)
        output = self.encoder(x, src_key_padding_mask=~attention_mask.bool())
        output = output.permute(1, 0, 2)
        start_logits = self.start_fc(output).squeeze(-1)
        end_logits = self.end_fc(output).squeeze(-1)
        return start_logits, end_logits

class QATrainer:
    def __init__(self, config, model, train_loader=None, dev_loader=None):
        self.config = config
        self.model = model.to(config.device)
        self.train_loader = train_loader
        self.dev_loader = dev_loader
        self.optimizer = AdamW(model.parameters(), lr=config.learning_rate)
        self.loss_fn = nn.CrossEntropyLoss()
    
    def train_epoch(self):
        self.model.train()
        total_loss = 0
        for batch in tqdm(self.train_loader, desc="Training"):
            input_ids = batch['input_ids'].to(self.config.device)
            mask = batch['attention_mask'].to(self.config.device)
            start = batch['start_pos'].to(self.config.device)
            end = batch['end_pos'].to(self.config.device)
            self.optimizer.zero_grad()
            s_logits, e_logits = self.model(input_ids, mask)
            loss = self.loss_fn(s_logits, start) + self.loss_fn(e_logits, end)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / len(self.train_loader)
    
    def evaluate(self):
        self.model.eval()
        total_loss = 0
        pred_starts, pred_ends, gold_starts, gold_ends = [], [], [], []

        print("\n>>> Example predictions:")
        with torch.no_grad():
            for batch_idx, batch in enumerate(tqdm(self.dev_loader, desc="Evaluating")):
                input_ids = batch['input_ids'].to(self.config.device)
                mask = batch['attention_mask'].to(self.config.device)
                start = batch['start_pos'].to(self.config.device)
                end = batch['end_pos'].to(self.config.device)

                s_logits, e_logits = self.model(input_ids, mask)
                loss = self.loss_fn(s_logits, start) + self.loss_fn(e_logits, end)
                total_loss += loss.item()

                s_preds = torch.argmax(s_logits, dim=1)
                e_preds = torch.argmax(e_logits, dim=1)

                pred_starts.extend(s_preds.cpu().tolist())
                pred_ends.extend(e_preds.cpu().tolist())
                gold_starts.extend(start.cpu().tolist())
                gold_ends.extend(end.cpu().tolist())

                # 仅前5个样本展示预测文本
                if batch_idx < 5:
                    for i in range(input_ids.size(0)):
                        input_id = input_ids[i].cpu()
                        tokens = self.model.tokenizer.convert_ids_to_tokens(input_id)
                        pred_answer = self.model.tokenizer.convert_tokens_to_string(tokens[s_preds[i]:e_preds[i]+1])
                        gold_answer = self.model.tokenizer.convert_tokens_to_string(tokens[start[i]:end[i]+1])
                        print(f"[{i+1}]")
                        print(f"  Gold: {gold_answer}")
                        print(f"  Pred: {pred_answer}")
                        print("")

        avg_loss = total_loss / len(self.dev_loader)
        em_score = compute_em(pred_starts, pred_ends, gold_starts, gold_ends)
        return {'dev_loss': avg_loss, 'EM': em_score}


    def save_model(self, path):
        dir_name = os.path.dirname(path)
        if dir_name:  # 只有路径不为空才创建目录
            os.makedirs(dir_name, exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load_model(self, path):
        self.model.load_state_dict(torch.load(path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "test"], required=True)
    parser.add_argument("--model_path", type=str, default=None)
    args = parser.parse_args()

    config = Config()
    processor = SQuADProcessor(config)
    tokenizer = processor.tokenizer

    if args.mode == "train":
        train_data = processor.load_data(config.train_path)
        train_examples = processor.process(train_data)
        train_features = processor.create_features(train_examples)
        train_loader = DataLoader(SQuADDataset(train_features), batch_size=config.batch_size, shuffle=True)

        dev_data = processor.load_data(config.dev_path)
        dev_examples = processor.process(dev_data)
        dev_features = processor.create_features(dev_examples)
        dev_loader = DataLoader(SQuADDataset(dev_features), batch_size=config.batch_size)

        model = TransformerQA(config, tokenizer)
        trainer = QATrainer(config, model, train_loader, dev_loader)
        for epoch in range(config.epochs):
            train_loss = trainer.train_epoch()
            print(f"Epoch {epoch+1} Train Loss: {train_loss:.4f}")
            metrics = trainer.evaluate()
            print(f"Epoch {epoch+1} Dev metrics: {metrics}")
            trainer.save_model(f"{config.model_dir}/epoch_{epoch+1}.pt")
            trainer.save_model("model_qa1.pth")


    else:
        dev_data = processor.load_data(config.dev_path)
        dev_examples = processor.process(dev_data)
        dev_features = processor.create_features(dev_examples)
        dev_loader = DataLoader(SQuADDataset(dev_features), batch_size=config.batch_size)

        model = TransformerQA(config, tokenizer)
        trainer = QATrainer(config, model, None, dev_loader)
        trainer.load_model(args.model_path)
        metrics = trainer.evaluate()
        print(f"Test metrics: {metrics}")

if __name__ == "__main__":
    main()
