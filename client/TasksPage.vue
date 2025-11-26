<template>
  <div v-if="accessDenied" class="alert alert-warning m-4">
    Нет доступа к задачам редакции.
  </div>
  <div v-else class="tasks-page container-fluid py-4">
    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
      <div>
        <h2 class="page-title mb-0">Задачи редакции</h2>
        <p class="page-subtitle mb-0 text-muted">
          Отслеживайте назначения, запросы правок и статусы работ в одном списке.
        </p>
      </div>
      <button class="btn btn-outline-primary d-inline-flex align-items-center gap-2" :disabled="loading" @click="loadWorks">
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
              <label class="form-label" for="filters-status">Статус</label>
              <select id="filters-status" v-model="filters.status" class="form-select">
                <option value="">Все статусы</option>
                <option v-for="option in workStatusOptions" :key="option.value" :value="option.value">
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
        <div v-if="works.length === 0" class="alert alert-light border text-center py-4">
          Черновики не найдены по выбранным параметрам.
        </div>
        <div v-else class="task-list d-grid">
          <article
            v-for="work in works"
            :key="work.id"
            class="task-card card shadow-sm"
            role="button"
            tabindex="0"
            @click="openWork(work)"
            @keydown.enter.prevent="openWork(work)"
          >
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <h5 class="card-title mb-1">{{ work.discipline_name || 'Без названия' }}</h5>
                  <div class="small text-muted">
                    Автор: {{ work.profile_display_name || work.profile_username || '—' }}
                  </div>
                  <div class="small text-muted">
                    Тип: {{ work.publication_kind_display || '—' }}
                  </div>
                </div>
                <div class="text-end">
                  <span class="badge" :class="workStatusBadge(work.status)">
                    {{ workStatusLabel(work.status) }}
                  </span>
                  <div v-if="work.current_editor_display_name" class="small text-muted mt-1">
                    Редактор: {{ work.current_editor_display_name }}
                  </div>
                  <div class="small text-muted mt-1">{{ formatDateTime(work.updated_at || work.created_at) }}</div>
                </div>
              </div>

              <div class="row row-cols-1 row-cols-md-2 gy-1 gx-3 text-muted small mt-3">
                <div>
                  <strong>Подтип:</strong>
                  <span>{{ work.guideline_subtype_display || '—' }}</span>
                </div>
                <div>
                  <strong>Форма обучения:</strong>
                  <span>{{ work.training_form_display || '—' }}</span>
                </div>
              </div>

              <div class="mt-3 d-flex flex-wrap gap-2">
                <a
                  v-if="work.document"
                  :href="workDocumentUrl(work)"
                  class="btn btn-sm btn-outline-primary"
                  target="_blank"
                  rel="noopener"
                  @click.stop
                >
                  Скачать файл
                </a>
                <span v-else class="text-muted small">Файл не прикреплён</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </template>

    <Teleport to="body">
      <div
        v-if="detailState.open"
        class="task-detail-overlay"
        role="dialog"
        aria-modal="true"
        @click.self="closeTask"
      >
        <div class="task-detail card shadow-lg">
          <div class="task-detail__header d-flex align-items-start justify-content-between mb-3 flex-wrap gap-3">
            <div class="me-3 flex-grow-1">
              <h4 class="mb-1">
                {{
                  detailState.work?.discipline_name ||
                  detailState.work?.title ||
                  'Детали работы'
                }}
              </h4>
              <div class="text-muted small">{{ taskAuthorDisplay }}</div>
            </div>
            <div class="d-flex flex-wrap align-items-start gap-2">
              <a
                v-if="detailState.work?.document"
                :href="workDocumentUrl(detailState.work)"
                target="_blank"
                rel="noopener"
                class="btn btn-outline-danger"
              >
                Скачать работу
              </a>
              <button type="button" class="btn-close ms-1" aria-label="Закрыть" @click="closeTask"></button>
            </div>
          </div>
          <div class="task-detail__body card-body pt-0">
            <div v-if="detailState.loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загружаем работу...</span>
              </div>
            </div>
            <div v-else-if="detailState.error" class="alert alert-danger mb-0">
              {{ detailState.error }}
            </div>
            <div v-else class="task-detail__layout">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <button
                  v-if="isChiefEditor"
                  type="button"
                  class="btn btn-success"
                  :disabled="detailState.actionLoading"
                  @click="publishWork"
                >
                  <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Опубликовать
                </button>
                <button
                  v-else-if="canSendToChiefWork"
                  type="button"
                  class="btn btn-outline-primary"
                  :disabled="detailState.actionLoading"
                  @click="sendToChiefWork"
                >
                  <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Отправить главному редактору
                </button>
                <button
                  v-if="canAssignEditorForWork"
                  type="button"
                  class="btn btn-outline-primary"
                  @click="openAssignModal"
                >
                  {{ detailState.work?.current_editor_display_name ? 'Сменить редактора' : 'Назначить редактора' }}
                </button>
              </div>
              <div class="task-detail__tabs">
                <button
                  type="button"
                  class="task-detail__tab"
                  :class="{ 'task-detail__tab--active': detailState.activeTab === 'chat' }"
                  @click="setDetailTab('chat')"
                >
                  Переписка
                </button>
                <button
                  type="button"
                  class="task-detail__tab"
                  :class="{ 'task-detail__tab--active': detailState.activeTab === 'attachments' }"
                  @click="setDetailTab('attachments')"
                >
                  Вложения
                  <span v-if="detailAttachments.length" class="task-detail__tab-count">
                    {{ detailAttachments.length }}
                  </span>
                </button>
              </div>

              <div ref="detailScrollRef" class="task-detail__content">
                <div v-if="detailState.activeTab === 'chat'" class="task-chat">
                  <div v-if="!detailState.chatMessages.length" class="alert alert-light border text-center mb-0">
                    Переписка пока пуста.
                  </div>
                  <div v-else class="task-chat__conversation">
                    <div class="task-chat__timeline">
                      <span class="task-chat__dot" :class="workStatusAccentClass(detailState.work?.status)"></span>
                    </div>
                    <div class="task-chat__content">
                      <header class="task-chat__header">
                        <div>
                          <div class="task-chat__subject">{{ detailState.work?.discipline_name || 'Без темы' }}</div>
                          <div class="task-chat__meta text-muted small">
                            <span>{{ currentEditorDisplay }}</span>
                            <span class="task-chat__divider" aria-hidden="true">•</span>
                            <span>{{ formatDateTime(detailState.work?.updated_at || detailState.work?.created_at) }}</span>
                          </div>
                        </div>
                        <span class="badge task-chat__status" :class="statusBadgeClass(detailState.work?.status)">
                          {{ statusLabel(detailState.work?.status) }}
                        </span>
                      </header>

                      <div class="chat-thread">
                        <div
                          v-for="message in detailState.chatMessages"
                          :key="message.id || message.created_at"
                          :class="['chat-entry', messageAlignmentClass(message)]"
                        >
                          <div class="chat-entry__heading">
                            <div class="chat-entry__name">{{ messageAuthorName(message) }}</div>
                            <span class="chat-entry__time text-muted small">{{ formatDateTime(message.created_at) }}</span>
                          </div>
                          <div class="chat-entry__body">
                            <p v-if="message.content" class="mb-2">{{ message.content }}</p>
                            <div v-if="messageHasChanges(message)" class="chat-entry__changes">
                              <div class="chat-entry__subtitle text-muted small">Изменения</div>
                              <ul class="chat-change-list">
                                <li v-for="change in message.changes" :key="change.field || change.name || change.label">
                                  <strong>{{ changeLabel(change) }}:</strong>
                                  <span class="text-muted ms-1">было {{ formatChangeValue(changeOld(change)) }}</span>
                                  <span class="ms-1">стало {{ formatChangeValue(changeNew(change)) }}</span>
                                </li>
                              </ul>
                            </div>
                            <div v-if="messageHasAttachments(message)" class="chat-entry__attachments">
                              <div class="chat-entry__subtitle text-muted small">Вложения</div>
                              <ul class="chat-attachment-list">
                                <li v-for="attachment in message.attachments" :key="attachment.url || attachment.absolute_url">
                                  <a :href="attachment.absolute_url || attachment.url" target="_blank" rel="noopener">
                                    {{ attachment.name || attachment.url || 'Файл' }}
                                  </a>
                                </li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="task-attachments">
                  <div class="task-attachments__search input-group mb-4">
                    <span class="input-group-text task-attachments__search-icon">
                      <Search size="16" stroke-width="1.75" />
                    </span>
                    <input
                      v-model.trim="detailState.attachmentQuery"
                      type="search"
                      class="form-control"
                      placeholder="Поиск по вложениям"
                    />
                  </div>
                  <div v-if="filteredAttachments.length" class="attachment-list">
                    <article
                      v-for="item in filteredAttachments"
                      :key="item.key"
                      class="attachment-card"
                    >
                      <div class="attachment-card__header">
                        <div class="attachment-card__title">
                          <a
                            v-if="item.url"
                            :href="item.url"
                            target="_blank"
                            rel="noopener"
                            class="attachment-card__link"
                          >
                            {{ item.name }}
                          </a>
                          <span v-else class="attachment-card__link attachment-card__link--muted">
                            {{ item.name }}
                          </span>
                        </div>
                        <span class="badge text-bg-light text-muted attachment-card__badge">
                          {{ item.originLabel }}
                        </span>
                      </div>
                      <div class="attachment-card__meta text-muted small">
                        <span>{{ item.taskSubject }}</span>
                        <span v-if="item.author" class="attachment-card__dot" aria-hidden="true">•</span>
                        <span v-if="item.author">{{ item.author }}</span>
                        <span v-if="item.displayDate" class="attachment-card__dot" aria-hidden="true">•</span>
                        <span v-if="item.displayDate">{{ item.displayDate }}</span>
                        <span v-if="item.statusDisplay" class="attachment-card__dot" aria-hidden="true">•</span>
                        <span v-if="item.statusDisplay">{{ item.statusDisplay }}</span>
                      </div>
                      <p v-if="item.context" class="attachment-card__context text-muted small mb-0">
                        {{ item.context }}
                      </p>
                    </article>
                  </div>
                  <div v-else class="alert alert-light border mb-0">
                    <span v-if="detailAttachments.length">Мы не нашли совпадений.</span>
                    <span v-else>Вложения ещё не добавлены.</span>
                  </div>
                </div>
              </div>

              <form
                v-if="detailState.activeTab === 'chat'"
                class="task-composer"
                @submit.prevent="sendMessage"
              >
                <label class="form-label" for="detail-message">Добавить сообщение</label>
                <div class="input-group">
                  <textarea
                    id="detail-message"
                    v-model="detailState.message"
                    class="form-control"
                    rows="2"
                    placeholder="Напишите комментарий..."
                    :disabled="detailState.messageLoading"
                  ></textarea>
                  <button
                    class="btn btn-primary"
                    type="submit"
                    :disabled="detailState.messageLoading || !detailState.message.trim()"
                  >
                    <span v-if="detailState.messageLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Отправить
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
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

  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue';
