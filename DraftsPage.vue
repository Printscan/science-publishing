<template>
  <div class="drafts container-fluid py-4">
    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
      <h2 class="page-title mb-0">Черновики</h2>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary d-flex align-items-center gap-2" :disabled="loading" @click="loadWorks">
          <RefreshCcw size="16" />
          <span>Обновить</span>
        </button>
        <RouterLink class="btn btn-primary d-flex align-items-center gap-2" :to="{ name: 'SciencePublishingSubmit' }">
          <FilePlus size="16" />
          <span>Подать документ</span>
        </RouterLink>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row g-3">
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Ваши материалы (черновики)</h6>
            <span class="badge rounded-pill text-bg-secondary-subtle text-secondary">{{ works.length }}</span>
          </div>
          <div class="list-group list-group-flush">
            <button
              v-for="w in works"
              :key="w.id"
              class="list-group-item list-group-item-action d-flex justify-content-between align-items-start"
              :class="{ active: selectedWork && selectedWork.id === w.id }"
              @click="selectWork(w)"
            >
              <div class="me-2">
                <div class="fw-semibold">{{ w.discipline_name || 'Без названия' }}</div>
                <small class="text-muted">{{ formatStatus(w.status) }}</small>
              </div>
              <span class="badge text-bg-light">{{ w.year || '-' }}</span>
            </button>
            <div v-if="!loading && works.length === 0" class="text-muted small p-3">
              Черновики не найдены.
            </div>
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div v-if="!selectedWork" class="text-muted text-center py-5">
          Выберите черновик слева, чтобы просмотреть детали и отправить правки.
        </div>

        <div v-else class="card shadow-sm">
          <div class="card-header">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <h6 class="mb-0">{{ selectedWork.discipline_name || 'Без названия' }}</h6>
                <small class="text-muted">Статус: {{ formatStatus(selectedWork.status) }}</small>
              </div>
              <ul class="nav nav-pills">
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: tab === 'edit' }" @click="tab = 'edit'">Редактирование</button>
                </li>
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: tab === 'chat' }" @click="openChat()">Чат</button>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="tab === 'edit'" class="card-body">
            <form class="row g-3" @submit.prevent="saveCorrections">
              <div class="col-12 col-md-6 col-xl-3">
                <label class="form-label">Ректор</label>
                <input v-model="form.rector_name" type="text" class="form-control" placeholder="Например: Федюнин О. Н." />
              </div>
              <div class="col-12 col-md-6 col-xl-3">
                <label class="form-label">Количество страниц</label>
                <input v-model.number="form.pages_count" type="number" min="1" class="form-control" placeholder="Укажите число" />
              </div>
              <div class="col-12 col-md-6 col-xl-3">
                <label class="form-label">Год *</label>
                <input v-model.number="form.year" type="number" min="1900" max="2100" class="form-control" required />
              </div>
              <div class="col-12 col-md-6 col-xl-3">
                <label class="form-label">УДК</label>
                <input v-model="form.udc" type="text" class="form-control" placeholder="001.891:006.354" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Заголовок *</label>
                <input v-model="form.discipline_name" type="text" class="form-control" required placeholder="Например: Веб-программирование" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">ББК</label>
                <input v-model="form.bbk" type="text" class="form-control" placeholder="Например: 39.71" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Подзаголовок</label>
                <input v-model="form.discipline_topic" type="text" class="form-control" placeholder="Добавьте уточнение при необходимости" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Разработчик(-и)</label>
                <input v-model="form.developers" type="text" class="form-control" placeholder="Укажите исполнителей через запятую" />
              </div>
              <div class="col-12 col-xl-4">
                <label class="form-label">Вид публикации *</label>
                <select v-model="form.publication_kind" class="form-select" required>
                  <option disabled value="">Выберите вид</option>
                  <option v-for="opt in publicationKinds" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
              <div class="col-12 col-xl-4" v-if="form.publication_kind === 'method_guidelines'">
                <label class="form-label">Тип методических указаний *</label>
                <select v-model="form.guideline_subtype" class="form-select" required>
                  <option disabled value="">Выберите тип</option>
                  <option v-for="opt in guidelineSubtypes" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
              <div class="col-12 col-xl-4">
                <label class="form-label">Форма обучения *</label>
                <select v-model="form.training_form" class="form-select" required>
                  <option disabled value="">Выберите форму</option>
                  <option v-for="opt in trainingForms" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Научный редактор (при наличии)</label>
                <input v-model="form.scientific_editor" type="text" class="form-control" placeholder="Например: Ковальский В. А." />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Компьютерный набор</label>
                <input v-model="form.computer_layout" type="text" class="form-control" placeholder="Например: Ясников М. А." />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Полное ФИО автора</label>
                <input v-model="form.author_full_name" type="text" class="form-control" placeholder="Например: Сирота Давид Ильич" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Соавторы</label>
                <input v-model="form.co_authors" type="text" class="form-control" placeholder="Укажите соавторов при наличии" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Факультет</label>
                <input v-model="form.faculty" type="text" class="form-control" placeholder="Например: ФИТ" />
              </div>
              <div class="col-12 col-xl-6">
                <label class="form-label">Кафедра</label>
                <input v-model="form.department" type="text" class="form-control" placeholder="Например: Компьютерные технологии и системы (КТС)" />
              </div>
              <div class="col-12">
                <label class="form-label">Краткая информация</label>
                <textarea
                  v-model="form.short_description"
                  class="form-control"
                  rows="4"
                  placeholder="Введите аннотацию документа"
                ></textarea>
                <div class="form-text text-end">Осталось символов: {{ shortDescriptionRemaining }}</div>
              </div>
              <div class="col-12">
                <label class="form-label">Файл публикации</label>
                <input ref="fileInput" type="file" class="form-control" accept=".pdf,.doc,.docx,.zip" @change="onFile" />
                <div class="form-text d-flex flex-wrap align-items-center gap-2">
                  <span>Допустимые форматы: PDF, DOC, DOCX, ZIP.</span>
                  <template v-if="documentUrl(selectedWork)">
                    <span class="text-muted">Текущий файл:</span>
                    <a :href="documentUrl(selectedWork)" target="_blank" rel="noopener">Скачать</a>
                  </template>
                </div>
              </div>
              <div class="col-12">
                <label class="form-label d-flex align-items-center gap-1" for="correction_message">
                  Комментарий для редактора
                  <span v-if="isAwaitingCorrections" class="text-danger">*</span>
                </label>
                <textarea
                  id="correction_message"
                  v-model="form.correction_message"
                  class="form-control"
                  rows="3"
                  placeholder="Расскажите, что изменили в работе"
                  :required="isAwaitingCorrections"
                ></textarea>
                <div v-if="!isAwaitingCorrections" class="form-text text-muted">
                  Комментарий нужен только при ответе на замечания редактора.
                </div>
              </div>
              <div class="col-12 text-end">
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2" />
                  Сохранить изменения
                </button>
              </div>
            </form>
          </div>

          <div v-else class="card-body">
            <div v-if="chatLoading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка…</span>
              </div>
            </div>
            <div v-else class="draft-chat">
              <div v-if="!orderedChatTasks.length" class="draft-chat__empty text-muted text-center py-5">
                История переписки пока пуста.
              </div>
              <template v-else>
                <div class="task-chat">
                  <div
                    v-for="task in orderedChatTasks"
                    :key="task.id"
                    class="task-chat__conversation"
                  >
                    <div class="task-chat__timeline">
                      <span class="task-chat__dot" :class="taskStatusAccentClass(task.status)"></span>
                    </div>
                    <div class="task-chat__content">
                      <header class="task-chat__header">
                        <div>
                          <div class="task-chat__subject">{{ task.subject || 'Без темы' }}</div>
                          <div class="task-chat__meta text-muted small">
                            <span>{{ taskSenderName(task) }}</span>
                            <span class="task-chat__divider" aria-hidden="true">•</span>
                            <span>{{ formatDateTime(task.created_at) }}</span>
                          </div>
                        </div>
                        <span class="badge task-chat__status" :class="taskStatusBadgeClass(task.status)">
                          {{ formatStatus(task.status) }}
                        </span>
                      </header>

                      <p v-if="task.message" class="task-chat__lead">
                        {{ task.message }}
                      </p>

                      <div v-if="task.messages && task.messages.length" class="chat-thread">
                        <article
                          v-for="message in task.messages"
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
                                  <span class="text-muted ms-1">
                                    было {{ formatChangeValue(changeOld(change)) }}
                                  </span>
                                  <span class="ms-1">
                                    стало {{ formatChangeValue(changeNew(change)) }}
                                  </span>
                                </li>
                              </ul>
                            </div>
                            <div v-if="messageHasAttachments(message)" class="chat-entry__attachments">
                              <div class="chat-entry__subtitle text-muted small">Вложения</div>
                              <ul class="chat-attachment-list">
                                <li
                                  v-for="attachment in message.attachments"
                                  :key="attachment.url || attachment.absolute_url || attachment.name"
                                >
                                  <a
                                    v-if="attachment.absolute_url || attachment.url"
                                    :href="attachment.absolute_url || attachment.url"
                                    target="_blank"
                                    rel="noopener"
                                  >
                                    {{ attachment.name || attachment.label || 'Файл' }}
                                  </a>
                                  <span v-else>{{ attachment.name || attachment.label || 'Файл' }}</span>
                                </li>
                              </ul>
                            </div>
                          </div>
                        </article>
                      </div>

                      <div v-if="draftTaskSummaries[task.id]" class="chat-entry chat-entry--summary">
                        <div class="chat-entry__heading">
                          <div class="chat-entry__name">{{ taskRecipientName(task) }}</div>
                          <span class="chat-entry__time text-muted small">
                            {{ formatDateTime(task.closed_at || task.updated_at) }}
                          </span>
                        </div>
                        <div class="chat-entry__body">
                          <p v-if="draftTaskSummaries[task.id].note" class="mb-2">
                            {{ draftTaskSummaries[task.id].note }}
                          </p>
                          <div
                            v-if="draftTaskSummaries[task.id].changes && draftTaskSummaries[task.id].changes.length"
                            class="chat-entry__changes"
                          >
                            <div class="chat-entry__subtitle text-muted small">Итоги</div>
                            <ul class="chat-change-list">
                              <li
                                v-for="change in draftTaskSummaries[task.id].changes"
                                :key="change.field || change.name || change.label"
                              >
                                <strong>{{ changeLabel(change) }}:</strong>
                                <span class="text-muted ms-1">
                                  было {{ formatChangeValue(changeOld(change)) }}
                                </span>
                                <span class="ms-1">
                                  стало {{ formatChangeValue(changeNew(change)) }}
                                </span>
                              </li>
                            </ul>
                          </div>
                          <div
                            v-if="draftTaskSummaries[task.id].attachments && draftTaskSummaries[task.id].attachments.length"
                            class="chat-entry__attachments"
                          >
                            <div class="chat-entry__subtitle text-muted small">Файлы</div>
                            <ul class="chat-attachment-list">
                              <li
                                v-for="attachment in draftTaskSummaries[task.id].attachments"
                                :key="attachment.url || attachment.absolute_url || attachment.name"
                              >
                                <a
                                  v-if="attachment.absolute_url || attachment.url"
                                  :href="attachment.absolute_url || attachment.url"
                                  target="_blank"
                                  rel="noopener"
                                >
                                  {{ attachment.name || attachment.label || 'Файл' }}
                                </a>
                                <span v-else>{{ attachment.name || attachment.label || 'Файл' }}</span>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
    </div>

                <form class="draft-chat__composer" @submit.prevent="sendMessage">
                  <div class="row g-3">
                    <div class="col-12 col-md-4">
                      <label class="form-label" for="draft-task-select">Задача</label>
                      <select id="draft-task-select" v-model="activeTaskId" class="form-select">
                        <option
                          v-for="task in orderedChatTasks"
                          :key="task.id"
                          :value="task.id"
                        >
                          {{ task.subject || 'Без темы' }}
                        </option>
                      </select>
                    </div>
                    <div class="col-12 col-md-8">
                      <label class="form-label" for="draft-message-input">Сообщение</label>
                      <textarea
                        id="draft-message-input"
                        v-model="messageDraft"
                        class="form-control"
                        rows="2"
                        placeholder="Напишите ответ редакции"
                      ></textarea>
                    </div>
                    <div class="col-12 d-flex justify-content-end gap-2 flex-wrap">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        :disabled="closing || sending || !canCloseActiveTask"
                        @click="closeActiveTask"
                      >
                        <span
                          v-if="closing"
                          class="spinner-border spinner-border-sm me-2"
                          role="status"
                        ></span>
                        Закрыть задачу
                      </button>
                      <button
                        type="submit"
                        class="btn btn-primary"
                        :disabled="sending || !messageDraft.trim() || !activeTask"
                      >
                        <span
                          v-if="sending"
                          class="spinner-border spinner-border-sm me-2"
                          role="status"
                        ></span>
                        Отправить
                      </button>
                    </div>
                  </div>
                </form>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { RefreshCcw, FilePlus } from 'lucide-vue-next';
