from snowflake.snowpark import Session

def create_snowflake_session():
    """
    Creates and returns a Snowflake session using predefined connection parameters.
    """
    connection_parameters = {
        "account": "WYB12201",
        "user": "PranayIngle",
        "password": "Pranayi25#",
        "role": "Public",
        "database": "SUSTAINABLITY_CORTEX_SEARCH_DOCS",
        "schema": "Data"
    }
    return Session.builder.configs(connection_parameters).create()
