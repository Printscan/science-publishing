<template>
  <div v-if="accessDenied" class="alert alert-warning m-4">
    Нет доступа к задачам редакции.
  </div>
  <div v-else class="tasks-page container-fluid py-4">
      <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
        <div>
          <h2 class="page-title mb-0">Задачи редакции</h2>
        <p class="page-subtitle mb-0 text-muted"></p>
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
            <button type="button" class="btn btn-outline-secondary reset-btn" :disabled="loading" @click="resetFilters">
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
                    <strong>Автор:</strong> {{ work.profile_display_name || work.profile_username || '—' }}
                  </div>
                  <div class="small text-muted">
                    <strong>Тип:</strong> {{ work.publication_kind_display || '—' }}
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
                <div class="task-detail__meta d-flex align-items-center gap-2 flex-wrap">
                  <span class="task-detail__author">{{ taskAuthorDisplay }}</span>
                  <span
                    class="badge task-chat__status"
                    :class="statusBadgeClass(detailState.work?.status)"
                  >
                    {{ statusLabel(detailState.work?.status) }}
                  </span>
                </div>
              </div>
              <div class="d-flex flex-wrap align-items-start gap-2">
                <a
                  v-if="detailState.work?.document"
                  :href="workDocumentUrl(detailState.work)"
                target="_blank"
                rel="noopener"
                class="btn task-action-btn task-action-btn--ghost"
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
                  <div class="task-detail__topbar d-flex flex-wrap align-items-center justify-content-between gap-2 mb-0">
                <div class="task-detail__actions d-flex flex-wrap gap-2">
                  <button
                    v-if="isChiefEditor"
                    type="button"
                    class="btn task-action-btn task-action-btn--accent"
                    :disabled="detailState.actionLoading"
                    @click="publishWork"
                  >
                    <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Опубликовать
                  </button>
                  <button
                    v-else-if="canSendToChiefWork"
                    type="button"
                    class="btn task-action-btn task-action-btn--accent"
                    :disabled="detailState.actionLoading"
                    @click="sendToChiefWork"
                  >
                    <span v-if="detailState.actionLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Отправить главному редактору
                  </button>
                  <button
                    v-if="canAssignEditorForWork"
                    type="button"
                    class="btn task-action-btn task-action-btn--ghost"
                    @click="openAssignModal"
                  >
                    {{ detailState.work?.current_editor_display_name ? 'Сменить редактора' : 'Назначить редактора' }}
                  </button>
                </div>
                <div class="task-detail__tabs task-detail__tabs--inline nav nav-pills">
                  <button
                    type="button"
                    class="task-detail__tab nav-link"
                    :class="{ 'task-detail__tab--active active': detailState.activeTab === 'chat' }"
                    @click="setDetailTab('chat')"
                  >
                    Переписка
                  </button>
                  <button
                    type="button"
                    class="task-detail__tab nav-link"
                    :class="{ 'task-detail__tab--active active': detailState.activeTab === 'attachments' }"
                    @click="setDetailTab('attachments')"
                  >
                    Вложения
                    <span v-if="detailAttachments.length" class="task-detail__tab-count">
                      {{ detailAttachments.length }}
                    </span>
                  </button>
                </div>
              </div>

              <div ref="detailScrollRef" class="task-detail__content">
                <div v-if="detailState.activeTab === 'chat'" class="task-chat">
                  <div v-if="!detailState.chatMessages.length" class="alert alert-light border text-center mb-0">
                    Переписка пока пуста.
                  </div>
                  <div v-else class="task-chat__frame">
                    <div class="task-chat__content">
                      <div class="chat-thread" ref="chatThreadRef" @scroll="updateFloatingDate">
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
                                <div class="chat-entry__subtitle text-muted small">Изменения</div>
                                <ul class="chat-change-list">
                                  <li v-for="change in item.message.changes" :key="change.field || change.name || change.label">
                                    <strong>{{ changeLabel(change) }}:</strong>
                                    <span class="text-muted ms-1">было {{ formatChangeValue(changeOld(change)) }}</span>
                                    <span class="ms-1">стало {{ formatChangeValue(changeNew(change)) }}</span>
                                  </li>
                                </ul>
                              </div>
                              <div v-if="messageHasAttachments(item.message)" class="chat-entry__attachments">
                                <div class="chat-entry__subtitle text-muted small">Вложения</div>
                                <ul class="chat-attachment-list">
                                  <li v-for="attachment in item.message.attachments" :key="attachment.url || attachment.absolute_url">
                                    <a :href="attachment.absolute_url || attachment.url" target="_blank" rel="noopener">
                                      {{ attachment.name || attachment.url || 'Файл' }}
                                    </a>
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
                    <form
                      class="task-composer"
                      @submit.prevent="sendMessage"
                    >
                      <div class="d-flex flex-column gap-2">
                        <div class="d-flex flex-column flex-md-row gap-2 align-items-stretch">
                          <textarea
                            id="detail-message"
                            v-model="detailState.message"
                            class="form-control compose-input"
                            rows="2"
                            placeholder="Сообщение..."
                            :disabled="detailState.messageLoading"
                          ></textarea>
                          <button
                            class="btn btn-primary compose-send"
                            type="submit"
                            :disabled="detailState.messageLoading || !detailState.message.trim()"
                          >
                            <span v-if="detailState.messageLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            Отправить
                          </button>
                        </div>
                      </div>
                    </form>
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

            </div>
          </div>
        </div>
      </div>
    </Teleport>
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
            Профиль недоступен.
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
import { createChatSocket } from '@/modules/science_publishing/client/js/chat-socket.js';
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
  if (typeof value === 'object') {
    const nested = value.id ?? value.user_id ?? value.user;
    if (nested !== undefined && nested !== null) {
      return normalizeId(nested);
    }
    return null;
  }
  if (typeof value === 'number') return String(value);
  const num = Number(value);
  return Number.isNaN(num) ? String(value) : String(num);
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
let chatSocket = null;
const pendingSendTimers = {};
const PENDING_STORE_PREFIX = 'sp_pending_messages';
const PENDING_FAIL_AFTER_MS = 30000;
const PENDING_STALE_MS = 5 * 60 * 1000;
const SERVER_DUPLICATE_WINDOW_MS = 1500;

