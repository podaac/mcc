from utils.testrailhelpers.stepresult import StepResult as SR


class Result():
    case_id:int = 0
    status_id:int = 0
    custom_step_results:SR = []
    elapsed = ""
    version = ""
    comment = ""
    