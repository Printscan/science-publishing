from rest_framework import serializers

from .models import (
    EditorialRole,
    UserProfile,
    UserProfileRole,
    Work,
    Publication,
    WorkChatMessage,
)


class EditorialRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorialRole
        fields = ('id', 'code', 'name', 'description')
        ref_name = 'SciencePublishingEditorialRole'


class UserProfileRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    profile_display_name = serializers.CharField(source='profile.display_name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = UserProfileRole
        fields = (
            'id',
            'profile',
            'profile_display_name',
            'role',
            'role_name',
            'assigned_by',
            'assigned_by_username',
            'assigned_at',
            'expires_at',
            'notes',
        )
        read_only_fields = ('assigned_at', 'assigned_by')
        ref_name = 'SciencePublishingUserProfileRole'


class WorkSerializer(serializers.ModelSerializer):
    publication_kind_display = serializers.CharField(source='get_publication_kind_display', read_only=True)
    guideline_subtype_display = serializers.CharField(source='get_guideline_subtype_display', read_only=True)
    training_form_display = serializers.CharField(source='get_training_form_display', read_only=True)
    profile_display_name = serializers.CharField(source='profile.display_name', read_only=True)
    author_display_name = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_editor_display_name = serializers.SerializerMethodField()
    current_editor_username = serializers.SerializerMethodField()
    current_editor_user_id = serializers.SerializerMethodField()
    profile_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        ref_name = 'SciencePublishingWork'
        extra_kwargs = {
            'profile': {'read_only': True},
            'status': {'read_only': True},
            'current_editor': {'read_only': True},
            'published_at': {'read_only': True},
        }

    def get_current_editor_display_name(self, obj):
        profile = getattr(obj, 'current_editor', None)
        if not profile:
            return None
        return profile.display_name or profile.user.get_full_name() or profile.user.get_username()

    def get_current_editor_username(self, obj):
        profile = getattr(obj, 'current_editor', None)
        if not profile or not getattr(profile, 'user', None):
            return None
        return profile.user.get_username()

    def get_current_editor_user_id(self, obj):
        profile = getattr(obj, 'current_editor', None)
        if not profile or not getattr(profile, 'user', None):
            return None
        return profile.user.id

    def get_profile_user_id(self, obj):
        user = getattr(getattr(obj, 'profile', None), 'user', None)
        return user.id if user else None

    def get_author_display_name(self, obj):
        profile = getattr(obj, 'profile', None)
        user = getattr(profile, 'user', None)
        candidates = [
            getattr(profile, 'display_name', '') if profile else '',
            getattr(obj, 'author_full_name', ''),
            user.get_full_name() if user else '',
            user.get_username() if user else '',
        ]
        for value in candidates:
            if value:
                return value
        return None

    def get_author_username(self, obj):
        user = getattr(getattr(obj, 'profile', None), 'user', None)
        return user.get_username() if user else None


class PublicationSerializer(serializers.ModelSerializer):
    publication_kind_display = serializers.CharField(source='get_publication_kind_display', read_only=True)
    guideline_subtype_display = serializers.CharField(source='get_guideline_subtype_display', read_only=True)
    training_form_display = serializers.CharField(source='get_training_form_display', read_only=True)
    profile_display_name = serializers.CharField(source='profile.display_name', read_only=True)
    author_display_name = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_editor_display_name = serializers.SerializerMethodField()
    current_editor_username = serializers.SerializerMethodField()
    current_editor_user_id = serializers.SerializerMethodField()
    profile_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        ref_name = 'SciencePublishingPublication'
        extra_kwargs = {
            'profile': {'read_only': True},
            'status': {'read_only': True},
        }

    def get_current_editor_display_name(self, obj):
        profile = getattr(obj, 'current_editor', None)
        if not profile:
            return None
        return profile.display_name or profile.user.get_full_name() or profile.user.get_username()

    def get_current_editor_username(self, obj):
        profile = getattr(obj, 'current_editor', None)
        if not profile or not getattr(profile, 'user', None):
            return None
        return profile.user.get_username()

    def get_current_editor_user_id(self, obj):
        profile = getattr(obj, 'current_editor', None)
        if not profile or not getattr(profile, 'user', None):
            return None
        return profile.user.id

    def get_profile_user_id(self, obj):
        user = getattr(getattr(obj, 'profile', None), 'user', None)
        return user.id if user else None

    def get_author_display_name(self, obj):
        profile = getattr(obj, 'profile', None)
        user = getattr(profile, 'user', None)
        candidates = [
            getattr(profile, 'display_name', '') if profile else '',
            getattr(obj, 'author_full_name', ''),
            user.get_full_name() if user else '',
            user.get_username() if user else '',
        ]
        for value in candidates:
            if value:
                return value
        return None

    def get_author_username(self, obj):
        user = getattr(getattr(obj, 'profile', None), 'user', None)
        return user.get_username() if user else None

class UserProfileSerializer(serializers.ModelSerializer):
    roles = EditorialRoleSerializer(many=True, read_only=True)
    works = WorkSerializer(many=True, read_only=True)
    publications = PublicationSerializer(many=True, read_only=True)
    role_assignments = UserProfileRoleSerializer(source='profile_roles', many=True, read_only=True)

    class Meta:
        model = UserProfile
        ref_name = 'SciencePublishingUserProfile'
        fields = (
            'id',
            'user',
            'display_name',
            'organization',
            'department',
            'position',
            'academic_degree',
            'academic_title',
            'phone',
            'orcid',
            'scopus_id',
            'elibrary_id',
            'website',
            'biography',
            'is_active',
            'created_at',
            'updated_at',
            'roles',
            'role_assignments',
            'works',
            'publications',
        )
        read_only_fields = ('created_at', 'updated_at')


class WorkChatMessageSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_display_name = serializers.SerializerMethodField()
    author_status = serializers.SerializerMethodField()
    author_roles = serializers.SerializerMethodField()
    author_profile_id = serializers.SerializerMethodField()
    changes = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    delivery_status = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = WorkChatMessage
        fields = (
            'id',
            'work',
            'author',
            'author_username',
            'author_display_name',
            'author_profile_id',
            'author_status',
            'author_roles',
            'content',
            'metadata',
            'changes',
            'attachments',
            'is_system',
            'delivery_status',
            'read_at',
            'read_by',
            'is_read',
            'created_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'author_username',
            'author_display_name',
            'author_profile_id',
            'author_status',
            'author_roles',
            'changes',
            'attachments',
            'is_system',
        )
        extra_kwargs = {
            'work': {'read_only': True},
            'author': {'read_only': True},
            'metadata': {'required': False},
        }
        ref_name = 'SciencePublishingWorkChatMessage'

    def get_author_display_name(self, obj):
        profile = getattr(obj.author, 'science_publishing_profile', None)
        if profile:
            return profile.display_name or obj.author.get_full_name() or obj.author.username
        return obj.author.get_full_name() or obj.author.username

    def get_author_profile_id(self, obj):
        profile = getattr(obj.author, 'science_publishing_profile', None)
        return getattr(profile, 'id', None)

    def get_author_roles(self, obj):
        cached = getattr(obj, '_cached_author_roles', None)
        if cached is not None:
            return cached
        if obj.is_system:
            result = [{'code': 'system', 'name': 'Система'}]
            obj._cached_author_roles = result
            return result
        profile = getattr(obj.author, 'science_publishing_profile', None)
        if not profile:
            obj._cached_author_roles = []
            return []
        roles = getattr(profile, '_prefetched_objects_cache', {}).get('roles')
        if roles is None:
            roles = profile.roles.all()
        result = [{'code': role.code, 'name': role.name} for role in roles]
        obj._cached_author_roles = result
        return result

    def _get_receipts(self, obj):
        receipts = getattr(obj, '_prefetched_receipts', None)
        if receipts is not None:
            return receipts
        return list(obj.receipts.select_related('recipient'))

    def get_delivery_status(self, obj):
        """
        Telegram-like ticks:
        - 'sent' (1 галка) если доставлено (есть квитанция)
        - 'read' (2 галки) если хоть кто-то прочитал (для автора) или текущий получатель прочитал (для получателя)
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        receipts = self._get_receipts(obj)
        if not receipts:
            return 'pending'
        # если отправитель смотрит
        if user and getattr(user, 'id', None) == getattr(obj.author, 'id', None):
            if any(r.read_at for r in receipts):
                return 'read'
            return 'sent'

        if user:
            for r in receipts:
                if r.recipient_id == user.id:
                    return 'read' if r.read_at else 'sent'
        # по умолчанию, если квитанции есть
        return 'sent'

    def get_read_at(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user:
            return None
        receipts = self._get_receipts(obj)
        for r in receipts:
            if r.recipient_id == user.id and r.read_at:
                return r.read_at
        return None

    def get_read_by(self, obj):
        receipts = self._get_receipts(obj)
        readers = []
        for r in receipts:
            if r.read_at:
                readers.append(
                    {
                        'user_id': r.recipient_id,
                        'username': getattr(r.recipient, 'username', None),
                        'read_at': r.read_at,
                    }
                )
        return readers

    def get_is_read(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user:
            return False
        receipts = self._get_receipts(obj)
        for r in receipts:
            if r.recipient_id == user.id and r.read_at:
                return True
        return False

    def get_author_status(self, obj):
        roles = self.get_author_roles(obj)
        if not roles:
            if obj.is_system:
                return 'Система'
            return None
        return roles[0]['name']

    def get_changes(self, obj):
        if not obj.metadata:
            return []
        return obj.metadata.get('changes', [])

    def get_attachments(self, obj):
        if not obj.metadata:
            return []
        attachments = obj.metadata.get('attachments', []) or []
        request = self.context.get('request')
        result = []
        for attachment in attachments:
            item = dict(attachment)
            url = item.get('url')
            if url and request and not url.startswith('http'):
                try:
                    item['absolute_url'] = request.build_absolute_uri(url)
                except Exception:  # pragma: no cover - safety net
                    item['absolute_url'] = url
            result.append(item)
        return result
