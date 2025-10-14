<template>
  <div class="science-profile container-fluid py-4">
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
      <div>
        <h2 class="page-title mb-1">Профиль научных публикаций</h2>
        <p class="text-muted mb-0">
          Управляйте личными данными, следите за статусами работ и общайтесь с редакторами прямо здесь.
        </p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button
          type="button"
          class="btn btn-outline-primary d-flex align-items-center gap-2"
          :disabled="isLoadingProfile || isLoadingWorks || isLoadingTasks"
          @click="refreshAll"
        >
          <RefreshCcw size="16" />
          <span>Обновить данные</span>
        </button>
        <button
          type="button"
          class="btn btn-primary d-flex align-items-center gap-2"
          @click="goToSubmit"
        >
          <FilePlus size="16" />
          <span>Подать работу</span>
        </button>
        <button
          v-if="isAdministrator"
          type="button"
          class="btn btn-outline-success d-flex align-items-center gap-2"
          @click="goToAdminPanel"
        >
          <Shield size="16" />
          <span>Администрирование</span>
        </button>
        <button
          v-if="devRolesEnabled"
          type="button"
          class="btn btn-outline-secondary d-flex align-items-center gap-2"
          @click="goToDevRoles"
        >
          <Users size="16" />
          <span>Управление ролями (dev)</span>
        </button>
      </div>
    </div>

    <div v-if="profileError || worksError || tasksError" class="alert alert-danger mb-4">
      <p v-if="profileError" class="mb-1">{{ profileError }}</p>
      <p v-if="worksError" class="mb-1">{{ worksError }}</p>
      <p v-if="tasksError" class="mb-0">{{ tasksError }}</p>
    </div>

    <div class="row g-4">
      <div class="col-xl-4">
        <div class="card shadow-sm h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Профиль</h5>
            <div v-if="!isLoadingProfile">
              <button
                v-if="!isEditing"
                type="button"
                class="btn btn-sm btn-outline-primary d-flex align-items-center gap-2"
                @click="startEditing"
              >
                <Contact size="14" />
                <span>Редактировать</span>
              </button>
              <div v-else class="d-flex gap-2">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  :disabled="isSaving"
                  @click="cancelEditing"
                >
                  Отмена
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-primary"
                  :disabled="isSaving"
                  @click="saveProfile"
                >
                  <span v-if="isSaving" class="spinner-border spinner-border-sm me-2" />
                  Сохранить
                </button>
              </div>
            </div>
          </div>

          <div v-if="isLoadingProfile" class="card-body text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Загрузка...</span>
            </div>
          </div>

          <template v-else>
            <div v-if="isEditing" class="card-body">
              <form class="profile-form" @submit.prevent="saveProfile">
                <div class="mb-3">
                  <label class="form-label">Отображаемое имя</label>
                  <input v-model="form.display_name" type="text" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Телефон</label>
                  <input v-model="form.phone" type="text" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Организация</label>
                  <input v-model="form.organization" type="text" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Подразделение</label>
                  <input v-model="form.department" type="text" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">Должность</label>
                  <input v-model="form.position" type="text" class="form-control" />
                </div>
                <div class="row g-3">
                  <div class="col-12 col-sm-6">
                    <label class="form-label">Учёная степень</label>
                    <input v-model="form.academic_degree" type="text" class="form-control" />
                  </div>
                  <div class="col-12 col-sm-6">
                    <label class="form-label">Учёное звание</label>
                    <input v-model="form.academic_title" type="text" class="form-control" />
                  </div>
                </div>
                <div class="row g-3 mt-1">
                  <div class="col-12 col-sm-6">
                    <label class="form-label">ORCID</label>
                    <input v-model="form.orcid" type="text" class="form-control" />
                  </div>
                  <div class="col-12 col-sm-6">
                    <label class="form-label">Scopus Author ID</label>
                    <input v-model="form.scopus_id" type="text" class="form-control" />
                  </div>
                </div>
                <div class="row g-3 mt-1">
                  <div class="col-12 col-sm-6">
                    <label class="form-label">eLIBRARY ID</label>
                    <input v-model="form.elibrary_id" type="text" class="form-control" />
                  </div>
                  <div class="col-12 col-sm-6">
                    <label class="form-label">Сайт</label>
                    <input v-model="form.website" type="url" class="form-control" />
                  </div>
                </div>
                <div class="mt-3">
                  <label class="form-label">О себе</label>
                  <textarea v-model="form.biography" class="form-control" rows="4" />
                </div>
              </form>
            </div>

            <div v-else-if="profile" class="card-body">
              <div class="profile-block">
                <div class="profile-block__label">Имя</div>
                <div class="profile-block__value">{{ profile.display_name || profile.user }}</div>
              </div>
              <div class="profile-block" v-if="profile.organization">
                <div class="profile-block__label">Организация</div>
                <div class="profile-block__value">{{ profile.organization }}</div>
              </div>
              <div class="profile-block" v-if="profile.department">
                <div class="profile-block__label">Подразделение</div>
                <div class="profile-block__value">{{ profile.department }}</div>
              </div>
              <div class="profile-block" v-if="profile.position">
                <div class="profile-block__label">Должность</div>
                <div class="profile-block__value">{{ profile.position }}</div>
              </div>
              <div class="profile-block" v-if="profile.phone">
                <div class="profile-block__label">Телефон</div>
                <div class="profile-block__value">{{ profile.phone }}</div>
              </div>
              <div class="profile-block" v-if="profile.website">
                <div class="profile-block__label">Сайт</div>
                <div class="profile-block__value">
                  <a :href="profile.website" target="_blank" rel="noopener">{{ profile.website }}</a>
                </div>
              </div>
              <div class="profile-block" v-if="profile.biography">
                <div class="profile-block__label">О себе</div>
                <div class="profile-block__value">{{ profile.biography }}</div>
              </div>
            </div>

            <div class="card-footer bg-body-tertiary" v-if="profile && profile.roles && profile.roles.length">
              <small class="text-muted d-block mb-1">Назначенные роли</small>
              <span
                v-for="role in profile.roles"
                :key="role.id"
                class="badge rounded-pill text-bg-primary-subtle text-primary me-2"
              >
                {{ role.name }}
              </span>
            </div>
          </template>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card shadow-sm mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Работы</h5>
            <span class="badge rounded-pill text-bg-primary-subtle text-primary">{{ works.length }}</span>
          </div>
          <div class="card-body p-0">
            <div v-if="isLoadingWorks" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>
            <div v-else-if="works.length === 0" class="py-5 text-center text-muted">
              <FileText size="32" class="mb-3" />
              <p class="mb-1">Работы пока не отправлялись.</p>
              <p class="mb-0 small">Как только вы подадите материалы, здесь появится их список и статусы.</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Работа</th>
                    <th>Тип</th>
                    <th>Год</th>
                    <th>Форма обучения</th>
                    <th>Статус</th>
                    <th>Редактор</th>
                    <th class="text-end">Документ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="work in works" :key="work.id">
                    <td>
                      <div class="fw-semibold">{{ work.discipline_name || 'Без названия' }}</div>
                      <div class="text-muted small" v-if="work.discipline_topic">
                        {{ work.discipline_topic }}
                      </div>
                    </td>
                    <td>{{ work.publication_kind_display || formatKind(work.publication_kind) }}</td>
                    <td>{{ work.year || '—' }}</td>
                    <td>{{ work.training_form_display || formatTrainingForm(work.training_form) }}</td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(work.status)">
                        {{ statusText(work) }}
                      </span>
                      <div v-if="work.published_at" class="text-muted small">
                        <CheckCircle2 size="12" class="me-1" /> {{ formatDate(work.published_at) }}
                      </div>
                      <div
                        v-if="work.status === 'waiting_for_author'"
                        class="text-warning small d-flex align-items-center gap-1 mt-1"
                      >
                        <AlertTriangle size="12" /> Требуются правки
                      </div>
                    </td>
                    <td>{{ work.current_editor_display_name || '—' }}</td>
                    <td class="text-end">
                      <a
                        v-if="documentUrl(work)"
                        :href="documentUrl(work)"
                        class="btn btn-sm btn-outline-primary d-inline-flex align-items-center gap-2"
                        target="_blank"
                        rel="noopener"
                      >
                        <Download size="14" />
                        Файл
                      </a>
                      <span v-else class="text-muted small">Нет файла</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Редакционные задачи</h5>
            <span class="badge rounded-pill text-bg-secondary-subtle text-secondary">{{ tasks.length }}</span>
          </div>
          <div v-if="isLoadingTasks" class="card-body text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Загрузка...</span>
            </div>
          </div>
          <div v-else class="card-body">
            <div v-if="tasks.length === 0" class="text-muted text-center py-4">
              <MessageSquare size="32" class="mb-3" />
              Пока нет активных задач.
            </div>
            <div v-else class="row">
              <div class="col-lg-5 border-end mb-3 mb-lg-0">
                <div
                  v-for="task in tasks"
                  :key="task.id"
                  class="task-item"
                  :class="{ active: task.id === activeTask?.id }"
                  @click="openTask(task)"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="fw-semibold">{{ task.subject || 'Без темы' }}</div>
                    <span class="badge" :class="taskBadgeClass(task.status)">
                      {{ taskStatusLabel(task.status) }}
                    </span>
                  </div>
                  <div class="text-muted small">
                    {{ formatDate(task.created_at) }}
                  </div>
                  <div class="text-muted small mt-1">
                    {{ task.work_title || '—' }}
                  </div>
                </div>
              </div>
              <div class="col-lg-7">
                <div v-if="!activeTask" class="text-muted text-center py-4">
                  Выберите задачу, чтобы просмотреть переписку.
                </div>
                <div v-else class="conversation">
                  <div class="conversation-header">
                    <h6 class="mb-1">{{ activeTask.subject || 'Без темы' }}</h6>
                    <div class="text-muted small">
                      Работа: {{ activeTask.work_title || '—' }}
                    </div>
                  </div>
                  <div class="conversation-messages" ref="messagesContainer">
                    <div
                      v-for="message in taskMessages"
                      :key="message.id"
                      class="conversation-message"
                    >
                      <div class="conversation-message__meta">
                        <strong>{{ message.author_display_name || message.author_username }}</strong>
                        <span>{{ formatDateTime(message.created_at) }}</span>
                      </div>
                      <div class="conversation-message__content">
                        {{ message.content }}
                      </div>
                    </div>
                    <div v-if="taskMessages.length === 0" class="text-muted small py-4 text-center">
                      Сообщений пока нет.
                    </div>
                  </div>
                  <form class="conversation-form" @submit.prevent="sendMessage">
                    <textarea
                      v-model="messageDraft"
                      class="form-control"
                      rows="3"
                      placeholder="Напишите сообщение..."
                      :disabled="isSendingMessage"
                    />
                    <div class="text-end mt-2">
                      <button
                        type="submit"
                        class="btn btn-primary d-inline-flex align-items-center gap-2"
                        :disabled="isSendingMessage || !messageDraft.trim()"
                      >
                        <span v-if="isSendingMessage" class="spinner-border spinner-border-sm" />
                        <Send v-else size="16" />
                        <span v-if="!isSendingMessage">Отправить</span>
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import {
  RefreshCcw,
  FilePlus,
  Shield,
  Users,
  Contact,
  FileText,
  Download,
  MessageSquare,
  Send,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-vue-next';
import { useToast } from 'vue-toastification';

import { sciencePublishingAPI } from '@/modules/science-publishing/js/science-publishing.js';
import { apiClient } from '@/js/api/manager.js';
import { useUserStore } from '@/core/cms/js/userStore.js';

const router = useRouter();
const toast = useToast();

const userStore = useUserStore();
const { isInitialized } = storeToRefs(userStore);
const devRolesEnabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_ROLES === 'true';

const profile = ref(null);
const profileError = ref('');
const isLoadingProfile = ref(false);

const works = ref([]);
const worksError = ref('');
const isLoadingWorks = ref(false);

const tasks = ref([]);
const taskMessages = ref([]);
const activeTask = ref(null);
const tasksError = ref('');
const isLoadingTasks = ref(false);
const isSendingMessage = ref(false);
const messageDraft = ref('');

const isEditing = ref(false);
const isSaving = ref(false);

const form = reactive({
  display_name: '',
  phone: '',
  organization: '',
  department: '',
  position: '',
  academic_degree: '',
  academic_title: '',
  orcid: '',
  scopus_id: '',
  elibrary_id: '',
  website: '',
  biography: '',
});

const STATUS_LABELS = {
  draft: 'Черновик',
  pending_chief_review: 'Ожидает главного редактора',
  in_editor_review: 'В работе у редактора',
  waiting_for_author: 'Ожидает правок автора',
  ready_for_chief_approval: 'Ожидает утверждения главреда',
  published: 'Опубликована',
};

const STATUS_BADGES = {
  draft: 'text-bg-secondary',
  pending_chief_review: 'text-bg-warning',
  in_editor_review: 'text-bg-info',
  waiting_for_author: 'text-bg-danger',
  ready_for_chief_approval: 'text-bg-primary',
  published: 'text-bg-success',
};

const TASK_STATUS_LABELS = {
  new: 'Новая',
  in_progress: 'В работе',
  done: 'Завершена',
  archived: 'Архив',
};

const TASK_BADGES = {
  new: 'text-bg-danger',
  in_progress: 'text-bg-warning',
  done: 'text-bg-success',
  archived: 'text-bg-secondary',
};

const isAdministrator = computed(() =>
  profile.value?.roles?.some((role) => role.code === 'administrator')
);
const isChiefEditor = computed(() =>
  profile.value?.roles?.some((role) => role.code === 'chief_editor')
);

const ensureUserInitialized = async () => {
  if (!isInitialized.value) {
    try {
      await userStore.initializeUser();
    } catch (error) {
      console.warn('Не удалось инициализировать пользователя', error);
    }
  }
};

const fillForm = (data) => {
  form.display_name = data.display_name || '';
  form.phone = data.phone || '';
  form.organization = data.organization || '';
  form.department = data.department || '';
  form.position = data.position || '';
  form.academic_degree = data.academic_degree || '';
  form.academic_title = data.academic_title || '';
  form.orcid = data.orcid || '';
  form.scopus_id = data.scopus_id || '';
  form.elibrary_id = data.elibrary_id || '';
  form.website = data.website || '';
  form.biography = data.biography || '';
};

const loadProfile = async () => {
  isLoadingProfile.value = true;
  profileError.value = '';
  try {
    const response = await sciencePublishingAPI.getCurrentProfile();
    const data = response?.data ?? response;
    profile.value = data;
    fillForm(data || {});
  } catch (error) {
    profileError.value = error?.message || 'Не удалось получить данные профиля.';
    profile.value = null;
  } finally {
    isLoadingProfile.value = false;
  }
};

const loadWorks = async () => {
  isLoadingWorks.value = true;
  worksError.value = '';
  try {
    const response = await sciencePublishingAPI.listMyWorks();
    const data = response?.data ?? response;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    works.value = list;
  } catch (error) {
    worksError.value = error?.message || 'Не удалось загрузить список работ.';
    works.value = [];
  } finally {
    isLoadingWorks.value = false;
  }
};

const loadTasks = async () => {
  isLoadingTasks.value = true;
  tasksError.value = '';
  try {
    const response = await sciencePublishingAPI.listTasks();
    const data = response?.data ?? response;
    tasks.value = Array.isArray(data) ? data : data?.results ?? [];
    if (tasks.value.length === 0) {
      activeTask.value = null;
      taskMessages.value = [];
    } else if (activeTask.value) {
      const updated = tasks.value.find((item) => item.id === activeTask.value.id);
      if (updated) {
        await openTask(updated);
      } else {
        activeTask.value = null;
        taskMessages.value = [];
      }
    }
  } catch (error) {
    tasksError.value = error?.message || 'Не удалось загрузить задачи.';
    tasks.value = [];
  } finally {
    isLoadingTasks.value = false;
  }
};

const refreshAll = async () => {
  await Promise.all([loadProfile(), loadWorks(), loadTasks()]);
};

const startEditing = () => {
  if (profile.value) {
    fillForm(profile.value);
  }
  isEditing.value = true;
};

const cancelEditing = () => {
  fillForm(profile.value || {});
  isEditing.value = false;
};

const saveProfile = async () => {
  isSaving.value = true;
  try {
    const payload = { ...form };
    const response = await sciencePublishingAPI.updateCurrentProfile(payload);
    const data = response?.data ?? response;
    profile.value = data;
    fillForm(data || {});
    isEditing.value = false;
    toast.success('Профиль обновлён.');
  } catch (error) {
    toast.error(error?.message || 'Не удалось сохранить профиль.');
  } finally {
    isSaving.value = false;
  }
};

const goToSubmit = () => {
  router.push({ name: 'SciencePublishingSubmit' });
};

const goToAdminPanel = () => {
  router.push({ name: 'SciencePublishingAdmin' });
};

const goToDevRoles = () => {
  router.push({ name: 'SciencePublishingDevRoles' });
};

const statusText = (work) => work?.status_display || STATUS_LABELS[work?.status] || 'Статус не определён';
const statusBadgeClass = (status) => STATUS_BADGES[status] || 'text-bg-secondary';
const taskStatusLabel = (status) => TASK_STATUS_LABELS[status] || '—';
const taskBadgeClass = (status) => TASK_BADGES[status] || 'text-bg-secondary';

const formatKind = (value) => {
  const map = {
    method_guidelines: 'Методические рекомендации',
    lab_practicum: 'Лабораторный практикум',
    textbook: 'Учебник',
    monograph: 'Монография',
    article: 'Статья',
    theses: 'Тезисы',
  };
  return map[value] || value || '—';
};

const formatTrainingForm = (value) => {
  const map = {
    full_time: 'Очная',
    part_time: 'Заочная',
    mixed: 'Очно-заочная',
  };
  return map[value] || value || '—';
};

const formatDate = (value) => {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
};

const formatDateTime = (value) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const documentUrl = (work) => {
  if (!work?.document) {
    return null;
  }
  try {
    return new URL(work.document, apiClient.baseUrl).toString();
  } catch {
    const documentPath = work.document.startsWith('/')
      ? work.document.substring(1)
      : work.document;
    return `${apiClient.baseUrl}${documentPath}`;
  }
};

const openTask = async (task) => {
  activeTask.value = task;
  messageDraft.value = '';
  taskMessages.value = [];
  try {
    const response = await sciencePublishingAPI.listTaskMessages(task.id);
    const data = response?.data ?? response;
    taskMessages.value = Array.isArray(data) ? data : data?.results ?? [];
    nextTickScrollMessages();
  } catch (error) {
    toast.error(error?.message || 'Не удалось загрузить переписку.');
  }
};

const messagesContainer = ref(null);
const nextTickScrollMessages = () => {
  requestAnimationFrame(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const sendMessage = async () => {
  if (!activeTask.value || !messageDraft.value.trim()) return;
  isSendingMessage.value = true;
  try {
    const payload = { content: messageDraft.value.trim() };
    await sciencePublishingAPI.postTaskMessage(activeTask.value.id, payload);
    messageDraft.value = '';
    await openTask(activeTask.value);
    await loadTasks();
  } catch (error) {
    toast.error(error?.message || 'Не удалось отправить сообщение.');
  } finally {
    isSendingMessage.value = false;
  }
};

onMounted(async () => {
  await ensureUserInitialized();
  await refreshAll();
});
</script>

<style scoped lang="scss">
.science-profile {
  .page-title {
    font-size: 1.875rem;
    font-weight: 600;
  }

  .profile-block {
    padding: 0.35rem 0;

    &__label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      color: var(--bs-secondary-color);
    }

    &__value {
      font-weight: 500;
      color: var(--bs-body-color);
    }
  }

  .task-item {
    padding: 0.75rem;
    border-radius: 0.75rem;
    border: 1px solid transparent;
    cursor: pointer;
    transition: border-color 0.2s ease, background 0.2s ease;
    margin-bottom: 0.75rem;

    &:hover {
      border-color: var(--bs-primary-border-subtle);
      background: var(--bs-primary-bg-subtle);
    }

    &.active {
      border-color: var(--bs-primary);
      background: var(--bs-primary-bg-subtle);
    }
  }

  .conversation {
    display: flex;
    flex-direction: column;
    height: 100%;

    &-header {
      margin-bottom: 1rem;
    }

    &-messages {
      min-height: 180px;
      max-height: 280px;
      overflow-y: auto;
      padding-right: 0.5rem;
      margin-bottom: 1rem;
    }

    &-message {
      background: var(--bs-body-bg);
      border: 1px solid var(--bs-border-color);
      border-radius: 0.75rem;
      padding: 0.75rem;
      margin-bottom: 0.75rem;

      &__meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: var(--bs-secondary-color);
        margin-bottom: 0.5rem;
      }
    }
  }
}
</style>
