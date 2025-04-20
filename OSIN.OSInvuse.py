#==============================================================================
#*   NAME: OSIN.SM5253
#* 
#*   PURPOSE: Validate Scanned Meters Before Create INVUSE Transaction
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
msgLocation="Invalid Location: "

def beforeProcess(ctx):
    error=False

    invuselines=ctx.getData().getChildrenData("INVUSELINE")
    siteId = ctx.getData().getCurrentData("siteid")
    location = ctx.getData().getCurrentData("fromstoreloc")
    metersArray = JSONArray()

    if invuselines.size()>0 :
            for i in range(invuselines.size()):
                meters=invuselines.get(i).getChildrenData("INVUSELINESPLIT")
                itemNum = invuselines.get(i).getCurrentData("itemnum")
                
                if meters.size()>0 :
                    for j in range(meters.size()):                     
                        msg=""
                        # Récupérer les valeurs des enfants
                        assetNum = meters.get(j).getCurrentData("rotassetnum")

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
                        meterJSONObject.put("location", location)
            
                        if(asset is not None):
                            if(location!=asset.getString("location")):
                                if(msg==""):
                                    msg= msgLocation + location
                                else:
                                    msg=msg+", "+ msgLocation + location
                
                            if(itemNum!=asset.getString("itemnum")):
                                if(msg==""):
                                    msg= msgItem + itemNum 
                                else:
                                    msg= msg +", " + msgItem + itemNum 
             
                            meterJSONObject.put("description", asset.getString("DESCRIPTION"))
                            if(msg==""):
                                meterJSONObject.put("status", "OK")
                            else:
                                error=True
                                meterJSONObject.put("status", "ERROR")  
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
        responseJSONObject.put("action", "INVUSE")

        responseEncode = Base64.getEncoder().encodeToString(responseJSONObject.serialize())

# Convert the encoded bytes to a string
        keyEncoded64 = str(responseEncode)
        params=["#"+keyEncoded64+"#"]
        ctx.error("N","mobileReponse",params)