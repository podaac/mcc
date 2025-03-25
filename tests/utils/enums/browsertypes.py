from enum import Enum

class BrowserTypes(Enum):
    CHROME = 1
    FIREFOX = 2
    IE = 3
    EDGE = 4
    SAFARI = 5
    NOT_DEFINED = 9

    @staticmethod
    def from_str(label):
        if label.lower() == 'chrome':
            return BrowserTypes.CHROME
        elif label.lower() == 'firefox':
            return BrowserTypes.FIREFOX
        elif label.lower() == 'ie':
            return BrowserTypes.IE
        elif label.lower() == 'edge':
            return BrowserTypes.EDGE
        elif label.lower() == 'safari':
            return BrowserTypes.SAFARI
        elif label.lower().strip() in ['none', '']:
            return BrowserTypes.NOT_DEFINED
        else:
            raise NotImplementedError(f'Browser type "{label}" not implemented')
    