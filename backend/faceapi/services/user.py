"""
顔認識システムのユーザーサービスモジュール。

このモジュールは認証とプロフィール操作を含む
ユーザー管理のビジネスロジックを含みます。
"""

from fastapi import HTTPException

from ..models.user import UserModel
from ..schemas import User, UserCreate, UserUpdate
from ..utils import hash_password, verify_password


async def authenticate_user(username: str, password: str):
    """
    ユーザー名/メールアドレスとパスワードでユーザーを認証。

    引数:
        username: ユーザーのユーザー名またはメールアドレス
        password: 検証する平文パスワード

    戻り値:
        成功した場合は認証されたユーザーオブジェクト、それ以外はNone
    """
    # ユーザー名またはメールアドレスでユーザーを検索
    user = await UserModel.get_or_none(
        username=username
    ) or await UserModel.get_or_none(email=username)

    if not user:
        return None

    # ユーザーがアクティブかどうか確認
    if not user.is_active:
        return None

    # パスワードを検証
    if not verify_password(
        plain_password=password,
        hashed_password=user.hashed_password,
    ):
        return None

    return user


async def create_user_service(user: UserCreate):
    """
    新しいユーザーを作成するサービス関数。

    引数:
        user: ユーザー詳細を含むユーザー作成リクエストオブジェクト

    戻り値:
        作成されたユーザーオブジェクト
    """
    # ユーザーが既に存在するか確認
    existing_user = await UserModel.get_or_none(username=user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    existing_email = await UserModel.get_or_none(email=user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # pass_utilsモジュールを使用してパスワードをハッシュ化
    hashed_password = hash_password(user.password)

    # データベースにユーザーを作成
    created_user = await UserModel.create(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
    )

    return created_user


async def get_current_user_profile_service(user_id: int):
    """
    現在のユーザーのプロフィールを取得するサービス関数。

    引数:
        user_id: プロフィールを取得するユーザーのID

    戻り値:
        見つかった場合はユーザープロフィールオブジェクト
    """
    user_obj = await UserModel.get_or_none(id=user_id)

    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    user = User(
        id=user_obj.id,
        username=user_obj.username,
        email=user_obj.email,
        full_name=user_obj.full_name,
        is_active=user_obj.is_active,
        created_at=user_obj.created_at,
        updated_at=user_obj.updated_at,
        head_pic=user_obj.head_pic,
        is_admin=user_obj.is_admin,
    )

    return user


async def update_user_profile_service(user_id: int, user_update: UserUpdate):
    """
    現在のユーザーのプロフィールを更新するサービス関数。

    引数:
        user_id: 更新するユーザーのID
        user_update: 更新するフィールドを含むユーザー更新リクエストオブジェクト

    戻り値:
        更新されたユーザーオブジェクト
    """
    # 存在を確認するために現在のユーザーを取得
    current_user_obj = await UserModel.get_or_none(id=user_id)

    if not current_user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    # 他のユーザーのためにユーザー名またはメールアドレスが既に存在するか確認
    if user_update.username:
        existing_user_with_username = await UserModel.get_or_none(
            username=user_update.username
        )
        if existing_user_with_username and existing_user_with_username.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken")

    if user_update.email:
        existing_user_with_email = await UserModel.get_or_none(email=user_update.email)
        if existing_user_with_email and existing_user_with_email.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    # 更新データを準備
    update_data = {}
    if user_update.username:
        update_data["username"] = user_update.username
    if user_update.email:
        update_data["email"] = user_update.email
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.password:
        update_data["hashed_password"] = hash_password(user_update.password)

    # ユーザーを更新
    await UserModel.filter(id=user_id).update(**update_data)

    # 更新されたユーザーを取得
    updated_user_obj = await UserModel.get(id=user_id)

    return updated_user_obj


async def delete_user_account_service(user_id: int):
    """
    現在のユーザーのアカウントを削除（非アクティブ化）するサービス関数。

    引数:
        user_id: 非アクティブ化するユーザーのID

    戻り値:
        成功を示すブール値
    """
    # 存在を確認するためにユーザーを取得
    user = await UserModel.get_or_none(id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 完全削除ではなくユーザーを非アクティブ化
    result = await UserModel.filter(id=user_id).update(is_active=False)

    return result > 0


async def get_user_service(*args, **kwargs):
    """
    IDで特定のユーザーを取得するサービス関数。

    引数:
        user_id: 取得するユーザーのID

    戻り値:
        見つかった場合はユーザーオブジェクト、それ以外はNone
    """
    user = await UserModel.get_or_none(*args, **kwargs)
    return user
