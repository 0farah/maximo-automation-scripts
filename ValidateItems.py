#==============================================================================
#*   NAME: N_MOBILEVALIDATEITEMS
#* 
#*   PURPOSE: Validate Scanned Items Action
#*
#*   REVISIONS:
#*   Ver        Date              Author                             Description
#*   ---------  ---------- ---  ---------- ---------------  -----------------------------------
#*   
#*     1.0       18/04/2025        SMARTECH                      Create initial script

#***************************** End Standard Header **************************** 
#==============================================================================

from com.ibm.json.java import JSONObject
from com.ibm.json.java import JSONArray
from psdi.server import MXServer
from psdi.mbo import SqlFormat

msgItem="Invalid Item: "

body =JSONObject.parse(requestBody)

action=body.get("action")

listItemToValidate = body.get("items")
resultArray = JSONArray()

if listItemToValidate is not None:
    # Itérer à travers chaque enfant (chaque item dans le tableau)
    for i in range(listItemToValidate.size()):
        # Obtenir l'objet enfant (item)
        itemToValidate = listItemToValidate.get(i)
        
        # Récupérer les valeurs des enfants
        itemNum = itemToValidate.get("itemnum")
        whereClause="itemnum=:1"
        
        sqlf =  SqlFormat(MXServer.getMXServer().getSystemUserInfo(),whereClause)
        sqlf.setObject(1, "ITEM", "ITEMNUM",itemNum)
        itemSet=MXServer.getMXServer().getMboSet("ITEM",MXServer.getMXServer().getSystemUserInfo())
        itemSet.setWhere(sqlf.format())
        itemSet.reset()
        item=itemSet.moveFirst()

        if(action=="METERPHYSICAL"):
            message=""
            meterJSONObject = JSONObject()
            meterJSONObject.put("itemnum", itemNum)
            if(item is not None):
                meterJSONObject.put("description", item.getString("description"))
                meterJSONObject.put("message", "")
                meterJSONObject.put("status", "OK")
            else:
                meterJSONObject.put("description", "")
                meterJSONObject.put("message", msgItem + itemNum)
                meterJSONObject.put("status", "ERROR") 
            resultArray.add(meterJSONObject)    

        itemSet.close()

json_obj=JSONObject()
json_obj.put("items", resultArray)
responseBody = json_obj.serialize()