import { RefreshCcw, Search } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { Modal } from 'bootstrap';

import { sciencePublishingAPI } from '@/modules/science_publishing/client/js/science-publishing.js';
import { apiClient } from '@/js/api/manager.js';
import { useScienceAccess } from '@/modules/science_publishing/client/js/access.js';

const router = useRouter();
const toast = useToast();

const WORK_STATUS_LABELS = {
  draft: 'Черновик',
  pending_chief_review: 'На рассмотрении у руководителя',
  in_editor_review: 'В редакторской проверке',
  waiting_for_author: 'Ожидает автора',
  ready_for_chief_approval: 'Готово к утверждению',
  published: 'Опубликовано',
};

const workStatusOptions = [
  { value: '', label: 'Все статусы' },
  ...Object.entries(WORK_STATUS_LABELS).map(([value, label]) => ({ value, label })),
];

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
const { allowed: accessAllowed, ensure: ensureAccess, loading: accessLoading } = useScienceAccess('SciencePublishingTasks');
const accessDenied = ref(false);

const ASSIGNABLE_STATUSES = new Set([
  'draft',
  'pending_chief_review',
  'in_editor_review',
  'waiting_for_author',
  'ready_for_chief_approval',
]);

const filters = reactive({
  author: '',
  workTitle: '',
  status: '',
  publicationKind: '',
  guidelineSubtype: '',
  trainingForm: '',
  year: '',
});

