import extractor
from extractor import searchFolder

'''
    Core file for all parsers
'''

if __name__ == "__main__":
    # Search for all extension files
    folderName = input("Please enter name of folder where you have extensions: ")
    filesFound = searchFolder(folderName)

    # Keep track of all extensions found
    ExtensionsUnpacked = []

    # Unpack every extension found
    for file in filesFound:
        newExtension = extractor.Extension()
        newExtension.extractExtension(file)
        ExtensionsUnpacked.append(newExtension)

    # Example of exsisting extension and calling its name
    extension = ExtensionsUnpacked[0]
    print("First extension was called: ", extension.getName())
