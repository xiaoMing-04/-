from firebase_admin import auth
from users.models import MyUser
from datetime import datetime
from users.firebase_helpers import firebase_config

# đồng bộ từ firebase về database của django
def sync_firebase_users(email=None, id=None):  
    firebase_config()
    
    try:
        if email:
            user = auth.get_user_by_email(email)
        elif id:
            user = auth.get_user(id)
        else:
            return  # Không có email hoặc id thì không làm gì cả

        firebase_uid = user.uid
        firebase_username = user.display_name
        firebase_email = user.email
        firebase_role = user.custom_claims.get('role') if user.custom_claims else None
        firebase_create_at = datetime.fromtimestamp(
            user.user_metadata.creation_timestamp / 1000.0
        ).strftime('%Y-%m-%d %H:%M:%S')

        user_obj, created = MyUser.objects.update_or_create(
            id=firebase_uid,
            defaults={
                "username": firebase_username,
                "email": firebase_email,
                "role": firebase_role,
                "created_at": firebase_create_at,
            }
        )
        return user_obj  # Trả về đối tượng người dùng đã đồng bộ
    except auth.UserNotFoundError:
        print("Firebase user not found.")
    except Exception as e:
        print(f"Lỗi đồng bộ người dùng: {e}")

    return None  # Trả về None nếu không tìm thấy người dùng hoặc có lỗi xảy ra