from django.contrib import admin

from .models import EditorialRole, UserProfile, UserProfileRole, Work, WorkChatMessage


@admin.register(EditorialRole)
class EditorialRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)


class UserProfileRoleInline(admin.TabularInline):
    model = UserProfileRole
    extra = 0
    autocomplete_fields = ('role',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'is_active')
    search_fields = ('display_name', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('is_active',)
    inlines = (UserProfileRoleInline,)
    autocomplete_fields = ('user',)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('discipline_name', 'year', 'publication_kind', 'profile')
    list_filter = ('publication_kind', 'training_form', 'year')
    search_fields = ('discipline_name', 'discipline_topic', 'author_full_name', 'profile__display_name')
    autocomplete_fields = ('profile',)


@admin.register(WorkChatMessage)
class WorkChatMessageAdmin(admin.ModelAdmin):
    list_display = ('work', 'author', 'is_system', 'created_at')
    list_filter = ('is_system', 'created_at')
    search_fields = ('content', 'author__username', 'author__last_name', 'work__discipline_name')
    autocomplete_fields = ('work', 'author')
