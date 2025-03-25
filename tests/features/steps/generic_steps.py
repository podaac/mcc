from behave import given, when, then
from behave.runner import Context


@given('fail')
@when('fail')
@then('fail')
def fail(context:Context):
    print(f'\r\n===== Fail the test =====')
    assert False, "Intentional fail step for debug"