const works = ref([]);
const loading = ref(false);
const error = ref('');

const profile = ref(null);
const profileLoading = ref(true);

const allowedRoles = ['editor', 'chief_editor', 'administrator'];
function normalizeId(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number' || typeof value === 'string') return value;
  if (typeof value === 'object') {
    return value.id || value.user_id || value.user || null;
  }
  return null;
}

const currentUserId = computed(() => normalizeId(profile.value?.user) ?? normalizeId(profile.value?.user_id));
const currentProfileId = computed(() => profile.value?.id || profile.value?.profile_id || null);
const normalizeLower = (value) => {
  if (value === undefined || value === null) return '';
  try {
    return value.toString().toLowerCase();
  } catch {
    return '';
  }
};
const extractErrorMessage = (err, fallback = 'Не удалось выполнить действие.') => {
  const data = err?.response?.data;
  if (typeof data === 'string') return data;
  const detail = data?.detail || data?.message;
  if (Array.isArray(detail)) return detail.join(' ');
  if (detail) return String(detail);
  const nonFieldErrors = data?.non_field_errors;
  if (Array.isArray(nonFieldErrors) && nonFieldErrors.length) {
    return nonFieldErrors.join(' ');
  }
  if (data && typeof data === 'object') {
    const firstFieldError = Object.values(data).find(
      (value) => typeof value === 'string' || (Array.isArray(value) && value.length)
    );
    if (Array.isArray(firstFieldError)) return firstFieldError.join(' ');
    if (typeof firstFieldError === 'string') return firstFieldError;
  }
  if (err?.message) return err.message;
  return fallback;
};
const roleCodes = computed(() =>
  (profile.value?.roles || [])
    .map((role) => normalizeLower(role?.code || role || ''))
    .filter(Boolean)
);
const hasRole = (code) => {
  const target = normalizeLower(code);
  if (!target) return false;
  return roleCodes.value.includes(target);
};
const isAllowed = computed(() => roleCodes.value.some((code) => allowedRoles.includes(code)));

