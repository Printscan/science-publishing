<template>
  <div class="drafts container-fluid py-4">
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="row g-3">
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-header d-flex justify-content-between align-items-center drafts-list__header">
            <h6 class="mb-0">Ваши материалы (черновики)</h6>
            <span class="badge rounded-pill text-bg-secondary-subtle text-secondary">{{ works.length }}</span>
          </div>
          <div class="list-group list-group-flush">
            <button
              v-for="w in works"
              :key="w.id"
              class="list-group-item list-group-item-action d-flex justify-content-between align-items-start drafts-list__item"
              :class="{ active: selectedWork && selectedWork.id === w.id }"
              @click="selectWork(w)"
            >
              <div class="me-2">
                <div class="fw-semibold drafts-list__title">{{ w.discipline_name || 'Без названия' }}</div>
                <small class="drafts-list__status">{{ formatStatus(w.status) }}</small>
                <div class="small text-muted" v-if="w.discipline_topic">{{ w.discipline_topic }}</div>
              </div>
              <span class="badge drafts-list__badge-year">{{ w.year || '-' }}</span>
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
              <ul class="nav nav-pills ms-auto">
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: tab === 'chat' }" @click="openChatTab">Чат с издательством</button>
                </li>
                <li class="nav-item">
                  <button class="nav-link" :class="{ active: tab === 'edit' }" @click="tab = 'edit'">Редактирование</button>
                </li>
              </ul>
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
              <div class="draft-panel">
                <div class="draft-panel__tabs">
                  <ul class="nav nav-pills">
                    <li class="nav-item">
                      <button class="nav-link" :class="{ active: chatTab === 'dialog' }" @click="chatTab = 'dialog'">Переписка</button>
                    </li>
                  <li class="nav-item">
                    <button class="nav-link" :class="{ active: chatTab === 'attachments' }" @click="chatTab = 'attachments'">Вложения</button>
                  </li>
                </ul>
              </div>

              <div class="draft-panel__body">
                <div v-if="chatTab === 'dialog'" class="draft-panel__section">
                  <div v-if="chatLoading" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Загрузка…</span>
                    </div>
                  </div>
                  <div v-else class="draft-chat">
                    <div class="chat-floating-date">
                      <transition name="chat-date-fade" mode="out-in">
                        <span
                          v-if="floatingDateLabel"
                          :key="floatingDayKey"
                          class="chat-date__pill chat-date__pill--floating"
                        >
                          {{ floatingDateLabel }}
                        </span>
                      </transition>
                    </div>
                    <div v-if="!messages.length" class="draft-chat__empty text-muted text-center py-5">
                      История переписки пока пуста.
                    </div>
                    <div v-else class="chat-thread" ref="chatThreadRef" @scroll="updateFloatingDate">
                      <template v-for="item in chatItems" :key="item.key">
                        <div
                          v-if="item.type === 'date' && item.dayKey !== firstChatDayKey"
                          class="chat-date"
                          :data-chat-day="item.dayKey"
                        >
                          <span class="chat-date__pill">{{ item.date }}</span>
                        </div>
                        <article
                          v-else-if="item.type === 'message'"
                          :class="['chat-entry', messageAlignmentClass(item.message)]"
                          :data-chat-day="item.dayKey"
                          :data-message-id="item.message.id || item.key"
                        >
                          <div class="chat-entry__heading" v-if="showMessageName(item.message)">
                            <button
                              type="button"
                              class="chat-entry__name"
                              @click.stop="openProfilePreview(item.message)"
                              :aria-label="`Открыть профиль ${messageAuthorName(item.message)}`"
                            >
                              {{ messageAuthorName(item.message) }}
                            </button>
                          </div>
                          <div class="chat-entry__body">
                            <div class="chat-entry__row" v-if="item.message.content">
                              <p class="chat-entry__text">{{ item.message.content }}</p>
                              <span class="chat-entry__time-inline">
                                {{ formatTime(item.message.created_at) }}
                                <span
                                  v-if="isOwnMessage(item.message)"
                                  class="chat-entry__status"
                                  :class="statusClass(item.message)"
                                  aria-label="Статус доставки"
                                >
                                  <span
                                    v-if="item.message.pending_status === 'pending'"
                                    class="spinner-border spinner-border-sm"
                                    role="status"
                                    aria-hidden="true"
                                  ></span>
                                  <button
                                    v-else-if="item.message.pending_status === 'failed'"
                                    type="button"
                                    class="btn btn-link btn-status-failed p-0"
                                    @click.stop="handleFailedMessage(item.message)"
                                    title="Сообщение не отправлено. Нажмите, чтобы повторить или удалить."
                                  >
                                    ✕
                                  </button>
                                  <span v-else>{{ statusSymbol(item.message) }}</span>
                                </span>
                              </span>
                            </div>

                            <div v-if="messageHasChanges(item.message)" class="chat-entry__changes">
                              <div class="chat-entry__subtitle text-muted">Изменения</div>
                              <ul class="chat-change-list">
                                <li v-for="change in item.message.changes" :key="change.field || change.name || change.label">
                                  <strong>{{ changeLabel(change) }}:</strong>
                                  <span class="text-muted ms-1">было {{ formatChangeValue(changeOld(change)) }}</span>
                                  <span class="ms-1">стало {{ formatChangeValue(changeNew(change)) }}</span>
                                </li>
                              </ul>
                            </div>

                            <div v-if="messageHasAttachments(item.message)" class="chat-entry__attachments">
                              <div class="chat-entry__subtitle text-muted">Вложения</div>
                              <ul class="chat-attachment-list">
                                <li
                                  v-for="attachment in item.message.attachments"
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
                            <div class="chat-entry__footer" v-if="!item.message.content">
                              <span class="chat-entry__time text-muted">
                                {{ formatTime(item.message.created_at) }}
                                <span
                                  v-if="isOwnMessage(item.message)"
                                  class="chat-entry__status"
                                  :class="statusClass(item.message)"
                                  aria-label="Статус доставки"
                                >
                                  {{ statusSymbol(item.message) }}
                                </span>
                              </span>
                            </div>
                          </div>
                        </article>
                      </template>
                    </div>
                  </div>

                  <form class="draft-chat__composer" @submit.prevent="sendMessage">
                    <div class="d-flex flex-column gap-2">
                      <div class="d-flex flex-column flex-md-row gap-2 align-items-stretch">
                        <textarea
                          id="messageDraft"
                          v-model="messageDraft"
                          class="form-control compose-input"
                          rows="2"
                          placeholder="Сообщение..."
                          :disabled="sending || chatLoading"
                        ></textarea>
                        <button
                          type="submit"
                          class="btn btn-primary compose-send d-inline-flex align-items-center gap-2"
                          :disabled="sending || chatLoading || !messageDraft.trim()"
                        >
                          <span v-if="sending" class="spinner-border spinner-border-sm" role="status" />
                          <Send v-else size="16" />
                          <span v-if="!sending">Отправить</span>
                        </button>
                      </div>
                    </div>
                  </form>
                </div>

                <div v-else class="attachments-panel draft-panel__section">
                  <div class="input-group attachments-search mb-3">
                    <span class="input-group-text">
                      <Search size="16" />
                    </span>
                    <input
                      v-model="attachmentsQuery"
                      type="search"
                      class="form-control"
                      placeholder="Поиск по вложениям"
                    />
                  </div>
                  <div v-if="attachments.length" class="attachment-list">
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
                        <span v-if="item.author">{{ item.author }}</span>
                        <span v-if="item.author && item.displayDate" class="attachment-card__dot" aria-hidden="true">•</span>
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
                    Вложения ещё не добавлены.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  <Teleport to="body">
    <div
      v-if="profilePreview.open"
      class="profile-preview-overlay"
      @click.self="closeProfilePreview"
    >
      <div class="profile-preview card shadow-lg">
        <div class="profile-preview__header">
          <div>
            <div class="profile-preview__title">
              {{ profilePreviewTitle }}
            </div>
          </div>
          <button type="button" class="btn-close" aria-label="Закрыть" @click="closeProfilePreview"></button>
        </div>

        <div v-if="profilePreview.loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка профиля...</span>
          </div>
        </div>

        <div v-else-if="profilePreview.error" class="alert alert-danger mb-0">
          {{ profilePreview.error }}
        </div>

                  <div v-else-if="profilePreview.profile" class="profile-preview__body">
            <div class="profile-preview__section">
              <div class="profile-preview__pair">
                <span class="profile-preview__label">Имя</span>
                <span class="profile-preview__value">{{ profilePreview.profile.display_name || '—' }}</span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.phone">
                <span class="profile-preview__label">Телефон</span>
                <span class="profile-preview__value">{{ profilePreview.profile.phone }}</span>
              </div>
            </div>

            <div class="profile-preview__section" v-if="profilePreview.profile.organization || profilePreview.profile.department || profilePreview.profile.position">
              <div class="profile-preview__pair" v-if="profilePreview.profile.organization">
                <span class="profile-preview__label">Организация</span>
                <span class="profile-preview__value">{{ profilePreview.profile.organization }}</span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.department">
                <span class="profile-preview__label">Подразделение</span>
                <span class="profile-preview__value">{{ profilePreview.profile.department }}</span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.position">
                <span class="profile-preview__label">Должность</span>
                <span class="profile-preview__value">{{ profilePreview.profile.position }}</span>
              </div>
            </div>

            <div class="profile-preview__section" v-if="profilePreview.profile.academic_degree || profilePreview.profile.academic_title">
              <div class="profile-preview__pair" v-if="profilePreview.profile.academic_degree">
                <span class="profile-preview__label">Учёная степень</span>
                <span class="profile-preview__value">{{ profilePreview.profile.academic_degree }}</span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.academic_title">
                <span class="profile-preview__label">Учёное звание</span>
                <span class="profile-preview__value">{{ profilePreview.profile.academic_title }}</span>
              </div>
            </div>

            <div class="profile-preview__section" v-if="profilePreview.profile.orcid || profilePreview.profile.scopus_id || profilePreview.profile.elibrary_id">
              <div class="profile-preview__pair" v-if="profilePreview.profile.orcid">
                <span class="profile-preview__label">ORCID</span>
                <span class="profile-preview__value">{{ profilePreview.profile.orcid }}</span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.scopus_id">
                <span class="profile-preview__label">Scopus Author ID</span>
                <span class="profile-preview__value">{{ profilePreview.profile.scopus_id }}</span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.elibrary_id">
                <span class="profile-preview__label">Elibrary ID</span>
                <span class="profile-preview__value">{{ profilePreview.profile.elibrary_id }}</span>
              </div>
            </div>

            <div class="profile-preview__section" v-if="profilePreview.profile.website || profilePreview.profile.bio">
              <div class="profile-preview__pair" v-if="profilePreview.profile.website">
                <span class="profile-preview__label">Сайт</span>
                <span class="profile-preview__value">
                  <a :href="profilePreview.profile.website" target="_blank" rel="noopener">{{ profilePreview.profile.website }}</a>
                </span>
              </div>
              <div class="profile-preview__pair" v-if="profilePreview.profile.bio">
                <span class="profile-preview__label">О себе</span>
                <span class="profile-preview__value">{{ profilePreview.profile.bio }}</span>
              </div>
            </div>

            <div class="profile-preview__section" v-if="(profilePreview.profile.roles || []).length">
              <div class="profile-preview__label">Назначенные роли</div>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="role in profilePreview.profile.roles"
                  :key="role.id || role.code || role.name"
                  class="badge rounded-pill text-bg-light text-muted"
                >
                  {{ role.name || role.code }}
                </span>
              </div>
            </div>
          </div>

          <div v-else class="text-muted small py-3">
            Профиль не найден.
        </div>
      </div>
    </div>
  </Teleport>
