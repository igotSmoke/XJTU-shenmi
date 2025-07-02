import torch
import argparse
from transformers import BertTokenizer
from transformerQA2 import TransformerQA, PositionalEncoding  # 确保这个模块名是 transformerQA2.py

def generate_answer(model, tokenizer, question, context, device, max_length=128):
    model.eval()
    input_text = f"[CLS] {question} [SEP] {context} [SEP]"
    inputs = tokenizer(input_text, max_length=max_length, padding='max_length', truncation=True, return_tensors="pt")
    input_ids = inputs['input_ids'].to(device)

    # 生成时先输入 [CLS]
    decoder_input = torch.tensor([[tokenizer.cls_token_id]], device=device)

    for _ in range(max_length):
        src_mask, tgt_mask = model.generate_mask(input_ids, decoder_input)
        outputs = model(input_ids, decoder_input, src_mask, tgt_mask)
        next_token = outputs[:, -1, :].argmax(-1).unsqueeze(1)

        # 如果遇到 [SEP] 则终止
        if next_token.item() == tokenizer.sep_token_id:
            break
        decoder_input = torch.cat([decoder_input, next_token], dim=1)

    answer = tokenizer.decode(decoder_input.squeeze(), skip_special_tokens=True)
    return answer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--question", type=str, required=True)
    parser.add_argument("--context", type=str, required=True)
    args = parser.parse_args()

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = TransformerQA(tokenizer.vocab_size, d_model=512).to(device)
    model.load_state_dict(torch.load(args.model_path, map_location=device))

    answer = generate_answer(model, tokenizer, args.question, args.context, device)
    print("Answer:", answer)
