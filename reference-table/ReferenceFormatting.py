import re
def VendorMacAddressToCsv():
    infile = open("VendorMacAddress.txt", 'r',encoding="cp1252", errors='ignore')
    outfile = open("VendorMacAddress.csv", 'w', encoding='utf-8', errors='ignore')
    outfile.write("MacAddressPrefix:Vendor\n")
    for line in infile.readlines():
        line = str(line)
        newline= re.sub("\s+", ":", line.strip(),1)
        outfile.write(newline+'\n')
    infile.close()
    outfile.close()
def main():
    VendorMacAddressToCsv()
if __name__ == '__main__':
    main()