</div>
</template>
<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch, nextTick } from 'vue';
import { RefreshCcw, FilePlus, Send, Search } from 'lucide-vue-next';
import { RouterLink } from 'vue-router';

import { sciencePublishingAPI } from '@/modules/science_publishing/client/js/science-publishing.js';
import { createChatSocket } from '@/modules/science_publishing/client/js/chat-socket.js';
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
const tab = ref('chat');
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
const attachments = computed(() => {
  const list = [];
  const msgs = Array.isArray(messages.value) ? messages.value : [];
  msgs.forEach((message, messageIndex) => {
    if (!Array.isArray(message.attachments)) return;
    message.attachments.forEach((attachment, attachmentIndex) => {
      const url = attachment.absolute_url || attachment.url || attachment.file || null;
      const name =
        attachment.name ||
        attachment.filename ||
        attachment.original_name ||
        attachment.label ||
        extractFileName(url) ||
        'Файл';
      const author = messageAuthorName(message);
      const createdAt = message.created_at || message.date || null;
      const displayDate = formatDateTime(createdAt);
      const statusDisplay = formatStatus(selectedWork.value?.status);
      const context = message.content || '';
      const keywords = [name, author, displayDate, statusDisplay, context]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      list.push({
        key: ['att', message.id || messageIndex, attachmentIndex].join('-'),
        name,
        url,
        author,
        displayDate,
        statusDisplay,
        context,
        originLabel: 'Комментарий',
        keywords,
      });
    });
  });
  return list;
});
const filteredAttachments = computed(() => {
  const query = (attachmentsQuery.value || '').toString().toLowerCase().trim();
  if (!query) return attachments.value;
  return attachments.value.filter((item) => item.keywords.includes(query));
});
const profilePreview = reactive({
  open: false,
  loading: false,
  error: '',
  profile: null,
  username: '',
});
const profilePreviewTitle = computed(() => {
  const raw = profilePreview.profile?.display_name || profilePreview.username || 'Профиль пользователя';
  if (raw && /^\d+$/.test(String(raw).trim())) {
    return 'Профиль пользователя';
  }
  return raw || 'Профиль пользователя';
});
const CHAT_REFRESH_INTERVAL = 10000;
const floatingDayKey = ref('');
const floatingDateLabel = computed(() => (floatingDayKey.value ? formatDateLabel(floatingDayKey.value) || '' : ''));
const firstChatDayKey = computed(() => chatItems.value.find((item) => item.type === 'date')?.dayKey || '');
const profileCache = reactive({});
let chatSocket = null;
let chatRefreshTimer = null;
let chatBackgroundLoading = false;

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

