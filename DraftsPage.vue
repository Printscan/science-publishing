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
                <label class="form-label" for="correction_message">Комментарий для редактора *</label>
                <textarea
                  id="correction_message"
                  v-model="form.correction_message"
                  class="form-control"
                  rows="3"
                  placeholder="Опишите, что поменяли и почему"
                  required
                ></textarea>
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
            <div v-else>
              <div v-if="!taskHistory.length" class="text-muted text-center">
                История переписки пока пуста.
              </div>
              <template v-else>
                <div class="conversation-timeline">
                  <div v-for="task in taskHistory" :key="task.id" class="timeline-item border rounded p-3 mb-3">
                    <div class="d-flex justify-content-between flex-wrap gap-2 mb-2">
                      <div>
                        <div class="fw-semibold">{{ task.subject }}</div>
                        <div class="small text-muted">
                          {{ formatTimelineParticipant(task.sender_username) }} &rarr;
                          {{ formatTimelineParticipant(task.recipient_username) }}
                        </div>
                      </div>
                      <div class="text-end">
                        <span class="badge text-bg-secondary">{{ task.status_display }}</span>
                        <div class="small text-muted">{{ formatDateTime(task.created_at) }}</div>
                      </div>
                    </div>
                    <div v-if="task.message" class="mb-3">
                      {{ task.message }}
                    </div>
                    <div v-if="task.messages?.length" class="timeline-messages">
                      <div
                        v-for="msg in task.messages"
                        :key="msg.id"
                        :class="messageRowClass(msg)"
                      >
                        <div :class="messageBubbleClass(msg)">
                          <div :class="messageHeaderClass(msg)">
                            <div>
                              <strong>{{ msg.author_display_name || msg.author_username || '?????' }}</strong>
                              <template v-if="msg.is_system">
                                <span class="badge text-bg-dark ms-1">?????</span>
                              </template>
                              <template v-else>
                                <span
                                  v-for="role in msg.author_roles"
                                  :key="`${msg.id}-${role.code}`"
                                  class="badge text-bg-primary-subtle text-primary ms-1"
                                >
                                  {{ role.name }}
                                </span>
                              </template>
                            </div>
                            <span>{{ formatDateTime(msg.created_at) }}</span>
                          </div>
                          <div v-if="msg.content" class="message-body mt-2">{{ msg.content }}</div>
                          <div v-if="hasChangeDetails(msg)" class="message-changes mt-2">
                            <button
                              class="btn btn-sm btn-link px-0"
                              type="button"
                              @click="toggleMessageDetails(msg.id)"
                            >
                              <span v-if="isMessageExpanded(msg.id)">*?????????* - ?????</span>
                              <span v-else>*?????????* - ??????</span>
                            </button>
                            <div v-if="isMessageExpanded(msg.id)" class="message-change-panel mt-2">
                              <ul v-if="msg.changes?.length" class="list-unstyled small mb-2">
                                <li
                                  v-for="change in msg.changes"
                                  :key="`${msg.id}-${change.field || change.label || change.old}`"
                                  class="message-change-entry"
                                >
                                  <div class="fw-semibold">{{ change.label }}</div>
                                  <div class="small text-muted">
                                    {{ formatChangeValue(change.old) }}
                                    <span class="mx-1">&rarr;</span>
                                    {{ formatChangeValue(change.new) }}
                                  </div>
                                </li>
                              </ul>
                              <div v-if="msg.attachments?.length" class="message-attachments small">
                                <div class="fw-semibold">????????:</div>
                                <ul class="list-unstyled mb-0">
                                  <li
                                    v-for="file in msg.attachments"
                                    :key="`${msg.id}-${file.field || file.url || file.name || file.label}`"
                                  >
                                    <a
                                      v-if="file.absolute_url || file.url"
                                      :href="file.absolute_url || file.url"
                                      target="_blank"
                                      rel="noopener"
                                    >
                                      {{ file.name || file.label || '????' }}
                                    </a>
                                    <span v-else>{{ file.name || file.label || '????' }}</span>
                                  </li>
                                </ul>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <form class="chat-reply mt-3" @submit.prevent="sendMessage">
                  <div class="row g-2">
                    <div class="col-12 col-md-4">
                      <label class="form-label">Задача для ответа</label>
                      <select v-model="activeTaskId" class="form-select">
                        <option v-for="task in taskHistory" :key="task.id" :value="task.id">
                          {{ task.subject }}
                        </option>
                      </select>
                    </div>
                    <div class="col-12 col-md-8">
                      <label class="form-label">Сообщение</label>
                      <textarea
                        v-model="messageDraft"
                        rows="2"
                        class="form-control"
                        placeholder="Напишите ответ"
                      ></textarea>
                    </div>
                    <div class="col-12 text-end">
                      <button class="btn btn-primary" :disabled="sending || !messageDraft.trim() || !activeTask">
                        <span v-if="sending" class="spinner-border spinner-border-sm me-2" />
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
const expandedMessages = ref(new Set());
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
    expandedMessages.value = new Set();
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

