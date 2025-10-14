<template>
  <div class="science-submit container-fluid py-4">
    <div class="submit-header">
      <div>
        <h2 class="page-title">Формирование документа</h2>
        <p class="page-subtitle">
          Заполните обязательные поля и прикрепите файл публикации. После отправки документ появится в вашем профиле.
        </p>
      </div>
      <button type="button" class="btn btn-outline-secondary" @click="goBack">
        Вернуться к профилю
      </button>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <form class="row g-4" @submit.prevent="submitWork">
          <div class="col-12 col-md-6 col-xl-3">
            <label class="form-label" for="rector_name">Ректор</label>
            <input
              id="rector_name"
              v-model="form.rector_name"
              type="text"
              class="form-control"
              placeholder="Например: Федюнин О. Н."
            />
          </div>

          <div class="col-12 col-md-6 col-xl-3">
            <label class="form-label" for="pages_count">Количество страниц</label>
            <input
              id="pages_count"
              v-model.number="form.pages_count"
              type="number"
              min="1"
              class="form-control"
              placeholder="Укажите число"
            />
          </div>

          <div class="col-12 col-md-6 col-xl-3">
            <label class="form-label" for="year">Год *</label>
            <input
              id="year"
              v-model.number="form.year"
              type="number"
              min="1900"
              max="2100"
              class="form-control"
              required
            />
          </div>

          <div class="col-12 col-md-6 col-xl-3">
            <label class="form-label" for="udc">УДК</label>
            <input
              id="udc"
              v-model="form.udc"
              type="text"
              class="form-control"
              placeholder="Например: 001.891:006.354"
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="discipline_name">Заголовок *</label>
            <input
              id="discipline_name"
              v-model="form.discipline_name"
              type="text"
              class="form-control"
              required
              placeholder="Например: Веб-программирование"
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="bbk">ББК</label>
            <input id="bbk" v-model="form.bbk" type="text" class="form-control" placeholder="Например: 39.71" />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="discipline_topic">Подзаголовок</label>
            <input
              id="discipline_topic"
              v-model="form.discipline_topic"
              type="text"
              class="form-control"
              placeholder="Добавьте уточнение при необходимости"
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="developers">Разработчик(-и)</label>
            <input
              id="developers"
              v-model="form.developers"
              type="text"
              class="form-control"
              placeholder="Укажите исполнителей через запятую"
            />
          </div>

          <div class="col-12 col-xl-4">
            <label class="form-label" for="publication_kind">Вид публикации *</label>
            <select id="publication_kind" v-model="form.publication_kind" class="form-select" required>
              <option disabled value="">Выберите вид</option>
              <option v-for="item in publicationKinds" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </div>

          <div v-if="showGuidelineSubtype" class="col-12 col-xl-4">
            <label class="form-label" for="guideline_subtype">Тип методических указаний *</label>
            <select id="guideline_subtype" v-model="form.guideline_subtype" class="form-select" required>
              <option disabled value="">Выберите тип</option>
              <option v-for="item in guidelineSubtypes" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </div>

          <div class="col-12 col-xl-4">
            <label class="form-label" for="training_form">Форма обучения *</label>
            <select id="training_form" v-model="form.training_form" class="form-select" required>
              <option disabled value="">Выберите форму</option>
              <option v-for="item in trainingForms" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="scientific_editor">Научный редактор (при наличии)</label>
            <input
              id="scientific_editor"
              v-model="form.scientific_editor"
              type="text"
              class="form-control"
              placeholder="Например: Ковальский В. А."
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="computer_layout">Компьютерный набор</label>
            <input
              id="computer_layout"
              v-model="form.computer_layout"
              type="text"
              class="form-control"
              placeholder="Например: Ясников М. А."
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="author_full_name">Полное ФИО автора</label>
            <input
              id="author_full_name"
              v-model="form.author_full_name"
              type="text"
              class="form-control"
              placeholder="Например: Сирота Давид Ильич"
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="co_authors">Соавторы</label>
            <input
              id="co_authors"
              v-model="form.co_authors"
              type="text"
              class="form-control"
              placeholder="Укажите соавторов при наличии"
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="faculty">Факультет</label>
            <input
              id="faculty"
              v-model="form.faculty"
              type="text"
              class="form-control"
              placeholder="Например: ФИТ"
            />
          </div>

          <div class="col-12 col-xl-6">
            <label class="form-label" for="department">Кафедра</label>
            <input
              id="department"
              v-model="form.department"
              type="text"
              class="form-control"
              placeholder="Например: Компьютерные технологии и системы (КТС)"
            />
          </div>

          <div class="col-12">
            <label class="form-label" for="short_description">Краткая информация</label>
            <textarea
              id="short_description"
              v-model="form.short_description"
              class="form-control"
              rows="4"
              placeholder="Введите аннотацию документа"
            ></textarea>
            <div class="form-text text-end">
              Осталось символов: {{ shortDescriptionRemaining }}
            </div>
          </div>

          <div class="col-12">
            <label class="form-label" for="document_file">Файл публикации *</label>
            <input
              id="document_file"
              ref="fileInput"
              type="file"
              class="form-control"
              accept=".pdf,.doc,.docx,.zip"
              required
              @change="onFileChange"
            />
            <div class="form-text">Допустимые форматы: PDF, DOC, DOCX, ZIP.</div>
          </div>

          <div class="col-12 d-flex justify-content-end">
            <button type="submit" class="btn btn-primary px-4" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" />
              {{ isSubmitting ? 'Отправка…' : 'Отправить на рассмотрение' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

import { sciencePublishingAPI } from './js/science-publishing.js';

const SHORT_DESCRIPTION_LIMIT = 400;

const router = useRouter();
const toast = useToast();

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
});

