#==============================================================================
#*   NAME: OSIN.OSPO
#* 
#*   PURPOSE: Validate Scanned Meters Before Receipt Transaction and Set Company Manufacturer value from MAMS Manufacturer
#*
#*   REVISIONS:
#*   Ver        Date              Author                             Description
#*   ---------  ---------- ---  ---------- ---------------  -----------------------------------
#*   
#*     1.0       15/04/2025        SMARTECH                      Create initial script
#*     1.1       17/04/2025        SMARTECH                      Enhance returned messages

#***************************** End Standard Header **************************** 
#==============================================================================

from com.ibm.json.java import JSONObject
from com.ibm.json.java import JSONArray
from psdi.server import MXServer
from psdi.mbo import SqlFormat
from  java.util import Base64

msgMeter = "Meter Already Exists"

def beforeProcess(ctx):
    error=False
    # Validate Asset
    meters=ctx.getData().getChildrenData("ASSET")
    metersArray = JSONArray()

    if meters.size()>0 :
      
        for j in range(meters.size()):
            assetSet=MXServer.getMXServer().getMboSet("ASSET",MXServer.getMXServer().getSystemUserInfo())
            whereClause="assetnum=:1 and siteid=:2"
            sqlf =  SqlFormat(MXServer.getMXServer().getSystemUserInfo(),whereClause)
            sqlf.setObject(1, "ASSET", "ASSETNUM",meters.get(j).getCurrentData("ASSETNUM"))
            sqlf.setObject(2, "ASSET", "SITEID",meters.get(j).getCurrentData("SITEID"))
            assetSet.setWhere(sqlf.format())
            assetSet.reset()
            asset=assetSet.moveFirst()

            meterJSONObject = JSONObject()
            meterJSONObject.put("assetnum", meters.get(j).getCurrentData("ASSETNUM"))
            meterJSONObject.put("siteid", meters.get(j).getCurrentData("SITEID"))

            if(asset is not None):
                error=True
                meterJSONObject.put("description", asset.getString("DESCRIPTION"))
                meterJSONObject.put("message", msgMeter)
                meterJSONObject.put("status", "ERROR")
            else:
                meterJSONObject.put("message", "")
                meterJSONObject.put("status", "OK")
            metersArray.add(meterJSONObject)         
            assetSet.close()

            # Read manufacturer info  and return associated company
            manufacturer = meters.get(j).getCurrentData("manufacturer")
            companiesSet = MXServer.getMXServer().getMboSet("COMPANIES",MXServer.getMXServer().getSystemUserInfo())
            whereClause = "N_MAMS_MANUF=:1"
            sqlf =  SqlFormat(MXServer.getMXServer().getSystemUserInfo(),whereClause)
            sqlf.setObject(1, "COMPANIES", "N_MAMS_MANUF",manufacturer)
            companiesSet.setWhere(sqlf.format())
            companiesSet.reset()
            company=companiesSet.moveFirst()
            if (company is not None):
                meters.get(j).setCurrentData("manufacturer",company.getString("COMPANY"))
            else:
                meters.get(j).setCurrentData("manufacturer",None)
            companiesSet.close()
            
    if (error):
        responseJSONObject = JSONObject()
        responseJSONObject.put("assets", metersArray)
        responseJSONObject.put("action", "RECEIPT")
        responseEncode = Base64.getEncoder().encodeToString(responseJSONObject.serialize())

# Convert the encoded bytes to a string
        keyEncoded64 = str(responseEncode)
        params=["#"+keyEncoded64+"#"]
        ctx.error("N","mobileReponse",params)