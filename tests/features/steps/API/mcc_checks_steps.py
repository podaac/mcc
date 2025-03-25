from behave import when
from behave.runner import Context

from API.MCC.check import Check

from config.globalvariables import GlobalVariables


# File wide variables
globalvars = GlobalVariables

@when('GET checks by MCC /check endpoint')
def step_impl(context:Context):
    print(f'\r\n===== GET checks by MCC /check endpoint =====')

    globalvars.ResponseToCheck = Check.GetCheck()


@when('POST "{uploadFileLocation}" file by MCC /check endpoint with Checkers "{checkerListString}" for "{responseTypeString}" response')
def uploadFileWithAllChecks(context:Context, uploadFileLocation:str, checkerListString:str, responseTypeString:str):
    print(f'\r\n===== POST "{uploadFileLocation}" file by MCC /check endpoint with Checkers "{checkerListString}" for "{responseTypeString}" response =====')

    if uploadFileLocation.lower() in ['nc', '.nc', 'default']:
        fileLocation = './data/ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc'
    elif uploadFileLocation.lower() in ['gz', '.gz']:
        fileLocation = './data/ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc.gz'
    elif uploadFileLocation.lower() in ['bz2', '.bz2']:
        fileLocation = './data/ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc.bz2'
    elif uploadFileLocation.lower() in ['h5', '.h5']:
        fileLocation = './data/tdset.h5'
    elif uploadFileLocation.lower() in ['nc4', '.nc4']:
        fileLocation = './data/windsat_remss_ovw_l3_20040102_v7.0.1.nc.gz.nc4'
    elif uploadFileLocation.lower() in ['hdf', '.hdf']:
        fileLocation = './data/20160101-NCDC-L4LRblend-GLOB-v01-fv02_0-AVHRR_OI.nc'
    elif uploadFileLocation.lower() in ['none']:
        fileLocation = None
    else:
        fileLocation = uploadFileLocation.strip(' ')
    
    if responseTypeString.lower() in ['none']:
        responseType = None
    else:
        responseType = responseTypeString.strip(' ')

    acdd_enbled = False
    acdd_Version = None
    cf_enabled = False
    cf_Version = None
    gds2_enbled = False
    gds2_Version = None
    newestVersion = ['1.3', '1.7', 'L4']
    oldestVersion = ['1.1', '1.6', 'L2P']

    checkerListRaw = checkerListString.strip(' ').split(',')
    for checkerPairRaw in checkerListRaw:
        checkerPair = checkerPairRaw.split(':')
        checker = checkerPair[0].strip(' ')
        if len(checkerPair) > 1:
            checkerVersion = checkerPair[1].strip(' ')
        elif len(checkerPair) == 1:
            checkerVersion = None
        
        if checker.lower() in ['acdd', 'all', 'acdd-none']:
            if checker.lower() == 'acdd-none':
                acdd_enbled = None
            else:
                acdd_enbled = True
            if checkerVersion in ['newest']:
                acdd_Version = newestVersion[0]
            elif checkerVersion in ['oldest']:
                acdd_Version = oldestVersion[0]
            else:
                acdd_Version = checkerVersion
        if checker.lower() in ['cf', 'all', 'cf-none']:
            if checker.lower() == 'cf-none':
                cf_enabled = None
            else:
                cf_enabled = True
            if checkerVersion in ['newest']:
                cf_Version = newestVersion[1]
            elif checkerVersion in ['oldest']:
                cf_Version = oldestVersion[1]
            else:
                cf_Version = checkerVersion
        if checker.lower() in ['gds2', 'all', 'gds2-none']:
            if checker.lower() == 'gds2-none':
                gds2_enbled = None
            else:
                gds2_enbled = True
            if checkerVersion in ['newest']:
                gds2_Version = newestVersion[2]
            elif checkerVersion in ['oldest']:
                gds2_Version = oldestVersion[2]
            else:
                gds2_Version = checkerVersion
        if checker.lower() == '':
            continue

    print(f'acdd_enbled: "{acdd_enbled}"')
    print(f'acdd_Version: "{acdd_Version}"')
    print(f'cf_enabled: "{cf_enabled}"')
    print(f'cf_Version: "{cf_Version}"')
    print(f'gds2_enbled: "{gds2_enbled}"')
    print(f'gds2_Version: "{gds2_Version}"')
    print(f'fileLocation: "{fileLocation}"')
    print(f'responseType: "{responseType}"')
    globalvars.ResponseToCheck = Check.PostCheck(
        fileLocation = fileLocation,
        responseType = responseType,
        useChecker_ACDD = acdd_enbled,
        acdd_Version = acdd_Version,
        useChecker_CF = cf_enabled,
        cf_Version = cf_Version,
        useChecker_GDS2 = gds2_enbled,
        gds2_Version = gds2_Version)
