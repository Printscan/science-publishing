<template>
  <div class="publications container-fluid py-4">
    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
      <div>
        <h2 class="page-title mb-0">Публикации</h2>
        <p class="text-muted mb-0">Список опубликованных работ с подробностями и скачиванием файла.</p>
      </div>
    </div>

    <PublishedWorksList />
  </div>
</template>

<script setup>
import PublishedWorksList from './components/PublishedWorksList.vue';
</script>
