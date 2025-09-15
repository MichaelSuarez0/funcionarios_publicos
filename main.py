from _spider_function import main_scrapy
from pathlib import Path
from datetime import datetime

if __name__ == "__main__":
    date = datetime.now()
    date_formatted = date.strftime("%Y%m%d")
    output_path = Path(__file__).parent / "funcionarios" / f"funcionarios_publicos_{date_formatted}.csv"

    main_scrapy(output_path)

