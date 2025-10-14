<template>
  <div class="container py-4 dev-roles">
    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
      <div>
        <h2 class="page-title mb-1">Роли пользователя Palmatorro</h2>
        <p class="text-muted mb-0">
          Страница доступна только в режиме разработки. Изменения затрагивают тестовые данные.
        </p>
      </div>
      <button type="button" class="btn btn-outline-secondary" @click="goBack">
        Вернуться к профилю
      </button>
    </div>

    <div v-if="loadError" class="alert alert-danger">{{ loadError }}</div>

    <div class="card shadow-sm">
      <div class="card-body">
        <div v-if="isLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
        </div>

        <template v-else>
          <div class="mb-4">
            <h5 class="mb-1">{{ profileName }}</h5>
            <p class="text-muted mb-0">
              ID пользователя: <strong>{{ profile?.user || '—' }}</strong>
            </p>
          </div>

          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Роль</th>
                  <th>Код</th>
                  <th class="text-center">Назначена</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="role in roles" :key="role.id">
                  <td>{{ role.name }}</td>
                  <td><code>{{ role.code }}</code></td>
                  <td class="text-center">
                    <span
                      class="badge"
                      :class="assignmentMap[role.id] ? 'text-bg-success' : 'text-bg-secondary'"
                    >
                      {{ assignmentMap[role.id] ? 'Да' : 'Нет' }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button
                      type="button"
                      class="btn btn-sm"
                      :class="assignmentMap[role.id] ? 'btn-outline-danger' : 'btn-outline-primary'"
                      :disabled="isSaving"
                      @click="toggleRole(role)"
                    >
                      <span v-if="isSaving && pendingRoleId === role.id" class="spinner-border spinner-border-sm me-2" />
                      {{ assignmentMap[role.id] ? 'Снять роль' : 'Назначить' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { sciencePublishingAPI } from '@/modules/science-publishing/js/science-publishing.js';

const router = useRouter();
const toast = useToast();
const devRolesEnabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_ROLES === 'true';

const isLoading = ref(true);
const isSaving = ref(false);
const loadError = ref('');
const roles = ref([]);
const profile = ref(null);
const assignmentMap = reactive({});
const pendingRoleId = ref(null);

const profileName = computed(() => profile.value?.display_name || 'Palmatorro');

const fetchData = async () => {
  isLoading.value = true;
  loadError.value = '';
  Object.keys(assignmentMap).forEach((key) => delete assignmentMap[key]);
  try {
    // загрузка всех ролей
    const rolesResponse = await sciencePublishingAPI.listRoles();
    const rolesData = Array.isArray(rolesResponse?.data) ? rolesResponse.data : rolesResponse?.data?.results ?? [];
    roles.value = rolesData;

    // загрузка профиля Palmatorro
    const profileResponse = await sciencePublishingAPI.fetchProfileByUsername('Palmatorro');
    const profileList = Array.isArray(profileResponse?.data)
      ? profileResponse.data
      : profileResponse?.data?.results ?? [];
    if (!profileList.length) {
      throw new Error('Профиль Palmatorro не найден.');
    }
    profile.value = profileList[0];

    // подготовка карты назначений
    const assignments = profile.value?.role_assignments ?? [];
    assignments.forEach((assignment) => {
      if (assignment.role) {
        assignmentMap[assignment.role] = assignment.id;
      }
    });
  } catch (error) {
    loadError.value = error?.message || 'Не удалось загрузить данные.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  if (!devRolesEnabled) {
    toast.error('Страница доступна только в режиме разработки.');
    router.replace({ name: 'SciencePublishingProfile' });
    return;
  }
  await fetchData();
});

const goBack = () => {
  router.push({ name: 'SciencePublishingProfile' });
};

const toggleRole = async (role) => {
  if (!profile.value?.id) {
    toast.error('Профиль ещё не загружен.');
    return;
  }

  isSaving.value = true;
  pendingRoleId.value = role.id;
  try {
    const assignmentId = assignmentMap[role.id];
    if (assignmentId) {
      await sciencePublishingAPI.removeRole(assignmentId);
      delete assignmentMap[role.id];
      toast.success(`Роль «${role.name}» снята.`);
    } else {
      const response = await sciencePublishingAPI.assignRole(profile.value.id, role.id);
      const assignment = response?.data ?? response;
      if (assignment?.id) {
        assignmentMap[role.id] = assignment.id;
      }
      toast.success(`Роль «${role.name}» назначена.`);
    }
  } catch (error) {
    toast.error(error?.message || 'Не удалось выполнить операцию с ролью.');
  } finally {
    pendingRoleId.value = null;
    isSaving.value = false;
  }
};
</script>

<style scoped lang="scss">
.dev-roles {
  .page-title {
    font-size: 1.75rem;
    font-weight: 600;
  }

  .table {
    th,
    td {
      vertical-align: middle;
    }
  }
}
</style>
