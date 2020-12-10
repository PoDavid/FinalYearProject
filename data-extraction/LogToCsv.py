from os import listdir
from os.path import isfile, join
import sys
import os
import shutil
import operator

def create_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        return True
    else:
        return False

def create_or_clean_dir(dir):
    if not create_dir(dir):
        shutil.rmtree(dir)

def split_by_log_level(dir, path):
    if os.path.isdir(path):
        files = [file for file in listdir(path) if isfile(join(path, file))]
        if files:
            print("Detected Log File: \n")
            for file in files:
                print(file)
        else:
            print("No log file in orilog/")
            return
    else:
        print("Directory Not Found.")
        return

    outpath= dir + '/sortlog'
    create_dir(outpath)
    try:
        logfiles = [file for file in listdir(path) if isfile(join(path, file))]
        typeset=set()

        for logfile in logfiles:
            others=[]
            flag=True
            line_count={"readline":0, "warning":0, "notice":0, "info":0}
            print("Sorting File: ", logfile)
            current_log_path = outpath + "/" + logfile.replace(".log", "")
            create_dir(current_log_path)
            warning_file = open(current_log_path + "/" + logfile.replace(".log","-warning.log"), "w", errors='ignore')
            notice_file = open(current_log_path + "/" + logfile.replace(".log","-notice.log"), "w", errors='ignore')
            info_file = open(current_log_path + "/" + logfile.replace(".log","-info.log"), "w", errors='ignore')
            infile = open(path+logfile, "r", encoding="utf-8", errors='ignore')

            #Handle the log line by line
            for line in infile.readlines():
                line = str(line)
                splitline = line.split()
                if flag:
                    date = " ".join([splitline[i] for i in [0,1,3]])
                    ip = splitline[5]
                    model = splitline[6]
                    flag = False

                if splitline[4] not in typeset:
                    typeset.add(splitline[4])

                if splitline[4] == 'warning':
                    for x in [6,5,4,3,1,0]:
                        splitline.pop(x)
                    if len(splitline)>=2:
                        warning_file.write(','.join(splitline)+'\n')
                        line_count["warning"] = line_count["warning"] + 1

                elif splitline[4] == 'notice':
                    for x in [6,5,4,3,1,0]:
                        splitline.pop(x)
                    notice_file.write(','.join(splitline)+'\n')
                    line_count["notice"] = line_count["notice"] + 1

                elif splitline[4] == 'info':
                    for x in [6,5,4,3,1,0]:
                        splitline.pop(x)
                    info_file.write(','.join(splitline)+'\n')
                    line_count["info"] = line_count["info"] + 1

                else:
                    others.append(','.join(splitline)+'\n')
                line_count["readline"] = line_count["readline"] + 1
                if line_count["readline"] % 1000000 == 0:
                    print("Reading the %d millionth line." % int(line_count["readline"] / 1000000))

            warning_file.close()
            notice_file.close()
            info_file.close()
            #Handle Unexpected Cases
            if len(others)>0:
                others_file = open(current_log_path + "/"+logfile.replace(".log","-others.log"), "w", errors='ignore')
                for line in others:
                    others_file.write(line)
                others_file.close()

            #Generate Statistical File
            stat_file = open(current_log_path + "/"+logfile.replace(".log","-statistic.txt"), "w")
            stat_file.write("Source File: " + logfile + "\n\nInfo:\n")
            stat_file.write("Date: " + date + "\n")
            stat_file.write("IP: " + ip + "\n")
            stat_file.write("Model: " + model + "\n\n")
            stat_file.write("Statistics:\n")
            total_line=0
            for type, count in line_count.items():
                if type == "readline":
                    total_line=count
                else:
                    stat_file.write(type+": "+str(count)+ " (" + str(round(count/int(total_line)*100,2)) + "%)"'\n')
            stat_file.write("Total lines: "+str(total_line)+'\n')
            stat_file.close()

    except Exception as err:
        print(err)

