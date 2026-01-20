import extractor, manifest_parser
from extractor import searchFolder

'''
    Core file for all parsers
'''
extensions = {}

if __name__ == "__main__":
    # Search for all extension files
    folderName = input("Please enter name of folder where you have extensions: ")
    filesFound = searchFolder(folderName)

    # Unpack every extension found
    for file in filesFound:
        ext = extractor.Extension()
        ext.extractExtension(file)
        extensions[ext.getName()] = ext

    # Example of exsisting extension and calling its name
    print(extensions)
