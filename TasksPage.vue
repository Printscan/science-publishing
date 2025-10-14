<template>
  <div class="tasks-page container-fluid py-4">
    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
      <div>
        <h2 class="page-title mb-0">Задачи редакции</h2>
        <p class="page-subtitle mb-0 text-muted">
          Отслеживайте назначения, запросы правок и статусы работ в одном списке.
        </p>
      </div>
      <button class="btn btn-outline-primary d-inline-flex align-items-center gap-2" :disabled="loading" @click="loadTasks">
        <RefreshCcw size="16" />
        <span>Обновить</span>
      </button>
    </div>

    <div v-if="profileLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка профиля...</span>
      </div>
    </div>

    <div v-else-if="!isAllowed" class="alert alert-warning">
      Страница доступна только редакторам и главным редакторам.
    </div>

    <template v-else>
      <form class="card shadow-sm mb-4" @submit.prevent="applyFilters">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-author">Автор</label>
              <input
                id="filters-author"
                v-model="filters.author"
                type="text"
                class="form-control"
                placeholder="Фамилия или логин"
              />
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-work-title">Название работы</label>
              <input
                id="filters-work-title"
                v-model="filters.workTitle"
                type="text"
                class="form-control"
                placeholder="Например, Экономика"
              />
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-subject">Тема задачи</label>
              <input
                id="filters-subject"
                v-model="filters.subject"
                type="text"
                class="form-control"
                placeholder="Например, правки"
              />
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-status">Статус</label>
              <select id="filters-status" v-model="filters.status" class="form-select">
                <option value="">Все статусы</option>
                <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-publication-kind">Тип публикации</label>
              <select id="filters-publication-kind" v-model="filters.publicationKind" class="form-select">
                <option value="">Все типы</option>
                <option v-for="option in publicationKinds" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-guideline-subtype">Подтип методических указаний</label>
              <select id="filters-guideline-subtype" v-model="filters.guidelineSubtype" class="form-select">
                <option value="">Все подтипы</option>
                <option v-for="option in guidelineSubtypes" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-training-form">Форма обучения</label>
              <select id="filters-training-form" v-model="filters.trainingForm" class="form-select">
                <option value="">Все формы</option>
                <option v-for="option in trainingForms" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-year">Год издания</label>
              <input
                id="filters-year"
                v-model="filters.year"
                type="number"
                min="1900"
                max="2100"
                class="form-control"
                placeholder="Например, 2025"
              />
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-created-from">Создана с</label>
              <input id="filters-created-from" v-model="filters.createdFrom" type="date" class="form-control" />
            </div>
            <div class="col-12 col-md-4 col-xl-3">
              <label class="form-label" for="filters-created-to">Создана до</label>
              <input id="filters-created-to" v-model="filters.createdTo" type="date" class="form-control" />
            </div>
            <div class="col-12 col-md-4 col-xl-3 align-self-end">
              <div class="form-check">
                <input id="filters-assigned" v-model="filters.assignedOnly" type="checkbox" class="form-check-input" />
                <label class="form-check-label" for="filters-assigned"> Только мои задачи </label>
              </div>
            </div>
          </div>
          <div class="d-flex justify-content-end gap-2 mt-3">
            <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="resetFilters">
              Сбросить
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              Применить
            </button>
          </div>
        </div>
      </form>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка списка...</span>
        </div>
      </div>

      <div v-else>
        <div v-if="tasks.length === 0" class="alert alert-light border text-center py-4">
          Задачи не найдены по выбранным параметрам.
        </div>
        <div v-else class="task-list d-grid">
          <article
            v-for="task in tasks"
            :key="task.id"
            class="task-card card shadow-sm"
            role="button"
            tabindex="0"
            @click="openTask(task)"
            @keydown.enter.prevent="openTask(task)"
          >
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <h5 class="card-title mb-1">{{ task.subject || 'Без названия' }}</h5>
                  <div class="small text-muted">
                    Работа: {{ task.work_title || '—' }}
                    <template v-if="task.work_year"> ({{ task.work_year }})</template>
                  </div>
                  <div class="small text-muted">
                    Автор: {{ task.work_author_display_name || task.work_author_username || '—' }}
                  </div>
                </div>
                <div class="text-end">
                  <span class="badge" :class="statusBadgeClass(task.status)">
                    {{ task.status_display || statusLabel(task.status) }}
                  </span>
                  <div class="small text-muted mt-1">{{ formatDateTime(task.updated_at || task.created_at) }}</div>
                </div>
              </div>

              <div class="row row-cols-1 row-cols-md-2 gy-1 gx-3 text-muted small mt-3">
                <div>
                  <strong>Тип публикации:</strong>
                  <span>{{ task.work_publication_kind_display || '—' }}</span>
                </div>
                <div>
                  <strong>Подтип:</strong>
                  <span>{{ task.work_guideline_subtype_display || '—' }}</span>
                </div>
                <div>
                  <strong>Форма обучения:</strong>
                  <span>{{ task.work_training_form_display || '—' }}</span>
                </div>
                <div>
                  <strong>Адресат:</strong>
                  <span>{{ task.recipient_username || '—' }}</span>
                </div>
              </div>

              <div v-if="task.message" class="task-message mt-3">
                <strong>Комментарий:</strong>
                <p class="mb-0">{{ task.message }}</p>
              </div>

              <div class="mt-3 d-flex flex-wrap gap-2">
                <button class="btn btn-outline-secondary btn-sm" type="button" @click.stop="goToDrafts">
                  Открыть черновики
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </template>

    <div v-if="detailState.open" class="task-detail-overlay" @click.self="closeTask">
      <div class="task-detail card shadow-lg">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
            <div>
              <h4 class="card-title mb-1">
                {{ detailState.task?.subject || 'Подробности задачи' }}
              </h4>
              <div class="small text-muted">
                Работа: {{ detailState.task?.work_title || '—' }}
                <template v-if="detailState.task?.work_year"> ({{ detailState.task?.work_year }})</template>
              </div>
              <div class="small text-muted">
                Автор: {{ detailState.task?.work_author_display_name || detailState.task?.work_author_username || '—' }}
              </div>
            </div>
            <button type="button" class="btn-close" aria-label="Закрыть" @click="closeTask"></button>
          </div>

          <div v-if="detailState.loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Загрузка задачи...</span>
            </div>
          </div>

          <div v-else-if="detailState.error" class="alert alert-danger">
            {{ detailState.error }}
          </div>

          <template v-else-if="detailState.task">
            <div class="row row-cols-1 row-cols-md-2 gy-2 gx-4 small text-muted mb-3">
              <div>
                <strong>Статус задачи:</strong>
                <span class="ms-1 badge" :class="statusBadgeClass(detailState.task.status)">
                  {{ detailState.task.status_display || statusLabel(detailState.task.status) }}
                </span>
              </div>
              <div>
                <strong>Получатель:</strong>
                <span class="ms-1">{{ detailState.task.recipient_username || '—' }}</span>
              </div>
              <div>
                <strong>Тип публикации:</strong>
                <span class="ms-1">{{ detailState.task.work_publication_kind_display || '—' }}</span>
              </div>
              <div>
                <strong>Подтип:</strong>
                <span class="ms-1">{{ detailState.task.work_guideline_subtype_display || '—' }}</span>
              </div>
              <div>
                <strong>Форма обучения:</strong>
                <span class="ms-1">{{ detailState.task.work_training_form_display || '—' }}</span>
              </div>
              <div>
                <strong>Обновлено:</strong>
                <span class="ms-1">{{ formatDateTime(detailState.task.updated_at || detailState.task.created_at) }}</span>
              </div>
              <div>
                <strong>Текущий редактор:</strong>
                <span class="ms-1">{{ currentEditorDisplay }}</span>
              </div>
              <div>
                <strong>Документ:</strong>
                <span class="ms-1">
                  <a v-if="workDocumentUrl" :href="workDocumentUrl" target="_blank" rel="noopener">Скачать</a>
                  <span v-else>Файл не загружен</span>
                </span>
              </div>
            </div>

            <div v-if="detailState.task.message" class="alert alert-light border">
              <strong>Комментарий редакции:</strong>
              <p class="mb-0">{{ detailState.task.message }}</p>
            </div>

            <div class="task-actions mb-3">
              <h6 class="fw-semibold mb-2">��������</h6>
              <div class="d-flex flex-wrap gap-2">
                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  v-if="canSendToChief"
                  :disabled="detailState.actionLoading || detailState.loading"
                  @click="sendToChief"
                >
                  Отправить главному редактору
                </button>
                <button
                  type="button"
                  class="btn btn-outline-danger btn-sm"
                  v-if="canRequestChanges"
                  :disabled="detailState.actionLoading || detailState.loading"
                  @click="sendBackToAuthor"
                >
                  Запросить исправления у автора
                </button>
                <button
                  type="button"
                  class="btn btn-outline-primary btn-sm"
                  v-if="canAssignEditorForWork"
                  :disabled="detailState.actionLoading || editorOptionsLoading || detailState.loading"
                  @click="openAssignModal"
                >
                  {{ detailState.work?.current_editor ? 'Сменить редактора' : 'Направить редактору' }}
                </button>
                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  v-if="canCreateAuthorTask"
                  :disabled="detailState.actionLoading || authorTaskLoadingRecipient || detailState.loading"
                  @click="openAuthorTaskModal"
                >
                  ������ ������
                </button>
                <button
                  type="button"
                  class="btn btn-outline-success btn-sm"
                  v-if="canApprovePublication"
                  :disabled="detailState.actionLoading || detailState.loading"
                  @click="approvePublication"
                >
                  ������� ����������
                </button>
</div>
              <div class="mt-3">
                <label class="form-label" for="detail-note">Комментарий к действию</label>
                <textarea
                  id="detail-note"
                  v-model="detailState.note"
                  rows="3"
                  class="form-control"
                  placeholder="Дополнительная информация для автора или главного редактора"
                ></textarea>
                <div class="form-text">Комментарий обязателен при отправке на доработку автору.</div>
              </div>
            </div>

            <div class="task-messages mb-4">
              <h6 class="fw-semibold mb-2">История сообщений</h6>
              <div v-if="detailState.task.messages?.length" class="message-timeline">
                <div v-for="msg in detailState.task.messages" :key="msg.id" class="message-item border rounded p-3 mb-2">
                  <div class="d-flex justify-content-between flex-wrap gap-2 small text-muted">
                    <div>
                      <strong>{{ msg.author_display_name || msg.author_username || 'Система' }}</strong>
                      <template v-if="msg.is_system">
                        <span class="badge text-bg-dark ms-1">Система</span>
                      </template>
                    </div>
                    <span>{{ formatDateTime(msg.created_at) }}</span>
                  </div>
                  <div v-if="msg.content" class="mt-2 message-body">
                    {{ msg.content }}
                  </div>
                  <div v-if="msg.changes?.length" class="mt-3">
                    <button
                      class="btn btn-sm btn-link px-0"
                      type="button"
                      @click="toggleExpanded(msg.id)"
                    >
                      <span v-if="expandedMessages.has(msg.id)">*изменения* — скрыть</span>
                      <span v-else>*изменения* — открыть</span>
                    </button>
                    <div v-if="expandedMessages.has(msg.id)" class="message-change-panel mt-2">
                      <ul class="list-unstyled mb-2">
                        <li v-for="change in msg.changes" :key="`${msg.id}-${change.field}`">
                          <div class="fw-semibold">{{ change.label }}</div>
                          <div class="small text-muted">
                            {{ formatChangeValue(change.old) }}
                            <span class="mx-1">→</span>
                            {{ formatChangeValue(change.new) }}
                          </div>
                        </li>
                      </ul>
                      <div v-if="msg.attachments?.length" class="small">
                        <div class="fw-semibold">Вложения:</div>
                        <ul class="list-unstyled mb-0">
                          <li v-for="file in msg.attachments" :key="`${msg.id}-${file.field}-${file.name}`">
                            <a
                              v-if="file.absolute_url || file.url"
                              :href="file.absolute_url || file.url"
                              target="_blank"
                              rel="noopener"
                            >
                              {{ file.name || file.label || 'Файл' }}
                            </a>
                            <span v-else>{{ file.name || file.label || 'Файл' }}</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="alert alert-light border small">
                Сообщений пока нет.
              </div>
              <form class="mt-3" @submit.prevent="sendMessage">
                <label class="form-label" for="detail-message">Добавить сообщение</label>
                <textarea
                  id="detail-message"
                  v-model="detailState.message"
                  rows="2"
                  class="form-control"
                  placeholder="Напишите ответ для коллег"
                ></textarea>
                <div class="d-flex justify-content-end mt-2">
                  <button class="btn btn-primary" type="submit" :disabled="detailState.messageLoading || !detailState.message.trim()">
                    <span v-if="detailState.messageLoading" class="spinner-border spinner-border-sm me-2" />
                    Отправить сообщение
                  </button>
                </div>
              </form>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
    <div class="modal fade" tabindex="-1" ref="assignModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Назначение редактора</h5>
            <button type="button" class="btn-close" @click="closeAssignModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-3" v-if="detailState.work">
              Работа: {{ detailState.work.discipline_name || 'Без названия' }}
            </p>
            <div class="mb-3">
              <label class="form-label">Редактор</label>
              <select v-model="assignForm.editor" class="form-select" :disabled="editorOptionsLoading">
                <option value="">Выберите редактора</option>
                <option v-for="profile in editorOptions" :key="profile.id" :value="profile.id">
                  {{ profile.display_name || profile.user }}
                </option>
              </select>
              <div v-if="editorOptionsLoading" class="form-text">Загрузка списка редакторов...</div>
              <div v-else-if="!editorOptions.length" class="form-text text-danger">Редакторы не найдены.</div>
            </div>
            <div class="mb-3">
              <label class="form-label">Комментарий</label>
              <textarea
                v-model="assignForm.message"
                class="form-control"
                rows="3"
                placeholder="Сообщение для редактора (необязательно)"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" :disabled="isAssigningEditor" @click="closeAssignModal">
              Отмена
            </button>
            <button type="button" class="btn btn-primary" :disabled="isAssigningEditor || editorOptionsLoading || !assignForm.editor" @click="submitAssignEditor">
              <span v-if="isAssigningEditor" class="spinner-border spinner-border-sm me-2"></span>
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" tabindex="-1" ref="authorTaskModalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Задача для автора</h5>
            <button type="button" class="btn-close" @click="closeAuthorTaskModal"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-2" v-if="detailState.work">
              Работа: {{ detailState.work.discipline_name || 'Без названия' }}
            </p>
            <p class="text-muted small mb-3" v-if="authorTaskRecipientName">
              Автор: {{ authorTaskRecipientName }}
            </p>
            <div class="mb-3">
              <label class="form-label">Тема</label>
              <input v-model="authorTaskForm.subject" type="text" class="form-control" placeholder="Введите тему задачи" />
            </div>
            <div class="mb-3">
              <label class="form-label">Сообщение *</label>
              <textarea
                v-model="authorTaskForm.message"
                class="form-control"
                rows="4"
                placeholder="Опишите требования для автора"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" :disabled="isCreatingAuthorTask" @click="closeAuthorTaskModal">
              Отмена
            </button>
            <button type="button" class="btn btn-primary" :disabled="isCreatingAuthorTask || authorTaskLoadingRecipient" @click="submitAuthorTask">
              <span v-if="isCreatingAuthorTask" class="spinner-border spinner-border-sm me-2"></span>
              Отправить
            </button>
          </div>
        </div>
      </div>
    </div>

</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { RefreshCcw } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { Modal } from 'bootstrap';

import { sciencePublishingAPI } from '@/modules/science-publishing/js/science-publishing.js';
import { apiClient } from '@/js/api/manager.js';

const router = useRouter();
const toast = useToast();

const STATUS_LABELS = {
  new: 'Новая',
  in_progress: 'В работе',
  done: 'Завершена',
  archived: 'Архивирована',
};

const statusOptions = Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }));

const publicationKinds = [
  { value: 'method_guidelines', label: 'Методические рекомендации' },
  { value: 'lab_practicum', label: 'Лабораторный практикум' },
  { value: 'textbook', label: 'Учебное пособие' },
  { value: 'monograph', label: 'Монография' },
  { value: 'article', label: 'Статья' },
  { value: 'theses', label: 'Тезисы' },
];

const guidelineSubtypes = [
  { value: 'coursework', label: 'Курсовая работа' },
  { value: 'laboratory', label: 'Лабораторная работа' },
  { value: 'practical', label: 'Практическое пособие' },
];

const trainingForms = [
  { value: 'full_time', label: 'Очная' },
  { value: 'part_time', label: 'Заочная' },
  { value: 'mixed', label: 'Очно-заочная' },
];

const ASSIGNABLE_STATUSES = new Set(['pending_chief_review', 'in_editor_review', 'waiting_for_author', 'ready_for_chief_approval']);
const AUTHOR_TASK_STATUSES = new Set(['pending_chief_review', 'in_editor_review', 'waiting_for_author', 'ready_for_chief_approval']);


