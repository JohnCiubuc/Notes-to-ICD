import pickle


from itertools import compress

# iterate = ["HPI:", "Physical Examination", "Assessment and Plan", "Diagnostic Studies"]
iterate = ['Problem list', 'Differential diagnosis', 'Diagnostic plan', 'Therapeutic plan']


def prune_rubric_entities(entity_list):
    for i,section in enumerate(entity_list):
        compress_list = []
        # print(i)
        # print(section)
        # Section is a dict of the section
        
        for entity in section[list(section.keys())[0]]:
            compress_list.append(entity['enable'])
            
        # compress list    
        section[list(section.keys())[0]] = list(compress(section[list(section.keys())[0]], compress_list))
        entity_list[i] = section
    return entity_list
        


# Generator by https://stackoverflow.com/a/4629770
def iterAllItems(self):
    for i in range(self.count()):
        yield self.item(i)
    
# Simplifies multiple sections into SOAP format
def pruneSections(sections):
    # Fix HPI. Temporary fix as we should have these sections separate
    saveSection = ''
    saveSectionID = 0
    sectionInc = 0
    for i in range(len(sections)):
        section = sections[i]
    # for section in sections:
        if section['trigger']['sectionNormalizedName'].lower() == iterate[0].lower(): #HPI
            saveSection = section
            saveSectionID = i
            sectionInc = 1
        if sectionInc == 1:
            if section['trigger']['sectionNormalizedName'].lower() == iterate[1].lower(): #Physical Examination
                saveSection['end'] = section['begin']-1
                sections[saveSectionID] = saveSection
                saveSectionID = i
                saveSection = section
                sectionInc = 2
        
        if sectionInc == 2:
            if section['trigger']['sectionNormalizedName'].lower() == iterate[2].lower(): #Assessment and Plan
                saveSection['end'] = section['begin']-1
                sections[saveSectionID] = saveSection
                saveSectionID = i
                saveSection = section
                sectionInc = 3
        if sectionInc == 3:
            if section['trigger']['sectionNormalizedName'].lower() == iterate[3].lower(): #Diagnostic Studies
                saveSection['end'] = section['begin']-1
                sections[saveSectionID] = saveSection
                saveSectionID = i
                saveSection = section
                sectionInc = -1
    

    return sections
        
def rearrangeToSections(inputJson):
    if 'dataBySection' in inputJson:
        print("dataBySection already exists. Using existing data structure")
        return inputJson
    # Get sections and concepts
    sections = pruneSections(inputJson['sections'])
    concepts = inputJson['concepts']
    conceptValues = inputJson['conceptValues']
    SymptomDiseaseInd = inputJson['SymptomDiseaseInd']
    insights = inputJson['attributeValues']
    
    # These are the sections we will create
    conceptsBySection = []
    
    # For each section we create
    for i in range(len(iterate)):
        tempDict = {}
        tempConceptList = []
        tempConceptValueList = []
        tempSymptomDiseaseIndList = []
        tempInsightList = []
        tempDict["section"] = iterate[i]
        # Find the related section, if exists
        for section in sections:
            if section['trigger']['sectionNormalizedName'].lower() == iterate[i].lower():
                # print("starting section ", iterate[i].lower())
                sectionBegin = section['begin']
                sectionEnd = section['end']
                # print('preadd')
                bInSection = False
                # For each concept that falls within that section, save it
                # Continue until we hit a concept that isn't in that section
                for concept in concepts:
                    if concept['begin'] >= sectionBegin and concept['end'] <= sectionEnd:
                        tempConceptList.append(concept)

                bInSection = False
                # For each insight that falls within that section, save it
                # Continue until we hit an insight that isn't in that section
                for insight in insights:
                    if insight['begin'] >= sectionBegin and insight['end'] <= sectionEnd:
                        tempInsightList.append(insight)
                        
                
                # For each concept value that falls within that section, save it
                # Continue until we hit an insight that isn't in that section
                for cvalue in conceptValues:
                    if cvalue['begin'] >= sectionBegin and cvalue['end'] <= sectionEnd:
                        tempConceptValueList.append(cvalue)
                
                # For each SymptomDiseaseInd value that falls within that section, save it
                # Continue until we hit an insight that isn't in that section
                for symptom in SymptomDiseaseInd:
                    if symptom['begin'] >= sectionBegin and symptom['end'] <= sectionEnd:
                        tempSymptomDiseaseIndList.append(symptom)
