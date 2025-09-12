from scrapy.exporters import CsvItemExporter

class SemiColonCsvItemExporter(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("delimiter", ";")
        kwargs.setdefault("encoding", "utf-8")
        super().__init__(*args, **kwargs)