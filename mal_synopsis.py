import math, time, sys, os.path, datetime, requests, argparse, codecs
from jikanpy import Jikan, Exceptions

sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

def getFromUrl(url, existingDataSet, newDataSet):
    dataDict = {}
    request = requests.get(url)
    dataList = request.content.decode("utf-8", "ignore").split("\r")[0].split("\n")
    for line in dataList:
        if line != "":
            malId = line.split("/")[2]
            if any(word in line for word in ["{content: \'None\'; }", "{content: \'\'; }"]):
                newDataSet.add(int(malId))
            else:
                existingDataSet.add(int(malId))
                dataDict[int(malId)] = line
    return dataDict

def getSynopsis(userName, listType, url, file):
    existingDataSet, newDataSet = set(), set()
    if url[0] == True:
        dataDict = getFromUrl(url[1], existingDataSet, newDataSet)
    elif file[0] == True:
        dataDict = getFromFile(file[1], existingDataSet, newDataSet)
    else:
        dataDict = {}
    getUserList(userName, listType, existingDataSet, newDataSet)
    appendDictWithNewSynopsis(newDataSet, dataDict, listType)
    return dataDict

def getUserList(userName, listType, existingDataSet, newDataSet):
    i = 1
    while True:
        try:
            user = jikan.user(username = userName, request = listType + "list", argument = "all", page = int(i))
            if len(user[listType]) == 0: 
                break;
            i += 1
            print("Sleeping 60 second")
            time.sleep(60)
            for data in user[listType]:
                if data["mal_id"] not in existingDataSet:
                    newDataSet.add(data["mal_id"])
        except Exception as e:
            print(e)
            print("Error, retrying in 60 second")
            time.sleep(60)

def appendDictWithNewSynopsis(newDataSet, dataDict, listType):
    remaining = len(newDataSet)
    print("New entries: ", remaining)
    for malId in newDataSet:
        try:
            if listType == "manga":
                entity = jikan.manga(malId)
            else:
                entity = jikan.anime(malId)
            time.sleep(2)
            dataDict[int(malId)] = ".list-table .list-table-data .data.image a[href*=\"/" + listType + "/" + str(entity["mal_id"]) + "/\"]:after {content: \'" + str(entity["synopsis"]).replace('"', '\\"').replace("'","\\'") + "\'; }"
            remaining = remaining - 1
            print("Remaining: ", remaining)
        except Exception as e:
            print("Something went wrong when requesting synopsis for the new entries")
            print(e)

def writeOutputFile(dataDict, listType):
    try:
        newFile = open("new_" + listType + ".css", "w", encoding = "utf-8")
        for key, value in sorted(dataDict.items()):
            newFile.write(value)
            newFile.write("\n")
        newFile.close()
    except Exception as e:
        print("Something went wring when weiring output")
        print(e)
        raise SystemExit(105)

def parseArgs():
    parser = argparse.ArgumentParser(description = "Get the description of the animes, mangas the user has on his list")
    parser.add_argument("-n", "--name",     help = "The profile name of the user",                          default = "checkIfNoName")
    parser.add_argument("-t", "--type",     help = "The type of the list, use the anime, manga keywords",   default = "checkIfNoType")
    parser.add_argument("-uc", "--urlcss",  help = "The url address of the css file",                       default = "checkIfNoUrl")
    parser.add_argument("-fc", "--filecss", help = "The absolute path of the css file",                     default = "checkIfNoFile")
    args = parser.parse_args()
    return args

def checkName(userName):
    while True:
        try:
            jikan.user(username = userName, request = "profile")
            break;
        except APIException as e:
            print(e)
            print("Error, retrying in 60 second")
            time.sleep(60)
        except Exception as e:
            print("The name does not exist, please check that you typed it correctly")
            input("Press Any key to exit...")
            raise SystemExit(102)

def checkType(listType):
    if listType != "anime" and listType != "manga":
        print("Use anime or manga keywords to specify the type")
        input("Press Any key to exit...")
        raise SystemExit(106)

def main():
    args = parseArgs()
    print(args)
    if args.name == "checkIfNoName":
        print("Use -n, --name to input the username")
        input("Press Any key to exit...")
        raise SystemExit(101)
    else:
        userName = args.name
        checkName(userName)
    if args.type == "checkIfNoType":
        print("Use -t, --type to input the type of the list")
        input("Press Any key to exit...")
        raise SystemExit(103)
    else:
        listType = args.type
    if args.urlcss != "checkIfNoUrl":
        urlCss = [True, args.urlcss]
    else:
        urlCss = [False]
    if args.filecss != "checkIfNoFile":
        fileCss = [True, args.filecss]
    else:
        fileCss = [False]
    if urlCss[0] == True and fileCss[0] == True:
        print("Either use urlcss or filecss")
        raise SystemError(104)
    synopsisDict = getSynopsis(userName, listType, urlCss, fileCss)
    writeOutputFile(synopsisDict, listType)

if __name__ == "__main__":
    jikan = Jikan()
    main()
