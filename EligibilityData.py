import datetime
import json
import pandas as pd

Data = open('JsonData1.json')
JsonData = json.load(Data)

Loop2110C = JsonData[0]['Loop2000A'][0]['Loop2000B'][0]['Loop2000C'][0]['Loop2100C']['Loop2110C']
dfList = []
for LoopData in Loop2110C:
    # print(LoopData['EB_SubscriberEligibilityorBenefitInformation'])
    res = LoopData['EB_SubscriberEligibilityorBenefitInformation']

    NewDict = {}

    if res['ServiceTypeCode_03'] != None and len(res['ServiceTypeCode_03']) == 1:
        res['ServiceTypeCode_03'] = res['ServiceTypeCode_03'][0]
    # elif res['ServiceTypeCode_03'] != None and len(res['ServiceTypeCode_03']) > 1:
    #     res['ServiceTypeCode_03'] = res['ServiceTypeCode_03'][-2]
    if LoopData['DTP_SubscriberEligibility_BenefitDate'] != None:
        if '-' in LoopData['DTP_SubscriberEligibility_BenefitDate'][-1]['AccidentDate_03']:
            Date = str(LoopData['DTP_SubscriberEligibility_BenefitDate'][-1]['AccidentDate_03']).split('-')

            StartDate = datetime.datetime.strptime(Date[0], '%Y%m%d').strftime('%m/%d/%Y')
            EndDate = datetime.datetime.strptime(Date[1], '%Y%m%d').strftime('%m/%d/%Y')

            res['Dates'] = str(StartDate)+' - '+str(EndDate)
        else:
            Date = datetime.datetime.strptime(LoopData['DTP_SubscriberEligibility_BenefitDate'][-1]['AccidentDate_03'], '%Y%m%d').strftime('%m/%d/%Y')
            res['Dates'] = str(Date)
    else:
        res['Dates'] = ''
    if LoopData['MSG_MessageText'] != None:
        res['Message'] = LoopData['MSG_MessageText'][-1]['FreeFormMessageText_01']
    else:
        res['Message'] = ''
    # print(res)
    res = dict(res)
    NewDict['Service Type'] = res['ServiceTypeCode_03']
    NewDict['Coverage Type'] = res['BenefitCoverageLevelCode_02']
    NewDict['In Net'] = res['InPlanNetworkIndicator_12']
    NewDict['Auth Req.'] = res['AuthorizationorCertificationIndicator_11']
    NewDict['Benefit'] = res['EligibilityorBenefitInformation_01']
    # if res['TimePeriodQualifier_06'] == None:
    #     NewDict['Benefit Amount'] = str(res['BenefitAmount_07'])
    # elif res['BenefitAmount_07'] == None:
    #     NewDict['Benefit Amount'] = str(res['TimePeriodQualifier_06'])
    if (res['TimePeriodQualifier_06'] == "" or res['TimePeriodQualifier_06'] == None) and res['BenefitAmount_07'] == None:
        if int(float(res['BenefitPercent_08'])) != 0:
            NewDict['Benefit Amount'] = str(int(float(res['BenefitPercent_08']))) +'%'
        else:
            NewDict['Benefit Amount'] = ''
    elif res['BenefitAmount_07'] == None and res['BenefitPercent_08'] == "0":
        NewDict['Benefit Amount'] = str(res['TimePeriodQualifier_06']) +" "+ str(res['BenefitQuantity_10'])
    elif res['BenefitAmount_07'] != None and res['TimePeriodQualifier_06'] != None:
        NewDict['Benefit Amount'] = str(res['TimePeriodQualifier_06']) + " $" + str(res['BenefitAmount_07'])

    NewDict['Dates'] = res['Dates']
    NewDict['Message'] = res['Message']
    # break
    dfList.append(NewDict)

df = pd.DataFrame(dfList)
df.to_excel('EligibilityNew.xlsx', index=False)