#==============================================================================
#*   NAME: OSIN.OSCompany
#* 
#*   PURPOSE: Set Company Manufacturer value from MAMS Manufacturer
#*
#*   REVISIONS:
#*   Ver        Date              Author                             Description
#*   ---------  ---------- ---  ---------- ---------------  -----------------------------------
#*   
#*     1.0       17/04/2025        Farah                      Create initial script

#***************************** End Standard Header **************************** 
#==============================================================================

from psdi.server import MXServer
from psdi.mbo import SqlFormat


def beforeProcess(ctx):
    struc=ctx.getData()
    manufacturer = struc.getCurrentData("manufacturer")
    companiesSet = MXServer.getMXServer().getMboSet("COMPANIES",MXServer.getMXServer().getSystemUserInfo())
    whereClause = "N_MAMS_MANUF=:1"
    sqlf =  SqlFormat(MXServer.getMXServer().getSystemUserInfo(),whereClause)
    sqlf.setObject(1, "COMPANIES", "N_MAMS_MANUF",manufacturer)
    companiesSet.setWhere(sqlf.format())
    companiesSet.reset()
    company=companiesSet.moveFirst()
    if (company is not None):
        struc.setCurrentData("manufacturer",company.getString("COMPANY"))
    companiesSet.close()