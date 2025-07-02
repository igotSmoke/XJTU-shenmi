import ollama

file_path = 'myd.md'
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()
paragraphs = content.split('##')

for i,paragraph in enumerate(paragraphs):
    print(f'paragraph {i + 1}:\n{paragraph}\n')
    print('-' * 20)



def embedding(text):
    vector = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return vector["embedding"]

text = "openGauss 是一款开源数据库"
emb = embedding(text)
dimensions = len(emb)

print("text: {}, embedding dim : {}, embedding : {}...".format(text, dimensions, emb[:10]))

import psycopg2

table_name = "opengauss_data"
conn = psycopg2.connect(
    database = "db1",
    user="user1",
    password="Test@123",
    host="127.0.0.1",
    port="5432"
)

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS {};".format(table_name))
cur.execute("CREATE TABLE {} (id INT PRIMARY KEY, content TEXT, emb vector({}))".format(table_name,dimensions))
conn.commit()

for i,paragraph in enumerate(paragraphs):
    emb = embedding(paragraph)
    insert_data_sql = f'''INSERT INTO {table_name} (id, content, emb) VALUES (%s, %s, %s);'''
    cur.execute(insert_data_sql, (i, paragraph, emb))
    conn.commit()

cur.execute("CREATE INDEX ON {} USING HNSW (emb vector_l2_ops);".format(table_name))
conn.commit()


question = "openGauss 发布了哪些版本？"

emb_data = embedding(question)
dimensions = len(emb_data)

cur = conn.cursor()
cur.execute("select content from {} order by emb <-> '{}' limit 1;".format(table_name), (emb_data))
conn.commit()

rows = cur.fetchall()
print(rows)

cur.close()
conn.close()

emb_data = embedding(question)
dimensions = len(emb_data)

cur = conn.cursor()
cur.execute("select content from {} order by emb <-> '{}' limit 1;".format(table_name), (emb_data))
conn.commit()

rows = cur.fetchall()
print(rows)

cur.close()
conn.close()

context = "\n".join(row[0] for row in rows)
SYSTEM_PROMPT = "你作为一个对话 AI 助手，结合上下文信息简练高效地回答用户提出的问题"
USER_PROMPT = f"请结合{context}信息来回答{question}的问题，不需要额外的无用回答"


response = ollama.chat(
    model = "deepseek-r1",
    messages = [
        {"role": "user", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
)
print(response["message"]["content"])


USER_PROMPT = f"请回答{question}的问题，不需要额外的无用回答"


response = ollama.chat(
    model = "deepseek-r1",
    messages = [
        {"role": "user", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
)
print(response["message"]["content"])



