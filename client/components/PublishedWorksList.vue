<template>
  <div class="card shadow-sm published-card">
    <div class="card-body">
      <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3"></div>

      <div class="row g-2 filters-bar mb-3">
        <div class="col-12 col-md-6 col-lg-3">
          <input
            v-model.trim="filters.query"
            type="search"
            class="form-control filter-input"
            placeholder="Поиск по названию, описанию"
          />
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <div class="filter-select-box">
            <select v-model="filters.author" class="form-select filter-select">
              <option value="">Все авторы</option>
              <option v-for="opt in authorOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <div class="filter-select-box">
            <select v-model="filters.kind" class="form-select filter-select">
              <option value="">Все типы</option>
              <option v-for="opt in kindOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <div class="filter-select-box">
            <select v-model="filters.subtype" class="form-select filter-select">
              <option value="">Все подтипы</option>
              <option v-for="opt in subtypeOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="col-6 col-md-3 col-lg-2">
          <div class="filter-select-box">
            <select v-model="filters.trainingForm" class="form-select filter-select">
              <option value="">Любая форма</option>
              <option v-for="opt in trainingOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="col-6 col-md-3 col-lg-1">
          <div class="filter-select-box">
            <select v-model="filters.year" class="form-select filter-select">
              <option value="">Год</option>
              <option v-for="opt in yearOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="col-12 col-md-auto">
          <button type="button" class="btn reset-btn w-100" @click="resetFilters">Сбросить</button>
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
                <strong>Автор:</strong> {{ item.author_full_name || item.profile_display_name || '—' }}
              </div>
              <div class="text-muted small">
                <strong>Подтип:</strong> {{ item.guideline_subtype_display || '—' }}
              </div>
              <div class="text-muted small">
                <strong>Форма обучения:</strong> {{ item.training_form_display || '—' }}
              </div>

              <div class="mt-auto d-flex justify-content-between align-items-center gap-2">
                <span class="badge text-bg-success badge-published">Опубликовано</span>
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
          <span class="badge text-bg-success badge-published">Опубликовано</span>
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
  font-size: 1.02rem;
}

.filters-bar input,
.filters-bar select {
  height: 46px;
}

.filters-bar {
  --filter-bg: #f7f8fb;
  --filter-border: #e1e5ee;
  --filter-shadow: 0 8px 30px -18px rgba(15, 23, 42, 0.35);
}

.filter-input,
.filter-select {
  background: var(--filter-bg);
  border: 1px solid var(--filter-border);
  border-radius: 12px;
  padding: 0.55rem 0.9rem;
  min-height: 46px;
  box-shadow: var(--filter-shadow);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  font-size: 1rem;
  font-weight: 600;
}

.filter-input:focus,
.filter-select:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 10px 36px -18px rgba(13, 110, 253, 0.35);
  background: #fff;
}

.filter-select-box {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 10px 28px -18px rgba(15, 23, 42, 0.3);
  background: linear-gradient(180deg, #f9fbff 0%, #f4f6fb 100%);
}

.filter-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding-right: 2.4rem;
  color: #1f2937;
  border: 1px solid #d5d9e3;
  background: linear-gradient(180deg, #f9fbff 0%, #f4f6fb 100%);
  border-radius: 14px;
  box-shadow: none;
  height: 100%;
}

.filter-select:focus {
  border-color: #c0c8d8;
  box-shadow: 0 12px 32px -18px rgba(13, 110, 253, 0.25);
}

.filter-select::-ms-expand {
  display: none;
}

.filter-select-box::after {
  content: '';
  position: absolute;
  right: 14px;
  top: 50%;
  width: 10px;
  height: 10px;
  border: 2px solid #4b5563;
  border-top: none;
  border-left: none;
  transform: translateY(-50%) rotate(45deg);
  pointer-events: none;
  transition: transform 0.18s ease, border-color 0.18s ease;
}

.filter-select-box:focus-within::after {
  transform: translateY(-50%) rotate(225deg);
  border-color: var(--bs-primary);
}

.filter-select option {
  background: #f7f9fc;
  color: #0f172a;
  padding: 0.65rem 0.9rem;
  font-size: 1rem;
  border-radius: 10px;
  margin: 4px;
}

.filter-select option:hover,
.filter-select option:checked,
.filter-select option:focus {
  background: #e8f0ff;
  color: #0b162f;
  font-weight: 700;
}

.reset-btn {
  border-radius: 12px;
  border: 1px solid rgba(224, 49, 49, 0.45);
  color: #c01e1e;
  background: rgba(224, 49, 49, 0.1);
  font-weight: 700;
  padding: 0.55rem 1rem;
}

.reset-btn:hover:not(:disabled),
.reset-btn:focus-visible:not(:disabled) {
  border-color: rgba(224, 49, 49, 0.65);
  background: rgba(224, 49, 49, 0.16);
  color: #a01717;
}

.reset-btn:disabled {
  opacity: 0.55;
}

.tiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.pub-tile {
  height: 100%;
  border: 1px solid rgba(15, 23, 42, 0.08);
  cursor: pointer;
  font-size: 1rem;
  border-radius: 16px;
  box-shadow: 0 18px 50px -38px rgba(15, 23, 42, 0.32);
  transition: transform 0.14s ease, box-shadow 0.14s ease, border-color 0.14s ease;
}

.pub-tile--active {
  border-color: rgba(224, 49, 49, 0.45);
  box-shadow: 0 20px 60px -40px rgba(224, 49, 49, 0.6);
  transform: translateY(-2px);
}

.pub-tile h6 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #1f2937;
}

.pub-tile .text-muted {
  font-size: 0.95rem;
  color: #4b5563 !important;
}

.pub-tile .badge {
  border-radius: 999px;
  font-weight: 700;
}

.pub-tile .card-body {
  padding: 1.4rem 1.25rem 1.2rem;
  gap: 0.4rem;
}

.pub-tile .btn.btn-outline-primary.btn-sm {
  border-radius: 999px;
  padding: 0.35rem 0.9rem;
  font-weight: 700;
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

.badge-published {
  font-size: 0.95rem;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
}

.detail-modal h5 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  margin-bottom: 0.2rem;
}

.detail-modal .text-muted.small {
  font-size: 1.08rem;
  color: #6b7280 !important;
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

.detail-modal .form-label {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0;
}

.form-control-plain {
  background: var(--bs-light-bg-subtle, #f6f7fb);
  border: 1px solid var(--bs-border-color-translucent);
  color: inherit;
  font-size: 1.05rem;
  font-weight: 400;
}
</style>
