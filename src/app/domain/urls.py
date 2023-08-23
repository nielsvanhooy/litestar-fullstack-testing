INDEX = "/"
SITE_ROOT = "/{path:str}"
OPENAPI_SCHEMA = "/schema"

TAG_LIST = "/api/tags"
TAG_CREATE = "/api/tags"
TAG_UPDATE = "/api/tags/{tag_id:uuid}"
TAG_DELETE = "/api/tags/{tag_id:uuid}"
TAG_DETAILS = "/api/tags/{tag_id:uuid}"

ACCOUNT_LOGIN = "/api/access/login"
ACCOUNT_REGISTER = "/api/access/signup"
ACCOUNT_PROFILE = "/api/me"
ACCOUNT_LIST = "/api/users"
ACCOUNT_DELETE = "/api/users/{user_id:uuid}"
ACCOUNT_DETAIL = "/api/users/{user_id:uuid}"
ACCOUNT_UPDATE = "/api/users/{user_id:uuid}"
ACCOUNT_CREATE = "/api/users"

TEAM_LIST = "/api/teams"
TEAM_DELETE = "/api/teams/{team_id:uuid}"
TEAM_DETAIL = "/api/teams/{team_id:uuid}"
TEAM_UPDATE = "/api/teams/{team_id:uuid}"
TEAM_CREATE = "/api/teams"
TEAM_INDEX = "/api/teams/{team_id:uuid}"
TEAM_INVITATION_LIST = "/api/workspaces/{team_id:uuid}/invitations"


STATS_WEEKLY_NEW_USERS = "/api/stats/weekly-new-users"


########## CPES

CPES_LIST = "/api/cpes"
CPES_DETAIL = "/api/cpes/{device_id:str}"
CPES_CREATE = "/api/cpes"
CPES_DELETE = "/api/cpes/{device_id:str}"
CPES_READOUT = "/api/cpes/{device_id:str}/readout"
CPES_UPDATE = "/api/cpes/{device_id:str}"


########## CPE Business Product

CPE_BUSINESS_LIST = "/api/cpe-business-products"
CPE_BUSINESS_DETAIL = "/api/cpe-business-products/{product_id:str}"
CPE_BUSINESS_CREATE = "/api/cpe-business-products"
CPE_BUSINESS_DELETE = "/api/cpe-business-products/{product_id:str}"
CPE_BUSINESS_UPDATE = "/api/cpe-business-products/{product_id:str}"


########## CPE Business Product

CPE_VENDORS_LIST = "/api/cpe-vendors"
CPE_VENDORS_DETAIL = "/api/cpe-vendors/{vendor_id:str}"
CPE_VENDORS_CREATE = "/api/cpe-vendors"
CPE_VENDORS_DELETE = "/api/cpe-vendors/{vendor_id:str}"
CPE_VENDORS_UPDATE = "/api/cpe-vendors/{vendor_id:str}"


########## TSCM Checks

TSCM_LIST = "/api/tscm"
TSCM_DETAIL = "/api/tscm/{tscm_check_id:str}"
TSCM_LIST_CREATE = "/api/tscm"
TSCM_LIST_DELETE = "/api/tscm/{tscm_check_id:str}"
TSCM_LIST_UPDATE = "/api/tscm/{tscm_check_id:str}"
TSCM_CHECK_CPE = "/api/tscm/{device_id:str}/check"


########## CPE Product Configurations
CPE_PROD_CONFIGS = "/api/product-configurations"
CPE_PROD_CONFIGS_DETAIL = "/api/product-configurations/{product_configuration_id:str}"
CPE_PROD_CONFIGS_CREATE = "/api/product-configurations"
CPE_PROD_CONFIGS_UPDATE = "/api/product-configurations/{product_configuration_id:str}"
CPE_PROD_CONFIGS_DELETE = "/api/product-configurations/{product_configuration_id:str}"