function formatTimelineParticipant(username) {
  return username || 'Система';
}

const activeTask = computed(() => taskHistory.value.find((task) => task.id === activeTaskId.value) || null);

function isOwnMessage(message) {
  if (!message || message.is_system || !currentProfile.value?.user?.username) {
    return false;
  }
  return message.author_username === currentProfile.value.user.username;
}

function messageRowClass(message) {
  if (message.is_system) {
    return 'message-row message-row-system';
  }
  return isOwnMessage(message) ? 'message-row message-row-outgoing' : 'message-row message-row-incoming';
}

function messageBubbleClass(message) {
  if (message.is_system) {
    return 'message-bubble message-bubble-system';
  }
  return isOwnMessage(message)
    ? 'message-bubble message-bubble-outgoing'
    : 'message-bubble message-bubble-incoming';
}

function messageHeaderClass(message) {
  const base = ['message-header', 'small', 'text-muted', 'd-flex', 'gap-2', 'flex-wrap'];
  if (message.is_system) {
    base.push('justify-content-center', 'text-center');
  } else if (isOwnMessage(message)) {
    base.push('justify-content-end', 'text-end');
  } else {
    base.push('justify-content-between');
  }
  return base.join(' ');
}
function formatChangeValue(value) {
  if (value === null || value === undefined || value === '') {
    return '-';
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

function hasChangeDetails(message) {
  return Boolean((message?.changes?.length || 0) || (message?.attachments?.length || 0));
}

function isMessageExpanded(id) {
  return expandedMessages.value.has(id);
}

function toggleMessageDetails(id) {
  const next = new Set(expandedMessages.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  expandedMessages.value = next;
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
  expandedMessages.value = new Set();
  messageDraft.value = '';
  fillFormFromWork(work);
}

function onFile(event) {
  const file = event.target?.files?.[0] ?? null;
  form.document = file;
}

async function saveCorrections() {
  if (!selectedWork.value) return;
  const message = form.correction_message?.trim();
  if (!message) {
    toast.error('Укажите комментарий для редактора перед отправкой.');
    return;
  }

  saving.value = true;
  try {
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
    payload.message = message;

    await sciencePublishingAPI.submitWorkCorrections(selectedWork.value.id, payload);
    toast.success('Исправления отправлены.');
    form.correction_message = '';
    await loadWorks();
  } catch (error_) {
    toast.error(error_?.message || 'Не удалось сохранить исправления.');
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
    expandedMessages.value = new Set();

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

.conversation-timeline {
  max-height: 420px;
  overflow-y: auto;
}

.timeline-item {
  background: var(--bs-body-bg);
}

.timeline-messages {
  margin-top: 1rem;
}

.timeline-message {
  background: var(--bs-body-bg);
  border: 1px solid var(--bs-border-color);
}

.conversation-messages {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.message-row {
  display: flex;
  margin-bottom: 0.75rem;
}

.message-row:last-child {
  margin-bottom: 0;
}

.message-row-incoming {
  justify-content: flex-start;
}

.message-row-outgoing {
  justify-content: flex-end;
}

.message-row-system {
  justify-content: center;
}

.message-bubble {
  max-width: min(420px, 100%);
  padding: 0.75rem;
  border-radius: 16px;
  background: var(--bs-light-bg-subtle);
  border: 1px solid var(--bs-border-color);
}

.message-bubble-incoming {
  background: var(--bs-body-bg);
}

.message-bubble-outgoing {
  background: var(--bs-primary-bg-subtle);
  border-color: var(--bs-primary-border-subtle);
}

.message-bubble-system {
  background: var(--bs-dark-bg-subtle);
  color: var(--bs-body-bg);
  text-align: center;
}

.message-header {
  align-items: center;
}

.message-author {
  font-weight: 600;
}

.message-body {
  white-space: pre-line;
}

.message-changes .btn-link {
  text-decoration: none;
  font-weight: 600;
}

.message-change-panel {
  background: var(--bs-light-bg-subtle);
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.message-change-entry + .message-change-entry {
  margin-top: 0.5rem;
}

.message-attachments a {
  text-decoration: none;
}

.chat-reply textarea {
  resize: vertical;
}

.timeline-message .badge {
  margin-top: 0.25rem;
}

</style>

