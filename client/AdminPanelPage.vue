<template>
  <div class="admin-panel container-fluid py-4">
    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
      <div>
        <h2 class="page-title mb-1">Административная панель</h2>
        <p class="text-muted mb-0">
          Управляйте пользователями, ролями и процессом публикации работ.
        </p>
      </div>
      <button type="button" class="btn btn-outline-secondary" @click="goBack">
        Вернуться к профилю
      </button>
    </div>

    <div v-if="!isAllowed" class="alert alert-warning">
      У вас нет прав для просмотра этой страницы. Обратитесь к администратору.
    </div>

    <div v-else>
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item" v-for="tab in tabs" :key="tab.id">
          <button
            class="nav-link"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </li>
      </ul>

      <!-- USERS TAB -->
      <div v-if="activeTab === 'users'">
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <form class="row g-3 align-items-end" @submit.prevent="loadProfiles">
              <div class="col-md-4">
                <label class="form-label">Имя / логин / почта пользователя</label>
                <input
                  v-model="userFilters.search"
                  type="text"
                  class="form-control"
                  placeholder="Поиск по имени, логину или почте..."
                />
              </div>
              <div class="col-md-3">
                <label class="form-label">Роль</label>
                <select v-model="userFilters.role" class="form-select">
                  <option value="">Все роли</option>
                  <option v-for="role in roles" :key="role.id" :value="role.code">
                    {{ role.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Подразделение</label>
                <input v-model="userFilters.department" type="text" class="form-control" />
              </div>
              <div class="col-md-2 d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="submit" class="btn btn-primary" :disabled="isLoadingProfiles">
                  <span v-if="isLoadingProfiles" class="spinner-border spinner-border-sm me-1" />
                  Найти
                </button>
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="resetUserFilters"
                  :disabled="isLoadingProfiles"
                >
                  Сбросить
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-body">
            <div v-if="profilesError" class="alert alert-danger mb-4">{{ profilesError }}</div>
            <div v-else-if="isLoadingProfiles" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Пользователь</th>
                    <th>Организация</th>
                    <th>Роли</th>
                    <th class="text-end">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="profile in profiles" :key="profile.id">
                    <td>
                      <div class="fw-semibold">{{ profile.display_name || profile.user }}</div>
                      <div class="text-muted small">ID пользователя: {{ profile.user }}</div>
                    </td>
                    <td>{{ profile.organization || 'Не указано' }}</td>
                    <td>
                      <span
                        v-for="role in profile.roles || []"
                        :key="role.id"
                        class="badge text-bg-light me-1 mb-1"
                      >
                        {{ role.name }}
                      </span>
                    </td>
                    <td class="text-end">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-primary"
                        @click="openRoleModal(profile)"
                      >
                        Управлять ролями
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- WORKS TAB -->
      <div v-else-if="activeTab === 'works'">
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <form class="row g-3 align-items-end" @submit.prevent="loadWorks">
              <div class="col-lg-3 col-md-6">
                <label class="form-label">Поиск</label>
                <input
                  v-model="workFilters.search"
                  type="text"
                  class="form-control"
                  placeholder="Название, автор, дисциплина..."
                />
              </div>
              <div class="col-lg-3 col-md-6">
                <label class="form-label">Вид публикации</label>
                <select v-model="workFilters.publication_kind" class="form-select">
                  <option value="">Все</option>
                  <option v-for="item in publicationKinds" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </div>
              <div class="col-lg-3 col-md-6">
                <label class="form-label">Форма обучения</label>
                <select v-model="workFilters.training_form" class="form-select">
                  <option value="">Все</option>
                  <option v-for="item in trainingForms" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </div>
              <div class="col-lg-2 col-md-4">
                <label class="form-label">Год</label>
                <input v-model="workFilters.year" type="number" class="form-control" min="1900" max="2100" />
              </div>
              <div class="col-lg-2 col-md-4">
                <label class="form-label">Статус</label>
                <select v-model="workFilters.status" class="form-select">
                  <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>
              <div class="col-lg-1 col-md-2 d-grid">
                <button type="submit" class="btn btn-primary" :disabled="isLoadingWorks">
                  <span v-if="isLoadingWorks" class="spinner-border spinner-border-sm me-1" />
                  OK
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-body">
            <div v-if="worksError" class="alert alert-danger mb-4">{{ worksError }}</div>
            <div v-else-if="isLoadingWorks" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Дисциплина</th>
                    <th>Автор</th>
                    <th>Тип</th>
                    <th>Форма обучения</th>
                    <th>Год</th>
                    <th>Статус</th>
                    <th>Редактор</th>
                    <th>Документ</th>
                    <th class="text-end">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="work in works" :key="work.id">
                    <td>
                      <div class="fw-semibold">{{ work.discipline_name || 'Без названия' }}</div>
                      <div class="text-muted small">{{ work.discipline_topic || 'Тема не указана' }}</div>
                    </td>
                    <td>{{ work.profile_display_name || work.author_full_name || 'Не указано' }}</td>
                    <td>{{ work.publication_kind_display || work.publication_kind || 'Не указано' }}</td>
                    <td>{{ work.training_form_display || work.training_form || 'Не указано' }}</td>
                    <td>{{ work.year || 'Не указан' }}</td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(work.status)">
                        {{ statusText(work) }}
                      </span>
                      <div v-if="work.published_at" class="text-muted small">
                        {{ formatDate(work.published_at) }}
                      </div>
                    </td>
                    <td>{{ currentEditorLabel(work) || 'Не назначен' }}</td>
                    <td>
                      <a
                        v-if="documentUrl(work)"
                        :href="documentUrl(work)"
                        target="_blank"
                        rel="noopener"
                        class="btn btn-sm btn-outline-primary"
                      >
                        Скачать
                      </a>
                      <span v-else class="text-muted small">Файл не загружен</span>
                    </td>
                    <td class="text-end">
                      <div class="d-flex flex-wrap gap-2 justify-content-end">
                        <button
                          v-if="canAssignEditor(work)"
                          type="button"
                          class="btn btn-sm btn-outline-primary"
                          @click="openAssignModal(work)"
                        >
                          {{ work.current_editor ? 'Сменить редактора' : 'Назначить редактора' }}
                        </button>
                        <button
                          v-if="canRequestChanges(work)"
                          type="button"
                          class="btn btn-sm btn-outline-warning"
                          @click="openChangesModal(work)"
                        >
                          Запросить правки
                        </button>
                        <button
                          v-if="canEditorApprove(work)"
                          type="button"
                          class="btn btn-sm btn-outline-success"
                          @click="editorApproveWork(work)"
                        >
                          Готово для главреда
                        </button>
                        <button
                          v-if="canChiefApprove(work)"
                          type="button"
                          class="btn btn-sm btn-primary"
                          @click="chiefApproveWork(work)"
                        >
                          Утвердить
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Role modal -->
    <div class="modal fade" id="roleModal" tabindex="-1" ref="roleModalRef">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Роли пользователя: {{ selectedProfile?.display_name || selectedProfile?.user }}
            </h5>
            <button type="button" class="btn-close" @click="closeRoleModal"></button>
          </div>
          <div class="modal-body">
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Роль</th>
                    <th>Код</th>
                    <th>Назначена</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="role in roles" :key="role.id">
                    <td>{{ role.name }}</td>
                    <td><code>{{ role.code }}</code></td>
                    <td>
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
                        :disabled="isUpdatingRole || disableRoleChange(role)"
                        @click="toggleRole(role)"
                      >
                        <span v-if="isUpdatingRole && pendingRoleId === role.id" class="spinner-border spinner-border-sm me-2" />
                        {{ assignmentMap[role.id] ? 'Снять' : 'Назначить' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeRoleModal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign editor modal -->
    <div class="modal fade" tabindex="-1" ref="assignModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Назначение редактора</h5>
            <button type="button" class="btn-close" @click="closeAssignModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-3" v-if="assignWorkTarget">
              Работа: {{ assignWorkTarget.discipline_name || 'Без названия' }}
            </p>
            <div class="mb-3">
              <label class="form-label">Редактор</label>
              <select v-model="assignForm.editor" class="form-select">
                <option value="">Выберите редактора</option>
                <option v-for="profile in editorOptions" :key="profile.id" :value="profile.id">
                  {{ profile.display_name || profile.user }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Сообщение</label>
              <textarea
                v-model="assignForm.message"
                class="form-control"
                rows="4"
                placeholder="Сообщение для редактора (необязательно)"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" :disabled="isAssigningEditor" @click="closeAssignModal">
              Отмена
            </button>
            <button type="button" class="btn btn-primary" :disabled="isAssigningEditor" @click="submitAssignEditor">
              <span v-if="isAssigningEditor" class="spinner-border spinner-border-sm me-2"></span>
              Назначить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Author task modal -->
    <div class="modal fade" tabindex="-1" ref="authorTaskModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Задача для автора</h5>
            <button type="button" class="btn-close" @click="closeAuthorTaskModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-2" v-if="authorTaskTarget">
              Работа: {{ authorTaskTarget.discipline_name || 'Без названия' }}
            </p>
            <p class="text-muted small mb-3" v-if="authorTaskRecipientName">
              Автор: {{ authorTaskRecipientName }}
            </p>
            <div class="mb-3">
              <label class="form-label">Тема</label>
              <input
                v-model="authorTaskForm.subject"
                type="text"
                class="form-control"
                placeholder="Введите тему задачи"
              />
            </div>
            <div class="mb-3">
              <label class="form-label">Сообщение *</label>
              <textarea
                v-model="authorTaskForm.message"
                class="form-control"
                rows="4"
                placeholder="Опишите требования для автора"
                required
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-outline-secondary"
              :disabled="isCreatingAuthorTask"
              @click="closeAuthorTaskModal"
            >
              Отмена
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="isCreatingAuthorTask || authorTaskLoadingRecipient"
              @click="submitAuthorTask"
            >
              <span v-if="isCreatingAuthorTask" class="spinner-border spinner-border-sm me-2"></span>
              Отправить задачу
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Request changes modal -->
    <div class="modal fade" tabindex="-1" ref="changesModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Запрос правок</h5>
            <button type="button" class="btn-close" @click="closeChangesModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-3" v-if="changesWorkTarget">
              Работа: {{ changesWorkTarget.discipline_name || 'Без названия' }}
            </p>
            <div class="mb-3">
              <label class="form-label">Комментарий для автора</label>
              <textarea
                v-model="changesMessage"
                class="form-control"
                rows="5"
                placeholder="Опишите, какие правки необходимо внести"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" :disabled="isSubmittingChanges" @click="closeChangesModal">
              Отмена
            </button>
            <button type="button" class="btn btn-primary" :disabled="isSubmittingChanges" @click="submitWorkChanges">
              <span v-if="isSubmittingChanges" class="spinner-border spinner-border-sm me-2"></span>
              Отправить запрос
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { Modal } from 'bootstrap';

import { sciencePublishingAPI } from '@/modules/science_publishing/client/js/science-publishing.js';
import { apiClient } from '@/js/api/manager.js';

const router = useRouter();
const toast = useToast();

const tabs = [
  { id: 'users', label: 'Пользователи' },
  { id: 'works', label: 'Работы' },
];

const statusLabels = {
  draft: 'Черновик',
  pending_chief_review: 'Ожидает главного редактора',
  in_editor_review: 'В работе у редактора',
  waiting_for_author: 'Ожидает правок автора',
  ready_for_chief_approval: 'Ожидает утверждения главреда',
  published: 'Опубликована',
};

const statusBadgeMap = {
  draft: 'text-bg-secondary',
  pending_chief_review: 'text-bg-warning',
  in_editor_review: 'text-bg-info',
  waiting_for_author: 'text-bg-danger',
  ready_for_chief_approval: 'text-bg-primary',
  published: 'text-bg-success',
};

const statusOptions = [
  { value: '', label: 'Все статусы' },
  { value: 'pending_chief_review', label: statusLabels.pending_chief_review },
  { value: 'in_editor_review', label: statusLabels.in_editor_review },
  { value: 'waiting_for_author', label: statusLabels.waiting_for_author },
  { value: 'ready_for_chief_approval', label: statusLabels.ready_for_chief_approval },
  { value: 'published', label: statusLabels.published },
];

const publicationKinds = [
  { value: 'method_guidelines', label: 'Методические рекомендации' },
  { value: 'lab_practicum', label: 'Лабораторный практикум' },
  { value: 'textbook', label: 'Учебник' },
  { value: 'monograph', label: 'Монография' },
  { value: 'article', label: 'Статья' },
  { value: 'theses', label: 'Тезисы' },
];

const trainingForms = [
  { value: 'full_time', label: 'Очная' },
  { value: 'part_time', label: 'Заочная' },
  { value: 'mixed', label: 'Очно-заочная' },
];
const ASSIGNABLE_STATUSES = new Set(['pending_chief_review', 'in_editor_review', 'waiting_for_author', 'ready_for_chief_approval']);

const AUTHOR_TASK_STATUSES = new Set(['pending_chief_review', 'in_editor_review', 'waiting_for_author', 'ready_for_chief_approval']);



const activeTab = ref('users');

const roles = ref([]);
const profiles = ref([]);
const profilesError = ref('');
const isLoadingProfiles = ref(false);

const works = ref([]);
const worksError = ref('');
const isLoadingWorks = ref(false);

const currentProfile = ref(null);

const userFilters = reactive({
  search: '',
  role: '',
  department: '',
});

const workFilters = reactive({
  search: '',
  publication_kind: '',
  training_form: '',
  year: '',
  status: '',
});

const assignmentMap = reactive({});
const selectedProfile = ref(null);
const roleModalRef = ref(null);
let roleModalInstance;

const isUpdatingRole = ref(false);
const pendingRoleId = ref(null);

const assignModalRef = ref(null);
let assignModalInstance;
const assignWorkTarget = ref(null);
const assignForm = reactive({ editor: '', message: '' });
const isAssigningEditor = ref(false);

const authorTaskModalRef = ref(null);

let authorTaskModalInstance;

const authorTaskTarget = ref(null);

const authorTaskForm = reactive({ subject: '', message: '' });

const authorTaskRecipientId = ref(null);

const authorTaskRecipientName = ref('');

const isCreatingAuthorTask = ref(false);

const authorTaskLoadingRecipient = ref(false);

const authorProfileCache = reactive({});



const changesModalRef = ref(null);
let changesModalInstance;
const changesWorkTarget = ref(null);
const changesMessage = ref('');
const isSubmittingChanges = ref(false);

const isAllowed = computed(() =>
  currentProfile.value?.roles?.some((role) => role.code === 'administrator')
);
const isChiefEditor = computed(() =>
  currentProfile.value?.roles?.some((role) => role.code === 'chief_editor')
);
const isEditor = computed(() =>
  currentProfile.value?.roles?.some((role) => role.code === 'editor')
);

const editorOptions = computed(() =>
  (profiles.value || []).filter((profile) =>
    (profile.roles || []).some((role) => role.code === 'editor')
  )
);

const statusText = (work) => work?.status_display || statusLabels[work?.status] || 'Статус не определён';
const statusBadgeClass = (status) => statusBadgeMap[status] || 'text-bg-secondary';

const documentUrl = (work) => {
  if (!work?.document) return null;
  try {
    return new URL(work.document, apiClient.baseUrl).toString();
  } catch {
    const documentPath = work.document.startsWith('/') ? work.document.substring(1) : work.document;
    return `${apiClient.baseUrl}${documentPath}`;
  }
};

const currentEditorLabel = (work) =>
  work?.current_editor_display_name || work?.current_editor_username || '';

const loadRoles = async () => {
  try {
    const response = await sciencePublishingAPI.listRoles();
    const data = response?.data ?? response;
    roles.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (error) {
    toast.error(error?.message || 'Не удалось загрузить справочник ролей.');
  }
};

const loadProfiles = async () => {
  if (!isAllowed.value) return;
  isLoadingProfiles.value = true;
  profilesError.value = '';
  try {
    const params = {};
    if (userFilters.search) params.search = userFilters.search;
    if (userFilters.role) params['roles__code'] = userFilters.role;
    if (userFilters.department) params.department = userFilters.department;
    const response = await sciencePublishingAPI.listProfiles(params);
    const data = response?.data ?? response;
    profiles.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (error) {
    profilesError.value = error?.message || 'Не удалось загрузить список пользователей.';
    profiles.value = [];
  } finally {
    isLoadingProfiles.value = false;
  }
};

const loadWorks = async () => {
  if (!isAllowed.value) return;
  isLoadingWorks.value = true;
  worksError.value = '';
  try {
    const params = {};
    if (workFilters.search) params.search = workFilters.search;
    if (workFilters.publication_kind) params.publication_kind = workFilters.publication_kind;
    if (workFilters.training_form) params.training_form = workFilters.training_form;
    if (workFilters.year) params.year = workFilters.year;
    if (workFilters.status) params.status = workFilters.status;
    const response = await sciencePublishingAPI.listWorks(params);
    const data = response?.data ?? response;
    works.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (error) {
    worksError.value = error?.message || 'Не удалось загрузить список работ.';
    works.value = [];
  } finally {
    isLoadingWorks.value = false;
  }
};

const resetUserFilters = () => {
  userFilters.search = '';
  userFilters.role = '';
  userFilters.department = '';
  loadProfiles();
};

const goBack = () => {
  router.push({ name: 'SciencePublishingProfile' });
};

const openRoleModal = (profile) => {
  selectedProfile.value = profile;
  Object.keys(assignmentMap).forEach((key) => delete assignmentMap[key]);
  (profile.role_assignments || []).forEach((assignment) => {
    if (assignment.role) {
      assignmentMap[assignment.role.id ?? assignment.role] = assignment.id;
    }
  });
  if (!roleModalInstance) {
    roleModalInstance = new Modal(roleModalRef.value);
  }
  roleModalInstance.show();
};

const closeRoleModal = () => {
  roleModalInstance?.hide();
  selectedProfile.value = null;
};

const disableRoleChange = (role) => {
  if (role.code !== 'administrator') return false;
  if (!selectedProfile.value) return true;
  const hasAdminRole = (selectedProfile.value.roles || []).some((item) => item.code === 'administrator');
  return hasAdminRole && selectedProfile.value.id === currentProfile.value?.id;
};

const toggleRole = async (role) => {
  if (!selectedProfile.value?.id) return;
  isUpdatingRole.value = true;
  pendingRoleId.value = role.id;
  try {
    const existing = assignmentMap[role.id];
    if (existing) {
      await sciencePublishingAPI.removeRole(existing);
      delete assignmentMap[role.id];
      selectedProfile.value.roles = (selectedProfile.value.roles || []).filter((r) => r.id !== role.id);
      toast.success(`Роль ${role.name} снята.`);
    } else {
      const response = await sciencePublishingAPI.assignRole(selectedProfile.value.id, role.id);
      const assignment = response?.data ?? response;
      if (assignment?.id) {
        assignmentMap[role.id] = assignment.id;
      }
      selectedProfile.value.roles = [...(selectedProfile.value.roles || []), role];
      toast.success(`Роль ${role.name} назначена.`);
    }
    await loadProfiles();
  } catch (error) {
    toast.error(error?.message || 'Не удалось изменить роли пользователя.');
  } finally {
    pendingRoleId.value = null;
    isUpdatingRole.value = false;
  }
};

const ensureAssignModal = () => {
  if (!assignModalInstance && assignModalRef.value) {
    assignModalInstance = new Modal(assignModalRef.value, { backdrop: 'static' });
  }
};

const ensureAuthorTaskModal = () => {
  if (!authorTaskModalInstance && authorTaskModalRef.value) {
    authorTaskModalInstance = new Modal(authorTaskModalRef.value, { backdrop: 'static' });
  }
};

const ensureChangesModal = () => {
  if (!changesModalInstance && changesModalRef.value) {
    changesModalInstance = new Modal(changesModalRef.value, { backdrop: 'static' });
  }
};

const openAssignModal = (work) => {
  assignWorkTarget.value = work;
  assignForm.editor = work?.current_editor || '';
  assignForm.message = '';
  ensureAssignModal();
  assignModalInstance?.show();
};

const closeAssignModal = () => {
  assignModalInstance?.hide();
  assignWorkTarget.value = null;
  assignForm.editor = '';
  assignForm.message = '';
};

const authorTaskDefaultSubject = (work) => {
  const title = work?.discipline_name || work?.publication_kind_display || work?.publication_kind || 'работе';
  return `Задача по работе ${title}`;
};

const resolveAuthorRecipient = async (profileId) => {
  if (!profileId) {
    throw new Error('Не удалось определить профиль автора.');
  }
  if (authorProfileCache[profileId]) {
    return authorProfileCache[profileId];
  }
  const response = await sciencePublishingAPI.getProfile(profileId);
  const data = response?.data ?? response;
  const userId = data?.user;
  if (!userId) {
    throw new Error('Не удалось определить пользователя автора.');
  }
  const record = {
    userId,
    displayName: data?.display_name || '',
  };
  authorProfileCache[profileId] = record;
  return record;
};

const openAuthorTaskModal = async (work) => {
  if (!isChiefEditor.value) return;
  if (!work?.profile) {
    toast.error('Не удалось определить профиль автора.');
    return;
  }
  authorTaskLoadingRecipient.value = true;
  try {
    const recipient = await resolveAuthorRecipient(work.profile);
    authorTaskRecipientId.value = recipient.userId;
    authorTaskRecipientName.value = recipient.displayName || work.profile_display_name || work.author_full_name || '—';
    authorTaskTarget.value = work;
    authorTaskForm.subject = authorTaskDefaultSubject(work);
    authorTaskForm.message = '';
    ensureAuthorTaskModal();
    authorTaskModalInstance?.show();
  } catch (error) {
    toast.error(error?.message || 'Не удалось получить данные автора.');
  } finally {
    authorTaskLoadingRecipient.value = false;
  }
};

const closeAuthorTaskModal = () => {
  authorTaskModalInstance?.hide();
  authorTaskTarget.value = null;
  authorTaskForm.subject = '';
  authorTaskForm.message = '';
  authorTaskRecipientId.value = null;
  authorTaskRecipientName.value = '';
};

const submitAssignEditor = async () => {
  if (!assignWorkTarget.value) return;
  if (!assignForm.editor) {
    toast.error('Выберите редактора.');
    return;
  }
  isAssigningEditor.value = true;
  try {
    await sciencePublishingAPI.assignWorkEditor(assignWorkTarget.value.id, {
      editor_profile: assignForm.editor,
      message: assignForm.message ? assignForm.message : undefined,
    });
    toast.success('Редактор назначен.');
    closeAssignModal();
    await loadWorks();
  } catch (error) {
    toast.error(error?.message || 'Не удалось назначить редактора.');
  } finally {
    isAssigningEditor.value = false;
  }
};
const submitAuthorTask = async () => {
  if (!authorTaskTarget.value || !authorTaskRecipientId.value) return;
  const subject = (authorTaskForm.subject || '').trim() || authorTaskDefaultSubject(authorTaskTarget.value);
  const message = (authorTaskForm.message || '').trim();
  if (!message) {
    toast.error('Добавьте сообщение для автора.');
    return;
  }

  isCreatingAuthorTask.value = true;
  try {
    await sciencePublishingAPI.createTask({
      work: authorTaskTarget.value.id,
      recipient: authorTaskRecipientId.value,
      subject,
      message,
    });
    toast.success('Задача отправлена автору.');
    closeAuthorTaskModal();
  } catch (error) {
    toast.error(error?.message || 'Не удалось отправить задачу автору.');
  } finally {
    isCreatingAuthorTask.value = false;
  }
};



const openChangesModal = (work) => {
  changesWorkTarget.value = work;
  changesMessage.value = '';
  ensureChangesModal();
  changesModalInstance?.show();
};

const closeChangesModal = () => {
  changesModalInstance?.hide();
  changesWorkTarget.value = null;
  changesMessage.value = '';
};

const submitWorkChanges = async () => {
  if (!changesWorkTarget.value) return;
  const message = changesMessage.value.trim();
  if (!message) {
    toast.error('Опишите необходимые правки.');
    return;
  }
  isSubmittingChanges.value = true;
  try {
    await sciencePublishingAPI.requestWorkChanges(changesWorkTarget.value.id, { message });
    toast.success('Запрос на правки отправлен.');
    closeChangesModal();
    await loadWorks();
  } catch (error) {
    toast.error(error?.message || 'Не удалось отправить запрос на правки.');
  } finally {
    isSubmittingChanges.value = false;
  }
};

const editorApproveWork = async (work) => {
  if (!work) return;
  const note = window.prompt('Комментарий для главного редактора (необязательно)', '');
  try {
    await sciencePublishingAPI.approveWorkAsEditor(work.id, { message: note?.trim() || undefined });
    toast.success('Работа передана главному редактору.');
    await loadWorks();
  } catch (error) {
    toast.error(error?.message || 'Не удалось обновить статус.');
  }
};

const chiefApproveWork = async (work) => {
  if (!work) return;
  const confirmed = window.confirm('Утвердить работу и перевести её в статус «Опубликована»?');
  if (!confirmed) return;
  const note = window.prompt('Комментарий для участников (необязательно)', '');
  try {
    await sciencePublishingAPI.approveWorkAsChief(work.id, { message: note?.trim() || undefined });
    toast.success('Работа утверждена.');
    await loadWorks();
  } catch (error) {
    toast.error(error?.message || 'Не удалось обновить статус.');
  }
};

const canAssignEditor = (work) => isChiefEditor.value && work && ASSIGNABLE_STATUSES.has(work.status);
const canCreateAuthorTask = (work) =>
  isChiefEditor.value && work?.profile && AUTHOR_TASK_STATUSES.has(work.status);
const canRequestChanges = (work) =>
  isEditor.value &&
  work?.current_editor === currentProfile.value?.id &&
  work?.status === 'in_editor_review';
const canEditorApprove = (work) =>
  isEditor.value &&
  work?.current_editor === currentProfile.value?.id &&
  ['in_editor_review', 'waiting_for_author'].includes(work?.status);
const canChiefApprove = (work) => isChiefEditor.value && work?.status === 'ready_for_chief_approval';

const formatDate = (value) => {
  if (!value) return '';
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return value;
  }
};

const loadCurrentProfile = async () => {
  try {
    const response = await sciencePublishingAPI.getCurrentProfile();
    currentProfile.value = response?.data ?? response;
  } catch {
    currentProfile.value = null;
  }
};

const init = async () => {
  await loadCurrentProfile();
  if (!isAllowed.value) {
    toast.error('Недостаточно прав для просмотра страницы.');
    router.replace({ name: 'SciencePublishingProfile' });
    return;
  }
  ensureAssignModal();
  ensureAuthorTaskModal();
  ensureChangesModal();
  await loadRoles();
  await Promise.all([loadProfiles(), loadWorks()]);
};

onMounted(init);
</script>

<style scoped lang="scss">
.admin-panel {
  .page-title {
    font-size: 1.875rem;
    font-weight: 600;
  }

  .nav-link {
    cursor: pointer;
  }
}
</style>
