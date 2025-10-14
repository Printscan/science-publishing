import { apiClient } from '@/js/api/manager.js';
import { endpoints } from '@/js/api/endpoints.js';

class SciencePublishingAPI {
  constructor() {
    this.base = endpoints.science_publishing || {};
  }

  async getCurrentProfile() {
    return apiClient.get(this.base.profileMe);
  }

  async updateCurrentProfile(payload) {
    return apiClient.patch(this.base.profileMe, payload);
  }

  async listRoles(params = {}) {
    return apiClient.get(this.base.roles, params);
  }

  async listWorks(params = {}) {
    return apiClient.get(this.base.works, params);
  }

  async listMyWorks(params = {}) {
    return apiClient.get(this.base.myWorks, params);
  }

  async createWork(payload = {}) {
    const form = new FormData();
    const directFields = [
      'discipline_name',
      'discipline_topic',
      'publication_kind',
      'guideline_subtype',
      'training_form',
      'year',
      'pages_count',
      'rector_name',
      'developers',
      'scientific_editor',
      'computer_layout',
      'co_authors',
      'faculty',
      'department',
      'short_description',
      'author_full_name',
      'udc',
      'bbk',
    ];

    directFields.forEach((field) => {
      if (payload[field] !== undefined && payload[field] !== null && payload[field] !== '') {
        form.append(field, payload[field]);
      }
    });

    if (payload.document instanceof Blob) {
      form.append('document', payload.document);
    }

    return apiClient.post(this.base.works, form);
  }

  async assignWorkEditor(workId, payload = {}) {
    return apiClient.post(`${this.base.works}${workId}/assign-editor/`, payload);
  }

  async requestWorkChanges(workId, payload = {}) {
    return apiClient.post(`${this.base.works}${workId}/request-changes/`, payload);
  }

  async submitWorkCorrections(workId, payload = {}) {
    if (payload instanceof FormData) {
      return apiClient.post(`${this.base.works}${workId}/submit-corrections/`, payload);
    }

    const form = new FormData();
    Object.entries(payload || {}).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') {
        return;
      }
      if (value instanceof Blob) {
        form.append(key, value);
      } else {
        form.append(key, value);
      }
    });

    return apiClient.post(`${this.base.works}${workId}/submit-corrections/`, form);
  }

  async approveWorkAsEditor(workId, payload = {}) {
    return apiClient.post(`${this.base.works}${workId}/editor-approve/`, payload);
  }

  async approveWorkAsChief(workId, payload = {}) {
    return apiClient.post(`${this.base.works}${workId}/chief-approve/`, payload);
  }

  async listTasks(params = {}) {
    return apiClient.get(this.base.tasks, params);
  }

  async getTask(taskId) {
    return apiClient.get(`${this.base.tasks}${taskId}/`);
  }

  async createTask(payload = {}) {
    return apiClient.post(this.base.tasks, payload);
  }

  async deleteTask(taskId) {
    return apiClient.delete(`${this.base.tasks}${taskId}/`);
  }

  async postTaskMessage(taskId, payload = {}) {
    return apiClient.post(`${this.base.tasks}${taskId}/messages/`, payload);
  }

  async updateTask(taskId, payload = {}) {
    return apiClient.patch(`${this.base.tasks}${taskId}/`, payload);
  }

  async listTaskMessages(taskId) {
    return apiClient.get(`${this.base.tasks}${taskId}/messages/`);
  }

  async fetchProfileByUsername(username) {
    const params = {};
    if (username) {
      params.search = username;
    }
    return apiClient.get(this.base.profiles, params);
  }

  async listProfiles(params = {}) {
    return apiClient.get(this.base.profiles, params);
  }

  async getWork(workId) {
    if (!workId) {
      throw new Error('workId is required');
    }
    return apiClient.get(`${this.base.works}${workId}/`);
  }

  async getProfile(profileId) {
    if (!profileId) {
      throw new Error('profileId is required');
    }
    return apiClient.get(`${this.base.profiles}${profileId}/`);
  }

  async assignRole(profileId, roleId) {
    return apiClient.post(this.base.profileRoles, {
      profile: profileId,
      role: roleId,
    });
  }

  async removeRole(assignmentId) {
    const endpoint = `${this.base.profileRoles}${assignmentId}/`;
    return apiClient.delete(endpoint);
  }
}

export const sciencePublishingAPI = new SciencePublishingAPI();