watch(
  () => tab.value,
  (value) => {
    if (value !== 'chat') {
      stopChatAutoRefresh();
    } else {
      markMessagesReadSoon();
    }
  }
);

watch(
  () => messages.value.length,
  () => {
    markMessagesReadSoon();
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

function isOwnMessage(message) {
  if (!message) return false;
  if (message.is_system) return false;
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
  return Boolean(userId && senderId && String(senderId) === String(userId));
}

function showMessageName(message) {
  return !isOwnMessage(message);
}

function extractProfileId(message) {
  return (
    message?.author_profile_id ||
    message?.author_profile ||
    message?.authorProfile ||
    null
  );
}

async function openProfilePreview(message) {
  if (!message || message.is_system) return;
  const profileId = extractProfileId(message);
  const username = message?.author_username || messageAuthorName(message);
  profilePreview.open = true;
  profilePreview.loading = true;
  profilePreview.error = '';
  profilePreview.profile = null;
  profilePreview.username = username || '';
  try {
    let data = null;
    if (profileId && profileCache[profileId]?.fullProfile) {
      data = profileCache[profileId];
    } else if (profileId) {
      const response = await sciencePublishingAPI.getProfile(profileId);
      data = response?.data ?? response;
      if (data?.id) {
        profileCache[profileId] = {
          ...data,
          userId: data.user,
          displayName: data.display_name || username || '',
          fullProfile: true,
        };
      }
    }

    if (!data && username) {
      const response = await sciencePublishingAPI.listProfiles({ search: username, page_size: 5 });
      const list = response?.data ?? response;
      const profiles = Array.isArray(list) ? list : list?.results ?? [];
      data = profiles.find((item) => (item.user === username) || (item.user?.username === username)) || profiles[0];
      if (data?.id) {
        profileCache[data.id] = {
          ...data,
          userId: data.user,
          displayName: data.display_name || username || '',
          fullProfile: true,
        };
      }
    }

    if (!data) {
      throw new Error('Профиль не найден.');
    }

    profilePreview.profile = data;
  } catch (error_) {
    profilePreview.error = error_?.message || 'Не удалось загрузить профиль.';
  } finally {
    profilePreview.loading = false;
  }
}

function closeProfilePreview() {
  profilePreview.open = false;
  profilePreview.loading = false;
  profilePreview.error = '';
  profilePreview.profile = null;
}

function messageHasChanges(message) {
  return Array.isArray(message?.changes) && message.changes.length > 0;
}

function messageHasAttachments(message) {
  return Array.isArray(message?.attachments) && message.attachments.length > 0;
}

const chatItems = computed(() => {
  const list = Array.isArray(messages.value) ? messages.value : [];
  const result = [];
  let lastDay = null;
  list.forEach((message, idx) => {
    const dayKey = formatDayKey(message.created_at);
    const label = formatDateLabel(dayKey);
    if (label && dayKey !== lastDay) {
      result.push({
        type: 'date',
        dayKey,
        date: label,
        key: `date-${dayKey}-${idx}`,
      });
      lastDay = dayKey;
    }
    result.push({
      type: 'message',
      message,
      dayKey,
      key: message.id || message.created_at || `msg-${idx}`,
    });
  });
  return result;
});

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

function pendingStoreKey(workId) {
  const userId = normalizeId(currentUserId.value) || 'anon';
  return `${PENDING_STORE_PREFIX}_${workId}_${userId}`;
}

function savePendingMessages(workId) {
  if (!workId) return;
  const pending = (Array.isArray(messages.value) ? messages.value : []).filter((m) => m.pending_status);
  try {
    localStorage.setItem(pendingStoreKey(workId), JSON.stringify(pending));
  } catch (e) {
    console.warn('Cannot save pending messages', e);
  }
}

function loadPendingMessages(workId) {
  if (!workId) return [];
  try {
    const raw = localStorage.getItem(pendingStoreKey(workId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    const now = Date.now();
    return Array.isArray(parsed)
      ? parsed
          .filter((m) => m && m.pending_status)
          .map((m) => {
            const created = new Date(m.created_at || 0).getTime();
            if (Number.isFinite(created) && now - created > PENDING_STALE_MS) {
              return { ...m, pending_status: 'failed' };
            }
            return m;
          })
      : [];
  } catch {
    return [];
  }
}

function removePendingMessage(workId, tempId) {
  if (!workId) return;
  messages.value = (Array.isArray(messages.value) ? messages.value : []).filter(
    (m) => String(m.id) !== String(tempId)
  );
  savePendingMessages(workId);
}

  function replacePendingWithServer(workId, tempId, serverMessage) {
    if (!workId || !tempId || !serverMessage) return;
    const list = Array.isArray(messages.value) ? [...messages.value] : [];
    const idx = list.findIndex((m) => String(m.id) === String(tempId));
    if (idx !== -1) {
    list[idx] = { ...serverMessage, pending_status: null };
    messages.value = list.sort((a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0));
    if (pendingSendTimers[tempId]) {
      clearTimeout(pendingSendTimers[tempId]);
      delete pendingSendTimers[tempId];
    }
      savePendingMessages(workId);
    }
  }

  function startPendingFailTimer(workId, tempId) {
    if (!tempId) return;
    if (pendingSendTimers[tempId]) {
      clearTimeout(pendingSendTimers[tempId]);
    }
    pendingSendTimers[tempId] = setTimeout(() => {
      markPendingFailed(workId, tempId);
      delete pendingSendTimers[tempId];
    }, PENDING_FAIL_AFTER_MS);
  }

  function markPendingFailed(workId, tempId) {
    messages.value = (Array.isArray(messages.value) ? messages.value : []).map((m) => {
      if (String(m.id) === String(tempId)) {
        return { ...m, pending_status: 'failed' };
      }
      return m;
    });
    if (pendingSendTimers[tempId]) {
      clearTimeout(pendingSendTimers[tempId]);
      delete pendingSendTimers[tempId];
    }
    savePendingMessages(workId);
  }

  function createPendingMessage(content) {
    const tempId = `temp-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const now = new Date().toISOString();
  return {
    id: tempId,
    metadata: { temp_id: tempId },
    pending_status: 'pending',
    delivery_status: 'pending',
    is_system: false,
    content,
    created_at: now,
    author_username: currentUsername.value || 'Вы',
    author_display_name: currentUsername.value || 'Вы',
    author_profile_id: currentProfile.value?.id || null,
    author: currentUserId.value,
  };
}

  async function sendPendingMessage(workId, pendingMessage) {
    if (!workId || !pendingMessage) return;
    startPendingFailTimer(workId, pendingMessage.id);
    const payload = {
      content: pendingMessage.content,
      metadata: { ...(pendingMessage.metadata || {}), temp_id: pendingMessage.id },
    };
  try {
    const response = await sciencePublishingAPI.postWorkChatMessage(workId, payload);
    const data = response?.data ?? response;
    if (data?.id) {
      replacePendingWithServer(workId, pendingMessage.id, data);
      return;
    }
    // если нет id, считаем отправленным
    replacePendingWithServer(workId, pendingMessage.id, { ...pendingMessage, pending_status: null, delivery_status: 'sent' });
  } catch (error_) {
    console.warn('Send message failed', error_);
    markPendingFailed(workId, pendingMessage.id);
  }
}

function handleFailedMessage(message) {
  if (!message) return;
  const retry = window.confirm('Повторить отправку сообщения? Нажмите "Отмена", чтобы удалить.');
  if (retry) {
    const patched = { ...message, pending_status: 'pending' };
    messages.value = (Array.isArray(messages.value) ? messages.value : []).map((m) =>
      String(m.id) === String(message.id) ? patched : m
    );
    savePendingMessages(selectedWork.value?.id);
    sendPendingMessage(selectedWork.value?.id, patched);
  } else {
    removePendingMessage(selectedWork.value?.id, message.id);
  }
}

function collectUnreadMessageIds() {
  const userId = normalizeId(currentUserId.value);
  return (Array.isArray(messages.value) ? messages.value : [])
    .filter((m) => !m.is_system && !isOwnMessage(m) && !m.is_read && !m.pending_status)
    .map((m) => String(m.id));
}

let markReadTimer = null;
let markReadUpToTimer = null;
const PENDING_STORE_PREFIX = 'sp_pending_messages';
const PENDING_FAIL_AFTER_MS = 30000;
const PENDING_STALE_MS = 5 * 60 * 1000;
const SERVER_DUPLICATE_WINDOW_MS = 1500;

function messageKey(message) {
  if (!message) return '';
  if (message.metadata?.temp_id) return `temp:${message.metadata.temp_id}`;
  if (message.id) return String(message.id);
  const author = normalizeId(message.author) || normalizeId(message.author_user_id) || 'unknown';
  const content = String(message.content || '').trim();
  return `content:${author}:${content}`;
}

function upsertMessages(existing, incomingList) {
  const map = new Map();
  const all = [...existing, ...incomingList];
  for (const msg of all) {
    const key = messageKey(msg);
    if (!key) continue;
    const prev = map.get(key);
    if (!prev) {
      map.set(key, msg);
      continue;
    }
    // серверное сообщение сильнее pending
    if (prev.pending_status && !msg.pending_status) {
      map.set(key, msg);
      continue;
    }
    if (!prev.pending_status && msg.pending_status) {
      // уже есть нормальное сообщение — игнорируем pending
      continue;
    }
    // если оба нормальные — оставляем более позднее
    const prevDate = new Date(prev.created_at || 0).getTime();
    const msgDate = new Date(msg.created_at || 0).getTime();
    if (msgDate >= prevDate) {
      map.set(key, msg);
    }
  }
  return Array.from(map.values()).sort((a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0));
}

function markMessagesReadSoon() {
  if (tab.value !== 'chat' || !selectedWork.value) return;
  const ids = collectUnreadMessageIds();
  if (!ids.length) return;
  if (markReadTimer) {
    clearTimeout(markReadTimer);
  }
  markReadTimer = setTimeout(async () => {
    try {
      await sciencePublishingAPI.markChatMessagesRead(selectedWork.value.id, ids);
      messages.value = (Array.isArray(messages.value) ? messages.value : []).map((m) => {
        if (ids.includes(String(m.id))) {
          return {
            ...m,
            is_read: true,
            delivery_status: 'read',
            read_at: m.read_at || new Date().toISOString(),
            read_by: Array.isArray(m.read_by)
              ? [...m.read_by, { user_id: currentUserId.value, username: currentUsername.value, read_at: new Date().toISOString() }]
              : [{ user_id: currentUserId.value, username: currentUsername.value, read_at: new Date().toISOString() }],
          };
        }
        return m;
      });
    } catch (error_) {
      console.warn('mark read failed', error_);
    } finally {
      markReadTimer = null;
    }
  }, 250);
}

function findLastVisibleMessageId() {
  const container = chatThreadRef.value;
  if (!container) return null;
  const entries = Array.from(container.querySelectorAll('.chat-entry[data-message-id]'));
  const viewportTop = container.scrollTop;
  const viewportBottom = viewportTop + container.clientHeight;
  let lastVisibleId = null;
  for (const el of entries) {
    const top = el.offsetTop;
    const bottom = top + el.offsetHeight;
    if (bottom >= viewportTop && top <= viewportBottom) {
      const msgId = el.getAttribute('data-message-id');
      const message = (Array.isArray(messages.value) ? messages.value : []).find(
        (m) => String(m.id) === String(msgId)
      );
      if (message && !message.pending_status && !isOwnMessage(message)) {
        lastVisibleId = msgId;
      }
    }
  }
  return lastVisibleId;
}

function markVisibleMessagesReadUpToSoon() {
  if (tab.value !== 'chat' || !selectedWork.value) return;
  const lastId = findLastVisibleMessageId();
  if (!lastId) return;
  if (markReadUpToTimer) {
    clearTimeout(markReadUpToTimer);
  }
  markReadUpToTimer = setTimeout(async () => {
    try {
      await sciencePublishingAPI.markChatMessagesReadUpTo(selectedWork.value.id, lastId);
    } catch (error_) {
      console.warn('mark read up to failed', error_);
    } finally {
      markReadUpToTimer = null;
    }
  }, 200);
}

function applyReceiptUpdate(payload) {
  const ids = (payload?.message_ids || (payload?.id ? [payload.id] : [])).map((x) => String(x));
  if (!ids.length) return;
  const readerId = payload.reader_id || payload.recipient_id || null;
  const readerUsername = payload.reader_username || payload.username || '';
  const readAt = payload.read_at || new Date().toISOString();
  messages.value = (Array.isArray(messages.value) ? messages.value : []).map((m) => {
    if (ids.includes(String(m.id))) {
      const readBy = Array.isArray(m.read_by) ? [...m.read_by] : [];
      if (readerId) {
        const exists = readBy.some((r) => String(r.user_id) === String(readerId));
        if (!exists) {
          readBy.push({ user_id: readerId, username: readerUsername, read_at: readAt });
        }
      }
      const isForeignReader =
        readerId &&
        String(readerId) !== String(m.author) &&
        String(readerId) !== String(m.author_user_id);
      return {
        ...m,
        delivery_status: isForeignReader ? 'read' : m.delivery_status,
        is_read: m.is_read || Boolean(isForeignReader),
        read_by: readBy,
        read_at: m.read_at || (isForeignReader ? readAt : m.read_at),
      };
    }
    return m;
  });
}

const chatThreadRef = ref(null);
const chatInitialScrollDone = ref(false);
const pendingSendTimers = {};

function resetChatScrollState() {
  chatInitialScrollDone.value = false;
}

function scrollChatToBottomOnce(force = false) {
  if (chatInitialScrollDone.value && !force) return;
  const el = chatThreadRef.value;
  if (!el) return;
  const doScroll = () => {
    const target = chatThreadRef.value;
    if (!target) return;
    target.scrollTop = target.scrollHeight;
    chatInitialScrollDone.value = true;
    markVisibleMessagesReadUpToSoon();
  };
  doScroll();
  requestAnimationFrame(doScroll);
  setTimeout(doScroll, 50);
}

function updateFloatingDate() {
  const container = chatThreadRef.value;
  if (!container) return;
  const items = Array.from(container.querySelectorAll('.chat-entry'));
  const viewportTop = container.scrollTop + 8;
  const threshold = viewportTop + container.clientHeight * 0.2; // переключаем дату раньше, когда новая дата близко к верху
  let lastPassedDay = '';
  let firstVisibleDay = '';
  for (const el of items) {
    const day = el.getAttribute('data-chat-day') || '';
    const top = el.offsetTop;
    const bottom = top + el.offsetHeight;
    if (bottom < threshold) {
      lastPassedDay = day;
    } else if (!firstVisibleDay) {
      firstVisibleDay = day;
    }
  }
  floatingDayKey.value = firstVisibleDay || lastPassedDay || '';
  markVisibleMessagesReadUpToSoon();
}

function syncFloatingDateSoon() {
  nextTick(updateFloatingDate);
}

function formatTime(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return value;
  }
}

function formatDateLabel(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'long',
    });
  } catch {
    return '';
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

function formatDayKey(value) {
  if (!value) return '';
  try {
    return new Date(value).toISOString().slice(0, 10);
  } catch {
    return '';
  }
}

function statusSymbol(message) {
  if (message?.pending_status === 'failed') return '✕';
  if (message?.pending_status === 'pending') return '';
  const status = message?.delivery_status || (message?.is_read ? 'read' : null);
  if (status === 'read') return '✓✓';
  if (status === 'sent' || status === 'pending') return '✓';
  return '';
}

function statusClass(message) {
  if (message?.pending_status === 'failed') return 'chat-status chat-status--failed';
  if (message?.pending_status === 'pending') return 'chat-status chat-status--pending';
  const status = message?.delivery_status || (message?.is_read ? 'read' : null);
  if (status === 'read') return 'chat-status chat-status--read';
  if (status === 'sent' || status === 'pending') return 'chat-status chat-status--sent';
  return 'chat-status';
}

function extractFileName(url) {
  if (!url) return '';
  try {
    const decoded = decodeURIComponent(url.toString());
    const parts = decoded.split(/[\\/]/).filter(Boolean);
    return parts[parts.length - 1] || '';
  } catch {
    return '';
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
  stopChatAutoRefresh();
  closeChatSocket();
  selectedWork.value = work;
  tab.value = 'edit';
  chatTab.value = 'dialog';
  messageDraft.value = '';
  messages.value = [];
  chatLoading.value = false;
  resetChatScrollState();
  fillFormFromWork(work);
  // подмешиваем сохранённые неотправленные сообщения
  const pending = loadPendingMessages(work?.id);
  if (pending?.length) {
    messages.value = pending;
  }
}

function onFile(event) {
  const file = event.target?.files?.[0] ?? null;
  form.document = file;
}

function closeChatSocket() {
  if (chatSocket) {
    chatSocket.close();
    chatSocket = null;
  }
}

function connectChatSocket(workId) {
  closeChatSocket();
  if (!workId) return;
  chatSocket = createChatSocket(workId, {
    onMessage: (data) => {
        if (data?.event === 'receipt') {
          applyReceiptUpdate(data);
          return;
        }
        if (!data || (data.work && String(data.work) !== String(workId))) return;
        messages.value = upsertMessages(messages.value, [data]);
        if (data?.metadata?.temp_id && pendingSendTimers[data.metadata.temp_id]) {
          clearTimeout(pendingSendTimers[data.metadata.temp_id]);
          delete pendingSendTimers[data.metadata.temp_id];
          savePendingMessages(workId);
        }
        syncFloatingDateSoon();
        if (!isOwnMessage(data) && tab.value === 'chat') {
          markMessagesReadSoon();
        }
      },
    onError: () => {
      // best-effort, ошибки игнорируем
    },
  });
}

function startChatAutoRefresh() {
  stopChatAutoRefresh();
  if (!selectedWork.value) return;
  loadChat({ background: true }).catch(() => {});
  chatRefreshTimer = setInterval(() => {
    loadChat({ background: true }).catch(() => {});
  }, CHAT_REFRESH_INTERVAL);
}

function stopChatAutoRefresh() {
  if (chatRefreshTimer) {
    clearInterval(chatRefreshTimer);
    chatRefreshTimer = null;
  }
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

async function loadChat(options = {}) {
  if (!selectedWork.value) return;
  const { background = false } = options;
  const workId = selectedWork.value.id;
  let token = null;
  let failTimer = null;
  if (background) {
    if (chatBackgroundLoading) return;
    chatBackgroundLoading = true;
  } else {
    resetChatScrollState();
    token = ++chatLoadToken.value;
    chatLoading.value = true;
    // защита от зависания: через 10с снимаем спиннер, если запрос не завершился
    failTimer = setTimeout(() => {
      if (chatLoadToken.value === token && chatLoading.value) {
        chatLoading.value = false;
        toast.error('Не удалось загрузить переписку. Попробуйте позже.');
      }
    }, 10000);
  }
  try {
    const response = await sciencePublishingAPI.listWorkChatMessages(workId);
    const data = response?.data ?? response;
    const baseMessages = Array.isArray(data) ? data : data?.results ?? [];
    const pending = loadPendingMessages(workId);
    messages.value = upsertMessages(baseMessages, pending);
    const socketState = chatSocket?.raw?.()?.readyState;
    if (!chatSocket || socketState === WebSocket.CLOSED || socketState === WebSocket.CLOSING) {
      connectChatSocket(workId);
    }
    if (!background) {
      await nextTick();
      scrollChatToBottomOnce(true);
    }
    syncFloatingDateSoon();
    markMessagesReadSoon();
  } catch (error_) {
    if (!background) {
      toast.error(error_?.message || 'Не удалось загрузить переписку.');
      messages.value = [];
    }
  } finally {
    if (failTimer) {
      clearTimeout(failTimer);
    }
    if (background) {
      chatBackgroundLoading = false;
    } else if (chatLoadToken.value === token) {
      chatLoading.value = false;
    }
  }
}

async function openChatTab() {
  tab.value = 'chat';
  chatTab.value = 'dialog';
  stopChatAutoRefresh();
  try {
    await loadChat();
  } catch (error_) {
    // Ошибку уже обработали внутри loadChat
  } finally {
    startChatAutoRefresh();
    syncFloatingDateSoon();
  }
}

async function sendMessage() {
  if (!selectedWork.value || !messageDraft.value.trim()) return;
  sending.value = true;
  try {
    const pending = createPendingMessage(messageDraft.value.trim());
    messages.value = [...(Array.isArray(messages.value) ? messages.value : []), pending];
    savePendingMessages(selectedWork.value.id);
    scrollChatToBottomOnce(true);
    sendPendingMessage(selectedWork.value.id, pending);
    messageDraft.value = '';
  } catch (error_) {
    toast.error(error_?.message || 'Не удалось обновить сообщения.');
  } finally {
    sending.value = false;
  }
}

onMounted(async () => {
  await fetchCurrentProfile();
  await loadWorks();
});

onUnmounted(() => {
  closeChatSocket();
  stopChatAutoRefresh();
});
</script>

<style scoped>
.page-title {
  font-weight: 600;
}

.drafts-list__header {
  background: linear-gradient(120deg, rgba(233, 236, 239, 0.9), rgba(222, 226, 230, 0.6));
  border-bottom: 1px solid var(--bs-border-color-translucent);
}

.drafts-list__item {
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease, background 0.12s ease;
  border-left: 4px solid transparent;
}

.drafts-list__item.active {
  background: #ffe0e0;
  border-color: #e03131;
  box-shadow: 0 10px 28px -18px rgba(224, 49, 49, 0.55);
}

.drafts-list__item:hover {
  border-color: #e03131;
  transform: translateX(2px);
  box-shadow: 0 8px 20px -18px rgba(15, 23, 42, 0.35);
}

.drafts-list__title {
  color: #d00000;
}

.drafts-list__status {
  color: #8a0000 !important;
  font-weight: 600;
}

.drafts-list__badge-year {
  background: #fff;
  border: 1px solid #e03131;
  color: #e03131;
  padding: 0.2rem 0.5rem;
}

.list-group-item.active {
  background: var(--bs-primary-bg-subtle);
  color: var(--bs-primary);
  border-color: var(--bs-primary);
}
.draft-chat {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  border: 0;
  padding: 0.8rem;
  background: transparent;
  box-shadow: none;
  max-height: 72vh;
  overflow-y: auto;
  margin-bottom: 0;
}

.draft-chat__empty {
  border: 1px dashed var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.85);
}

.chat-thread {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.2rem 0;
  max-height: 60vh;
  overflow-y: auto;
}

.chat-entry {
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 0.9rem;
  padding: 0.55rem 0.65rem 0.45rem 0.65rem;
  background: rgba(248, 249, 252, 0.92);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: fit-content;
  max-width: 72%;
}

.chat-entry__heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.chat-entry__name {
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  font-weight: 700;
  color: var(--bs-primary);
  cursor: pointer;
  text-align: left;
  font-size: 0.92rem;
}

.chat-entry__name:hover,
.chat-entry__name:focus {
  text-decoration: underline;
  outline: none;
}

.chat-entry__time {
  font-size: 0.75rem;
  color: rgba(15, 23, 42, 0.6);
}

.chat-entry__status {
  display: inline-block;
  margin-left: 4px;
  font-size: 0.75rem;
  line-height: 1;
}

.chat-status--sent {
  color: #6c757d;
}

.chat-status--read {
  color: #0d6efd;
}

.chat-status--pending {
  color: #6c757d;
}

.chat-status--failed {
  color: #dc3545;
}

.btn-status-failed {
  color: #dc3545;
  font-weight: 700;
  text-decoration: none;
}

.btn-status-failed:hover,
.btn-status-failed:focus {
  color: #c82333;
  text-decoration: underline;
}

.chat-entry__footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.1rem;
}

.chat-entry__body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.9rem;
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
  padding: 0.5rem 0.65rem;
  border-radius: 0.65rem;
  background: rgba(248, 249, 252, 0.8);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.chat-entry__row {
  display: flex;
  gap: 0.35rem;
  align-items: flex-end;
}

.chat-entry__text {
  margin: 0;
  flex: 1;
  line-height: 1.25;
}

.chat-entry__time-inline {
  white-space: nowrap;
  align-self: flex-end;
  font-size: 0.78rem;
  color: rgba(15, 23, 42, 0.6);
  margin-left: 0.4rem;
}

.chat-entry--sender {
  align-self: flex-end;
  margin-left: auto;
  border-color: rgba(13, 110, 253, 0.2);
  background: rgba(13, 110, 253, 0.08);
  color: rgba(15, 23, 42, 0.9);
}

.chat-entry--recipient,
.chat-entry--summary {
  align-self: flex-start;
  margin-right: auto;
  border-color: rgba(25, 135, 84, 0.2);
  background: rgba(25, 135, 84, 0.08);
  color: rgba(15, 23, 42, 0.9);
}

.chat-entry--system {
  border-style: dashed;
  color: rgba(15, 23, 42, 0.65);
  background: rgba(108, 117, 125, 0.1);
}

.draft-chat__composer {
  border: 0;
  border-top: 1px solid var(--bs-border-color-translucent);
  border-radius: 0;
  padding: 0.45rem 0.55rem;
  background: transparent;
  box-shadow: none;
  margin-top: 0;
}

.draft-chat__composer textarea {
  resize: vertical;
  min-height: 48px;
  max-height: 120px;
  overflow-y: auto;
  display: block;
  width: 100%;
}

.draft-panel {
  background: transparent;
  border: 0;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.draft-panel__tabs {
  padding: 0 0.75rem 0.2rem;
  background: transparent;
  display: flex;
  align-items: center;
}

.draft-panel__tabs .nav {
  margin: 0;
  width: 100%;
}

.draft-panel__tabs .nav-pills {
  gap: 0.5rem;
}

.draft-panel__tabs .nav-link {
  border: 1px solid transparent;
  border-radius: 0.9rem 0.9rem 0 0;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
}

.draft-panel__tabs .nav-link.active {
  border-color: var(--bs-border-color-translucent);
  border-bottom: 0;
  background: #e03131;
  color: #fff;
  position: relative;
  bottom: -1px;
  box-shadow: 0 8px 24px -16px rgba(224, 49, 49, 0.4);
}

.drafts .card-header .nav-pills {
  gap: 0.5rem;
}

.drafts .card-header .nav-link {
  border: 1px solid transparent;
  border-radius: 0.9rem;
  padding: 0.55rem 1.25rem;
  font-weight: 600;
  color: #c00000;
  background: transparent;
  transition: color 0.2s ease, border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}

.drafts .card-header .nav-link:hover {
  border-color: rgba(224, 49, 49, 0.35);
  color: #a40000;
  background: rgba(224, 49, 49, 0.08);
}

.drafts .card-header .nav-link.active {
  background: #e03131;
  color: #fff;
  border-color: #e03131;
  box-shadow: 0 12px 28px -20px rgba(224, 49, 49, 0.45);
}

.draft-panel__body {
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 0;
  border-radius: 1.25rem;
  background: transparent;
  box-shadow: none;
  position: relative;
  top: -1px;
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
  font-size: 1.08rem;
}

.attachment-card__link {
  text-decoration: none;
}

.attachment-card__link:hover {
  text-decoration: underline;
}

.attachment-card__context {
  line-height: 1.4;
  font-size: 1rem;
}

.attachment-card__meta {
  font-size: 1rem;
}

.draft-panel__section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.1rem;
  padding: 1rem 1.1rem;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 50px -36px rgba(15, 23, 42, 0.25);
}

.drafts .card-body form .form-label {
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 0.2rem;
}

.compose-label {
  margin: 0;
  font-weight: 600;
  font-size: 0.95rem;
}

.compose-input {
  resize: vertical;
  min-height: 18px;
  padding: 0.2rem 0.35rem;
  font-size: 0.85rem; /* под размер текста на кнопке */
}

.compose-send {
  white-space: nowrap;
  min-height: 16px;
  padding: 0.25rem 0.45rem;
  border-radius: 0.5rem;
}

.draft-chat__composer .d-flex.flex-column {
  gap: 0.25rem !important;
}

.draft-chat__composer .flex-md-row {
  gap: 0.25rem !important;
}

.profile-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem 1rem;
  z-index: 1055;
}

.profile-preview {
  width: min(90vw, 520px);
  border: 0;
  border-radius: 18px;
  box-shadow: 0 28px 70px -40px rgba(15, 23, 42, 0.35);
  max-height: 92vh;
  overflow-y: auto;
}

.profile-preview__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 1.25rem 0.75rem;
  border-bottom: 1px solid var(--bs-border-color-translucent);
}

.profile-preview__title {
  font-weight: 700;
  font-size: 1.25rem;
  color: #1f2937;
}

.profile-preview__body {
  padding: 1rem 1.25rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.profile-preview__section {
  padding: 0.85rem 0.95rem;
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 12px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.profile-preview__section .profile-preview__label {
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b7280;
}

.profile-preview__section .profile-preview__value {
  color: #111827;
  font-weight: 600;
}

.profile-preview__pair {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.chat-date {
  display: flex;
  justify-content: center;
  margin: 0.4rem 0 0.15rem;
}

.chat-date__pill {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  background: rgba(15, 23, 42, 0.8);
  color: #fff;
  padding: 0.15rem 0.9rem;
  border-radius: 999px;
  font-size: 0.82rem;
  box-shadow: 0 6px 20px -12px rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  margin-left: auto;
  margin-right: auto;
}

.chat-floating-date {
  --floating-date-offset: 0px; /* регулирует смещение всплывающей даты относительно центра */
  position: sticky;
  top: 0.25rem;
  z-index: 3;
  display: flex;
  justify-content: center;
  pointer-events: none;
  width: 100%;
  transform: translateZ(0);
  height: 26px;
  padding-right: 18px; /* компенсация ширины скроллбара для ровного центрирования */
}

.chat-date__pill--floating {
  position: relative;
  transform: translateX(var(--floating-date-offset));
}

.chat-date-fade-enter-active,
.chat-date-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.chat-date-fade-enter-from,
.chat-date-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>


