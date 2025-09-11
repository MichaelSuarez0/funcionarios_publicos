from scrapy_cfg.spider_function import scrapear_urls
from pathlib import Path

scrapear_urls(output_path=Path(__file__).parent / "funcionarios.jsonl")