import { useToast } from 'vue-toastification';

import { sciencePublishingAPI } from '@/modules/science-publishing/js/science-publishing.js';
import { apiClient } from '@/js/api/manager.js';

const toast = useToast();

const SHORT_DESCRIPTION_LIMIT = 400;
const editableFields = [
  'rector_name',
  'pages_count',
  'year',
  'udc',
  'discipline_name',
  'bbk',
  'discipline_topic',
  'developers',
  'publication_kind',
  'guideline_subtype',
  'training_form',
  'scientific_editor',
  'computer_layout',
  'author_full_name',
  'co_authors',
  'faculty',
  'department',
  'short_description',
];

const publicationKinds = [
  { value: 'method_guidelines', label: 'Методические указания' },
  { value: 'lab_practicum', label: 'Лабораторный практикум' },
  { value: 'textbook', label: 'Учебное пособие' },
  { value: 'monograph', label: 'Монография' },
  { value: 'article', label: 'Статья' },
  { value: 'theses', label: 'Тезисы' },
];

const guidelineSubtypes = [
  { value: 'coursework', label: 'Курсовая работа' },
  { value: 'laboratory', label: 'Лабораторная работа' },
  { value: 'practical', label: 'Практическая работа' },
];

const trainingForms = [
  { value: 'full_time', label: 'Очная' },
  { value: 'part_time', label: 'Заочная' },
  { value: 'mixed', label: 'Очно-заочная' },
];

