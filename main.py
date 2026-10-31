from datetime import datetime
from pathlib import Path

from funcionarios_publicos import main_scrapy

if __name__ == "__main__":
    date = datetime.now()
    date_formatted = date.strftime("%Y%m%d")
    output_name = f"funcionarios_publicos_{date_formatted}.csv"
    output_path = Path(__file__).parent / "data" / output_name

    main_scrapy(output_path)
