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
                <div class="small text-muted" v-if="w.discipline_topic">{{ w.discipline_topic }}</div>
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
                  <button class="nav-link" :class="{ active: tab === 'chat' }" @click="openChatTab">Чат</button>
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
            <div class="mb-3">
              <ul class="nav nav-pills">
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: chatTab === 'dialog' }" @click="chatTab = 'dialog'">Переписка</button>
                </li>
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: chatTab === 'attachments' }" @click="chatTab = 'attachments'">Вложения</button>
                </li>
              </ul>
            </div>

            <div v-if="chatTab === 'dialog'">
              <div v-if="chatLoading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Загрузка…</span>
                </div>
              </div>
              <div v-else class="draft-chat">
                <div v-if="!messages.length" class="draft-chat__empty text-muted text-center py-5">
                  История переписки пока пуста.
                </div>
                <div v-else class="chat-thread">
                  <article
                    v-for="message in messages"
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
                        <div class="chat-entry__subtitle text-muted">Изменения</div>
                        <ul class="chat-change-list">
                          <li v-for="change in message.changes" :key="change.field || change.name || change.label">
                            <strong>{{ changeLabel(change) }}:</strong>
                            <span class="text-muted ms-1">было {{ formatChangeValue(changeOld(change)) }}</span>
                            <span class="ms-1">стало {{ formatChangeValue(changeNew(change)) }}</span>
                          </li>
                        </ul>
                      </div>

                      <div v-if="messageHasAttachments(message)" class="chat-entry__attachments">
                        <div class="chat-entry__subtitle text-muted">Вложения</div>
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

                <form class="draft-chat__composer" @submit.prevent="sendMessage">
                  <label class="form-label" for="messageDraft">Сообщение</label>
                  <textarea
                    id="messageDraft"
                    v-model="messageDraft"
                    class="form-control"
                    rows="4"
                    placeholder="Напишите ответ редакции"
                    :disabled="sending || chatLoading"
                  ></textarea>
                  <div class="d-flex justify-content-end gap-2 mt-3">
                    <button
                      type="submit"
                      class="btn btn-primary d-inline-flex align-items-center gap-2"
                      :disabled="sending || chatLoading || !messageDraft.trim()"
                    >
                      <span v-if="sending" class="spinner-border spinner-border-sm" role="status" />
                      <Send v-else size="16" />
                      <span v-if="!sending">Отправить</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <div v-else class="attachments-panel">
              <div class="input-group attachments-search mb-3">
                <span class="input-group-text">
                  <Search size="16" />
                </span>
                <input
                  v-model="attachmentsQuery"
                  type="search"
                  class="form-control"
                  placeholder="Поиск по вложениям"
                  disabled
                />
              </div>
              <div class="alert alert-light border mb-0">Вложения ещё не добавлены.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { RefreshCcw, FilePlus, Send, Search } from 'lucide-vue-next';
import { RouterLink } from 'vue-router';

import { sciencePublishingAPI } from '@/modules/science_publishing/client/js/science-publishing.js';
import { useToast } from 'vue-toastification';
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
const chatTab = ref('dialog'); // dialog | attachments
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
const messages = ref([]);
const messageDraft = ref('');
const sending = ref(false);
const currentProfile = ref(null);
const profileLoading = ref(true);
const chatLoadToken = ref(0);
const attachmentsQuery = ref('');

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
const currentUserId = computed(
  () => currentProfile.value?.user?.id || currentProfile.value?.user_id || currentProfile.value?.user || null
);
const normalizeId = (value) => {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number') return String(value);
  const num = Number(value);
  return Number.isNaN(num) ? String(value) : String(num);
};

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

function formatStatus(status) {
  return STATUS_LABELS[status] || status || '-';
}

function messageAlignmentClass(message) {
  if (!message) return 'chat-entry--neutral';
  if (message.is_system) return 'chat-entry--system';
  const userId = normalizeId(currentUserId.value);
  const senderId = normalizeId(
    message.sender_id ??
      message.senderId ??
      message.author_id ??
      message.author_user_id ??
      message.user_id ??
      message.author?.id ??
      message.author_user?.id ??
      message.user?.id ??
      message.author ??
      message.author_user ??
      message.user ??
      message.authorId
  );
  if (userId && senderId && String(senderId) === String(userId)) {
    return 'chat-entry--sender';
  }
  return 'chat-entry--recipient';
}

function messageAuthorName(message) {
  return message?.author_display_name || message?.author_username || message?.author_name || '—';
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

function formatDateTime(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleString('ru-RU');
  } catch {
    return value;
  }
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
  chatTab.value = 'dialog';
  messageDraft.value = '';
  messages.value = [];
  chatLoading.value = false;
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
      await loadChat();
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

async function loadChat() {
  if (!selectedWork.value) return;
  const token = ++chatLoadToken.value;
  chatLoading.value = true;
  // защита от зависания: через 10с снимаем спиннер, если запрос не завершился
  setTimeout(() => {
    if (chatLoadToken.value === token && chatLoading.value) {
      chatLoading.value = false;
      toast.error('Не удалось загрузить переписку. Попробуйте позже.');
    }
  }, 10000);
  try {
    const response = await sciencePublishingAPI.listWorkChatMessages(selectedWork.value.id);
    const data = response?.data ?? response;
    messages.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (error_) {
    toast.error(error_?.message || 'Не удалось загрузить переписку.');
    messages.value = [];
  } finally {
    if (chatLoadToken.value === token) {
      chatLoading.value = false;
    }
  }
}

function openChatTab() {
  tab.value = 'chat';
  chatTab.value = 'dialog';
  // ждем загрузку переписки, чтобы не зависал спиннер
  loadChat().catch(() => {
    chatLoading.value = false;
  });
}

async function sendMessage() {
  if (!selectedWork.value || !messageDraft.value.trim()) return;

  sending.value = true;
  try {
    await sciencePublishingAPI.postWorkChatMessage(selectedWork.value.id, { content: messageDraft.value.trim() });
    messageDraft.value = '';
    await loadChat();
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
.draft-chat {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 32px 80px -48px rgba(15, 23, 42, 0.35);
  max-height: 78vh;
  overflow-y: auto;
}

.draft-chat__empty {
  border: 1px dashed var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.85);
}

.chat-thread {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem 0;
  max-height: 65vh;
  overflow-y: auto;
}

.chat-entry {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(248, 249, 252, 0.9);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: fit-content;
  max-width: 80%;
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

.chat-entry__subtitle {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
}

.chat-change-list,
.chat-attachment-list {
  list-style: none;
  margin: 0;
  padding-left: 0;
  display: grid;
  gap: 0.35rem;
}

.chat-entry__changes,
.chat-entry__attachments {
  padding: 0.75rem 0.9rem;
  border-radius: 0.85rem;
  background: rgba(248, 249, 252, 0.75);
  border: 1px solid rgba(15, 23, 42, 0.08);
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

.draft-chat__composer {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 26px 60px -44px rgba(15, 23, 42, 0.4);
}

.draft-chat__composer textarea {
  resize: vertical;
  min-height: 120px;
}
</style>
