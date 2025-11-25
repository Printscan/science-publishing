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
                <button class="btn btn-outline-secondary btn-sm" type="button" @click.stop="goToDrafts(work)">
                  Открыть черновики
                </button>
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
          <div class="task-detail__header d-flex align-items-start justify-content-between mb-3">
            <div class="me-3">
              <h4 class="mb-1">
                {{ detailState.work?.title || detailState.task?.subject || 'Детали задачи' }}
              </h4>
              <div class="text-muted small">
                {{ detailState.work?.author_display_name || detailState.task?.work_author_display_name || detailState.task?.work_author_username || '—' }}
              </div>
            </div>
            <button type="button" class="btn-close" aria-label="Закрыть" @click="closeTask"></button>
          </div>
          <div class="task-detail__body card-body pt-0">
            <div v-if="detailState.loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загружаем задачу...</span>
              </div>
            </div>
            <div v-else-if="detailState.error" class="alert alert-danger mb-0">
              {{ detailState.error }}
            </div>
            <div v-else-if="!detailState.task" class="alert alert-light border mb-0">
              Нет данных по задаче.
            </div>
            <div v-else class="task-detail__layout">
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
                  <div
                    v-for="task in orderedTasks"
                    :key="task.id"
                    class="task-chat__conversation"
                  >
                    <div class="task-chat__timeline">
                      <span class="task-chat__dot" :class="statusAccentClass(task.status)"></span>
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
                        <span class="badge task-chat__status" :class="statusBadgeClass(task.status)">
                          {{ task.status_display || statusLabel(task.status) }}
                        </span>
                      </header>

                      <div v-if="task.message" class="task-chat__lead">
                        {{ task.message }}
                      </div>

                      <div v-if="task.messages && task.messages.length" class="chat-thread">
                        <div
                          v-for="message in task.messages"
                          :key="message.id || message.created_at"
                          :class="['chat-entry', messageAlignmentClass(task, message)]"
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

                      <div v-if="taskSummaries[task.id]" class="chat-entry chat-entry--summary">
                        <div class="chat-entry__heading">
                          <div class="chat-entry__name">{{ taskRecipientName(task) }}</div>
                          <span class="chat-entry__time text-muted small">{{ formatDateTime(task.closed_at || task.updated_at) }}</span>
                        </div>
                        <div class="chat-entry__body">
                          <p v-if="taskSummaries[task.id].note" class="mb-2">
                            {{ taskSummaries[task.id].note }}
                          </p>
                          <div v-if="taskSummaries[task.id].changes && taskSummaries[task.id].changes.length" class="chat-entry__changes">
                            <div class="chat-entry__subtitle text-muted small">Итоги</div>
                            <ul class="chat-change-list">
                            <li v-for="change in taskSummaries[task.id].changes" :key="change.field || change.name || change.label">
                              <strong>{{ changeLabel(change) }}:</strong>
                              <span class="text-muted ms-1">было {{ formatChangeValue(changeOld(change)) }}</span>
                              <span class="ms-1">стало {{ formatChangeValue(changeNew(change)) }}</span>
                            </li>
                          </ul>
                        </div>
                          <div v-if="taskSummaries[task.id].attachments && taskSummaries[task.id].attachments.length" class="chat-entry__attachments">
                            <div class="chat-entry__subtitle text-muted small">Файлы</div>
                            <ul class="chat-attachment-list">
                              <li v-for="attachment in taskSummaries[task.id].attachments" :key="attachment.url || attachment.absolute_url">
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

              <section v-if="showTaskActions" class="task-actions-bar">
                <div class="task-actions d-flex flex-wrap gap-2">
                  <button
                    v-if="canApprovePublication"
                    type="button"
                    class="btn btn-success"
                    :disabled="detailState.actionLoading"
                    @click="approvePublication"
                  >
                    <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Утвердить публикацию
                  </button>
                  <button
                    v-if="canSendToChief"
                    type="button"
                    class="btn btn-primary"
                    :disabled="detailState.actionLoading"
                    @click="sendToChief"
                  >
                    <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Отправить главному редактору
                  </button>
                  <button
                    v-if="canRequestChanges"
                    type="button"
                    class="btn btn-outline-danger"
                    :disabled="detailState.actionLoading"
                    @click="sendBackToAuthor"
                  >
                    <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Вернуть на доработку
                  </button>
                  <button
                    v-if="canAssignEditorForWork"
                    type="button"
                    class="btn btn-outline-primary"
                    @click="openAssignModal"
                  >
                    Назначить редактора
                  </button>
                  <button
                    v-if="canCreateAuthorTask"
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="openAuthorTaskModal"
                  >
                    Назначить новое задание
                  </button>
                </div>
              </section>

              <form
                v-if="showMessageComposer && detailState.activeTab === 'chat'"
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
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';
import { RefreshCcw, Search } from 'lucide-vue-next';
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
const currentProfileId = computed(() => profile.value?.id || profile.value?.profile_id || null);
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

