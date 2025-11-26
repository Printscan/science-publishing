<template>
  <div class="card shadow-sm published-card">
    <div class="card-body">
      <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
        <div>
          <h6 class="mb-0">Опубликованные работы</h6>
          <small class="text-muted">Фильтруйте и открывайте публикации</small>
        </div>
        <span class="badge rounded-pill text-bg-secondary-subtle text-secondary">{{ filteredPublications.length }}</span>
      </div>

      <div class="row g-2 filters-bar mb-3">
        <div class="col-12 col-md-6 col-lg-3">
          <input
            v-model.trim="filters.query"
            type="search"
            class="form-control"
            placeholder="Поиск по названию, описанию"
          />
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <select v-model="filters.author" class="form-select">
            <option value="">Все авторы</option>
            <option v-for="opt in authorOptions" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <select v-model="filters.kind" class="form-select">
            <option value="">Все типы</option>
            <option v-for="opt in kindOptions" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <select v-model="filters.subtype" class="form-select">
            <option value="">Все подтипы</option>
            <option v-for="opt in subtypeOptions" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <select v-model="filters.trainingForm" class="form-select">
            <option value="">Любая форма</option>
            <option v-for="opt in trainingOptions" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="col-6 col-md-3 col-lg-1">
          <select v-model="filters.year" class="form-select">
            <option value="">Год</option>
            <option v-for="opt in yearOptions" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="col-12 col-md-auto">
          <button type="button" class="btn btn-outline-secondary w-100" @click="resetFilters">Сбросить</button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger mb-0">
        {{ error }}
      </div>
      <div v-else>
        <div v-if="!filteredPublications.length" class="text-muted text-center py-4">
          Публикации не найдены.
        </div>
        <div v-else class="tiles-grid">
          <article
            v-for="item in filteredPublications"
            :key="item.id"
            class="pub-tile card shadow-sm"
            :class="{ 'pub-tile--active': selectedPublication && selectedPublication.id === item.id }"
            @click="openDetail(item)"
          >
            <div class="card-body d-flex flex-column gap-2">
              <div class="d-flex justify-content-between align-items-start gap-2">
                <div>
                  <h6 class="mb-1">{{ item.discipline_name || 'Без названия' }}</h6>
                  <div class="text-muted small">
                    {{ item.publication_kind_display || item.publication_kind || '—' }}
                  </div>
                </div>
                <span class="badge text-bg-light">{{ item.year || '—' }}</span>
              </div>

              <div class="text-muted small">
                Автор: {{ item.author_full_name || item.profile_display_name || '—' }}
              </div>
              <div class="text-muted small">
                Подтип: {{ item.guideline_subtype_display || '—' }}
              </div>
              <div class="text-muted small">
                Форма обучения: {{ item.training_form_display || '—' }}
              </div>

              <div class="mt-auto d-flex justify-content-between align-items-center gap-2">
                <span class="badge text-bg-success">Опубликовано</span>
                <a
                  v-if="documentUrl(item)"
                  :href="documentUrl(item)"
                  class="btn btn-outline-primary btn-sm"
                  target="_blank"
                  rel="noopener"
                >
                  Скачать файл
                </a>
                <span v-else class="text-muted small">Файл не прикреплён</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showDetail && selectedPublication" class="detail-overlay" role="dialog" aria-modal="true">
      <div class="detail-modal card shadow-lg">
        <div class="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h5 class="mb-1">{{ selectedPublication.discipline_name || 'Без названия' }}</h5>
            <div class="text-muted small">
              {{ selectedPublication.publication_kind_display || selectedPublication.publication_kind || '—' }}
            </div>
          </div>
          <button type="button" class="btn-close" aria-label="Закрыть" @click="closeDetail"></button>
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3">
          <span class="badge text-bg-success">Опубликовано</span>
          <span class="text-muted small">{{ formatDate(selectedPublication.published_at) || '—' }}</span>
        </div>

        <div class="detail-grid">
          <div class="form-group">
            <label class="form-label">Ректор</label>
            <div class="form-control form-control-plain">{{ selectedPublication.rector_name || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Количество страниц</label>
            <div class="form-control form-control-plain">{{ selectedPublication.pages_count || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Год</label>
            <div class="form-control form-control-plain">{{ selectedPublication.year || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">УДК</label>
            <div class="form-control form-control-plain">{{ selectedPublication.udc || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Заголовок</label>
            <div class="form-control form-control-plain">{{ selectedPublication.discipline_name || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">ББК</label>
            <div class="form-control form-control-plain">{{ selectedPublication.bbk || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Подзаголовок</label>
            <div class="form-control form-control-plain">{{ selectedPublication.discipline_topic || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Разработчик(-и)</label>
            <div class="form-control form-control-plain">{{ selectedPublication.developers || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Научный редактор</label>
            <div class="form-control form-control-plain">{{ selectedPublication.scientific_editor || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Компьютерный набор</label>
            <div class="form-control form-control-plain">{{ selectedPublication.computer_layout || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Полное ФИО автора</label>
            <div class="form-control form-control-plain">{{ selectedPublication.author_full_name || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Соавторы</label>
            <div class="form-control form-control-plain">{{ selectedPublication.co_authors || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Факультет</label>
            <div class="form-control form-control-plain">{{ selectedPublication.faculty || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Кафедра</label>
            <div class="form-control form-control-plain">{{ selectedPublication.department || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Тип публикации</label>
            <div class="form-control form-control-plain">{{ selectedPublication.publication_kind_display || selectedPublication.publication_kind || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Подтип</label>
            <div class="form-control form-control-plain">{{ selectedPublication.guideline_subtype_display || '—' }}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Форма обучения</label>
            <div class="form-control form-control-plain">{{ selectedPublication.training_form_display || '—' }}</div>
          </div>
          <div class="form-group form-group-wide">
            <label class="form-label">Описание</label>
            <div class="form-control form-control-plain">{{ selectedPublication.short_description || '—' }}</div>
          </div>
        </div>

        <div class="d-flex flex-wrap gap-2 mt-3">
          <a
            v-if="documentUrl(selectedPublication)"
            :href="documentUrl(selectedPublication)"
            class="btn btn-outline-primary"
            target="_blank"
            rel="noopener"
          >
            Скачать файл
          </a>
          <button type="button" class="btn btn-secondary" @click="closeDetail">Закрыть</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';

import { sciencePublishingAPI } from '@/modules/science_publishing/client/js/science-publishing.js';
import { apiClient } from '@/js/api/manager.js';

const toast = useToast();

const publications = ref([]);
const loading = ref(false);
const error = ref('');
const filters = ref({
  query: '',
  author: '',
  kind: '',
  subtype: '',
  trainingForm: '',
  year: '',
});
const selectedPublication = ref(null);
const showDetail = ref(false);

const kindOptions = computed(() => {
  const set = new Set();
  publications.value.forEach((item) => {
    const label = item.publication_kind_display || item.publication_kind;
    if (label) set.add(label);
  });
  return Array.from(set).sort();
});

const authorOptions = computed(() => {
  const set = new Set();
  publications.value.forEach((item) => {
    const label = item.author_full_name || item.profile_display_name;
    if (label) set.add(label);
  });
  return Array.from(set).sort();
});

const subtypeOptions = computed(() => {
  const set = new Set();
  publications.value.forEach((item) => {
    const label = item.guideline_subtype_display;
    if (label) set.add(label);
  });
  return Array.from(set).sort();
});

const trainingOptions = computed(() => {
  const set = new Set();
  publications.value.forEach((item) => {
    const label = item.training_form_display;
    if (label) set.add(label);
  });
  return Array.from(set).sort();
});

const yearOptions = computed(() => {
  const set = new Set();
  publications.value.forEach((item) => {
    if (item.year) set.add(item.year);
  });
  return Array.from(set).sort((a, b) => b - a);
});

const filteredPublications = computed(() => {
  const query = (filters.value.query || '').toLowerCase();
  const author = filters.value.author || '';
  const kind = filters.value.kind || '';
  const subtype = filters.value.subtype || '';
  const trainingForm = filters.value.trainingForm || '';
  const year = filters.value.year || '';
  return publications.value.filter((item) => {
    const matchesKind = !kind || item.publication_kind_display === kind || item.publication_kind === kind;
    const matchesSubtype = !subtype || item.guideline_subtype_display === subtype || item.guideline_subtype === subtype;
    const matchesTraining = !trainingForm || item.training_form_display === trainingForm || item.training_form === trainingForm;
    const matchesYear = !year || String(item.year) === String(year);
    const matchesAuthor = !author || item.author_full_name === author || item.profile_display_name === author;
    const haystack = [
      item.discipline_name,
      item.publication_kind_display,
      item.publication_kind,
      item.author_full_name,
      item.profile_display_name,
      item.guideline_subtype_display,
      item.short_description,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    return matchesKind && matchesSubtype && matchesTraining && matchesYear && matchesAuthor && matchesQuery;
  });
});

function formatDate(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleString('ru-RU');
  } catch {
    return value;
  }
}

function documentUrl(item) {
  const doc = item?.document;
  if (!doc) return null;
  try {
    return new URL(doc, apiClient.baseUrl).toString();
  } catch (err) {
    const normalized = doc.startsWith('/') ? doc.slice(1) : doc;
    return `${apiClient.baseUrl}${normalized}`;
  }
}

async function loadPublications() {
  loading.value = true;
  error.value = '';
  try {
    const response = await sciencePublishingAPI.listPublications();
    const data = response?.data ?? response;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    publications.value = list;
  } catch (err) {
    error.value = err?.message || 'Не удалось загрузить публикации.';
    toast.error(error.value);
    publications.value = [];
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.value.query = '';
  filters.value.author = '';
  filters.value.kind = '';
  filters.value.subtype = '';
  filters.value.trainingForm = '';
  filters.value.year = '';
}

function openDetail(item) {
  selectedPublication.value = item;
  showDetail.value = true;
}

function closeDetail() {
  showDetail.value = false;
}

onMounted(loadPublications);
</script>

<style scoped>
.published-card {
  border: 1px solid var(--bs-border-color-translucent);
}

.filters-bar input,
.filters-bar select {
  height: 38px;
}

.tiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.pub-tile {
  height: 100%;
  border: 1px solid var(--bs-border-color-translucent);
  cursor: pointer;
}

.pub-tile--active {
  border-color: var(--bs-primary);
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.08);
}

.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.detail-modal {
  width: min(960px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.25rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.75rem 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group-wide {
  grid-column: 1 / -1;
}

.form-control-plain {
  background: var(--bs-light-bg-subtle, #f6f7fb);
  border: 1px solid var(--bs-border-color-translucent);
  color: inherit;
}
</style>
