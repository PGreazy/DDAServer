from typing import Any
from typing import Callable
from typing import Coroutine
from typing import TypeAlias
from typing import TypeVar
from django.http import HttpRequest
from django.http import HttpResponse


ChildRequestType = TypeVar("ChildRequestType", bound=HttpRequest)


ResponseProcessor: TypeAlias = Callable[[ChildRequestType], Coroutine[Any, Any, HttpResponse]]
