import { ref } from 'vue';
import { sciencePublishingAPI } from './science-publishing.js';

const ROUTE_ROLE_MAP = {
  SciencePublishingProfile: ['author', 'editor', 'chief_editor', 'administrator', 'reviewer'],
  SciencePublishingSubmit: ['author', 'editor', 'chief_editor', 'administrator', 'reviewer'],
  SciencePublishingDrafts: ['author', 'editor', 'chief_editor', 'administrator', 'reviewer'],
  SciencePublishingPublications: ['author', 'editor', 'chief_editor', 'administrator', 'reviewer'],
  SciencePublishingTasks: ['editor', 'chief_editor'],
  SciencePublishingAdmin: ['administrator'],
};

let cachedRoles = null;
let pending = null;

async function fetchRoles() {
  if (cachedRoles) return cachedRoles;
  if (pending) return pending;
  pending = sciencePublishingAPI
    .getCurrentProfile()
    .then((resp) => {
      const data = resp?.data ?? resp ?? {};
      const roles = Array.isArray(data.roles) ? data.roles : data.role_assignments || [];
      cachedRoles = roles
        .map((r) => r.code || r.role?.code)
        .filter(Boolean);
      return cachedRoles;
    })
    .catch(() => {
      cachedRoles = null;
      return [];
    })
    .finally(() => {
      pending = null;
    });
  return pending;
}

export async function getScienceRoles() {
  return fetchRoles();
}

export function isScienceRouteAllowed(routeName, roles = null) {
  const routeRoles = ROUTE_ROLE_MAP[routeName];
  if (!routeRoles) return true;
  const list = Array.isArray(roles) ? roles : cachedRoles;
  if (!list || list.length === 0) return false;
  return list.some((code) => routeRoles.includes(code));
}

export function useScienceAccess(requiredRoute) {
  const roles = ref(cachedRoles || []);
  const loading = ref(!cachedRoles);
  const error = ref('');
  const allowed = ref(false);

  const ensure = async () => {
    loading.value = true;
    try {
      roles.value = await getScienceRoles();
      allowed.value = isScienceRouteAllowed(requiredRoute, roles.value);
    } catch (err) {
      error.value = err?.message || 'Не удалось проверить доступ.';
      allowed.value = false;
    } finally {
      loading.value = false;
    }
  };

  // если роли уже были закэшированы
  if (cachedRoles) {
    allowed.value = isScienceRouteAllowed(requiredRoute, cachedRoles);
  }

  return {
    roles,
    loading,
    error,
    allowed,
    ensure,
    canView: (route) => isScienceRouteAllowed(route, roles.value),
  };
}
