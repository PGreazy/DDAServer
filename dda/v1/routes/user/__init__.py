import logging
from typing import cast
from ninja import Router

from dda.v1.exceptions import ConflictError
from dda.v1.exceptions import NotFoundError
from dda.v1.exceptions import UnauthorizedError
from dda.v1.exceptions import UnauthenticatedError
from dda.v1.models.user import User
from dda.v1.models.user import UserId
from dda.v1.routes.http import APIRequest
from dda.v1.routes.http import APIResponse
from dda.v1.schemas.user import UserDto
from dda.v1.schemas.user import UserUpdateDto
from dda.v1.services.user import UserService

logger = logging.getLogger("dda")


user_router = Router(tags=["user"])


def authorize_user_is_me(target_user_id: UserId, request_user: User | None) -> None:
    if request_user is None:
        raise UnauthenticatedError()
    if target_user_id != request_user.id:
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
    request: APIRequest, user_id: UserId, update_user_dto: UserUpdateDto
) -> APIResponse[UserDto]:
    authorize_user_is_me(user_id, request.state.user)
    user = await UserService.get_user_by_id(user_id)
    # No need to check if None, we know it is since the only user
    # that can update a profile is the owner of the profile.

    if update_user_dto.email is not None:
        existing_user_with_email = await UserService.get_user_by_email(
            update_user_dto.email
        )
        if existing_user_with_email is not None:
            raise ConflictError(resource_name="User", resource_id=str(user_id))

    updated_user = await UserService.update_user_profile(
        update_user_dto, cast(User, user)
    )
    return APIResponse(data=UserDto.from_orm(updated_user))