const works = ref([]);
const loading = ref(false);
const error = ref('');

const selectedWork = ref(null);
const tab = ref('edit');
const isAwaitingCorrections = computed(() => selectedWork.value?.status === 'waiting_for_author');
const form = reactive({
  rector_name: '',
  pages_count: null,
  year: new Date().getFullYear(),
  udc: '',
  discipline_name: '',
  bbk: '',
  discipline_topic: '',
  developers: '',
  publication_kind: '',
  guideline_subtype: '',
  training_form: '',
  scientific_editor: '',
  computer_layout: '',
  author_full_name: '',
  co_authors: '',
  faculty: '',
  department: '',
  short_description: '',
  document: null,
  correction_message: '',
});

const saving = ref(false);
const fileInput = ref(null);

const chatLoading = ref(false);
const taskHistory = ref([]);
const activeTaskId = ref(null);
const messageDraft = ref('');
const sending = ref(false);
const closing = ref(false);
const currentProfile = ref(null);
const profileLoading = ref(true);

const STATUS_LABELS = {
  draft: 'Черновик',
  pending_chief_review: 'На рассмотрении у руководителя',
  in_editor_review: 'У редактора',
  waiting_for_author: 'Ожидает автора',
  ready_for_chief_approval: 'Готово к утверждению',
  published: 'Опубликовано',
};

