from django.contrib import admin

from .models import EditorialRole, EditorialTask, UserProfile, UserProfileRole, Work


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


@admin.register(EditorialTask)
class EditorialTaskAdmin(admin.ModelAdmin):
    list_display = ('subject', 'work', 'recipient', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'recipient__username', 'recipient__last_name', 'work__discipline_name')
    autocomplete_fields = ('work', 'recipient', 'sender')
