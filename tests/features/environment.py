from behave.model import Feature

from hooks.afterTests import AfterTestHooks
from hooks.beforeTests import BeforeTestHooks


def before_all(context):
    BeforeTestHooks.before_all(context)
    print("Finished: before-all")

def before_feature(context, feature:Feature):
    BeforeTestHooks.before_feature(context, feature)
    print("Finished: before-feature")

def before_scenario(context, scenario):
    BeforeTestHooks.before_scenario(context, scenario)
    print("Finished: before-scenario")

def after_all(context):
    AfterTestHooks.after_all(context)
    print("Finished: after-all")

def after_feature(context, feature:Feature):
    AfterTestHooks.after_feature(context, feature)
    print("Finished: after-feature")

def after_scenario(context, scenario):
    AfterTestHooks.after_scenario(context, scenario)
    print("Finished: after-scenario")