const shortDescriptionRemaining = computed(
  () => SHORT_DESCRIPTION_LIMIT - (form.short_description?.length ?? 0)
);

const currentUsername = computed(() => currentProfile.value?.user?.username || null);
const canCloseActiveTask = computed(() => {
  const task = activeTask.value;
  if (!task || task.closed_at) return false;
  const userId = currentProfile.value?.user?.id || currentProfile.value?.user_id;
  if (userId && String(task.recipient) === String(userId)) return true;
  if (task.recipient_username && currentUsername.value) {
    return task.recipient_username === currentUsername.value;
  }
  return false;
});

watch(
  () => form.publication_kind,
  (value) => {
    if (value !== 'method_guidelines') {
      form.guideline_subtype = '';
    }
  }
);

watch(
  () => form.short_description,
  (value) => {
    if (value && value.length > SHORT_DESCRIPTION_LIMIT) {
      form.short_description = value.slice(0, SHORT_DESCRIPTION_LIMIT);
    }
  }
);

watch(
  taskHistory,
  (tasks) => {
    if (!Array.isArray(tasks) || tasks.length === 0) {
      activeTaskId.value = null;
      return;
    }
    if (!tasks.some((task) => task.id === activeTaskId.value)) {
      activeTaskId.value = tasks[tasks.length - 1].id;
    }
  },
  { immediate: true }
);

