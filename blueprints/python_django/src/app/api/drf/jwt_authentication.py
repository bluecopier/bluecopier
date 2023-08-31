#
#
# if TYPE_CHECKING:
#
#
# class AuthorizationHeaderParseResult(NamedTuple):
#
#
# # Note: This depends on a tenant so we know which public key to use to decode
# def parse_authorization_header(
#     *,
#     authorization_header: str,
# ) -> AuthorizationHeaderParseResult:
#     if not authorization_header.startswith("Bearer "):
#
#
#         strategy,
#         backend,
#
#             strategy,
#             backend,
#
#
#     return AuthorizationHeaderParseResult(
#
#
# class JWTAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request: Request) -> tuple[User, str] | None:
#
#
#
#     def authenticate_header(self, request: Request) -> str:
