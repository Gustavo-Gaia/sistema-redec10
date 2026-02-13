# supabase_client.py
from supabase import create_client
import os

SUPABASE_URL = os.getenv("https://tfdmjadkmneslswsxwvg.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_szvWANlFRSVR6wylaI8sQw_n24x2-9_")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
