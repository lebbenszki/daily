import math, time, sys, os.path, datetime, requests, argparse, codecs
from jikanpy import Jikan, APIException

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

def getSynopsis(userName, listType, url, file, bearerToken):
    existingDataSet, newDataSet = set(), set()
    if url[0] == True:
        dataDict = getFromUrl(url[1], existingDataSet, newDataSet)
    #elif file[0] == True:
        #dataDict = getFromFile(file[1], existingDataSet, newDataSet, bearerToken)
    else:
        dataDict = {}
    getUserList(userName, listType, existingDataSet, newDataSet, bearerToken)
    appendDictWithNewSynopsis(newDataSet, dataDict, listType)
    return dataDict

def getUserList(userName, listType, existingDataSet, newDataSet, bearerToken):
    i = 1
    endpoint = "https://api.myanimelist.net/v2/users/" + userName + "/" + listType + "list?limit=1000"
    header = {"Authorization": bearerToken}
    while True:
        try:
            response = requests.get(endpoint, headers=header)
            if response.status_code == requests.codes.unauthorized:
                print("Reacuthenticate yourself! Refresh the bearer token!")
                raise SystemError(110)
            data = response.json()
            while True:
                for node in data["data"]:
                    if node["node"]["id"] not in existingDataSet:
                        newDataSet.add(node["node"]["id"])
                if "next" not in data["paging"]:
                    break;
                data = requests.get(data["paging"]["next"], headers=header).json()
            break;
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
    parser.add_argument("-b", "--bearer",   help = "The bearer token for accessing userlist",               default = "checkIfNoBearer")
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
            print(e)
            print("The name does not exist, please check that you typed it correctly")
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
    if args.bearer == "checkIfNoBearer":
        print("Bearer token is required to get the userlist")
        raise SystemError(105)
    else:
        bearerToken = "Bearer " + args.bearer
    synopsisDict = getSynopsis(userName, listType, urlCss, fileCss, bearerToken)
    writeOutputFile(synopsisDict, listType)

if __name__ == "__main__":
    jikan = Jikan()
    main()
