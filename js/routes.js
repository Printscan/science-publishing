export default {
  SciencePublishing: {
    name: 'SciencePublishing',
    path: '/science-publishing',
    component: '@/modules/science-publishing/ParentLayout.vue',
    redirect: 'SciencePublishingProfile',
    meta: {
      title: 'Научные публикации',
      requiresAuth: true,
    },
  },
  SciencePublishingProfile: {
    name: 'SciencePublishingProfile',
    path: '/science-publishing/profile',
    component: '@/modules/science-publishing/ProfilePage.vue',
    meta: {
      title: 'Профиль редакции',
      requiresAuth: true,
    },
  },
  SciencePublishingSubmit: {
    name: 'SciencePublishingSubmit',
    path: '/science-publishing/submit',
    component: '@/modules/science-publishing/WorkSubmitPage.vue',
    meta: {
      title: 'Подача работы',
      requiresAuth: true,
    },
  },
  SciencePublishingDevRoles: {
    name: 'SciencePublishingDevRoles',
    path: '/science-publishing/dev-roles',
    component: '@/modules/science-publishing/DevRolePage.vue',
    meta: {
      title: 'Управление ролями (DEV)',
      requiresAuth: true,
    },
  },
  SciencePublishingTasks: {
    name: 'SciencePublishingTasks',
    path: '/science-publishing/tasks',
    component: '@/modules/science-publishing/TasksPage.vue',
    meta: {
      title: 'Задачи редакции',
      requiresAuth: true,
    },
  },
  SciencePublishingAdmin: {
    name: 'SciencePublishingAdmin',
    path: '/science-publishing/admin',
    component: '@/modules/science-publishing/AdminPanelPage.vue',
    meta: {
      title: 'Администрирование',
      requiresAuth: true,
    },
  },
  SciencePublishingDrafts: {
    name: 'SciencePublishingDrafts',
    path: '/science-publishing/drafts',
    component: '@/modules/science-publishing/DraftsPage.vue',
    meta: {
      title: 'Черновики',
      requiresAuth: true,
    },
  },
};

