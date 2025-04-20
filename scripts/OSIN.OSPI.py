#==============================================================================
#*   NAME: OSIN.OSPI
#* 
#*   PURPOSE: Validate Scanned Meters Before Create PHYSICALMETER Transaction
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
from  java.util import Base64

msgMeter="Invalid Meter: "
msgItem="Invalid Item: "

def beforeProcess(ctx):
    error=False
    pilines=ctx.getData().getChildrenData("PILINE")
    siteId = ctx.getData().getCurrentData("siteid")
    metersArray = JSONArray()

    if pilines.size()>0 :
          for i in range(pilines.size()):
                assetNum = pilines.get(i).getCurrentData("scan_meter")
                itemNum = pilines.get(i).getCurrentData("scan_itemnum")
                
                assetSet = MXServer.getMXServer().getMboSet("ASSET",MXServer.getMXServer().getSystemUserInfo())
                whereClause = "assetnum=:1 and siteid=:2"
        
                sqlf =  SqlFormat(MXServer.getMXServer().getSystemUserInfo(),whereClause);
                sqlf.setObject(1, "ASSET", "ASSETNUM",assetNum)
                sqlf.setObject(2, "ASSET", "SITEID",siteId)
                assetSet.setWhere(sqlf.format())
                assetSet.reset()
                asset=assetSet.moveFirst()
                meterJSONObject = JSONObject()
                meterJSONObject.put("assetnum", assetNum)
                meterJSONObject.put("siteid", siteId)   
                meterJSONObject.put("itemnum", itemNum)
            
                if(asset is not None):
                    meterJSONObject.put("description", asset.getString("DESCRIPTION"))
                    if(itemNum!=asset.getString("itemnum")):
                        error=True
                        msg=msgItem + itemNum 
                        meterJSONObject.put("status", "ERROR") 
                    else:
                        msg=""
                        meterJSONObject.put("status", "OK") 
                    meterJSONObject.put("message", msg)
            
                else:
                    error=True
                    meterJSONObject.put("description", "")
                    meterJSONObject.put("message", msgMeter + assetNum)
                    meterJSONObject.put("status", "ERROR")
                metersArray.add(meterJSONObject)         
                assetSet.close()
          
    if (error):
        responseJSONObject = JSONObject()
        responseJSONObject.put("assets", metersArray)
        responseJSONObject.put("action", "METERPHYSICAL")
        responseEncode = Base64.getEncoder().encodeToString(responseJSONObject.serialize())

# Convert the encoded bytes to a string
        keyEncoded64 = str(responseEncode)
        params=["#"+keyEncoded64+"#"]
        ctx.error("N","mobileReponse",params)