const detailState = reactive({
  open: false,
  loading: false,
  task: null,
  work: null,
  tasks: [],
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
  () => detailState.tasks,
  async () => {
    if (detailState.activeTab === 'chat') {
      await nextTick();
      scrollChatToEnd();
    }
  }
);

const orderedTasks = computed(() => {
  const list = Array.isArray(detailState.tasks) ? [...detailState.tasks] : [];
  return list.sort((a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0));
});

const taskSummaries = computed(() => {
  const summaries = {};
  (detailState.tasks || []).forEach((task) => {
    const summary = buildTaskSummary(task);
    if (summary) {
      summaries[task.id] = summary;
    }
  });
  return summaries;
});

const detailAttachments = computed(() => {
  const items = [];
  const summaries = taskSummaries.value || {};
  const tasks = Array.isArray(detailState.tasks) ? detailState.tasks : [];

  tasks.forEach((task, taskIndex) => {
    if (!task) return;
    const taskSubject = task.subject || detailState.work?.title || 'Без темы';
    const statusDisplay = task.status_display || statusLabel(task.status);
    const senderName = taskSenderName(task);

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
      const origin = meta.origin || 'message';
      const originLabel =
        origin === 'summary'
          ? 'Итоги задачи'
          : origin === 'task'
            ? 'Постановка'
            : 'Комментарий';
      const author = meta.author || '';
      const createdAt = meta.createdAt || null;
      const displayDate = formatDateTime(createdAt);

      const keywords = [name, author, originLabel, taskSubject, statusDisplay, context, displayDate]
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
        origin,
        originLabel,
        taskSubject,
        statusDisplay,
        context,
        keywords,
      });
    };

    if (Array.isArray(task.attachments) && task.attachments.length > 0) {
      task.attachments.forEach((attachment, attachmentIndex) => {
        const key = ['task', task.id || taskIndex, attachmentIndex].join('-');
        pushAttachment(attachment, {
          key,
          origin: 'task',
          author: senderName,
          createdAt: task.created_at,
          context: task.message || '',
        });
      });
    }

    if (Array.isArray(task.messages)) {
      task.messages.forEach((message, messageIndex) => {
        if (!Array.isArray(message.attachments)) return;
        message.attachments.forEach((attachment, attachmentIndex) => {
          const key = ['message', task.id || taskIndex, message.id || messageIndex, attachmentIndex].join('-');
          pushAttachment(attachment, {
            key,
            origin: 'message',
            author: messageAuthorName(message),
            createdAt: message.created_at,
            context: message.content || '',
          });
        });
      });
    }

    const summary = summaries[task.id];
    if (summary?.attachments && summary.attachments.length) {
      summary.attachments.forEach((attachment, attachmentIndex) => {
        const key = ['summary', task.id || taskIndex, attachmentIndex].join('-');
        pushAttachment(attachment, {
          key,
          origin: 'summary',
          author: taskRecipientName(task),
          createdAt: task.closed_at || task.updated_at,
          context: summary.note || '',
        });
      });
    }
  });

  return items;
});

const filteredAttachments = computed(() => {
  const query = detailState.attachmentQuery.trim().toLowerCase();
  if (!query) return detailAttachments.value;
  return detailAttachments.value.filter((item) => item.keywords.includes(query));
});

const lastOpenTask = computed(() => {
  const open = orderedTasks.value.filter((task) => !task.closed_at);
  return open.length ? open[open.length - 1] : null;
});