const filters = reactive({
  author: '',
  workTitle: '',
  subject: '',
  status: '',
  publicationKind: '',
  guidelineSubtype: '',
  trainingForm: '',
  year: '',
  createdFrom: '',
  createdTo: '',
  assignedOnly: false,
});

const tasks = ref([]);
const loading = ref(false);
const error = ref('');

const profile = ref(null);
const profileLoading = ref(true);

const allowedRoles = ['editor', 'chief_editor'];
const currentUserId = computed(() => profile.value?.user || profile.value?.user_id || null);
const isAllowed = computed(() => {
  const roles = profile.value?.roles;
  if (!Array.isArray(roles)) {
    return false;
  }
  return roles.some((role) => allowedRoles.includes(role.code));
});

const isChiefEditor = computed(() =>
  profile.value?.roles?.some((role) => role.code === 'chief_editor')
);

const isEditor = computed(() =>
  profile.value?.roles?.some((role) => role.code === 'editor')
);

const expandedMessages = ref(new Set());

const detailState = reactive({
  open: false,
  loading: false,
  task: null,
  work: null,
  error: '',
  note: '',
  message: '',
  actionLoading: false,
  messageLoading: false,
});

const assignModalRef = ref(null);
let assignModalInstance;
const assignForm = reactive({
  editor: '',
  message: '',
});
const isAssigningEditor = ref(false);
const editorOptions = ref([]);
const editorOptionsLoading = ref(false);

