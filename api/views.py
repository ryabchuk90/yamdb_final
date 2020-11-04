from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import filters, status, viewsets, exceptions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .filters import TitlesFilter
from .services.email_service import send_confirmition_email
from .serializers import (ConfirmationCodeSerializer, UserSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer)
from .premissions import IsCustomAdmin, IsAuthor, IsCustomModerator
from .models import ConfirmationCode, Category, Genre, Title, Review

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCustomAdmin]
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    @action(methods=['get', 'patch'], detail=False, permission_classes=[IsAuthenticated],
            url_path='me', url_name='profile')
    def profile(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            data = request.data.copy()
            data['username'] = request.user.username
            data['email'] = request.user.email
            serializer = UserSerializer(request.user, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    email = request.data.get('email')
    try:
        confirmation_code_object = ConfirmationCode.objects.get(email=email)
        serializer = ConfirmationCodeSerializer(
            confirmation_code_object,
            data={'email': email},
            partial=True
        )
    except ConfirmationCode.DoesNotExist:
        serializer = ConfirmationCodeSerializer(data=request.data)

    if serializer.is_valid():
        confirmation_code = get_random_string(length=16)
        is_sent = send_confirmition_email(
            email=email,
            confirmation_code=confirmation_code
        )

        if is_sent:
            serializer.save(confirmation_code=confirmation_code)
            return Response(
                {'message': f'Check your email inbox ({email}) for confirmation.'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': 'Here was an error while sending confirmation email.'},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')

    try:
        ConfirmationCode.objects.get(
            email=email, confirmation_code=confirmation_code)
    except ConfirmationCode.DoesNotExist:
        return Response(
            {'message': 'Invalid email or confirmation code.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create(email=email, username=email)

    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    return Response(
        {'token': token},
        status=status.HTTP_200_OK
    )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsCustomAdmin]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, slug):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, slug):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsCustomAdmin]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, slug):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, slug):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            self.permission_classes = [IsCustomAdmin]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthor |
                                       IsCustomModerator | IsCustomAdmin]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAuthor |
                                       IsCustomModerator | IsCustomAdmin]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        title = Title.objects.get(pk=self.kwargs['title_id'])
        return title.review.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])

        if Review.objects.filter(author=self.request.user, title=title).exists():
            raise exceptions.ValidationError('Вы уже оставили отзыв')
        serializer.save(author=self.request.user, title=title)

        avg_score = Review.objects.filter(title=title).aggregate(Avg('score'))

        title.rating = avg_score['score__avg']
        title.save(update_fields=['rating'])

    def perform_update(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)
        avg_score = Review.objects.filter(title=title).aggregate(Avg('score'))

        title.rating = avg_score['score__avg']
        title.save(update_fields=['rating'])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthor |
                                       IsCustomModerator | IsCustomAdmin]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAuthor |
                                       IsCustomModerator | IsCustomAdmin]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        review = Review.objects.get(pk=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])

        serializer.save(author=self.request.user, review=review)