const canManageCurrentTask = computed(() => {
  if (!detailState.task) return false;
  if (isChiefEditor.value) return true;
  return detailState.task.recipient === currentUserId.value;
});

const showTaskActions = computed(() => canManageCurrentTask.value);

const showMessageComposer = computed(() => {
  if (!canManageCurrentTask.value) return false;
  return Boolean(
    lastOpenTask.value && detailState.task && detailState.task.id === lastOpenTask.value.id
  );
});

const canAssignEditorForWork = computed(
  () =>
    isChiefEditor.value &&
    detailState.work &&
    ASSIGNABLE_STATUSES.has(detailState.work.status)
);

const canCreateAuthorTask = computed(() =>
  detailState.work?.profile &&
  AUTHOR_TASK_STATUSES.has(detailState.work.status) &&
  (isChiefEditor.value || isCurrentEditor.value)
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

function statusAccentClass(status) {
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
  return task?.sender_display_name || task?.sender_username || 'Отправитель';
}

function taskRecipientName(task) {
  return task?.recipient_display_name || task?.recipient_username || 'Получатель';
}

function messageAlignmentClass(task, message) {
  if (!message) return 'chat-entry--neutral';
  if (message.is_system) return 'chat-entry--system';
  if (task?.sender && message.author === task.sender) return 'chat-entry--sender';
  if (task?.recipient && message.author === task.recipient) return 'chat-entry--recipient';
  return 'chat-entry--neutral';
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

function goToDrafts(work) {
  const workId = work?.workId;
  const query = workId ? { work: workId } : undefined;
  router.push({ name: 'SciencePublishingDrafts', query });
}

function closeTask() {
  detailState.open = false;
  detailState.task = null;
  detailState.work = null;
  detailState.tasks = [];
  detailState.error = '';
  detailState.note = '';
  detailState.message = '';
  resetDetailTabs();
  closeAssignModal();
  closeAuthorTaskModal();
}

async function openTask(task) {
  if (!task) return;
  detailState.open = true;
  detailState.error = '';
  detailState.task = null;
  detailState.work = null;
  detailState.tasks = [];
  detailState.note = '';
  detailState.message = '';
  resetDetailTabs();
  await loadWorkTasks(task.work || task.work_id, { selectTaskId: task.id });
}

async function refreshDetail() {
  const workId = detailState.work?.id || detailState.task?.work;
  if (!workId) return;
  const currentTaskId = detailState.task?.id ?? null;
  await loadWorkTasks(workId, { selectTaskId: currentTaskId });
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

async function loadWorkTasks(workId, options = {}) {
  if (!workId) return;
  detailState.loading = true;
  detailState.error = '';
  const { selectTaskId = null } = options;
  try {
    await loadDetailWork(workId);
    const params = {
      ordering: '-created_at',
      page_size: 100,
    };
    if (workId) {
      params.work = workId;
    }
    if (selectTaskId) {
      params.selected_task = selectTaskId;
    }
    const response = await sciencePublishingAPI.listTasks(params);
    const data = response?.data ?? response;
    const taskList = Array.isArray(data) ? data : data?.results ?? [];
    const detailedTasks = await Promise.all(
      taskList.map(async (item) => {
        try {
          const detailResp = await sciencePublishingAPI.getTask(item.id);
          return detailResp?.data ?? detailResp;
        } catch (err) {
          return item;
        }
      })
    );
    detailState.tasks = detailedTasks;
    const nextActive =
      (selectTaskId && detailedTasks.find((item) => item.id === selectTaskId)) ||
      detailedTasks.find((item) => !item.closed_at) ||
      detailedTasks[0] ||
      null;
    detailState.task = nextActive;
    detailState.note = '';
    detailState.message = '';
    await nextTick();
    scrollChatToEnd();
  } catch (err) {
    detailState.tasks = [];
    detailState.task = null;
    detailState.note = '';
    detailState.message = '';
    detailState.error = err?.message || 'Не удалось загрузить задачи по работе.';
  } finally {
    detailState.loading = false;
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
    await Promise.all([refreshDetail(), loadTasks()]);
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
    await nextTick();
    scrollChatToEnd();
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
