import argparse
import math
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer
from transformerRaw import TransformerEncoder, TransformerDecoder

class QADataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=512):
        self.data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            squad_data = json.load(f)
        for article in squad_data['data']:
            for paragraph in article['paragraphs']:
                context = paragraph['context']
                for qa in paragraph['qas']:
                    question = qa['question']
                    answer = qa['answers'][0]['text'] if qa['answers'] else ""
                    input_text = f"[CLS] {question} [SEP] {context} [SEP]"
                    output_text = f"[CLS] {answer} [SEP]"
                    inputs = tokenizer(input_text, max_length=max_length, padding='max_length', truncation=True, return_tensors="pt")
                    targets = tokenizer(output_text, max_length=max_length, padding='max_length', truncation=True, return_tensors="pt")
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
    def __init__(self, vocab_size, d_model=512, nhead=8, num_encoder_layers=6, num_decoder_layers=6, dim_feedforward=2048, dropout=0.1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout=dropout)
        self.encoder = TransformerEncoder(num_encoder_layers, d_model, nhead, dim_feedforward, dropout)
        self.decoder = TransformerDecoder(num_decoder_layers, d_model, nhead, dim_feedforward, dropout)
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.d_model = d_model
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        memory = self.encoder(src, src_mask)
        tgt = self.embedding(tgt) * math.sqrt(self.d_model)
        tgt = self.pos_encoder(tgt)
        output = self.decoder(tgt, memory, tgt_mask)
        return self.fc_out(output)
    def generate_mask(self, src, tgt):
        src_pad = (src == 0).unsqueeze(1).unsqueeze(2)
        tgt_pad = (tgt == 0).unsqueeze(1).unsqueeze(2)
        seq_len = tgt.size(1)
        tgt_sub = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
        tgt_mask = tgt_pad | tgt_sub.to(src.device)
        return src_pad, tgt_mask

class QATrainer:
    def __init__(self, model, tokenizer, device='cuda'):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
    def prepare_batch(self, batch):
        src = batch['input_ids'].to(self.device)
        tgt = batch['labels'].to(self.device)
        decoder_in = tgt[:, :-1]
        decoder_out = tgt[:, 1:]
        src_mask, tgt_mask = self.model.generate_mask(src, decoder_in)
        return src, decoder_in, decoder_out, src_mask, tgt_mask
    def train_epoch(self, dataloader, optimizer):
        self.model.train()
        total_loss = 0
        for i, batch in enumerate(dataloader):
            src, dec_in, dec_out, src_mask, tgt_mask = self.prepare_batch(batch)
            optimizer.zero_grad()
            outputs = self.model(src, dec_in, src_mask, tgt_mask)
            loss = self.criterion(outputs.reshape(-1, outputs.shape[-1]), dec_out.reshape(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            if i % 100 == 0:
                print(f"Batch {i} | Loss: {total_loss/(i+1):.4f}")
        return total_loss / len(dataloader)
    def evaluate(self, dataloader):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch in dataloader:
                src, dec_in, dec_out, src_mask, tgt_mask = self.prepare_batch(batch)
                outputs = self.model(src, dec_in, src_mask, tgt_mask)
                loss = self.criterion(outputs.reshape(-1, outputs.shape[-1]), dec_out.reshape(-1))
                total_loss += loss.item()
        return total_loss / len(dataloader)
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "test"], required=True)
    parser.add_argument("--train_path", type=str, default="SQuAD-train-small.json")
    parser.add_argument("--dev_path", type=str, default="SQuAD-dev-small.json")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--max_length", type=int, default=128)
    parser.add_argument("--model_path", type=str, default="./model_qa2.pth")
    args = parser.parse_args()

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.mode == "train":
        train_ds = QADataset(args.train_path, tokenizer, args.max_length)
        dev_ds = QADataset(args.dev_path, tokenizer, args.max_length)
        train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
        dev_loader = DataLoader(dev_ds, batch_size=args.batch_size)
        model = TransformerQA(tokenizer.vocab_size, d_model=512).to(device)
        trainer = QATrainer(model, tokenizer, device)
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
        for epoch in range(args.epochs):
            train_loss = trainer.train_epoch(train_loader, optimizer)
            print(f"Epoch {epoch+1}/{args.epochs} Train Loss: {train_loss:.4f}")
            dev_loss = trainer.evaluate(dev_loader)
            print(f"Epoch {epoch+1}/{args.epochs} Dev Loss: {dev_loss:.4f}")
            torch.save(model.state_dict(), f"qa2_epoch_{epoch+1}.pt")
            torch.save(model.state_dict(), args.model_path)

            
    else:
        dev_ds = QADataset(args.dev_path, tokenizer, args.max_length)
        dev_loader = DataLoader(dev_ds, batch_size=args.batch_size)
        model = TransformerQA(tokenizer.vocab_size, d_model=512).to(device)
        model.load_state_dict(torch.load(args.model_path))
        trainer = QATrainer(model, tokenizer, device)
        test_loss = trainer.evaluate(dev_loader)
        print(f"Test Loss: {test_loss:.4f}")


