# run_inference.py
import torch
from transformerQA1 import TransformerQA, Config
from transformers import BertTokenizerFast
import argparse

def answer_question(model, tokenizer, config, question, context):
    encoding = tokenizer(
        question,
        context,
        max_length=config.max_length,
        truncation=True,
        padding='max_length',
        return_tensors='pt',
        return_offsets_mapping=True
    )

    input_ids = encoding['input_ids'].to(config.device)
    attention_mask = encoding['attention_mask'].to(config.device)
    offsets = encoding['offset_mapping'][0]  # (seq_len, 2)

    with torch.no_grad():
        start_logits, end_logits = model(input_ids, attention_mask)
        start_index = torch.argmax(start_logits, dim=1).item()
        end_index = torch.argmax(end_logits, dim=1).item()

    if start_index <= end_index and end_index < len(offsets):
        start_char = offsets[start_index][0]
        end_char = offsets[end_index][1]
        return context[start_char:end_char]
    else:
        return "Unable to find answer."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--question", type=str, required=True)
    parser.add_argument("--context", type=str, required=True)
    args = parser.parse_args()

    config = Config()
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    model = TransformerQA(config, tokenizer).to(config.device)
    model.load_state_dict(torch.load(args.model_path, map_location=config.device))
    model.eval()

    answer = answer_question(model, tokenizer, config, args.question, args.context)
    print("Answer:", answer)
