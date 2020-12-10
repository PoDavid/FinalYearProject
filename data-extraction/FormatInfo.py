import sys
import os
from os import listdir
import pandas as pd

def remove_duplicate_line(file,column=None, keep='first'):
    #Remove duplicate line using pandas
    print("Removing Duplicate Line")
    df = pd.read_csv(file, engine='python')
    df.drop_duplicates(subset=column, inplace=True)
    df.to_csv(file, header=True, index=None, na_rep='NaN')

def format_mac(mac):
    #Covert xxxx-xxxx-xxxx to xx:xx:xx:xx:xx:xx
    if '-' in mac:
        mac = mac.replace('-', '')
        mac = ':'.join(mac[i:i + 2] for i in range(0, 12, 2))
    return mac
def get_dir(path):
    dirs = []
    if os.path.isdir(path):
        for file in listdir(path):
            if os.path.isdir(path+file):
                dirs.append(file)
        if dirs:
            print("Detected Log File: \n")
            for dir in dirs:
                print(dir)
        else:
            print("No  Directory in sortlog/")
    else:
        print("Directory Not Found.")
    return dirs

def FormatSucessfulLogin(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "successfully"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting Successfully Login File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserName,UserMacAddress,SSID,APID,BSSID\n")
        for line in infile.readlines():
            splitline = line.split(',')
            newline=[]
            if splitline[1] == "Client":
                newline.append(splitline[0]) #Time
                newline.append("Successfully Join") #Status Code
                newline.append("NaN") # UserName
                newline.append(format_mac(splitline[2]).upper())
                if "Universities" in line:
                    newline.append("Universities WiFi")  # SSID
                    newline.append(splitline[11])#APID
                    newline.append(format_mac(splitline[14].replace('.','')).upper()) #BSSID
                elif "Wi-Fi" in line:
                    newline.append("Wi-Fi.HK via HKU")  # SSID
                    newline.append(splitline[12])  # APID
                    newline.append(format_mac(splitline[15].replace('.','')).upper()) #BSSID
                elif "eduroam" in line:
                    newline.append("eduroam")  # SSID
                    newline.append(splitline[10])  # APID
                    newline.append(format_mac(splitline[13].replace('.','')).upper()) #BSSID
                elif "HKU" in line:
                    newline.append("HKU")  # SSID
                    newline.append(splitline[10])  # APID
                    newline.append(format_mac(splitline[13].replace('.','')).upper()) #BSSID
                elif "Y5ZONE" in line:
                    newline.append("Y5ZONE")  # SSID
                    newline.append(splitline[10])  # APID
                    newline.append(format_mac(splitline[13].replace('.','')).upper()) #BSSID
                elif "CSL" in line:
                    newline.append("CSL Auto Connect")  # SSID
                    if "Auto" in line:
                        newline.append(splitline[12])  # APID
                        newline.append(format_mac(splitline[15].replace('.','')).upper()) # BSSID
                    else:
                        newline.append(splitline[10])  # APID
                        newline.append(format_mac(splitline[13].replace('.','')).upper()) #BSSID
                else:
                    print("Line not being handled: ")
                    print(line)
                    continue
            else:
                UserName = "NaN"
                MacAddress = "NaN"
                SSID = "NaN"
                APID = "NaN"
                BSSID = "NaN"
                #SSID
                if "SSID=" in line:
                    pos = line.find("SSID=") + 5
                    dashpos = line.find("-", pos)
                    SSID = line[pos:dashpos]
                    SSID = SSID.replace(',',' ')
                # Mac Address
                if "MACAddr=" in line:
                    pos = line.find("MACAddr=") + 8
                    dashpos = line.find("-", pos)
                    MacAddress = line[pos:dashpos]
                    MacAddress = MacAddress.replace(',', ' ').upper()
                # User Name
                if "UserName=" in line:
                    pos = line.find("UserName=") + 9
                    colonpos = line.find(";", pos)
                    dashpos = line.find("-", pos)
                    if colonpos > dashpos and dashpos!= -1:
                        UserName = line[pos:dashpos]
                    else:
                        UserName = line[pos:colonpos]
                    UserName = UserName.replace(',', ' ')

                newline.append(splitline[0])  # Time
                newline.append("Successfully Join")  # Status Code
                newline.append(UserName)  # UserName
                newline.append(MacAddress)  #User Mac Address
                newline.append(SSID)  # SSID
                newline.append(APID)  # APID
                newline.append(BSSID)  # BSSID

            outfile.write(",".join(newline).strip('\n')+'\n')
        infile.close()
        outfile.close()
        remove_duplicate_line(outfile_path, column=['Time','UserMacAddress'])

def FormatAuthtication(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "authetication"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting Authentication File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserName,UserMacAddress,VLanID\n")
        for line in infile.readlines():
            splitline = line.split(',')
            newline=[]
            #print(splitline)
            newline.append(splitline[0])  # Time
            newline.append("Failed Authentication")

            line = splitline[1]
            UserName = "NaN"
            MacAddress = "NaN"
            VLanID = "NaN"
            # User Name
            if "UserName=" in line:
                pos = line.find("UserName=") + 9
                colonpos = line.find(";", pos)
                UserName = line[pos:colonpos]
                UserName = UserName.replace(',', ' ')
                if UserName == "NULL":
                    UserName = "NaN"

            if "MACAddr=" in line:
                pos = line.find("MACAddr=") + 8
                dashpos = line.find("-", pos)
                MacAddress = line[pos:dashpos]
                MacAddress = MacAddress.replace(',', ' ').upper()

            if "VlanId=" in line:
                pos = line.find("VlanId=") + 7
                dashpos = line.find("-", pos)
                VLanID = line[pos:dashpos]
                VLanID = VLanID.replace(',', ' ').upper()

            newline.append(UserName)
            newline.append(MacAddress)
            newline.append(VLanID)

            outfile.write(",".join(newline).strip('\n') + '\n')
        infile.close()
        outfile.close()
def FormatRoamed(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "roamed"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting Roamed File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserMacAddress,FromMacAddress,FromAPID,ToMacAddress,ToAPID\n")
        missing_field = []
        for line in infile.readlines():
            splitline = line.split(',')
            newline = []
            newline.append(splitline[0])  # Time
            newline.append("Roamed") # StatusCode
            if len(splitline) != 22:
                missing_field.append(line)
                continue
            newline.append(format_mac(splitline[2]).upper()) # UserMacAddress
            newline.append(format_mac(splitline[9]).upper()) # FromMacAddress
            newline.append(splitline[6]) # FromAPID
            newline.append(format_mac(splitline[18]).upper()) # ToMacAddress
            newline.append(splitline[15]) # ToAPID

            outfile.write(",".join(newline).strip('\n') + '\n')
        if missing_field:
            print("Error Lines: ")
            for line in missing_field:
                print(line)
                print("\n")
        infile.close()
        outfile.close()

def FormatDisconnected(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "disconnected"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting Disconnected File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserMacAddress,SSID,ReasonCode\n")
        for line in infile.readlines():
            splitline = line.split(',')
            newline = []
            newline.append(splitline[0])  # Time
            newline.append("Disconnected") # StatusCode
            newline.append(format_mac(splitline[2]).upper()) #APID
            if "Universities" in line:
                newline.append("Universities WiFi")  # SSID
                newline.append(format_mac(splitline[11].replace('.', '')).upper())  # Reason Code
            elif "Wi-Fi" in line:
                newline.append("Wi-Fi.HK via HKU")  # SSID
                newline.append(format_mac(splitline[12].replace('.', '')).upper())  # Reason Code
            elif "eduroam" in line:
                newline.append("eduroam")  # SSID
                newline.append(format_mac(splitline[10].replace('.', '')).upper())  # Reason Code
            elif "HKU" in line:
                newline.append("HKU")  # SSID
                newline.append(format_mac(splitline[10].replace('.', '')).upper())  # Reason Code
            elif "Y5ZONE" in line:
                newline.append("Y5ZONE")  # SSID
                newline.append(format_mac(splitline[10].replace('.', '')).upper())  # Reason Code
            elif "CSL" in line:
                newline.append("CSL Auto Connect")  # SSID
                if "Auto" in line:
                    newline.append(format_mac(splitline[12].replace('.', '')).upper())  # Reason Code
                else:
                    newline.append(format_mac(splitline[10].replace('.', '')).upper())  # Reason Code
            else:
                print("Line not being handled: ")
                print(line)
                continue
            outfile.write(",".join(newline).strip('\n') + '\n')

        infile.close()
        outfile.close()


def FormatSecureLogoff(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "hh3cSecureLogoff"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting SecureLogoff File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserMacAddress,UserName,PortNum,Cause,VLANID,VLANList\n")

        missing_field = []
        for line in infile.readlines():
            splitline = line.split(',')
            newline = []
            newline.append(splitline[0])  # Time
            newline.append("hh3cSecureLogoff")  # StatusCode
            if len(splitline) != 25:
                missing_field.append(line)
                continue
            newline.append(format_mac(splitline[13]).upper())  # UserMacAddress
            newline.append(splitline[20]) # Username
            newline.append(splitline[18]) # PortNum
            newline.append(splitline[22]) # Cause
            newline.append(splitline[16]) # VLANDID
            newline.append(splitline[24])  # VLANLIST

            outfile.write(",".join(newline).strip('\n') + '\n')
        if missing_field:
            print("Error Lines: ")
            for line in missing_field:
                print(line)
                print("\n")

        infile.close()
        outfile.close()

def FormatLogged(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "logged"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting UserLoggedOff(logged) File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserMacAddress,UserName,VLANID\n")
        for line in infile.readlines():
            splitline = line.split(',')
            newline = []
            newline.append(splitline[0])  # Time
            newline.append("User logged off")  # StatusCode

            UserMacAddress = "NaN"
            UserName = "NaN"
            VLANID = "NaN"
            if "MACAddr" in line:
                pos = line.find("MACAddr=") + 8
                dash = line.find("-", pos)
                UserMacAddress = line[pos:dash]
                UserMacAddress = UserMacAddress.replace(',', ' ')
                if UserMacAddress == "NULL":
                    UserMacAddress = "NaN"
            if "UserName" in line:
                pos = line.find("UserName=") + 9
                dash = line.find("-", pos)
                UserName = line[pos:dash]
                UserName = UserName.replace(',', ' ')
                if UserName == "NULL":
                    UserName = "NaN"
            if "VlanId" in line:
                pos = line.find("VlanId=") + 7
                dash = line.find("-", pos)
                VLANID = line[pos:dash]
                VLANID = VLANID.replace(',', ' ')
                if VLANID == "NULL":
                    VLANID = "NaN"
            newline.append(UserMacAddress)
            newline.append(UserName)
            newline.append(VLANID)

            outfile.write(",".join(newline).strip('\n') + '\n')
        infile.close()
        outfile.close()
        remove_duplicate_line(outfile_path, column=['Time', 'UserMacAddress'], keep='last')

def FormatWasTerminated(path):
    dirs = get_dir(path)
    if not dirs:
        return
    status = "was,terminated"
    for dirtory in dirs:
        infile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-clean/" + dirtory + "-" + status + ".csv"
        out_dir = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/"
        outfile_path = "../sortlog/" + dirtory + "/" + dirtory + "-info-formatted/" + dirtory + "-" + status + "-formatted.csv"
        print("Formatting Was Terminated File: ", dirtory + "-" + status + ".csv")

        infile = open(infile_path, 'r')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        outfile = open(outfile_path, 'w')
        outfile.write("Time,StatusCode,UserMacAddress,UserName,VLANID\n")
        for line in infile.readlines():
            splitline = line.split(',')
            newline = []
            newline.append(splitline[0])  # Time
            newline.append("User was terminated")  # StatusCode

            UserMacAddress = "NaN"
            UserName = "NaN"
            VLANID = "NaN"
            if "MACAddr" in line:
                pos = line.find("MACAddr=") + 8
                dash = line.find("-", pos)
                UserMacAddress = line[pos:dash]
                UserMacAddress = UserMacAddress.replace(',', ' ')
                if UserMacAddress == "NULL":
                    UserMacAddress = "NaN"
            if "UserName" in line:
                pos = line.find("UserName=") + 9
                dash = line.find("-", pos)
                UserName = line[pos:dash]
                UserName = UserName.replace(',', ' ')
                if UserName == "NULL":
                    UserName = "NaN"
            if "VlanId" in line:
                pos = line.find("VlanId=") + 7
                dash = line.find("-", pos)
                VLANID = line[pos:dash]
                VLANID = VLANID.replace(',', ' ')
                if VLANID == "NULL":
                    VLANID = "NaN"

            newline.append(UserMacAddress)
            newline.append(UserName)
            newline.append(VLANID)

            outfile.write(",".join(newline).strip('\n') + '\n')
        infile.close()
        outfile.close()
        remove_duplicate_line(outfile_path, column=['Time', 'UserMacAddress'])

def CombineDisconnection(path):
    dirs = get_dir(path)
    if not dirs:
        return
    for dir in dirs:
        print("Combining Disconnected Files in Dir: ", dir)
        # Load in Disconnected File
        disconnected_file = "../sortlog/" + dir + "/" + dir + "-info-formatted/" + dir + "-disconnected-formatted.csv"
        logged_file = "../sortlog/" + dir + "/" + dir + "-info-formatted/" + dir + "-logged-formatted.csv"
        terminated_file = "../sortlog/" + dir + "/" + dir + "-info-formatted/" + dir + "-was,terminated-formatted.csv"
        securelog_file = "../sortlog/" + dir + "/" + dir + "-info-formatted/" + dir + "-hh3cSecureLogoff-formatted.csv"

        discon_df = pd.read_csv(disconnected_file, engine='python')
        logged_df = pd.read_csv(logged_file, engine='python')
        term_df = pd.read_csv(terminated_file, engine='python')
        securelog_df = pd.read_csv(securelog_file, engine='python')

        # Drop the StatusCode columns in each dataframe
        discon_df = discon_df.drop('StatusCode', axis=1)
        logged_df = logged_df.drop('StatusCode', axis=1)
        securelog_df = securelog_df.drop('StatusCode', axis=1)
        term_df = term_df.drop('StatusCode', axis=1)

        # Outer join all 4 files related to disconnection
        joined_df = pd.merge(discon_df, logged_df, how='outer', on=['UserMacAddress', 'Time'])
        joined_df = pd.merge(joined_df, securelog_df, how='outer', on=['UserMacAddress', 'Time', 'UserName', 'VLANID'])
        joined_df = pd.merge(joined_df, term_df, how='outer', on=['UserMacAddress', 'Time', 'UserName', 'VLANID'])
        joined_df.sort_values(by="Time")
        print(joined_df.head(20))

        # Output the joined dataframe to csv
        outfile="../sortlog/" + dir + "/" + dir + "-info-formatted/" + dir + "-disconnection-formatted.csv"
        joined_df.to_csv(outfile, index=None, header=True, na_rep='NaN')

def main():
    if len(sys.argv) == 2:
        root_dir = sys.argv[1]
        source_path = root_dir + "sortlog/"
        #FormatSucessfulLogin(source_path)
        #FormatAuthtication(source_path)
        #FormatRoamed(source_path)
        #FormatDisconnected(source_path)
        #FormatSecureLogoff(source_path)
        # FormatLogged(source_path)
        # FormatWasTerminated(source_path)
        CombineDisconnection(source_path)
    else:
        print("Invalid input format. Please enter \"python FormatInfo.py [root directory]\"")

if __name__ == '__main__':
    main()