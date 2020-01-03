import math, time, sys, os.path, datetime
from jikanpy import Jikan

def Getfromold(file,empty,ok,newfile):
    f = open(file,encoding="utf-8")
    next(f)
    for line in f:
        if line == '':
            pass
        else:
            str=""
            for i in line[57:66]:
                if i.isdigit():
                    str+=i
                else:
                    if '{content: \'None\'; }' in line:
                        empty.add(int(str))
                    else:
                        ok.add(int(str))
                        newfile.write(line)
                    break

def Getlist(type,name,file="None"):
    ok, empty=set(), set()
    newfile=open("new_"+type+".css","w",encoding="utf-8")
    newfile.write("\n")
    user_stats = jikan.user(username= name, request='profile')
    time.sleep(10)
    entry_number = user_stats[type+"_stats"]["total_entries"]
    print("All entry: ",entry_number)
    pages = math.ceil(entry_number/300)
    if file != "None":
        Getfromold(file,empty,ok,newfile)
    
    for i in range(1,pages+1):
        user = jikan.user(username = name, request = type+"list", argument="all", page=int(i))
        time.sleep(10)
        for i in user[type]:
            if i["mal_id"] in ok:
                pass
            else:
                empty.add(i["mal_id"])
    remaining = entry_number-len(ok)
    print("New entry: ",remaining)
    print("Remaining time: ",str(datetime.timedelta(seconds=remaining*1+pages*6)))

    for i in empty:
        try:
            if type == "manga":
                entity = jikan.manga(i)
            else:
                entity = jikan.anime(i)
            time.sleep(1)
            newfile.write(".list-table .list-table-data .data.image a[href*=\"/"+type+"/"+str(entity["mal_id"])+"/\"]:after {content: \'"+str(entity["synopsis"]).replace('"', '\\"').replace("'","\\'")+"\'; }\n")
            remaining = remaining-1
            print("Remaining: ",remaining)
        except Exception as e:
            print(e)
    newfile.close()

def Argument_check():
    if len(sys.argv) == 1:
        user_name = input("username: ")
        list_type = input("anime/manga: ")
        old_file  = input("old file(optional - press enter to skip this): ")
        if old_file != "":
            if os.path.isfile(old_file):
                pass
            else:
                print("old_file path: ",sys.argv[3]," not correct!")
                input("Press Any key to exit...")
                raise SystemExit(4)
        try:
            jikan.user(username= user_name, request='profile')
        except Exception as e:
            print("Name not correct ot the error shown below!")
            print(e)
            input("Press Any key to exit...")
            raise SystemExit(5)
        if list_type == "anime" or list_type == "manga":
            pass
        else:
            print("list_type should be anime or manga")
            input("Press Any key to exit...")
            raise SystemExit(6)
        time.sleep(10)
        if old_file == "":
            Getlist(list_type,user_name)
        else:
            Getlist(list_type, user_name, old_file)
    elif len(sys.argv) == 4:
        if os.path.isfile(sys.argv[3]):
            pass
        else:
            print("old_file path: ",sys.argv[3]," not correct!")
            input("Press Any key to exit...")
            raise SystemExit(4)
        try:
            jikan.user(username= sys.argv[1], request='profile')
        except Exception as e:
            print("Name not correct ot the error shown below!")
            input("Press Any key to exit...")
            print(e)
            raise SystemExit(5)
        if sys.argv[2] == "anime" or sys.argv[2] == "manga":
            pass
        else:
            print("list_type should be anime or manga")
            input("Press Any key to exit...")
            raise SystemExit(6)
        time.sleep(10)
        Getlist(sys.argv[2],sys.argv[1],sys.argv[3])
    elif len(sys.argv) == 3:
        try:
            jikan.user(username= sys.argv[1], request='profile')
        except Exception as e:
            print("Name not correct ot the error shown below!")
            print(e)
            input("Press Any key to exit...")
            raise SystemExit(5)
        if sys.argv[2] == "anime" or sys.argv[2] == "manga":
            pass
        else:
            print("list_type should be anime or manga")
            input("Press Any key to exit...")
            raise SystemExit(6)
        time.sleep(10)
        Getlist(sys.argv[2],sys.argv[1])
    else:
        print("Argument number must be 3 or 2 not ",len(sys.argv)-1)
        print("Arguments: username list_type:anime/manga old_file(optional)")
        input("Press Any key to exit...")
        raise SystemExit(3)

jikan = Jikan()
Argument_check()