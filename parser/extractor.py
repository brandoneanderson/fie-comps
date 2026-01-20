import manifest_parser
from crx_unpack import unpack

def extractExtension(filename):
    if '.crx' in filename:
        crx_unpack.unpack
        return print("Omg a crx file, contents are in extensions!\n")
    else:
        return print("Not a valid file\n")

filename = str(input("Please enter the path to the file: "))
extractExtension(filename)