def sort_status_code(path, dict):
    sorted_dict = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
    file = open(path,"w")
    for status, num in sorted_dict:
        file.write(status+"\n")

def prepare_csv(path, level):
    level ="-" + level
    if os.path.isdir(path):
        dirs=[]
        for file in listdir(path):
            if os.path.isdir(path+file):
                dirs.append(file)
        if dirs:
            print("Detected Log File: \n")
            for dir in dirs:
                print(dir)
        else:
            print("No  Directory in sortlog/")
            return
    else:
        print("Directory Not Found.")
        return

    #Get all Status Code from Status Code File
    StatusCode_path = path + "/StatusCode" + level
    StatusCodeFile = open(StatusCode_path, "r")
    StatusCodeList = []
    for line in StatusCodeFile.readlines():
        StatusCodeList.append(line.strip("\n"))
    StatusCodeFile.close()
    if len(StatusCodeList) == 0:
        print("Empty Status Code File")
        return

    #Clean all loglevel-other.log
    for dir in dirs:
        log_path = path + dir + "/" + dir + level + "-clean" + "/" + dir + level + "-other.log"
        if os.path.exists(log_path):
            os.remove(log_path)

    for dir in dirs:
        dir_path = path + dir + "/" + dir + level + "-clean/"
        infile_name = dir + level + ".log"
        create_dir(dir_path)

        #Copy warning.log to *-warning-clean/
        if not os.path.isfile(dir_path + infile_name):
            shutil.copy(path + dir + "/" + infile_name, dir_path)
        if os.path.isfile(dir_path + dir + level + "-cleaning.log"):
            os.remove(dir_path + dir + level + "-cleaning.log")

        os.rename(dir_path + infile_name, dir_path + dir + level + "-cleaning.log")
        infile_path = dir_path + dir + level + "-cleaning.log"
        residue_path = dir_path + dir + level + "-residue.log"

        print("\nPreparing File: " + infile_name)
        line_count_dict={}
        for StatusCode in StatusCodeList:

            infile = open(infile_path, "r")
            outfile = open(dir_path + dir + "-" + StatusCode + ".csv", "w")
            residuefile = open(residue_path, "w")

            print("\nWriting " + StatusCode + "File")
            line_count = 0
            line_count_dict[StatusCode] = 0
            for line in infile.readlines():
                if StatusCode in line:
                    outfile.write(line)
                    line_count_dict[StatusCode]+=1
                else:
                    residuefile.write(line)

                line_count+=1
                if line_count % 1000000 == 0:
                    print("Reading the %d millionth line." % int(line_count / 1000000))

            outfile.close()
            residuefile.close()
            infile.close()

            #Residue File becomes the Infile
            os.remove(infile_path)
            os.rename(residue_path, infile_path)
        os.rename(infile_path, residue_path)
        #If residue file is not empty, some logs are not being precessed
        #Handle those logs by adding new Status Code to the StatusCode file
        sort_status_code(StatusCode_path, line_count_dict)

        statistic_file = open(dir_path + dir + level + "-statistic.txt", "w")
        sorted_dict = sorted(line_count_dict.items(), key=operator.itemgetter(1), reverse=True)
        statistic_file.write("Statistic: \nStatusCode    LineCount\n\n")
        total=0
        for status, num in sorted_dict:
            statistic_file.write(status + " " + str(num) + "\n")
            total+=num
        statistic_file.write("Total Line: "+ str(total) + "\n")

def main():
    if len(sys.argv) == 2:
        root_dir = sys.argv[1]
        sort_path = root_dir + "orilog/"
        prepare_path = root_dir + "sortlog/"
        split_by_log_level(root_dir, sort_path)
        prepare_csv(prepare_path, "warning")
        prepare_csv(prepare_path, "info")
        prepare_csv(prepare_path, "notice")
    else:
        print("Invalid input format. Please enter \"python log_to_csv.py [root directory]\"")

if __name__ == '__main__':
    main()