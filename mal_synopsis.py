import math, time, sys, os.path, datetime, requests
from jikanpy import Jikan

def getFromExistingUrl(existingDataUrl, newDataSet, existingDataSet, newFile):
    url = existingDataUrl
    r = requests.get(url)
    dataList = (r.content.decode("utf-8", "ignore").split("\r"))[0].split("\n")
    for line in dataList:
        if line != "":
            str = ""
            for i in line[57:66]:
                if i.isdigit():
                    str += i
                elif str != "":
                    if any(word in line for word in ["{content: \'None\'; }", "{content: \'\'; }"]):
                        newDataSet.add(int(str))
                    else:
                        existingDataSet.add(int(str))
                        newFile.write(line)
                        newFile.write("\n")
                    break

def getList(listType, userName, existingDataUrl = "None"):
    existingDataSet, newDataSet = set(), set()
    newFile = open("new_" + listType + ".css", "w", encoding = "utf-8")
    if existingDataUrl != "None":
        getFromExistingUrl(existingDataUrl, newDataSet, existingDataSet, newFile)
    i = 1
    while True:
        user = jikan.user(username = userName, request = listType + "list", argument = "all", page = int(i))
        if len(user[listType]) == 0: break;
        i += 1
        print("Sleeping 10 seconds...")
        time.sleep(10)
        for data in user[listType]:
            if data["mal_id"] not in existingDataSet:
                newDataSet.add(data["mal_id"])
    remaining = len(newDataSet)
    print("New entry: ", remaining)
    for i in newDataSet:
        try:
            if listType == "manga":
                entity = jikan.manga(i)
            else:
                entity = jikan.anime(i)
            time.sleep(1)
            newFile.write("\n.list-table .list-table-data .data.image a[href*=\"/" + listType + "/" + str(entity["mal_id"]) + "/\"]:after {content: \'" + str(entity["synopsis"]).replace('"', '\\"').replace("'","\\'") + "\'; }")
            remaining = remaining - 1
            print("Remaining: ", remaining)
        except Exception as e:
            print(e)
    newFile.close()

def main():
    if len(sys.argv) == 4:
        """
        try:
            jikan.user(username = sys.argv[1], request= "profile")
        except Exception as e:
            print("Name not correct ot the error shown below!")
            input("Press Any key to exit...")
            print(e)
            raise SystemExit(5)
        """
        if sys.argv[2] != "anime" and sys.argv[2] != "manga":
            print("listType should be anime or manga")
            input("Press Any key to exit...")
            raise SystemExit(6)
        getList(sys.argv[2], sys.argv[1], sys.argv[3])
    elif len(sys.argv) == 3:
        """
        try:
            jikan.user(username= sys.argv[1], request='profile')
        except Exception as e:
            print("Name not correct ot the error shown below!")
            print(e)
            input("Press Any key to exit...")
            raise SystemExit(5)
        """
        if sys.argv[2] != "anime" and sys.argv[2] != "manga":
            print("list_type should be anime or manga")
            input("Press Any key to exit...")
            raise SystemExit(6)
        getList(sys.argv[2], sys.argv[1])
    else:
        print("Argument number must be 3 or 2 not ", len(sys.argv)-1)
        print("Arguments: userame list_type(anime/manga) old_css(optional)")
        input("Press Any key to exit...")
        raise SystemExit(3)

jikan = Jikan()
main()