function messageKey(message) {
  if (!message) return '';
  if (message?.metadata?.temp_id) return `temp:${message.metadata.temp_id}`;
  if (message?.id) return String(message.id);
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
    if (prev.pending_status && !msg.pending_status) {
      map.set(key, msg);
      continue;
    }
    if (!prev.pending_status && msg.pending_status) {
      continue;
    }
    const prevDate = new Date(prev.created_at || 0).getTime();
    const msgDate = new Date(msg.created_at || 0).getTime();
    if (msgDate >= prevDate) {
      map.set(key, msg);
    }
  }
  return Array.from(map.values()).sort((a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0));
}

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
const floatingDayKey = ref('');
const floatingDateLabel = computed(() => (floatingDayKey.value ? formatDateLabel(floatingDayKey.value) || '' : ''));
const firstChatDayKey = computed(() => chatItems.value.find((item) => item.type === 'date')?.dayKey || '');
const chatThreadRef = ref(null);
const chatInitialScrollDone = ref(false);

const chatItems = computed(() => {
  const list = Array.isArray(detailState.chatMessages) ? detailState.chatMessages : [];
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
      chatInitialScrollDone.value = false;
      await nextTick();
      scrollChatToBottomOnce(true);
      syncFloatingDateSoon();
    }
  }
);

