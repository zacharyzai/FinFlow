# for testing backend

from app.core.database import supabase

response = supabase.auth.sign_in_with_password({
    "email": "zachary.zai.2025@computing.smu.edu.sg",
    "password": "password"
})

print(response.session.access_token)
