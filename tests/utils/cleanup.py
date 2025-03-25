from behave.runner import Context
from os import popen

from utils.filehandler import FileHandler


class Cleanup():

    def CleanupAfterRun():
        print(f"\r\nStarting Scenario cleanup...")
        Cleanup.FileCleanup()


    def FileCleanup():
        FileHandler.DeleteTempData()


    def CustomDataCleanup(context:Context):
        print(f"Cleaning up generated custom data...")
        tagGroups = str(context.config.tags).split(' ')
        for tagGroup in tagGroups:
            tags = tagGroup.split(',')
            for tag in tags:
                if tag.__contains__('TRID_C'):
                    if tag.startswith('TRID_'):
                        scenarioId = tag[6:]
                    elif tag.startswith('@'):
                        scenarioId = tag[7:]
                    print(f'Removing custom data for {tag}...')
                    command = f'python3 addCustomTestdata.py -Id {scenarioId}'
                    process = popen(command)
                    process.close()