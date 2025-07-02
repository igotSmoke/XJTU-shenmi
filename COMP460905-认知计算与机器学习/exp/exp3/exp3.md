一、自动问答
在SQuAD数据集(SQuAD-dev-v2.0.json; SQuAD-train-v2.0.json)上用2种基于Transformer的模型完成自动问答任务。
补全示例代码，调整模型的训练参数，包括词向量维度、优化方法、学习率、batch大小等等，观察这些参数对模型训练和测试结果的影响。

```transfomerQA1.py
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
import argparse
import os
from tqdm import tqdm
from transformers import BertTokenizerFast

class Config:
    def __init__(self):
        self.batch_size = 8
        self.learning_rate = 3e-5
        self.epochs = 3
        self.max_length = 384
        self.model_dir = "./model"
        self.train_path = "train-v1.1.json"
        self.dev_path = "dev-v1.1.json"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.d_model = 768
        self.nhead = 12
        self.dim_feedforward = 3072
        self.dropout = 0.1
        self.num_layers = 7

class SQuADProcessor:
    def __init__(self, config):
        self.config = config
        self.tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    
    def load_data(self, path):
        with open(path, 'r') as f:
            return json.load(f)['data']
    
    def process(self, data):
        examples = []
        for article in data:
            for para in article['paragraphs']:
                context = para['context']
                for qa in para['qas']:
                    example = {
                        'context': context,
                        'question': qa['question'],
                        'answer': qa['answers'][0]
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
            
            start_char = ans_start
            end_char = ans_end
            sequence_ids = encoding.sequence_ids()
            
            # Find token positions
            start_token, end_token = -1, -1
            for i, (idx, (s, e)) in enumerate(zip(sequence_ids, encoding.offset_mapping)):
                if idx != 1: continue  # Only look at context tokens
                if s <= start_char < e: start_token = i
                if s < end_char <= e: end_token = i
            
            if start_token != -1 and end_token != -1:
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
    def __init__(self, config):
        super().__init__()
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
        x = x.permute(1, 0, 2)  # [seq_len, bs, dim]
        
        output = self.encoder(x, src_key_padding_mask=~attention_mask.bool())
        output = output.permute(1, 0, 2)  # [bs, seq_len, dim]
        
        start_logits = self.start_fc(output).squeeze(-1)
        end_logits = self.end_fc(output).squeeze(-1)
        return start_logits, end_logits

class QATrainer:
    def __init__(self, config, model, train_loader, dev_loader=None):
        self.config = config
        self.model = model.to(config.device)
        self.train_loader = train_loader
        self.dev_loader = dev_loader
        self.optimizer = AdamW(model.parameters(), lr=config.learning_rate)
    
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
            
            loss = nn.CrossEntropyLoss()(s_logits, start) + \
                   nn.CrossEntropyLoss()(e_logits, end)
            
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / len(self.train_loader)
    
    def evaluate(self):
        self.model.eval()
        # 请补全evaluate过程

    
    def save_model(self, path):
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path):
        self.model.load_state_dict(torch.load(path))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "test"], required=True)
    parser.add_argument("--model_path", type=str)
    args = parser.parse_args()
    
    # 训练命令：python script.py --mode train 
    # 测试命令：python script.py --mode test --model_path /path/to/model
    
    config = Config()
    processor = SQuADProcessor(config)
    
    if args.mode == "train":
        # 训练流程
        train_data = processor.load_data(config.train_path)
        train_examples = processor.process(train_data)
        train_features = processor.create_features(train_examples)
        train_dataset = SQuADDataset(train_features)
        train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
        
        dev_data = processor.load_data(config.dev_path)
        dev_examples = processor.process(dev_data)
        dev_features = processor.create_features(dev_examples)
        dev_loader = DataLoader(SQuADDataset(dev_features), batch_size=config.batch_size)
        
        model = TransformerQA(config)
        trainer = QATrainer(config, model, train_loader, dev_loader)
        
        for epoch in range(config.epochs):
            avg_loss = trainer.train_epoch()
            print(f"Epoch {epoch+1} Loss: {avg_loss}")
            metrics = trainer.evaluate()
            print(metrics)
            trainer.save_model(f"{config.model_dir}/epoch_{epoch+1}.pt")
    
    elif args.mode == "test":
        # 测试流程
        dev_data = processor.load_data(config.dev_path)
        dev_examples = processor.process(dev_data)
        dev_features = processor.create_features(dev_examples)
        dev_loader = DataLoader(SQuADDataset(dev_features), batch_size=config.batch_size)
        
        model = TransformerQA(config)
        trainer = QATrainer(config, model, None, dev_loader)
        trainer.load_model(args.model_path)
        metrics = trainer.evaluate()
        print(f"Test Results - {metrics}")

if __name__ == "__main__":
    main()


```

