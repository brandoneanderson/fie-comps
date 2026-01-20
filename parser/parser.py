import extractor

'''
    Core file for all parsers
'''

if __name__ == "__main__":
    Extension = extractor.Extension()
    Extension.extractExtension()
    print(Extension.getFolderPath())
    print(Extension.getManifestPath())
    print(Extension.getIndexPath())