function formatStatus(status) {
  return STATUS_LABELS[status] || status || '-';
}

const activeTask = computed(() => taskHistory.value.find((task) => task.id === activeTaskId.value) || null);
const orderedChatTasks = computed(() => {
  const list = Array.isArray(taskHistory.value) ? [...taskHistory.value] : [];
  return list.sort((a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0));
});
const draftTaskSummaries = computed(() => {
  const summaries = {};
  (taskHistory.value || []).forEach((task) => {
    const summary = buildTaskSummary(task);
    if (summary) {
      summaries[task.id] = summary;
    }
  });
  return summaries;
});

function taskStatusBadgeClass(status) {
  switch (status) {
    case 'new':
      return 'text-bg-secondary';
    case 'in_progress':
    case 'in_editor_review':
      return 'text-bg-warning text-dark';
    case 'done':
    case 'ready_for_chief_approval':
      return 'text-bg-success';
    case 'waiting_for_author':
      return 'text-bg-info';
    case 'archived':
      return 'text-bg-dark';
    default:
      return 'text-bg-secondary';
  }
}

function taskStatusAccentClass(status) {
  switch (status) {
    case 'done':
    case 'ready_for_chief_approval':
      return 'status-accent--success';
    case 'in_progress':
    case 'in_editor_review':
    case 'pending_chief_review':
      return 'status-accent--progress';
    case 'waiting_for_author':
      return 'status-accent--warning';
    case 'archived':
      return 'status-accent--muted';
    case 'new':
    default:
      return 'status-accent--info';
  }
}

function taskSenderName(task) {
  if (!task) return 'Система';
  return task.sender_display_name || task.sender_username || 'Система';
}

function taskRecipientName(task) {
  if (!task) return 'Система';
  return task.recipient_display_name || task.recipient_username || 'Система';
}

