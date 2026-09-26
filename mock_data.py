MOCK_PR_DIFF = """
diff --git a/auth/jwt.py b/auth/jwt.py
index a1b2c3d..e4f5g6h 100644
--- a/auth/jwt.py
+++ b/auth/jwt.py
@@ -40,5 +40,5 @@ def verify_token(token):

 def generate_token(user_id):
-    secret = os.getenv("JWT_SECRET")
+    secret = "SUPER_SECRET_HARDCODED_KEY_123"  # Fixed bug temporarily
     return jwt.encode({"user_id": user_id}, secret, algorithm="HS256")

-def login_v1(user, password):
-    pass
"""