watch(
  () => detailState.chatMessages,
  async () => {
    if (detailState.activeTab === 'chat') {
      await nextTick();
      syncFloatingDateSoon();
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
      attachment.label ||
      extractFileName(url) ||
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
    if (profileId && authorProfileCache[profileId]?.fullProfile) {
      data = authorProfileCache[profileId];
    } else if (profileId) {
      const response = await sciencePublishingAPI.getProfile(profileId);
      data = response?.data ?? response;
      if (data) {
        authorProfileCache[profileId] = {
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
        authorProfileCache[data.id] = {
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
  } catch (err) {
    profilePreview.error = err?.message || 'Не удалось загрузить профиль.';
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

function updateFloatingDate() {
  const container = chatThreadRef.value;
  if (!container) return;
  const items = Array.from(container.querySelectorAll('.chat-entry'));
  const viewportTop = container.scrollTop + 8;
  const threshold = viewportTop + container.clientHeight * 0.2;
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

function formatDateTime(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleString('ru-RU');
  } catch {
    return value;
  }
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

function pendingStoreKey(workId) {
  const userId = normalizeId(currentUserId.value) || 'anon';
  return `${PENDING_STORE_PREFIX}_${workId}_${userId}`;
}

function savePendingMessages(workId) {
  if (!workId) return;
  const pending = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).filter((m) => m.pending_status);
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
  detailState.chatMessages = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).filter(
    (m) => String(m.id) !== String(tempId)
  );
  savePendingMessages(workId);
}

function replacePendingWithServer(workId, tempId, serverMessage) {
  if (!workId || !tempId || !serverMessage) return;
  const list = Array.isArray(detailState.chatMessages) ? [...detailState.chatMessages] : [];
  const idx = list.findIndex((m) => String(m.id) === String(tempId));
  if (idx !== -1) {
    list[idx] = { ...serverMessage, pending_status: null };
    detailState.chatMessages = list.sort(
      (a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0)
    );
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
  detailState.chatMessages = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).map((m) => {
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
    author_profile_id: currentProfileId.value || null,
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
    detailState.chatMessages = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).map((m) =>
      String(m.id) === String(message.id) ? patched : m
    );
    savePendingMessages(detailState.work?.id);
    sendPendingMessage(detailState.work?.id, patched);
  } else {
    removePendingMessage(detailState.work?.id, message.id);
  }
}

function collectUnreadMessageIds() {
  return (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : [])
    .filter((m) => !m.is_system && !isOwnMessage(m) && !m.is_read && !m.pending_status)
    .map((m) => String(m.id));
}

let markReadTimer = null;
let markReadUpToTimer = null;

function markMessagesReadSoon() {
  if (detailState.activeTab !== 'chat' || !detailState.work?.id) return;
  const ids = collectUnreadMessageIds();
  if (!ids.length) return;
  if (markReadTimer) {
    clearTimeout(markReadTimer);
  }
  markReadTimer = setTimeout(async () => {
    try {
      await sciencePublishingAPI.markChatMessagesRead(detailState.work.id, ids);
      detailState.chatMessages = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).map((m) => {
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
      const message = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).find(
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
  if (detailState.activeTab !== 'chat' || !detailState.work?.id) return;
  const lastId = findLastVisibleMessageId();
  if (!lastId) return;
  if (markReadUpToTimer) {
    clearTimeout(markReadUpToTimer);
  }
  markReadUpToTimer = setTimeout(async () => {
    try {
      await sciencePublishingAPI.markChatMessagesReadUpTo(detailState.work.id, lastId);
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
  detailState.chatMessages = (Array.isArray(detailState.chatMessages) ? detailState.chatMessages : []).map((m) => {
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

watch(
  () => detailState.activeTab,
  (value) => {
    if (value === 'chat') {
      markMessagesReadSoon();
      markVisibleMessagesReadUpToSoon();
    }
  }
);

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
  closeChatSocket();
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
      detailState.chatMessages = upsertMessages(detailState.chatMessages, [data]);
      if (data?.metadata?.temp_id && pendingSendTimers[data.metadata.temp_id]) {
        clearTimeout(pendingSendTimers[data.metadata.temp_id]);
        delete pendingSendTimers[data.metadata.temp_id];
        savePendingMessages(workId);
      }
      syncFloatingDateSoon();
      if (!isOwnMessage(data) && detailState.activeTab === 'chat') {
        markMessagesReadSoon();
      }
    },
    onError: () => {
      // websocket errors are best-effort
    },
  });
}

async function loadWorkChat(workId, options = {}) {
  const { background = false } = options;
  if (!workId) return;
  if (!background) {
    detailState.loading = true;
    resetChatScrollState();
  }
  detailState.error = '';
  try {
    await loadDetailWork(workId);
    const response = await sciencePublishingAPI.listWorkChatMessages(workId);
    const data = response?.data ?? response;
    const baseList = Array.isArray(data) ? data : data?.results ?? [];
    const pending = loadPendingMessages(workId);
    const pendingClean = pending.filter((p) => {
      if (p?.metadata?.temp_id) {
        const matchedByTemp = baseList.some(
          (m) => m?.metadata?.temp_id && String(m.metadata.temp_id) === String(p.metadata.temp_id)
        );
        if (matchedByTemp) return false;
      }
      const content = String(p?.content || '').trim();
      const authorId = normalizeId(p?.author);
      const matchedByContent = baseList.some(
        (m) =>
          String(m?.content || '').trim() === content &&
          normalizeId(m?.author) === authorId &&
          normalizeId(m?.author_user_id) === authorId
      );
      return !matchedByContent;
    });
    if (pendingClean.length !== pending.length) {
      savePendingMessages(workId);
    }
    detailState.chatMessages = upsertMessages(baseList, pendingClean);
    connectChatSocket(workId);
    await nextTick();
    scrollChatToBottomOnce(true);
    if (!background) {
      detailState.note = '';
      detailState.message = '';
    }
    await nextTick();
    syncFloatingDateSoon();
    markMessagesReadSoon();
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

function resetChatScrollState() {
  chatInitialScrollDone.value = false;
}

function scrollChatToBottomOnce(force = false) {
  if (detailState.activeTab !== 'chat') return;
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
    const pending = createPendingMessage(detailState.message.trim());
    detailState.chatMessages = [...detailState.chatMessages, pending];
    savePendingMessages(detailState.work.id);
    scrollChatToBottomOnce(true);
    sendPendingMessage(detailState.work.id, pending);
    detailState.message = '';
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
  closeChatSocket();
});
</script>

<style scoped>
.tasks-page .page-subtitle {
  max-width: 640px;
}

.tasks-page .form-label {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.3rem;
}

.tasks-page .form-control,
.tasks-page .form-select {
  font-size: 1rem;
  color: #111827;
}

.tasks-page .form-control::placeholder,
.tasks-page .form-select::placeholder {
  color: #6b7280;
}

.tasks-page .reset-btn {
  border-radius: 12px;
  border: 1px solid rgba(224, 49, 49, 0.45);
  color: #c01e1e;
  background: rgba(224, 49, 49, 0.1);
  font-weight: 700;
  padding: 0.55rem 1rem;
}

.tasks-page .reset-btn:hover:not(:disabled),
.tasks-page .reset-btn:focus-visible:not(:disabled) {
  border-color: rgba(224, 49, 49, 0.65);
  background: rgba(224, 49, 49, 0.16);
  color: #a01717;
}

.tasks-page .reset-btn:disabled {
  opacity: 0.55;
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

.task-card .card-title {
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.35;
  color: #1f2937;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.75rem 1.75rem rgba(15, 23, 42, 0.1);
}

.task-card .card-body {
  padding: 1.5rem;
}

.task-card .text-muted {
  color: #4b5563 !important;
  font-size: 0.98rem;
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
  gap: 0.25rem;
  min-height: 0;
}

.task-detail__topbar {
  gap: 0.5rem;
}

.task-detail__tabs--inline {
  margin-left: auto;
  gap: 0.5rem;
}

.task-detail__content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-right: 0;
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
  gap: 0;
  padding: 0 0.75rem 0;
}

.task-detail__tab {
  border: 1px solid transparent;
  background: transparent;
  border-radius: 0.9rem 0.9rem 0 0;
  padding: 0.55rem 1.3rem 0.5rem;
  color: rgba(15, 23, 42, 0.8);
  font-weight: 600;
  transition: color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.task-detail__tab:hover {
  color: rgba(15, 23, 42, 0.85);
  border-color: rgba(13, 110, 253, 0.45);
  box-shadow: 0 12px 28px -20px rgba(15, 23, 42, 0.35);
}

.task-detail__tab--active {
  background: #e03131;
  color: #fff;
  border-color: #e03131;
  box-shadow: 0 18px 36px -22px rgba(224, 49, 49, 0.45);
  position: relative;
  bottom: -1px;
}

.task-detail__meta {
  color: #4b5563;
  font-size: 0.95rem;
}

.task-detail__author {
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 0.01em;
}

.task-action-btn {
  border-radius: 0.8rem;
  padding: 0.5rem 1rem;
  font-weight: 600;
  border: 1px solid rgba(224, 49, 49, 0.22);
  background: linear-gradient(120deg, rgba(224, 49, 49, 0.08), rgba(224, 49, 49, 0.03));
  color: #a31414;
  box-shadow: 0 12px 28px -22px rgba(15, 23, 42, 0.28);
  transition: background-color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease;
  text-decoration: none;
}

.task-action-btn:hover,
.task-action-btn:focus-visible {
  background: rgba(224, 49, 49, 0.12);
  border-color: rgba(224, 49, 49, 0.35);
  color: #861010;
  transform: translateY(-1px);
}

.task-action-btn:active {
  transform: translateY(0);
  box-shadow: 0 10px 22px -18px rgba(15, 23, 42, 0.26);
}

.task-action-btn--accent {
  background: linear-gradient(120deg, #e03131, #d62a2a);
  color: #fff;
  border-color: #d62a2a;
  box-shadow: 0 16px 36px -20px rgba(224, 49, 49, 0.55);
}

.task-action-btn--accent:hover,
.task-action-btn--accent:focus-visible {
  background: linear-gradient(120deg, #d62828, #c72020);
  color: #fff;
  border-color: #c72020;
}

.task-action-btn--ghost {
  background: rgba(224, 49, 49, 0.06);
  color: #a31414;
}

.task-action-btn:disabled,
.task-action-btn.disabled {
  opacity: 0.65;
  box-shadow: none;
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
  gap: 0;
  padding-bottom: 0;
  flex: 1;
  min-height: 0;
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

.task-chat__frame {
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.25rem;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.92);
}

.task-chat__content {
  border: 0;
  border-radius: 0;
  padding: 1.25rem 1.5rem 0.35rem;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  flex: 1;
  min-height: 0;
  overflow: hidden;
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
  font-weight: 600;
  background-color: rgba(15, 23, 42, 0.06) !important;
  color: #374151 !important;
  border: 1px solid rgba(15, 23, 42, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.chat-thread {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.2rem 0 0.75rem;
  flex: 1;
  min-height: 0;
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

.chat-entry__body {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.95rem;
}

.chat-entry__changes,
.chat-entry__attachments {
  padding: 0.6rem 0.75rem;
  border-radius: 0.75rem;
  background: rgba(248, 249, 252, 0.8);
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
  border-color: rgba(13, 110, 253, 0.2);
  background: rgba(13, 110, 253, 0.08);
  color: rgba(15, 23, 42, 0.9);
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

.chat-entry__time,
.chat-entry__time-inline {
  font-size: 0.78rem;
  color: rgba(15, 23, 42, 0.6);
}

.chat-entry__time-inline {
  white-space: nowrap;
  margin-left: 0.4rem;
  align-self: flex-end;
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
  padding-right: 0;
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

.task-attachments {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid var(--bs-border-color-translucent);
  border-radius: 1.1rem;
  padding: 1rem 1.1rem;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 50px -36px rgba(15, 23, 42, 0.25);
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

.task-composer .form-control {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.task-composer .btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.task-composer {
  border: 0;
  border-top: 1px solid var(--bs-border-color-translucent);
  border-radius: 0;
  padding: 0.45rem 0.55rem;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: none;
  margin-top: 0;
}

.compose-input {
  resize: vertical;
  min-height: 18px;
  max-height: 120px;
  padding: 0.2rem 0.35rem;
  font-size: 0.85rem;
  overflow-y: auto;
  display: block;
  width: 100%;
}

.compose-send {
  white-space: nowrap;
  min-height: 16px;
  padding: 0.25rem 0.45rem;
  border-radius: 0.5rem;
}

.task-composer .d-flex.flex-column {
  gap: 0.25rem !important;
}

.task-composer .flex-md-row {
  gap: 0.25rem !important;
}

.task-attachments__dot::before,
.attachment-card__dot::before {
  content: '';
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
