FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]

def is_safe_sql(sql : str) -> bool:
    
    sql_list = sql.split()
    # empty string
    if(sql == ""):
        return False
    
    if(sql_list[0].lower() != "select"):
        return False
    
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql.upper():
            return False
        
        
    
