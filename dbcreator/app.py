from dbcreator.extractors import *


class App:

    def __init__(self, filePath):
        self.filePath = filePath


    def run(self, isNEChecked, isNPEChecked):

        text = getContentFromFile(self.filePath)

        entityList = []

        ### Primary Data Sets
        tagged_sentences = getTaggedSentences(text)
        chunked_sentences = getChunkedSentences(tagged_sentences)
        ne_chunked_sentences = getNamedEntities(text)


        ### Extractors List in the Order of Execution
        extractorsList = [PossessionBasedExtractor, RemoveDuplicateEntities, RemoveNonPotentialEntities,
                          RemoveDuplicateAttributes, UniqueKeyExtractor, SuggestRelationshipTypes, IdentifyAttributeDataType]


        for extractor in extractorsList:
            extObject = extractor()

            if isinstance(extObject, PrimaryExtractor):
                extObject.execute(tagged_sents=tagged_sentences, chunked_sents=chunked_sentences, ne_chunked_sents=ne_chunked_sentences, target=entityList, isNEExcluded = isNEChecked)

            elif isinstance(extObject, SecondaryExtractor):
                extObject.execute(entities=entityList, isNPEExcluded = isNPEChecked)


        return entityList


### Main Program Execution

if __name__ == "__main__":
    app = App(filePath='samples/sample1.txt')
    entities = app.run()

    for i, e in enumerate(entities):
        print('Entity: ', e.name())
        print('Candidate Attributes', [x.name() for x in e.attributes])
        print()