const authorTaskModalRef = ref(null);
let authorTaskModalInstance;
const authorTaskForm = reactive({
  subject: '',
  message: '',
});
const authorTaskRecipientId = ref(null);
const authorTaskRecipientName = ref('');
const isCreatingAuthorTask = ref(false);
const authorTaskLoadingRecipient = ref(false);
const authorProfileCache = reactive({});

const isMyTask = computed(() => {
  if (!detailState.task) return false;
  return detailState.task.recipient === currentUserId.value;
});

const canSendToChief = computed(() => {
  if (!detailState.task || !detailState.work) return false;
  if (!isEditor.value) return false;
  if (detailState.task.recipient !== currentUserId.value) return false;
  return ['in_editor_review', 'waiting_for_author'].includes(detailState.work.status);
});

const canRequestChanges = computed(() => {
  if (!detailState.task || !detailState.work) return false;
  if (!isEditor.value && !isChiefEditor.value) return false;
  if (!isChiefEditor.value && detailState.task.recipient !== currentUserId.value) return false;
  return detailState.work.status === 'in_editor_review';
});

const currentEditorDisplay = computed(() => detailState.work?.current_editor_display_name || detailState.work?.current_editor_username || 'Не назначен');

const workDocumentUrl = computed(() => {
  const doc = detailState.work?.document;
  if (!doc) return null;
  try {
    return new URL(doc, apiClient.baseUrl).toString();
  } catch (err) {
    const normalized = doc.startsWith('/') ? doc.slice(1) : doc;
    return `${apiClient.baseUrl}${normalized}`;
  }
});

