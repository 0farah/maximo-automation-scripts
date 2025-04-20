#==============================================================================
#*   NAME: N_MOBILEVALIDATEMETERS
#* 
#*   PURPOSE: Validate Scanned Meters Action
#*
#*   REVISIONS:
#*   Ver        Date              Author                             Description
#*   ---------  ---------- ---  ---------- ---------------  -----------------------------------
#*   
#*     1.0       15/04/2025        SMARTECH                      Create initial script
#*     1.1       18/04/2025        SMARTECH                      Enhance returned messages

#***************************** End Standard Header **************************** 
#==============================================================================

from com.ibm.json.java import JSONObject
from com.ibm.json.java import JSONArray
from psdi.server import MXServer
from psdi.mbo import SqlFormat

msgMeter="Invalid Meter: "
msgItem="Invalid Item: "
msgLocation="Invalid Location: "

body =JSONObject.parse(requestBody)

action=body.get("action")

listMeterToValidate = body.get("assets")
resultArray = JSONArray()

if listMeterToValidate is not None:
    # Itérer à travers chaque enfant (chaque asset dans le tableau)
    for i in range(listMeterToValidate.size()):
        # Obtenir l'objet enfant (asset)
        meterToValidate = listMeterToValidate.get(i)
        
        # Récupérer les valeurs des enfants
        assetNum = meterToValidate.get("assetnum")
        siteId = meterToValidate.get("siteid")
        itemNum = meterToValidate.get("itemnum")
        location = meterToValidate.get("location")
        whereClause="assetnum=:1 and siteid=:2"
        
        sqlf =  SqlFormat(MXServer.getMXServer().getSystemUserInfo(),whereClause)
        sqlf.setObject(1, "ASSET", "ASSETNUM",assetNum)
        sqlf.setObject(2, "ASSET", "SITEID",siteId)
        assetSet=MXServer.getMXServer().getMboSet("ASSET",MXServer.getMXServer().getSystemUserInfo())
        assetSet.setWhere(sqlf.format())
        assetSet.reset()
        asset=assetSet.moveFirst()
        if(action=="INVUSE"):
            if(asset is not None):
                message=""
                if(location!=asset.getString("location")):
                    if(message==""):
                        message=msgLocation+location
                    else:
                        message=message+", "+msgLocation+location
                
                if(itemNum!=asset.getString("ITEMNUM")):
                    if(message==""):
                        message=msgItem+itemNum
                    else:
                        message=message+", " + msgItem+itemNum                  
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", asset.getString("ASSETNUM"))
                meterJSONObject.put("siteid", asset.getString("siteid"))
                meterJSONObject.put("description", asset.getString("DESCRIPTION"))
                if(message==""):
                    meterJSONObject.put("status", "OK")
                else:
                    meterJSONObject.put("status", "ERROR")           
                meterJSONObject.put("message", message)
                resultArray.add(meterJSONObject) 
                
            else:
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", assetNum)
                meterJSONObject.put("siteid", siteId)
                meterJSONObject.put("description", "")
                meterJSONObject.put("message", msgMeter+assetNum)
                meterJSONObject.put("status", "ERROR")
                resultArray.add(meterJSONObject) 
                
        if(action=="RECEIPT"):
            if(asset is not None):
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", assetNum)
                meterJSONObject.put("siteid", siteId)
                meterJSONObject.put("description", asset.getString("description"))
                message="Valid Meter: "+assetNum 
                meterJSONObject.put("message", message)
                meterJSONObject.put("status", "ERROR")
                resultArray.add(meterJSONObject)
            else:
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", assetNum)
                meterJSONObject.put("siteid", siteId)
                meterJSONObject.put("description", "")
                message=""
                meterJSONObject.put("message", message)
                meterJSONObject.put("status", "OK")
                resultArray.add(meterJSONObject)

        if(action=="METERPHYSICAL"):
            if(asset is not None):
                message=""
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", assetNum)
                meterJSONObject.put("siteid", siteId)
                meterJSONObject.put("description", asset.getString("description"))
                if(itemNum!=asset.getString("ITEMNUM")):
                    message=msgItem+itemNum     
                meterJSONObject.put("message", message)

                if(message==""):
                    meterJSONObject.put("status", "OK")
                else:
                    meterJSONObject.put("status", "ERROR")  
                resultArray.add(meterJSONObject)
            else:
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", assetNum)
                meterJSONObject.put("siteid", siteId)
                meterJSONObject.put("description", "")
                meterJSONObject.put("message", msgMeter+assetNum)
                meterJSONObject.put("status", "ERROR") 
                resultArray.add(meterJSONObject)

        assetSet.close()

json_obj=JSONObject()
json_obj.put("assets", resultArray)
responseBody = json_obj.serialize()