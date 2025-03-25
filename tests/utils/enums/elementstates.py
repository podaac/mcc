from enum import Enum

class ElementStates(Enum):
    HIDDEN = 1
    VISIBLE = 2
    INACTIVE = 3
    CLICKABLE = 4

    @staticmethod
    def from_str(stateName):
        if stateName.lower() == "hidden" or \
            stateName.lower() == "invisible":
            return ElementStates.HIDDEN
        elif stateName.lower() == "visible":
            return ElementStates.VISIBLE
        elif stateName.lower() == "inactive":
            return ElementStates.INACTIVE
        elif stateName.lower() == "clickable" or \
            stateName.lower() == "active":
            return ElementStates.CLICKABLE
        else:
            NotImplemented