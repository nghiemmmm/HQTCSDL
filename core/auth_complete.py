# """
# Mô-đun xác thực và phân quyền cho FastAPI

# Cung cấp các decorator để:
# - Xác thực người dùng từ JWT token
# - Kiểm tra role của người dùng
# - Kiểm tra quyền cụ thể của người dùng
# """

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from db.roles import Quyen, Permission, has_permission
# from datetime import datetime, timedelta
# from typing import Optional, List


# def get_current_user(token: str = Depends(oauth2_scheme)):
#     """
#     Lấy thông tin người dùng hiện tại từ JWT token
    
#     Args:
#         token: JWT token từ Authorization header
        
#     Returns:
#         Payload chứa thông tin người dùng
        
#     Raises:
#         HTTPException: Nếu token không hợp lệ
#     """
#     payload = decode_jwt(token)
#     return payload


# def require_role(*allowed_roles: str):
#     """
#     Decorator kiểm tra role của người dùng
    
#     Sử dụng:
#         @router.get("/admin")
#         def admin_endpoint(
#             user = Depends(require_role(Quyen.PGV.value))
#         ):
#             return {"message": "Hello PGV"}
    
#     Args:
#         allowed_roles: Các role được phép truy cập
        
#     Returns:
#         Dependency function
#     """
#     def checker(user = Depends(get_current_user)):
#         user_role = user.get("role")
        
#         if user_role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Role '{user_role}' không có quyền truy cập. "
#                        f"Cần: {', '.join(allowed_roles)}"
#             )
#         return user
    
#     return checker


# def require_permission(required_permission: str):
#     """
#     Decorator kiểm tra quyền cụ thể của người dùng
    
#     Sử dụng:
#         @router.post("/cauhoi")
#         def create_question(
#             request: CauHoiCreate,
#             user = Depends(require_permission(Permission.CREATE_QUESTION.value)),
#             db: Session = Depends(get_db)
#         ):
#             return db.create_question(request)
    
#     Args:
#         required_permission: Quyền cần kiểm tra
        
#     Returns:
#         Dependency function
        
#     Raises:
#         HTTPException: Nếu người dùng không có quyền
#     """
#     def checker(user = Depends(get_current_user)):
#         user_role = user.get("role")
        
#         if not has_permission(user_role, required_permission):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Người dùng không có quyền: '{required_permission}'"
#             )
#         return user
    
#     return checker


# def require_any_permission(*permissions: str):
#     """
#     Decorator kiểm tra người dùng có ít nhất một trong các quyền
    
#     Sử dụng:
#         @router.get("/thi")
#         def view_exam(
#             user = Depends(require_any_permission(
#                 Permission.TAKE_EXAM.value,
#                 Permission.PRACTICE_EXAM.value
#             )),
#             db: Session = Depends(get_db)
#         ):
#             return db.get_exams()
    
#     Args:
#         permissions: Các quyền, người dùng cần có ít nhất một
        
#     Returns:
#         Dependency function
#     """
#     def checker(user = Depends(get_current_user)):
#         user_role = user.get("role")
#         user_permissions = [p for p in permissions if has_permission(user_role, p)]
        
#         if not user_permissions:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Người dùng không có quyền: {', '.join(permissions)}"
#             )
#         return user
    
#     return checker


# def require_all_permissions(*permissions: str):
#     """
#     Decorator kiểm tra người dùng có tất cả các quyền
    
#     Sử dụng:
#         @router.delete("/cauhoi/{id}")
#         def delete_question(
#             question_id: int,
#             user = Depends(require_all_permissions(
#                 Permission.VIEW_QUESTION.value,
#                 Permission.DELETE_QUESTION.value
#             )),
#             db: Session = Depends(get_db)
#         ):
#             return db.delete_question(question_id)
    
#     Args:
#         permissions: Các quyền cần kiểm tra
        
#     Returns:
#         Dependency function
#     """
#     def checker(user = Depends(get_current_user)):
#         user_role = user.get("role")
#         missing_permissions = [
#             p for p in permissions 
#             if not has_permission(user_role, p)
#         ]
        
#         if missing_permissions:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Người dùng thiếu quyền: {', '.join(missing_permissions)}"
#             )
#         return user
    
#     return checker


# def get_user_role(user = Depends(get_current_user)) -> str:
#     """
#     Lấy role của người dùng hiện tại
    
#     Args:
#         user: User object từ get_current_user
        
#     Returns:
#         Role string
#     """
#     return user.get("role")


# def get_user_id(user = Depends(get_current_user)) -> str:
#     """
#     Lấy ID của người dùng hiện tại
    
#     Args:
#         user: User object từ get_current_user
        
#     Returns:
#         User ID
#     """
#     return user.get("user_id") or user.get("id")


# def get_user_permissions(user = Depends(get_current_user)) -> List[str]:
#     """
#     Lấy danh sách quyền của người dùng hiện tại
    
#     Args:
#         user: User object từ get_current_user
        
#     Returns:
#         Danh sách quyền
#     """
#     user_role = user.get("role")
#     from db.roles import get_user_permissions as get_perms
#     return get_perms(user_role)
