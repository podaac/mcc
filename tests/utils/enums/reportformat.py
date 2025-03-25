from enum import Enum

class ReportFormat(Enum):
    HTML = 1
    PDF = 2
    JSON = 3

    @staticmethod
    def from_str(formatName):
        if formatName.lower() == "web page" or \
            formatName.lower() == "html":
            return ReportFormat.HTML
        elif formatName.lower() == "pdf":
            return ReportFormat.PDF
        elif formatName.lower() == "json":
            return ReportFormat.JSON
        else:
            NotImplemented