const documentFile = ref(null);
const fileInput = ref(null);
const isSubmitting = ref(false);

const showGuidelineSubtype = computed(() => form.publication_kind === 'method_guidelines');
const shortDescriptionRemaining = computed(
  () => SHORT_DESCRIPTION_LIMIT - (form.short_description?.length ?? 0)
);

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

const onFileChange = (event) => {
  const files = event.target.files;
  documentFile.value = files && files[0] ? files[0] : null;
};

const resetForm = () => {
  Object.assign(form, {
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
  });
  documentFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const goBack = () => {
  router.push({ name: 'SciencePublishingProfile' });
};

const submitWork = async () => {
  if (!form.discipline_name || !form.publication_kind || !form.training_form || !form.year) {
    toast.error('Пожалуйста, заполните обязательные поля.');
    return;
  }

  if (showGuidelineSubtype.value && !form.guideline_subtype) {
    toast.error('Выберите тип методических указаний.');
    return;
  }

  if (!documentFile.value) {
    toast.error('Прикрепите файл публикации.');
    return;
  }

  isSubmitting.value = true;
  try {
    const payload = { ...form };
    if (!payload.pages_count) {
      delete payload.pages_count;
    } else {
      payload.pages_count = Number(payload.pages_count);
    }
    payload.year = Number(payload.year);
    payload.document = documentFile.value;

    await sciencePublishingAPI.createWork(payload);
    toast.success('Документ отправлен на проверку.');
    resetForm();
    router.push({ name: 'SciencePublishingProfile' });
  } catch (error) {
    toast.error(error?.message || 'Не удалось отправить документ. Попробуйте ещё раз.');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped lang="scss">
.science-submit {
  .submit-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .page-title {
    margin-bottom: 0.25rem;
    font-size: 1.875rem;
    font-weight: 600;
  }

  .page-subtitle {
    margin: 0;
    color: var(--bs-secondary-color);
    max-width: 640px;
  }

  .card {
    border-radius: 16px;
  }

  .form-label {
    font-weight: 600;
    color: var(--bs-secondary-color);
  }

  .form-control,
  .form-select {
    border-radius: 12px;
  }

  .form-text {
    color: var(--bs-secondary-color);
  }

  .btn {
    border-radius: 12px;
  }

  @media (max-width: 767px) {
    .submit-header {
      flex-direction: column;
      align-items: stretch;

      .btn {
        width: 100%;
      }
    }

    .d-flex.justify-content-end {
      justify-content: stretch !important;

      .btn {
        width: 100%;
      }
    }
  }
}
</style>
