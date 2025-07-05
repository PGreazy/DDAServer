import logging

from ninja import Router

from dda.v1.exceptions import NotFoundError
from dda.v1.exceptions import UnauthorizedError
from dda.v1.models.user import User
from dda.v1.models.user import UserId
from dda.v1.routes.http import APIRequest
from dda.v1.routes.http import APIResponse
from dda.v1.schemas.user import UserDto
from dda.v1.services.user import UserService

logger = logging.getLogger("dda")


user_router = Router(tags=["user"])


def authorize_user_is_me(target_user_id: UserId, user: User):
    if target_user_id != user.id:
        raise UnauthorizedError(resource_name="User", resource_id=str(target_user_id))


@user_router.get(
    by_alias=True,
    path="/{user_id}",
    response=APIResponse[UserDto],
    summary="Get the a user's profile.",
)
async def get_user_profile(
    request: APIRequest, user_id: UserId
) -> APIResponse[UserDto]:
    authorize_user_is_me(user_id, request.state.user)
    user = await UserService.get_user_by_id(user_id)
    if user is None:
        raise NotFoundError(resource_name="User", resource_id=str(user_id))
    return APIResponse(data=UserDto.from_orm(user))


@user_router.patch(
    by_alias=True,
    path="/{user_id}",
    response=APIResponse[UserDto],
    summary="Update a user's profile.",
)
async def update_user_profile(
    request: APIRequest, user_id: UserId
) -> APIResponse[UserDto]:
    pass
