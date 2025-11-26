export default {
  SciencePublishing: {
    name: 'SciencePublishing',
    path: '/science-publishing',
    component: '@/modules/science_publishing/client/ParentLayout.vue',
    redirect: 'SciencePublishingProfile',
    meta: {
      title: 'Science publishing',
      requiresAuth: true,
    },
  },
  SciencePublishingProfile: {
    name: 'SciencePublishingProfile',
    path: '/science-publishing/profile',
    component: '@/modules/science_publishing/client/ProfilePage.vue',
    meta: {
      title: 'Profile',
      requiresAuth: true,
    },
  },
  SciencePublishingSubmit: {
    name: 'SciencePublishingSubmit',
    path: '/science-publishing/submit',
    component: '@/modules/science_publishing/client/WorkSubmitPage.vue',
    meta: {
      title: 'Submit work',
      requiresAuth: true,
    },
  },
  SciencePublishingDevRoles: {
    name: 'SciencePublishingDevRoles',
    path: '/science-publishing/dev-roles',
    component: '@/modules/science_publishing/client/DevRolePage.vue',
    meta: {
      title: 'Roles (dev)',
      requiresAuth: true,
    },
  },
  SciencePublishingTasks: {
    name: 'SciencePublishingTasks',
    path: '/science-publishing/tasks',
    component: '@/modules/science_publishing/client/TasksPage.vue',
    meta: {
      title: 'Tasks',
      requiresAuth: true,
    },
  },
  SciencePublishingAdmin: {
    name: 'SciencePublishingAdmin',
    path: '/science-publishing/admin',
    component: '@/modules/science_publishing/client/AdminPanelPage.vue',
    meta: {
      title: 'Admin',
      requiresAuth: true,
    },
  },
  SciencePublishingDrafts: {
    name: 'SciencePublishingDrafts',
    path: '/science-publishing/drafts',
    component: '@/modules/science_publishing/client/DraftsPage.vue',
    meta: {
      title: 'Drafts',
      requiresAuth: true,
    },
  },
  SciencePublishingPublications: {
    name: 'SciencePublishingPublications',
    path: '/science-publishing/publications',
    component: '@/modules/science_publishing/client/PublicationsPage.vue',
    meta: {
      title: 'Publications',
      requiresAuth: true,
    },
  },
};