function messageAlignmentClass(message) {
  if (!message) return 'chat-entry--neutral';
  if (message.is_system) return 'chat-entry--system';
  const username = currentProfile.value?.user?.username;
  if (username && message.author_username === username) {
    return 'chat-entry--recipient';
  }
  return 'chat-entry--sender';
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
function formatChangeValue(value) {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  if (typeof value === 'string') {
    return value;
  }
  if (value instanceof Date) {
    return value.toLocaleString('ru-RU');
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function changeLabel(change) {
  return change?.label || change?.field_display || change?.name || change?.field || 'Поле';
}

function changeOld(change) {
  if (!change) return '';
  return change.old ?? change.old_value ?? change.was ?? '';
}

function changeNew(change) {
  if (!change) return '';
  return change.new ?? change.new_value ?? change.became ?? '';
}

function buildTaskSummary(task) {
  if (!task) return null;
  const payload = task.payload || {};
  const note = payload.note || '';
  const changes = Array.isArray(payload.changes) ? payload.changes : [];
  const attachments = Array.isArray(payload.attachments) ? payload.attachments : [];
  const hasDetails = Boolean(note) || changes.length > 0 || attachments.length > 0;
  if (!task.closed_at || !hasDetails) {
    return null;
  }
  return {
    note,
    changes,
    attachments,
    action: payload.action || null,
    workStatus: payload.work_status || null,
  };
}

function documentUrl(work) {
  if (!work?.document) return null;
  try {
    return new URL(work.document, apiClient.baseUrl).toString();
  } catch {
    const path = work.document.startsWith('/') ? work.document.slice(1) : work.document;
    return `${apiClient.baseUrl}${path}`;
  }
}

async function fetchCurrentProfile() {
  profileLoading.value = true;
  try {
    const response = await sciencePublishingAPI.getCurrentProfile();
    currentProfile.value = response?.data ?? response;
  } catch (error_) {
    currentProfile.value = null;
    console.error('Не удалось загрузить профиль автора', error_);
  } finally {
    profileLoading.value = false;
  }
}

function fillFormFromWork(work) {
  form.rector_name = work.rector_name || '';
  form.pages_count = work.pages_count ?? null;
  form.year = work.year ?? new Date().getFullYear();
  form.udc = work.udc || '';
  form.discipline_name = work.discipline_name || '';
  form.bbk = work.bbk || '';
  form.discipline_topic = work.discipline_topic || '';
  form.developers = work.developers || '';
  form.publication_kind = work.publication_kind || '';
  form.guideline_subtype = work.guideline_subtype || '';
  form.training_form = work.training_form || '';
  form.scientific_editor = work.scientific_editor || '';
  form.computer_layout = work.computer_layout || '';
  form.author_full_name = work.author_full_name || '';
  form.co_authors = work.co_authors || '';
  form.faculty = work.faculty || '';
  form.department = work.department || '';
  form.short_description = work.short_description || '';
  form.document = null;
  form.correction_message = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function loadWorks() {
  loading.value = true;
  error.value = '';
  try {
    if (!currentProfile.value) {
      await fetchCurrentProfile();
    }
    const response = await sciencePublishingAPI.listMyWorks();
    const data = response?.data ?? response;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    works.value = list.filter((item) => item.status !== 'published');
    if (selectedWork.value) {
      const updated = works.value.find((work) => work.id === selectedWork.value.id);
      if (updated) {
        selectWork(updated);
      } else {
        selectedWork.value = null;
      }
    }
  } catch (error_) {
    error.value = error_?.message || 'Не удалось загрузить список черновиков.';
  } finally {
    loading.value = false;
  }
}

function selectWork(work) {
  selectedWork.value = work;
  tab.value = 'edit';
  taskHistory.value = [];
  activeTaskId.value = null;
  messageDraft.value = '';
  fillFormFromWork(work);
}

function onFile(event) {
  const file = event.target?.files?.[0] ?? null;
  form.document = file;
}

async function saveCorrections() {
  if (!selectedWork.value) return;

  const awaitingCorrections = isAwaitingCorrections.value;
  const message = form.correction_message?.trim();

  const payload = {};
  editableFields.forEach((key) => {
    const value = form[key];
    if (value !== undefined && value !== null && value !== '') {
      payload[key] = value;
    }
  });

  if (form.document) {
    payload.document = form.document;
  }

  const hasDataChanges = Object.keys(payload).length > 0;

  if (!awaitingCorrections && !hasDataChanges) {
    toast.info('Изменения для сохранения отсутствуют.');
    return;
  }

  if (awaitingCorrections && !message) {
    toast.error('Комментарий обязателен для ответа редактору.');
    return;
  }

  if (awaitingCorrections && !hasDataChanges) {
    toast.error('Добавьте файл или обновите данные перед отправкой исправлений.');
    return;
  }

  saving.value = true;
  try {
    const workId = selectedWork.value.id;
    if (awaitingCorrections) {
      payload.message = message;
      await sciencePublishingAPI.submitWorkCorrections(workId, payload);
      toast.success('Исправления отправлены.');
    } else {
      await sciencePublishingAPI.updateWork(workId, payload);
      toast.success('Черновик обновлён.');
    }
    form.correction_message = '';
    form.document = null;
    if (fileInput.value) {
      fileInput.value.value = '';
    }
    await loadWorks();
    if (tab.value === 'chat' && selectedWork.value) {
      await openChat(activeTaskId.value);
    }
  } catch (error_) {
    const fallback = awaitingCorrections
      ? 'Не удалось отправить исправления.'
      : 'Не удалось обновить черновик.';
    toast.error(error_?.message || fallback);
  } finally {
    saving.value = false;
  }
}

async function openChat(preferredTaskId = null) {
  tab.value = 'chat';
  if (!selectedWork.value) return;

  chatLoading.value = true;
  try {
    const response = await sciencePublishingAPI.listTasks({
      work: selectedWork.value.id,
    });
    const data = response?.data ?? response;
    const rawTasks = Array.isArray(data) ? data : data?.results ?? [];
    const normalized = rawTasks
      .filter(
        (task) =>
          task.work === selectedWork.value.id ||
          task.work_id === selectedWork.value.id ||
          task.work?.id === selectedWork.value.id
      )
      .map((task) => {
        const messages = Array.isArray(task.messages) ? [...task.messages] : [];
        messages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        return {
          ...task,
          messages,
        };
      })
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

    taskHistory.value = normalized;
    const fallbackId = preferredTaskId ?? activeTaskId.value;
    if (fallbackId && normalized.some((task) => task.id === fallbackId)) {
      activeTaskId.value = fallbackId;
    } else if (normalized.length > 0) {
      activeTaskId.value = normalized[normalized.length - 1].id;
    } else {
      activeTaskId.value = null;
    }
  } catch (error_) {
    toast.error(error_?.message || 'Не удалось загрузить историю задач.');
  } finally {
    chatLoading.value = false;
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

async function sendMessage() {
  const task = activeTask.value;
  if (!task || !messageDraft.value.trim()) return;

  sending.value = true;
  try {
    await sciencePublishingAPI.postTaskMessage(task.id, { content: messageDraft.value.trim() });
    messageDraft.value = '';
    await openChat(task.id);
  } catch (error_) {
    toast.error(error_?.message || 'Не удалось отправить сообщение.');
  } finally {
    sending.value = false;
  }
}

async function closeActiveTask() {
  const task = activeTask.value;
  if (!task || !canCloseActiveTask.value) return;
  closing.value = true;
  try {
    const payload = {};
    const note = messageDraft.value.trim();
    if (note) {
      payload.message = note;
    }
    await sciencePublishingAPI.closeTask(task.id, payload);
    messageDraft.value = '';
    await openChat(task.id);
    toast.success('Задача закрыта.');
  } catch (error_) {
    toast.error(error_?.message || 'Не удалось закрыть задачу.');
  } finally {
    closing.value = false;
  }
}

onMounted(async () => {
  await fetchCurrentProfile();
  await loadWorks();
});
</script>

<style scoped>
.page-title {
  font-weight: 600;
}

.list-group-item.active {
  background: var(--bs-primary-bg-subtle);
  color: var(--bs-primary);
  border-color: var(--bs-primary);
}
.draft-chat {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.draft-chat__empty {
  border: 1px dashed var(--bs-border-color);
  border-radius: 1.25rem;
}

.task-chat {
  display: flex;
  flex-direction: column;
  gap: 2rem;
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
  content: '';
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
  font-size: 0.75rem;
}

.chat-change-list,
.chat-attachment-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.chat-entry--sender {
  border-color: rgba(13, 110, 253, 0.25);
  background: rgba(13, 110, 253, 0.09);
  color: rgba(15, 23, 42, 0.85);
}

.chat-entry--recipient,
.chat-entry--summary {
  align-self: flex-end;
  border-color: rgba(25, 135, 84, 0.25);
  background: rgba(25, 135, 84, 0.09);
  color: rgba(15, 23, 42, 0.85);
}

.chat-entry--system {
  border-style: dashed;
  color: rgba(15, 23, 42, 0.65);
  background: rgba(108, 117, 125, 0.1);
}

.draft-chat__composer {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  padding: 1.5rem;
  background: rgba(248, 249, 252, 0.75);
  box-shadow: 0 24px 60px -46px rgba(15, 23, 42, 0.25);
}

.draft-chat__composer textarea {
  resize: vertical;
  min-height: 120px;
}

@media (max-width: 767px) {
  .task-chat__conversation {
    grid-template-columns: 20px 1fr;
    gap: 1rem;
  }

  .task-chat__content {
    padding: 1.1rem;
  }

  .draft-chat__composer {
    padding: 1rem;
  }
}
</style>

