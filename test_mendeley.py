# %%
from mendeley import Mendeley

# %%
mendeley = Mendeley(
    client_id=9773,
    client_secret="WyqXCFUPhmh0V7W0",
    redirect_uri="http://localhost:5000/oauth",
)
# %%
auth = mendeley.start_authorization_code_flow()
# %%
login_url = auth.get_login_url()
# %%
login_url
# %%


from mendeley import Mendeley

# These values should match the ones supplied when registering your application.
mendeley = Mendeley(
    client_id=9773,
    client_secret="WyqXCFUPhmh0V7W0",
    redirect_uri="http://localhost:5000/oauth",
)

auth = mendeley.start_implicit_grant_flow()

# The user needs to visit this URL, and log in to Mendeley.
login_url = auth.get_login_url()


#%%
login_url
#%%

# After logging in, the user will be redirected to a URL, auth_response.
session = auth.authenticate(auth_response)
# %%



import mendeley.resources.documents
import mendeley

mendeley.resources.documents
# %%
