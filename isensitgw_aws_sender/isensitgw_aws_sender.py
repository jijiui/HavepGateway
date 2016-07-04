import sys

# adding api to path
api_folder = "/home/pi/ISensitGateway/isensitgwapi/"
if api_folder not in sys.path:
    sys.path.insert(0, api_folder)

from isensit_cloud import *
from isensit_sql import *
jsonDict = {}
deviceInfoDict = {}
deviceValueDict = {}
row_count = 0
#try:
    # initialize database reader
#    a = 2
#except Exception as e:
#    print("Error in initializing db, reason: ", str(e))
#    exit(-1)

uploader = ISensitCloud()
data = None
count = 0

while True:
    try:
        db = ISensitGWMysql()
        db.connect_to_db()
        data = db.read_first_beacon_data()
        if data is None:
            print("No data left")
        else:
            row_count = data["row_count"]
            deviceInfoDict['ID'] = data["beacon_id"]
            deviceValueDict['accx'] = data["beacon_accx"]
            deviceValueDict['accy'] = data["beacon_accy"]
            deviceValueDict['accz'] = data["beacon_accz"]
            deviceValueDict['rssi'] = data["beacon_rssi"]
            
            #row_count = data["row_count"]
            #deviceInfoDict['UUID'] = data["beacon_uuid"]
            #deviceInfoDict['ID'] = data["beacon_major"]
            #deviceValueDict['minor'] = data["beacon_minor"]
            #deviceValueDict['rssi'] = data["beacon_rssi"]

            jsonDict['gatewayID'] = db.gatewayID
            jsonDict["device"] = deviceInfoDict
            jsonDict["values"] = deviceValueDict
            # data = json.dumps(deviceInfoDict, ensure_ascii=False)

            print(jsonDict)

    except Exception as e:
        print("Error in Aws Sender, reason: ", str(e))
    else:
        if data is not None:
            print("uploading...")
            db.delete_acc_beacon_data(row_count)
            upload = uploader.post_data(jsonDict)

            if upload:
                print("upload successful, deleting row..")
                db.delete_acc_beacon_data(row_count)

            else:
                print("Data was not uploaded reason: ")
                print(upload)
        db.close_db()