const isChiefEditor = computed(() => hasRole('chief_editor') || hasRole('administrator'));

const isEditor = computed(() => hasRole('editor'));

const currentUserDisplay = computed(() => profile.value?.display_name || profile.value?.user || '');
const currentUsername = computed(() =>
  normalizeLower(profile.value?.user || profile.value?.username || '')
);

const isCurrentEditor = computed(() => {
  const editorId =
    detailState.work?.current_editor ||
    detailState.work?.current_editor_id ||
    detailState.work?.current_editor?.id;
  return editorId && currentProfileId.value
    ? String(editorId) === String(currentProfileId.value)
    : false;
});

const detailScrollRef = ref(null);
let detailRefreshTimer = null;

const detailState = reactive({
  open: false,
  loading: false,
  work: null,
  chatMessages: [],
  error: '',
  note: '',
  message: '',
  actionLoading: false,
  messageLoading: false,
  activeTab: 'chat',
  attachmentQuery: '',
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

const canRequestChanges = computed(
  () =>
    detailState.work &&
    (isEditor.value || isChiefEditor.value) &&
    detailState.work.status === 'in_editor_review'
);

const currentEditorDisplay = computed(() => detailState.work?.current_editor_display_name || detailState.work?.current_editor_username || 'Не назначен');
const taskAuthorDisplay = computed(() => {
  const apiDisplay =
    detailState.work?.author_display_name ||
    detailState.work?.author_username ||
    '';

  const authorProfileId = detailState.work?.profile;
  const workAuthorUsername = normalizeLower(detailState.work?.author_username || '');

  if (authorProfileId && currentProfileId.value && String(authorProfileId) === String(currentProfileId.value)) {
    return currentUserDisplay.value || apiDisplay || '—';
  }

  if (workAuthorUsername && workAuthorUsername === currentUsername.value && currentUserDisplay.value) {
    return currentUserDisplay.value;
  }

  return apiDisplay || '—';
});

function workDocumentUrl(work) {
  const doc = work?.document;
  if (!doc) return null;
  try {
    return new URL(doc, apiClient.baseUrl).toString();
  } catch (err) {
    const normalized = doc.startsWith('/') ? doc.slice(1) : doc;
    return `${apiClient.baseUrl}${normalized}`;
  }
}

watch(
  () => detailState.activeTab,
  async (tab) => {
    if (tab === 'chat') {
      await nextTick();
      scrollChatToEnd();
    }
  }
);

watch(
  () => detailState.chatMessages,
  async () => {
    if (detailState.activeTab === 'chat') {
      await nextTick();
      scrollChatToEnd();
    }
  }
);

const detailAttachments = computed(() => {
  const items = [];
  const messages = Array.isArray(detailState.chatMessages) ? detailState.chatMessages : [];
  const workTitle = detailState.work?.discipline_name || 'Без названия';

  const pushAttachment = (attachment, meta) => {
    if (!attachment) return;
    const url = attachment.absolute_url || attachment.url || attachment.file || null;
    const name =
      attachment.name ||
      attachment.filename ||
      attachment.original_name ||
      attachment.url ||
      attachment.absolute_url ||
      'Файл';
    const context = meta.context || '';
    const originLabel = meta.originLabel || 'Комментарий';
    const author = meta.author || '';
    const createdAt = meta.createdAt || null;
    const displayDate = formatDateTime(createdAt);

    const keywords = [name, author, originLabel, workTitle, context, displayDate]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    items.push({
      key: meta.key,
      name,
      url,
      author,
      createdAt,
      displayDate,
      origin: meta.origin || 'message',
      originLabel,
      taskSubject: workTitle,
      statusDisplay: statusLabel(detailState.work?.status),
      context,
      keywords,
    });
  };

  messages.forEach((message, messageIndex) => {
    if (!Array.isArray(message.attachments)) return;
    message.attachments.forEach((attachment, attachmentIndex) => {
      const key = ['message', message.id || messageIndex, attachmentIndex].join('-');
      pushAttachment(attachment, {
        key,
        origin: 'message',
        originLabel: 'Комментарий',
        author: messageAuthorName(message),
        createdAt: message.created_at,
        context: message.content || '',
      });
    });
  });

  return items;
});

const filteredAttachments = computed(() => {
  const query = normalizeLower(detailState.attachmentQuery || '').trim();
  if (!query) return detailAttachments.value;
  return detailAttachments.value.filter((item) => item.keywords.includes(query));
});

const showMessageComposer = computed(() => Boolean(detailState.work));

const canAssignEditorForWork = computed(
  () =>
    isChiefEditor.value &&
    detailState.work &&
    ASSIGNABLE_STATUSES.has(detailState.work.status)
);

const canApprovePublication = computed(
  () => isChiefEditor.value && detailState.work?.status === 'ready_for_chief_approval'
);
const canForcePublish = computed(() => isChiefEditor.value);
const canSendToChiefWork = computed(() => {
  if (!isEditor.value || !detailState.work) return false;
  return ['in_editor_review', 'waiting_for_author', 'pending_chief_review'].includes(
    detailState.work.status
  );
});

function statusLabel(status) {
  return workStatusLabel(status);
}

function statusBadgeClass(status) {
  return workStatusBadge(status);
}

function startDetailAutoRefresh() {
  stopDetailAutoRefresh();
  detailRefreshTimer = setInterval(() => {
    if (detailState.open && detailState.work?.id) {
      refreshDetail();
    }
  }, 10000);
}

function stopDetailAutoRefresh() {
  if (detailRefreshTimer) {
    clearInterval(detailRefreshTimer);
    detailRefreshTimer = null;
  }
}

function workStatusLabel(status) {
  return WORK_STATUS_LABELS[status] || status || '—';
}

function workStatusBadge(status) {
  switch (status) {
    case 'draft':
      return 'text-bg-secondary';
    case 'pending_chief_review':
      return 'text-bg-warning text-dark';
    case 'in_editor_review':
      return 'text-bg-info';
    case 'waiting_for_author':
      return 'text-bg-danger';
    case 'ready_for_chief_approval':
      return 'text-bg-primary';
    case 'published':
      return 'text-bg-success';
    default:
      return 'text-bg-secondary';
  }
}

function workStatusAccentClass(status) {
  switch (status) {
    case 'ready_for_chief_approval':
    case 'published':
      return 'status-accent--success';
    case 'in_editor_review':
    case 'pending_chief_review':
      return 'status-accent--progress';
    case 'waiting_for_author':
      return 'status-accent--warning';
    case 'draft':
    default:
      return 'status-accent--info';
  }
}

function messageAlignmentClass(message) {
  if (!message) return 'chat-entry--neutral';
  if (message.is_system) return 'chat-entry--system';
  const userId = currentUserId.value;
  const authorId =
    normalizeId(message.author_id) ||
    normalizeId(message.author_user_id) ||
    normalizeId(message.author) ||
    normalizeId(message.authorId);
  if (userId && authorId && String(authorId) === String(userId)) {
    return 'chat-entry--sender';
  }
  return 'chat-entry--recipient';
}

function messageAuthorName(message) {
  return message?.author_display_name || message?.author_username || '—';
}

function messageHasChanges(message) {
  return Array.isArray(message?.changes) && message.changes.length > 0;
}

function messageHasAttachments(message) {
  return Array.isArray(message?.attachments) && message.attachments.length > 0;
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

function changeLabel(change) {
  return (
    change?.label ||
    change?.field_display ||
    change?.name ||
    change?.field ||
    'Поле'
  );
}

function changeOld(change) {
  if (!change) return '';
  return change.old ?? change.old_value ?? change.was ?? '';
}

function changeNew(change) {
  if (!change) return '';
  return change.new ?? change.new_value ?? change.became ?? '';
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

async function loadWorks() {
  loading.value = true;
  error.value = '';
  try {
    const params = {
      publication_kind: filters.publicationKind || undefined,
      guideline_subtype: filters.guidelineSubtype || undefined,
      training_form: filters.trainingForm || undefined,
      year: filters.year || undefined,
      search: filters.workTitle?.trim() || undefined,
      author: filters.author?.trim() || undefined,
      status: filters.status || undefined,
    };
    const response = await sciencePublishingAPI.listWorks(params);
    const data = response?.data ?? response;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    works.value = list.map((item) => ({
      ...item,
      profile_display_name: item.profile?.display_name || item.profile_display_name,
      profile_username: item.profile?.user || item.profile_username,
      publication_kind_display: item.publication_kind_display || item.get_publication_kind_display,
      guideline_subtype_display: item.guideline_subtype_display || item.get_guideline_subtype_display,
      training_form_display: item.training_form_display || item.get_training_form_display,
    }));
  } catch (err) {
    error.value = err?.message || 'Не удалось загрузить черновики.';
    toast.error(error.value);
    works.value = [];
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  loadWorks();
}

function resetFilters() {
  filters.author = '';
  filters.workTitle = '';
  filters.status = '';
  filters.publicationKind = '';
  filters.guidelineSubtype = '';
  filters.trainingForm = '';
  filters.year = '';
  loadWorks();
}

function goToDrafts(work) {
  const workId = work?.id || work?.workId;
  const query = workId ? { work: workId } : undefined;
  router.push({ name: 'SciencePublishingDrafts', query });
}

function closeTask() {
  detailState.open = false;
  detailState.work = null;
  detailState.error = '';
  detailState.note = '';
  detailState.message = '';
  resetDetailTabs();
  closeAssignModal();
  closeAuthorTaskModal();
  stopDetailAutoRefresh();
}

async function openWork(work) {
  if (!work) return;
  detailState.open = true;
  detailState.error = '';
  detailState.work = work;
  detailState.chatMessages = [];
  detailState.note = '';
  detailState.message = '';
  resetDetailTabs();
  await loadWorkChat(work.id);
  startDetailAutoRefresh();
}

async function refreshDetail() {
  const workId = detailState.work?.id;
  if (!workId) return;
  await loadWorkChat(workId, { background: true });
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

async function loadWorkChat(workId, options = {}) {
  const { background = false } = options;
  if (!workId) return;
  if (!background) {
    detailState.loading = true;
  }
  detailState.error = '';
  try {
    await loadDetailWork(workId);
    const response = await sciencePublishingAPI.listWorkChatMessages(workId);
    const data = response?.data ?? response;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    detailState.chatMessages = list.sort(
      (a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0)
    );
    if (!background) {
      detailState.note = '';
      detailState.message = '';
    }
    await nextTick();
    scrollChatToEnd();
  } catch (err) {
    detailState.chatMessages = [];
    detailState.note = '';
    detailState.message = '';
    detailState.error = err?.message || 'Не удалось загрузить переписку по работе.';
  } finally {
    if (!background) {
      detailState.loading = false;
    }
  }
}

async function performTaskAction(handler, successMessage) {
  detailState.actionLoading = true;
  try {
    await handler();
    await Promise.all([refreshDetail(), loadWorks()]);
    if (successMessage) {
      toast.success(successMessage);
    }
  } catch (err) {
    toast.error(extractErrorMessage(err, 'Не удалось выполнить действие.'));
  } finally {
    detailState.actionLoading = false;
  }
}

function setDetailTab(tab) {
  if (tab !== 'chat' && tab !== 'attachments') {
    return;
  }
  detailState.activeTab = tab;
}

function resetDetailTabs() {
  detailState.activeTab = 'chat';
  detailState.attachmentQuery = '';
}

function scrollChatToEnd() {
  if (detailState.activeTab !== 'chat') return;
  const el = detailScrollRef.value;
  if (el) {
    el.scrollTop = el.scrollHeight;
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
    const response = await sciencePublishingAPI.listProfiles({
      'roles__code': 'editor',
      page_size: 1000,
    });
    const data = response?.data ?? response;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    editorOptions.value = list.filter((profile) => {
      const roles = profile?.roles || profile?.role_assignments || [];
      return roles.some((r) => (r.code || r.role?.code) === 'editor');
    });
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
  assignForm.editor = detailState.work.current_editor?.id || detailState.work.current_editor_id || detailState.work.current_editor || '';
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
    const payload = {
      editor_profile: String(assignForm.editor),
    };
    const message = (assignForm.message || '').trim();
    if (message) {
      payload.message = message;
    }
    await sciencePublishingAPI.assignWorkEditor(detailState.work.id, payload);
    toast.success('Редактор назначен.');
    closeAssignModal();
    await Promise.all([refreshDetail(), loadWorks()]);
  } catch (err) {
    const fieldError = err?.response?.data?.editor_profile;
    const detailError = err?.response?.data?.detail || err?.response?.data?.message;
    const message = Array.isArray(fieldError)
      ? fieldError.join(' ')
      : fieldError || detailError || err?.message || 'Не удалось назначить редактора.';
    toast.error(message);
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
      detailState.work?.author_display_name ||
      detailState.work?.author_username ||
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
    await Promise.all([refreshDetail(), loadWorks()]);
  } catch (err) {
    toast.error(err?.message || 'Не удалось отправить задачу автору.');
  } finally {
    isCreatingAuthorTask.value = false;
  }
}

async function approvePublication() {
  if (!detailState.work) {
    toast.error('Данные по работе ещё не загружены.');
    return;
  }
  await performTaskAction(
    () =>
      sciencePublishingAPI.approveWorkAsChief(detailState.work.id, {
        message: detailState.note.trim() || undefined,
      }),
    'Публикация принята.'
  );
  detailState.note = '';
}

async function forcePublish() {
  if (!detailState.work) {
    toast.error('Данные по работе ещё не загружены.');
    return;
  }
  detailState.actionLoading = true;
  try {
    await sciencePublishingAPI.forcePublish(detailState.work.id, {
      message: detailState.note.trim() || undefined,
    });
    toast.success('Публикация завершена.');
    detailState.note = '';
    await Promise.all([refreshDetail(), loadWorks()]);
  } catch (err) {
    toast.error(extractErrorMessage(err, 'Не удалось опубликовать работу.'));
  } finally {
    detailState.actionLoading = false;
  }
}

function publishWork() {
  if (!detailState.work) {
    toast.error('Данные по работе ещё не загружены.');
    return;
  }
  const handler = canApprovePublication.value ? approvePublication : forcePublish;
  handler();
}

async function sendToChiefWork() {
  if (!detailState.work) return;
  detailState.actionLoading = true;
  try {
    await sciencePublishingAPI.approveWorkAsEditor(detailState.work.id, {
      message: detailState.note.trim() || undefined,
    });
    detailState.note = '';
    toast.success('Отправлено главному редактору.');
    await Promise.all([refreshDetail(), loadWorks()]);
  } catch (err) {
    toast.error(extractErrorMessage(err, 'Не удалось отправить главному редактору.'));
  } finally {
    detailState.actionLoading = false;
  }
}

async function sendMessage() {
  if (!detailState.work || !detailState.message.trim()) return;
  detailState.messageLoading = true;
  try {
    await sciencePublishingAPI.postWorkChatMessage(detailState.work.id, { content: detailState.message.trim() });
    detailState.message = '';
    await refreshDetail();
    await nextTick();
    scrollChatToEnd();
    toast.success('Сообщение отправлено.');
  } catch (err) {
    toast.error(extractErrorMessage(err, 'Не удалось отправить сообщение.'));
  } finally {
    detailState.messageLoading = false;
  }
}

onMounted(async () => {
  await ensureAccess();
  accessDenied.value = !accessAllowed.value;
  if (accessDenied.value) return;
  await fetchProfile();
  if (isAllowed.value) {
    await loadWorks();
  }
});

onUnmounted(() => {
  stopDetailAutoRefresh();
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

.task-detail__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: hidden;
}

.task-detail__layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 0;
}

.task-detail__content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 0.35rem;
}

.task-detail__empty {
  border-radius: 1.25rem;
  box-shadow: 0 18px 40px -32px rgba(15, 23, 42, 0.35);
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

.task-actions-bar {
  border-top: 1px solid var(--bs-border-color-translucent);
  padding-top: 0.75rem;
}

.task-actions .btn {
  min-width: 200px;
}

.task-detail__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.task-detail__tab {
  border: 1px solid var(--bs-border-color-translucent);
  background: rgba(255, 255, 255, 0.75);
  border-radius: 999px;
  padding: 0.5rem 1.25rem;
  color: rgba(15, 23, 42, 0.65);
  font-weight: 500;
  transition: color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.task-detail__tab:hover {
  color: rgba(15, 23, 42, 0.85);
  border-color: rgba(13, 110, 253, 0.45);
  box-shadow: 0 12px 28px -20px rgba(15, 23, 42, 0.35);
}

.task-detail__tab--active {
  background: var(--bs-primary);
  color: #fff;
  border-color: var(--bs-primary);
  box-shadow: 0 18px 36px -22px rgba(13, 110, 253, 0.6);
}

.task-detail__tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 999px;
  padding: 0 0.5rem;
  margin-left: 0.5rem;
  font-size: 0.85rem;
}

.task-chat {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 0.5rem;
}

.task-chat__filter {
  padding: 1rem 1.25rem;
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 18px 40px -30px rgba(15, 23, 42, 0.35);
}

.task-chat__selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.task-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--bs-border-color-translucent);
  background: rgba(248, 249, 252, 0.8);
  color: var(--bs-body-color);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.1s ease;
}

.task-chip:hover {
  border-color: rgba(13, 110, 253, 0.35);
  box-shadow: 0 12px 30px -24px rgba(15, 23, 42, 0.35);
}

.task-chip--active {
  border-color: var(--bs-primary);
  background: rgba(13, 110, 253, 0.1);
  box-shadow: 0 14px 34px -26px rgba(13, 110, 253, 0.4);
}

.task-chip__title {
  font-weight: 600;
}

.task-chat__conversation {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 1.5rem;
  position: relative;
}

.task-chat__timeline {
  position: relative;
  display: flex;
  justify-content: center;
}

.task-chat__timeline::after {
  content: "";
  position: absolute;
  top: 0.75rem;
  bottom: -2.5rem;
  width: 2px;
  background: rgba(15, 23, 42, 0.08);
}

.task-chat__conversation:last-child .task-chat__timeline::after {
  display: none;
}

.task-chat__dot {
  display: inline-flex;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin-top: 0.25rem;
  box-shadow: 0 0 0 4px rgba(15, 23, 42, 0.05);
}

.status-accent--info {
  background: #0d6efd;
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.15);
}

.status-accent--progress {
  background: #f59f00;
  box-shadow: 0 0 0 4px rgba(245, 159, 0, 0.18);
}

.status-accent--warning {
  background: #ffa94d;
  box-shadow: 0 0 0 4px rgba(255, 169, 77, 0.2);
}

.status-accent--success {
  background: #198754;
  box-shadow: 0 0 0 4px rgba(25, 135, 84, 0.18);
}

.status-accent--muted {
  background: #adb5bd;
  box-shadow: 0 0 0 4px rgba(173, 181, 189, 0.2);
}

.task-chat__content {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 32px 80px -48px rgba(15, 23, 42, 0.35);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.task-chat__content:hover {
  border-color: rgba(13, 110, 253, 0.35);
  box-shadow: 0 28px 70px -48px rgba(15, 23, 42, 0.45);
}

.task-chat__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
}

.task-chat__subject {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.task-chat__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.task-chat__divider {
  color: rgba(15, 23, 42, 0.25);
}

.task-chat__status {
  font-size: 0.875rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  text-transform: none;
  letter-spacing: 0;
}

.task-chat__lead {
  font-size: 0.98rem;
  line-height: 1.6;
  color: rgba(15, 23, 42, 0.85);
  white-space: pre-line;
}

.chat-thread {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-entry {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(248, 249, 252, 0.9);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chat-entry__heading {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
}

.chat-entry__name {
  font-weight: 600;
  color: rgba(15, 23, 42, 0.85);
}

.chat-entry__body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chat-entry__changes,
.chat-entry__attachments {
  padding: 0.75rem 0.9rem;
  border-radius: 0.85rem;
  background: rgba(248, 249, 252, 0.75);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.chat-entry__subtitle {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.chat-change-list,
.chat-attachment-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.chat-entry--sender {
  align-self: flex-end;
  margin-left: auto;
  border-color: rgba(13, 110, 253, 0.25);
  background: rgba(13, 110, 253, 0.09);
  color: rgba(15, 23, 42, 0.85);
}

.chat-entry--recipient,
.chat-entry--summary {
  align-self: flex-start;
  margin-right: auto;
  border-color: rgba(25, 135, 84, 0.25);
  background: rgba(25, 135, 84, 0.09);
  color: rgba(15, 23, 42, 0.85);
}

.chat-entry--system {
  border-style: dashed;
  color: rgba(15, 23, 42, 0.65);
  background: rgba(108, 117, 125, 0.1);
}

.task-attachments {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.task-attachments__search .form-control {
  border-radius: 999px;
  padding-left: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
}

.task-attachments__search-icon {
  border-top-left-radius: 999px;
  border-bottom-left-radius: 999px;
  background: rgba(15, 23, 42, 0.05);
  border: 1px solid var(--bs-border-color-translucent);
  border-right: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.attachment-card {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.1rem;
  padding: 1.1rem 1.25rem;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 26px 60px -44px rgba(15, 23, 42, 0.4);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.attachment-card:hover {
  border-color: rgba(13, 110, 253, 0.35);
  box-shadow: 0 28px 70px -48px rgba(15, 23, 42, 0.45);
}

.attachment-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.attachment-card__title {
  font-weight: 600;
}

.attachment-card__link {
  text-decoration: none;
}

.attachment-card__link:hover {
  text-decoration: underline;
}

.attachment-card__context {
  line-height: 1.4;
}

.task-composer .form-control {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.task-composer .btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.task-attachments__dot::before,
.attachment-card__dot::before {
  content: '';
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