#SymptomDiseaseInd
                    
        # Sort lists then
        # Remove duplications per section
        tempConceptList = sorted(tempConceptList, key=lambda d: d['preferredName']) 
        tempConceptValueList = sorted(tempConceptValueList, key=lambda d: d['preferredName']) 
        tempInsightList = sorted(tempInsightList, key=lambda d: d['preferredName']) 
        tempSymptomDiseaseIndList = sorted(tempSymptomDiseaseIndList, key=lambda d: d['symptomDiseaseNormalizedName']) 
        tempConceptListFixed = []
        tempName = ''
        tempNameList = []
        for i in tempConceptList:
            if tempName.lower() != i['preferredName'].lower():
                # This is not a duplicate entry
                tempName = i['preferredName']
                if tempName not in tempNameList:
                    tempNameList.append(tempName)
                    tempConceptListFixed.append(i)
        tempInsightListFixed = []
        tempName = ''
        for i in tempInsightList:
            if tempName.lower() != i['preferredName'].lower():
                tempName = i['preferredName']
                if tempName not in tempNameList:
                    tempNameList.append(tempName)
                    tempInsightListFixed.append(i)
        
        tempConceptValueListFixed = []
        tempName = ''
        tempNameList = []
        for i in tempConceptValueList:
            if tempName.lower() != i['preferredName'].lower():
                # This is not a duplicate entry
                tempName = i['preferredName']
                if tempName not in tempNameList:
                    tempNameList.append(tempName)
                    tempConceptValueListFixed.append(i)
        
        SymptomDiseaseIndListFixed = []
        tempName = ''
        tempNameList = []
        for i in tempSymptomDiseaseIndList:
            if tempName.lower() != i['symptomDiseaseNormalizedName'].lower():
                # This is not a duplicate entry
                tempName = i['symptomDiseaseNormalizedName']
                if tempName not in tempNameList:
                    tempNameList.append(tempName)
                    SymptomDiseaseIndListFixed.append(i)
        tempDict['concepts'] = tempConceptListFixed
        tempDict['insights'] = tempInsightListFixed
        tempDict['conceptValues'] = tempConceptValueListFixed
        tempDict['SymptomDiseaseInd'] = SymptomDiseaseIndListFixed
        conceptsBySection.append(tempDict)                 
        
    inputJson['dataBySection'] = conceptsBySection
    return inputJson

def printIBM(SymptomDiseaseInd_cont,Sections_cont,Insights_cont,ConceptValues_cont,TemporalValues_cont):
    stringToPrint = 'This note has the following sections:\n'
    line = ''
    for sec in Sections_cont:
        line = line + sec + ', '
    line = line[:-2]
    stringToPrint = stringToPrint + '\t'+line+'\n\nWith the following symptoms:\n'
    for symp in SymptomDiseaseInd_cont:
        stringToPrint = stringToPrint + symp + ', ' + SymptomDiseaseInd_cont[symp] + ' ID: ' + SymptomDiseaseInd_cont['id'] + '\n'

    stringToPrint = stringToPrint + '\nInsights reveal:'
    for con in ConceptValues_cont:
        string = con['insight'] + ", "
        if 'value' in con:
            string = string + con["value"] + ' '
        if 'unit' in con:
            string = string + con["unit"] + ' '
                
        stringToPrint = stringToPrint + string+ ' ID: ' + con['id']  + '\n'
    
    
    stringToPrint = stringToPrint + '\n\nConcept maps reveal the following:\n'
    stringToPrint = stringToPrint + "-----------------------" +'\n'
    concepts = {}
    for con in Insights_cont:
        string = con['insight']
        if 'temporal' in con:
            string = string + " since " + con['temporal'] 
        if con['type'] in concepts:
            concepts[con['type']].append(string)
        else:
            concepts[con['type']] = []
            concepts[con['type']].append(string)
        
        # concepts.append([con['type'],append(string))
    for largeC in concepts:
        stringToPrint = stringToPrint + "Concept: " + largeC + '\n'
        prepend = '';
        if largeC[0:2] == 'No':
            prepend = "There has been no "
        for smallC in concepts[largeC]:
            stringToPrint = stringToPrint + prepend + smallC + '\n'
        stringToPrint = stringToPrint + "-----------------------" +'\n'
    print(stringToPrint)
    return stringToPrint


def loadJsonFromFile(file):
    pickle_off = open(file, 'rb')
    jresponse = pickle.load(pickle_off)

    if 'unstructured' in jresponse:
        jsonTwo = jresponse['unstructured'][0]['data']
    else:
        jsonTwo = jresponse
    pickle_off.close()
    return jsonTwo


def sanitizeIBMDuplicates(inputJson): 
    
    purifier = []
    fixedConcepts = []
    # Sanitize duplicates
    for concept in inputJson['concepts']:
        if 'CTCAE' in concept['preferredName']:
            inputJson['concepts'].remove(concept)
            continue
        if concept['preferredName'] in purifier:
            inputJson['concepts'].remove(concept)
            continue
        else:
            purifier.append(concept['preferredName'])
            fixedConcepts.append(concept)
    
    inputJson['concepts'] = fixedConcepts
    return inputJson