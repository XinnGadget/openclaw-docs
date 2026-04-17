import glob
import os
from pathlib import Path
from dotenv import load_dotenv

import openai

load_dotenv()

YANDEX_CLOUD_FOLDER = os.environ.get("YANDEX_CLOUD_FOLDER")
YANDEX_CLOUD_API_KEY = os.environ.get("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_MODEL = os.environ.get("YANDEX_CLOUD_MODEL", "aliceai-llm/latest")

DOCS_DIR = Path(os.environ.get("DOCS_DIR", r".\openclaw-docs\docs"))
RU_DOCS_DIR = Path(DOCS_DIR, "ru")

DIRS = [
    'automation',
    'channels',
    'concepts',
    'debug',
    'diagnostics',
    'gateway',
    'help',
    'install',
    'nodes',
    'platforms',
    'plugins',
    'providers',
    'refactor',
    'reference',
    'security',
    'start',
    'tools',
    'web'
]

client = openai.OpenAI(
  api_key=YANDEX_CLOUD_API_KEY,
  base_url="https://ai.api.cloud.yandex.net/v1",
  project=YANDEX_CLOUD_FOLDER
)

with open('sys.md', 'r', encoding='utf-8') as f:
    sys_prompt = f.read()


for dir in DIRS:
    Path(RU_DOCS_DIR, dir).mkdir(exist_ok=True)
    md_files = glob.glob(os.path.join(DOCS_DIR, dir, "*.md"))
    
    for md_file in md_files:
        md_file_relative_path = Path(md_file).relative_to(DOCS_DIR)
        
        print(f"Обрабатываю {md_file_relative_path}")
 
        with open(md_file, "r", encoding="utf-8") as f:
            prompt = f.read()
 
        try:
            response = client.responses.create(
              model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
              temperature=0.3,
              instructions=sys_prompt,
              input=f"{prompt}",
            )
        except openai.BadRequestError as e:
            print(f"Ошибка при переводе файла {md_file_relative_path}")
        
        with open(Path(RU_DOCS_DIR, md_file_relative_path), 'w', encoding='utf-8') as f:
            f.write(response.output_text)
        