from rest_framework.views import APIView
from rest_framework import status
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import AuthTokenSerializer, TokenSerializer

from ..serializers import UserTokenSerializer


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context=request)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            try:
                token = user.token
            except:
                token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': TokenSerializer(instance=token).data,
                'user': UserTokenSerializer(instance=user).data
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

obtain_auth_token = ObtainAuthToken.as_view()
