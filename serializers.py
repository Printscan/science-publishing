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
    changes = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = WorkChatMessage
        fields = (
            'id',
            'work',
            'author',
            'author_username',
            'author_display_name',
            'author_status',
            'author_roles',
            'content',
            'metadata',
            'changes',
            'attachments',
            'is_system',
            'created_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'author_username',
            'author_display_name',
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
