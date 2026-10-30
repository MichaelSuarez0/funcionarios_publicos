from datetime import datetime
from pathlib import Path

from _spider_function import main_scrapy

if __name__ == "__main__":
    date = datetime.now()
    date_formatted = date.strftime("%Y%m%d")
    output_path = (
        Path(__file__).parent
        / "funcionarios"
        / f"funcionarios_publicos_{date_formatted}.csv"
    )

    main_scrapy(output_path)
