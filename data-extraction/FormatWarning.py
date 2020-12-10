import sys
import os
from os import listdir
from FormatInfo import get_dir,format_mac,remove_duplicate_line
import pandas as pd

def FormatAPMtChlIntf(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "hh3cDot11APMtChlIntfDetected"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-warning-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-warning-formatted/"
        outfile_path = r"../sortlog/" + dirtory + "/" + dirtory + "-warning-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting " + "status" + " File: ", dirtory + "-" + status + ".csv")

        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)

        df = pd.read_csv(infile_path, engine='python', header=None)

        #Drop Extra Column & rename columns
        to_drop = [1,2,3,4,5,6,7,8,10,12]
        df.drop(to_drop, inplace=True, axis=1)
        df=df.rename(columns={0: "Time", 9: "APSerialId",11: "RadioId",13: "ChannelNumber",})

        #Format Columns
        df["APSerialId"]=df["APSerialId"].str.replace("Id:", '')
        df["RadioId"]=df["RadioId"].str.replace("id:", '')
        df["ChannelNumber"]=df["ChannelNumber"].str.replace("Number:", '')

        #Create new columns
        df.insert(1, "StatusCode", "hh3cDot11APMtChlIntfDetected", True)

        #Change data types to optimze storage space
        df = df.astype({"RadioId": int, "ChannelNumber": int})

        # Output CSV to destination directory
        if  len(df)>1000000:
            df_new1 = df.iloc[:500000, :]
            df_new2 = df.iloc[500000:, :]
            df_new1.to_csv(outfile_path, index=None, header=True)
            df_new2.to_csv(outfile_path, index=None, header=False,mode='a')
        else:
            df.to_csv(outfile_path, index = None, header=True)

def FormatStationDeAssocTrap(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "hh3cDot11StationDeAssocTrap"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-warning-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-warning-formatted/"
        outfile_path = r"../sortlog/" + dirtory + "/" + dirtory + "-warning-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting " + "status" + " File: ", dirtory + "-" + status + ".csv")

        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserMacAddress,Username,VLANId,RadioId,SSID,SessionDuration,APID,Location,APMacAddress\n")
        for line in infile.readlines():
            splitline = line.split(',')
            newline = []
            newline.append(splitline[0])  # Time
            newline.append("StationDeAssocTrap") # StatusCode

            UserMacAddress = "NaN"
            Username = "NaN"
            VLANId = "NaN"
            RadioId = "NaN"
            SSID = "NaN"
            SessionDuration = "NaN"
            APID = "NaN"
            Location = "NaN"
            APMacAddress = "NaN"
            UserMacAddress = splitline[4].replace('StaMac1:', '')

            line = ','.join(splitline[4:]).strip('\n')
            if "UserName:" in line:
                pos = line.find("UserName:")
                comma = line.find(",StaMac3:", pos)
                Username = line[pos:comma]
                Username = Username.replace('UserName:', '')
                Username = Username.replace(',', ' ')

            if "VLANId:" in line:
                pos = line.find("VLANId:")
                comma = line.find(",", pos)
                VLANId = line[pos:comma]
                VLANId = VLANId.replace('VLANId:', '')

            if "Radioid:" in line:
                pos = line.find("Radioid:")
                comma = line.find(",", pos)
                RadioId = line[pos:comma]
                RadioId = RadioId.replace('Radioid:', '')

            line = ','.join(splitline[10:]).strip('\n')
            if "Universities" in line:
                SSID = "Universities WiFi"
            elif "Wi-Fi" in line:
                SSID = "Wi-Fi.HK via HKU"
            elif "eduroam" in line:
                SSID = "eduroam"
            elif "HKU" in line:
                SSID = "HKU"
            elif "Y5ZONE" in line:
                SSID = "Y5ZONE"
            elif "CSL" in line:
                SSID = "CSL Auto Connect"
            else:
                print("Line not being handled: ")
                print(line)

            if "SessionDuration" in line:
                pos = line.find("SessionDuration:")
                comma = line.find(",", pos)
                SessionDuration = line[pos:comma]
                SessionDuration = SessionDuration.replace('SessionDuration:', '')

            if "APID" in line:
                pos = line.find("APID:")
                comma = line.find(",", pos)
                APID = line[pos:comma]
                APID = APID.replace('APID:', '')

            if "AP,Name" in line:
                pos = line.find("AP,Name:")
                comma = line.find(",", pos+3)
                Location = line[pos:comma]
                Location = Location.replace('AP,Name:', '')

            if "BSSID" in line:
                pos = line.find("BSSID:")
                APMacAddress = line[pos:]
                APMacAddress = APMacAddress.replace('BSSID:', '')

            newline.append(UserMacAddress)
            newline.append(Username)
            newline.append(VLANId)
            newline.append(RadioId)
            newline.append(SSID)
            newline.append(SessionDuration)
            newline.append(APID)
            newline.append(Location)
            newline.append(APMacAddress)

            outfile.write(",".join(newline).strip('\n') + '\n')
        infile.close()
        outfile.close()
        remove_duplicate_line(outfile_path, column=['Time', 'UserMacAddress'])

def main():
    if len(sys.argv) == 2:
        root_dir = sys.argv[1]
        source_path = root_dir + "sortlog/"
        #FormatAPMtChlIntf(source_path)
        FormatStationDeAssocTrap(source_path)
    else:
        print("Invalid input format. Please enter \"python FormatInfo.py [root directory]\"")

if __name__ == '__main__':
    main()

