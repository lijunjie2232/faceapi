from ..models import UserModel
from ..utils import hash_password
from ..core import _CONFIG_

async def create_init_account():
    """
    Create the init account
    
    default init account:
        ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
        ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
        ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
        ADMIN_FULL_NAME: str = os.getenv("ADMIN_FULL_NAME", "Administrator")
    """

    hashed_password = hash_password(_CONFIG_.ADMIN_PASSWORD)

    created_user = await UserModel.get_or_create(
        username=_CONFIG_.ADMIN_USERNAME,
        email=_CONFIG_.ADMIN_EMAIL,
        full_name=_CONFIG_.ADMIN_FULL_NAME,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=True,
    )

    assert created_user is not None, "Failed to create init account"
    return