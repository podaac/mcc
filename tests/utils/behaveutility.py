from behave.runner import Context


class BehaveUtility():
    
    def GetCurrentScenarioID(context:Context) -> str:
        for tag in context.scenario.tags:
            if tag.startswith("TRID_"):
                return tag[6:]
    

    def GetIndexForCurrentTag(context:Context) -> tuple:
        # Get the unique tag of the current test
        scenarioId = BehaveUtility.GetCurrentScenarioID(context)
        currentUniqueTagId = f"TRID_C{scenarioId}"

        # Extract the original tags into a list
        originalTags = str(context._config.tags).split(' ')
        tagIndex = 0
        i = 0
        tagsToAdd = []
        for tag in originalTags:
            tagsToAdd.append(tag)
            if currentUniqueTagId in tag:
                tagIndex = i
            i += 1

        return (tagIndex, tagsToAdd)