const canAssignEditorForWork = computed(() =>
  isChiefEditor.value && detailState.work && ASSIGNABLE_STATUSES.has(detailState.work.status)
);

const canCreateAuthorTask = computed(() =>
  isChiefEditor.value && detailState.work?.profile && AUTHOR_TASK_STATUSES.has(detailState.work.status)
);

const canApprovePublication = computed(() =>
  isChiefEditor.value && detailState.work?.status === 'ready_for_chief_approval'
);

function statusLabel(status) {
  return STATUS_LABELS[status] || status || '—';
}

function statusBadgeClass(status) {
  switch (status) {
    case 'new':
      return 'text-bg-secondary';
    case 'in_progress':
      return 'text-bg-warning text-dark';
    case 'done':
      return 'text-bg-success';
    case 'archived':
      return 'text-bg-dark';
    default:
      return 'text-bg-secondary';
  }
}

function formatDateTime(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleString('ru-RU');
  } catch {
    return value;
  }
}

function formatChangeValue(value) {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number') {
    return value;
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function toggleExpanded(id) {
  const next = new Set(expandedMessages.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  expandedMessages.value = next;
}

async function fetchProfile() {
  profileLoading.value = true;
  try {
    const response = await sciencePublishingAPI.getCurrentProfile();
    profile.value = response?.data ?? response;
  } catch (err) {
    profile.value = null;
    toast.error('Не удалось загрузить профиль редакции.');
    console.error(err);
  } finally {
    profileLoading.value = false;
  }
}

function buildParams() {
  const params = {};
  if (filters.author.trim()) params.author = filters.author.trim();
  if (filters.workTitle.trim()) params.work_title = filters.workTitle.trim();
  if (filters.subject.trim()) params.subject = filters.subject.trim();
  if (filters.status) params.status = filters.status;
  if (filters.publicationKind) params.publication_kind = filters.publicationKind;
  if (filters.guidelineSubtype) params.guideline_subtype = filters.guidelineSubtype;
  if (filters.trainingForm) params.training_form = filters.trainingForm;
  if (filters.year) params.year = filters.year;
  if (filters.createdFrom) params.created_from = filters.createdFrom;
  if (filters.createdTo) params.created_to = filters.createdTo;
  if (filters.assignedOnly) params.assigned = '1';
  return params;
}

async function loadTasks() {
  loading.value = true;
  error.value = '';
  try {
    const response = await sciencePublishingAPI.listTasks(buildParams());
    const data = response?.data ?? response;
    tasks.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (err) {
    error.value = err?.message || 'Не удалось загрузить задачи.';
    toast.error(error.value);
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  loadTasks();
}

function resetFilters() {
  filters.author = '';
  filters.workTitle = '';
  filters.subject = '';
  filters.status = '';
  filters.publicationKind = '';
  filters.guidelineSubtype = '';
  filters.trainingForm = '';
  filters.year = '';
  filters.createdFrom = '';
  filters.createdTo = '';
  filters.assignedOnly = false;
  loadTasks();
}

function goToDrafts() {
  router.push({ name: 'SciencePublishingDrafts' });
}

function closeTask() {
  detailState.open = false;
  detailState.task = null;
  detailState.work = null;
  detailState.error = '';
  detailState.note = '';
  detailState.message = '';
  expandedMessages.value = new Set();
  closeAssignModal();
  closeAuthorTaskModal();
}

async function openTask(task) {
  detailState.open = true;
  detailState.loading = true;
  detailState.error = '';
  detailState.task = null;
  detailState.work = null;
  detailState.note = '';
  detailState.message = '';
  expandedMessages.value = new Set();
  try {
    const response = await sciencePublishingAPI.getTask(task.id);
    const taskData = response?.data ?? response;
    detailState.task = taskData;
    await loadDetailWork(taskData.work);
  } catch (err) {
    detailState.error = err?.message || 'Не удалось загрузить задачу.';
  } finally {
    detailState.loading = false;
  }
}

async function refreshDetail() {
  if (!detailState.task) return;
  try {
    const response = await sciencePublishingAPI.getTask(detailState.task.id);
    const taskData = response?.data ?? response;
    detailState.task = taskData;
    await loadDetailWork(taskData.work);
  } catch (err) {
    detailState.error = err?.message || 'Не удалось обновить задачу.';
  }
}

async function loadDetailWork(workId) {
  if (!workId) {
    detailState.work = null;
    return;
  }
  try {
    const response = await sciencePublishingAPI.getWork(workId);
    detailState.work = response?.data ?? response;
  } catch (err) {
    detailState.work = null;
    const message = err?.message || 'Не удалось загрузить данные работы.';
    toast.error(message);
  }
}

async function performTaskAction(handler, successMessage) {
  detailState.actionLoading = true;
  try {
    await handler();
    await Promise.all([refreshDetail(), loadTasks()]);
    if (successMessage) {
      toast.success(successMessage);
    }
  } catch (err) {
    const message = err?.message || 'Не удалось выполнить действие.';
    toast.error(message);
  } finally {
    detailState.actionLoading = false;
  }
}

function ensureAssignModal() {
  if (!assignModalInstance && assignModalRef.value) {
    assignModalInstance = new Modal(assignModalRef.value, { backdrop: 'static' });
  }
}

function ensureAuthorTaskModal() {
  if (!authorTaskModalInstance && authorTaskModalRef.value) {
    authorTaskModalInstance = new Modal(authorTaskModalRef.value, { backdrop: 'static' });
  }
}

async function loadEditorOptions() {
  editorOptionsLoading.value = true;
  try {
    const response = await sciencePublishingAPI.listProfiles({ 'roles__code': 'editor', page_size: 1000 });
    const data = response?.data ?? response;
    editorOptions.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (err) {
    toast.error(err?.message || 'Не удалось получить список редакторов.');
  } finally {
    editorOptionsLoading.value = false;
  }
}

async function openAssignModal() {
  if (!detailState.work) {
    toast.error('Данные по работе ещё не загружены.');
    return;
  }
  await loadEditorOptions();
  assignForm.editor = detailState.work.current_editor || '';
  assignForm.message = '';
  ensureAssignModal();
  assignModalInstance?.show();
}

function closeAssignModal() {
  assignModalInstance?.hide();
  assignForm.editor = '';
  assignForm.message = '';
  editorOptionsLoading.value = false;
}

async function submitAssignEditor() {
  if (!detailState.work) return;
  if (!assignForm.editor) {
    toast.error('Выберите редактора.');
    return;
  }
  isAssigningEditor.value = true;
  try {
    await sciencePublishingAPI.assignWorkEditor(detailState.work.id, {
      editor_profile: assignForm.editor,
      message: assignForm.message ? assignForm.message : undefined,
    });
    toast.success('Редактор назначен.');
    closeAssignModal();
    await Promise.all([refreshDetail(), loadTasks()]);
  } catch (err) {
    toast.error(err?.message || 'Не удалось назначить редактора.');
  } finally {
    isAssigningEditor.value = false;
  }
}

function authorTaskDefaultSubject(work) {
  const title =
    work?.discipline_name || work?.publication_kind_display || work?.publication_kind || 'работе';
  return `Задача по работе ${title}`;
}

async function resolveAuthorRecipient(profileId) {
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
}

async function openAuthorTaskModal() {
  if (!detailState.work?.profile) {
    toast.error('Не удалось определить профиль автора.');
    return;
  }
  authorTaskLoadingRecipient.value = true;
  try {
    const recipient = await resolveAuthorRecipient(detailState.work.profile);
    authorTaskRecipientId.value = recipient.userId;
    authorTaskRecipientName.value =
      recipient.displayName ||
      detailState.task?.work_author_display_name ||
      detailState.task?.work_author_username ||
      '—';
    authorTaskForm.subject = authorTaskDefaultSubject(detailState.work);
    authorTaskForm.message = '';
    ensureAuthorTaskModal();
    authorTaskModalInstance?.show();
  } catch (err) {
    toast.error(err?.message || 'Не удалось подготовить задачу для автора.');
  } finally {
    authorTaskLoadingRecipient.value = false;
  }
}

function closeAuthorTaskModal() {
  authorTaskModalInstance?.hide();
  authorTaskForm.subject = '';
  authorTaskForm.message = '';
  authorTaskRecipientId.value = null;
  authorTaskRecipientName.value = '';
  authorTaskLoadingRecipient.value = false;
}

async function submitAuthorTask() {
  if (!detailState.work || !authorTaskRecipientId.value) return;
  const subject =
    (authorTaskForm.subject || '').trim() || authorTaskDefaultSubject(detailState.work);
  const message = (authorTaskForm.message || '').trim();
  if (!message) {
    toast.error('Добавьте сообщение для автора.');
    return;
  }
  isCreatingAuthorTask.value = true;
  try {
    await sciencePublishingAPI.createTask({
      work: detailState.work.id,
      recipient: authorTaskRecipientId.value,
      subject,
      message,
    });
    toast.success('Задача отправлена автору.');
    closeAuthorTaskModal();
    await Promise.all([refreshDetail(), loadTasks()]);
  } catch (err) {
    toast.error(err?.message || 'Не удалось отправить задачу автору.');
  } finally {
    isCreatingAuthorTask.value = false;
  }
}

async function approvePublication() {
  if (!detailState.work) return;
  await performTaskAction(
    () =>
      sciencePublishingAPI.approveWorkAsChief(detailState.work.id, {
        message: detailState.note.trim() || undefined,
      }),
    'Публикация принята.'
  );
  detailState.note = '';
}

function sendToChief() {
  if (!detailState.task) return;
  performTaskAction(
    () =>
      sciencePublishingAPI.approveWorkAsEditor(detailState.task.work, {
        message: detailState.note.trim() || undefined,
      }),
    'Задача направлена главному редактору.'
  ).then(() => {
    detailState.note = '';
  });
}

function sendBackToAuthor() {
  if (!detailState.task) return;
  if (!detailState.note.trim()) {
    toast.error('Опишите, что необходимо исправить.');
    return;
  }
  performTaskAction(
    () =>
      sciencePublishingAPI.requestWorkChanges(detailState.task.work, {
        message: detailState.note.trim(),
      }),
    'Запрос правок отправлен автору.'
  ).then(() => {
    detailState.note = '';
  });
}

async function sendMessage() {
  if (!detailState.task || !detailState.message.trim()) return;
  detailState.messageLoading = true;
  try {
    await sciencePublishingAPI.postTaskMessage(detailState.task.id, { content: detailState.message.trim() });
    detailState.message = '';
    await refreshDetail();
    toast.success('Сообщение отправлено.');
  } catch (err) {
    const message = err?.message || 'Не удалось отправить сообщение.';
    toast.error(message);
  } finally {
    detailState.messageLoading = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  if (isAllowed.value) {
    await loadTasks();
  }
});
</script>

<style scoped>
.tasks-page .page-subtitle {
  max-width: 640px;
}

.task-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.task-card {
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.75rem 1.75rem rgba(15, 23, 42, 0.1);
}

.task-card .card-body {
  padding: 1.5rem;
}

.task-message p {
  white-space: pre-line;
}

.task-detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 1040;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 1rem;
}

.task-detail {
  width: min(960px, 100%);
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 1.5rem;
}

.task-detail .card-body {
  flex: 1;
  overflow-y: auto;
}

.task-detail .message-item {
  background: var(--bs-body-bg);
}

.message-body {
  white-space: pre-line;
}

.message-change-panel {
  background: var(--bs-light-bg-subtle);
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.message-timeline {
  max-height: 360px;
  overflow-y: auto;
}

.task-actions .btn {
  min-width: 200px;
}

@media (max-width: 767px) {
  .task-card .card-body {
    padding: 1.25rem;
  }

  .task-actions .btn {
    min-width: 100%;
  }

  .task-detail-overlay {
    padding: 0;
  }

  .task-detail {
    width: 100%;
    border-radius: 0;
    max-height: 100vh;
    padding: 1.25rem;
  }
}
</style>