```transformerQA2.py
import torch
import torch.nn as nn
import json
import transformerRaw
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer


class QADataset(Dataset):
    """SQuAD格式数据处理"""
    def __init__(self, file_path, tokenizer, max_length=512):
        self.data = []
        with open(file_path) as f:
            squad_data = json.load(f)
        
        for article in squad_data['data']:
            for paragraph in article['paragraphs']:
                context = paragraph['context']
                for qa in paragraph['qas']:
                    question = qa['question']
                    answer = qa['answers'][0]['text'] if qa['answers'] else ""
                    
                    # 构造模型输入输出
                    input_text = f"[CLS] {question} [SEP] {context} [SEP]"
                    output_text = f"[CLS] {answer} [SEP]"
                    
                    # 编码文本
                    inputs = tokenizer(input_text, max_length=max_length, 
                                     padding='max_length', truncation=True, 
                                     return_tensors="pt")
                    targets = tokenizer(output_text, max_length=max_length,
                                      padding='max_length', truncation=True,
                                      return_tensors="pt")
                    
                    self.data.append({
                        'input_ids': inputs['input_ids'].squeeze(0),
                        'attention_mask': inputs['attention_mask'].squeeze(0),
                        'labels': targets['input_ids'].squeeze(0)
                    })

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


class PositionalEncoding(nn.Module):
    """位置编码模块"""
    def __init__(self, d_model, max_len=512, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(1), :]
        return self.dropout(x)

class TransformerQA(nn.Module):
    """问答模型（含自定义编码器/解码器）"""
    def __init__(self, vocab_size, d_model=512, nhead=8, 
                 num_encoder_layers=6, num_decoder_layers=6,
                 dim_feedforward=2048, dropout=0.1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout=dropout)
        
        self.encoder = TransformerEncoder(
            num_encoder_layers, d_model, nhead, dim_feedforward, dropout)
        
        self.decoder = TransformerDecoder(
            num_decoder_layers, d_model, nhead, dim_feedforward, dropout)
        
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.d_model = d_model

    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        # 编码器处理
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        memory = self.encoder(src, src_mask)
        
        # 解码器处理
        tgt = self.embedding(tgt) * math.sqrt(self.d_model)
        tgt = self.pos_encoder(tgt)
        output = self.decoder(tgt, memory, tgt_mask)
        
        return self.fc_out(output)

    def generate_mask(self, src, tgt):
        """生成注意力掩码"""
        # 源序列填充掩码
        src_pad_mask = (src == 0).unsqueeze(1).unsqueeze(2)
        
        # 目标序列掩码（自回归+填充）
        tgt_pad_mask = (tgt == 0).unsqueeze(1).unsqueeze(2)
        seq_len = tgt.size(1)
        tgt_sub_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
        tgt_mask = tgt_pad_mask | tgt_sub_mask.to(src.device)
        
        return src_pad_mask, tgt_mask
        
    # 实现自回归生成过程
    def generate_answer(self, src, max_len=50):
        memory = self.encoder(src)
        outputs = torch.LongTensor([[self.tokenizer.cls_token_id]]).to(device)
    
        for _ in range(max_len):
            out = self.decoder(outputs, memory)
            next_token = out.argmax(-1)[:, -1:]
            outputs = torch.cat([outputs, next_token], dim=-1)
        
            if next_token == self.tokenizer.sep_token_id:
                break
            
        return self.tokenizer.decode(outputs[0])



class QATrainer:
    """训练管理类"""
    def __init__(self, model, tokenizer, device='cuda'):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
        
    def prepare_batch(self, batch):
        """数据预处理"""
        src = batch['input_ids'].to(self.device)   # 源序列（问题+上下文）
        tgt = batch['labels'].to(self.device)      # 目标序列（答案）
        # 注意：batch是否在前。
        
        # 构造解码器输入（去尾）和输出（去头）
        decoder_input = tgt[:, :-1]  # 移除最后一个token
        decoder_output = tgt[:, 1:]  # 移除第一个token
        
        # 生成注意力掩码
        src_mask, tgt_mask = self.model.generate_mask(src, decoder_input)
        return src, decoder_input, decoder_output, src_mask, tgt_mask
        
    def train_epoch(self, dataloader, optimizer):
        self.model.train()
        total_loss = 0
        
        for batch in dataloader:
            # 数据准备
            src, decoder_in, decoder_out, src_mask, tgt_mask = self.prepare_batch(batch)

            optimizer.zero_grad()
            
            # 前向传播 (B, S) -> (B, S, V)
            # 直接使用目标序列来训练
            outputs = self.model(
                src.transpose(0, 1),   # (S, B) 时间维在前
                decoder_in.transpose(0, 1),
                src_mask,
                tgt_mask
            ).transpose(0, 1)  # 转回(B, S, V)
            
            # 计算损失
            loss = self.criterion(
                outputs.reshape(-1, outputs.shape[-1]), 
                decoder_out.reshape(-1)
            )
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            # 每100批次打印进度
            if batch_idx % 100 == 0:
                current_loss = total_loss / (batch_idx + 1)
                print(f"  Batch {batch_idx} | Loss: {current_loss:.4f}")
            
        return total_loss / len(dataloader)

    def evaluate(self, dataloader):
        # 请补全验证过程代码
                
        return total_loss / len(dataloader)

# 使用示例
if __name__ == "__main__":
    # 补全命令行参数设置
    	
    # 初始化组件参考代码
    # tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # train_dataset = QADataset('train-v2.0.json', tokenizer)
    # train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    
    # model = TransformerQA(vocab_size=tokenizer.vocab_size)
    # trainer = QATrainer(model, tokenizer)
    # optimizer = torch.optim.Adam(model.parameters(), lr=3e-5)
    
    # 请补全后面的代码

```

```transformerRaw.py

```