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

  async listMyDrafts(params = {}) {
    return apiClient.get(this.base.myDrafts, params);
  }

  async listMyPublished(params = {}) {
    return apiClient.get(this.base.myPublished, params);
  }

  async listPublications(params = {}) {
    return apiClient.get(this.base.publications, params);
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

  async updateWork(workId, payload = {}) {
    if (!workId) {
      throw new Error('workId is required');
    }

    if (payload instanceof FormData) {
      return apiClient.patch(`${this.base.works}${workId}/`, payload);
    }

    const form = new FormData();
    Object.entries(payload || {}).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') {
        return;
      }
      form.append(key, value);
    });

    return apiClient.patch(`${this.base.works}${workId}/`, form);
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

  async forcePublish(workId, payload = {}) {
    return apiClient.post(`${this.base.works}${workId}/force-publish/`, payload);
  }

  async listWorkChatMessages(workId) {
    if (!workId) throw new Error('workId is required');
    return apiClient.get(`${this.base.works}${workId}/chat/`);
  }

  async markChatMessagesRead(workId, messageIds = []) {
    if (!workId) throw new Error('workId is required');
    return apiClient.post(`${this.base.works}${workId}/chat/mark-read/`, { message_ids: messageIds });
  }

  async markChatMessagesReadUpTo(workId, messageId) {
    if (!workId) throw new Error('workId is required');
    if (!messageId) throw new Error('messageId is required');
    return apiClient.post(`${this.base.works}${workId}/chat/mark-read-up-to/`, { message_id: messageId });
  }

  async postWorkChatMessage(workId, payload = {}) {
    if (!workId) throw new Error('workId is required');
    return apiClient.post(`${this.base.works}${workId}/chat/`, payload);
  }

  // Compatibility wrappers: task endpoints are now backed by a single chat per work.
  async listTasks(params = {}) {
    const workId = params?.work;
    if (!workId) {
      return { data: [] };
    }
    const [messagesResp, workResp] = await Promise.allSettled([
      this.listWorkChatMessages(workId),
      this.getWork(workId),
    ]);
    const rawMessages =
      messagesResp.status === 'fulfilled'
        ? messagesResp.value?.data ?? messagesResp.value ?? []
        : [];
    const messages = Array.isArray(rawMessages) ? rawMessages : rawMessages?.results ?? [];
    const workData =
      workResp.status === 'fulfilled'
        ? workResp.value?.data ?? workResp.value
        : { id: workId };
    const recipient =
      workData?.current_editor_user_id ||
      workData?.current_editor ||
      workData?.current_editor_id ||
      workData?.current_editor?.id ||
      null;
    const sender = workData?.profile_user_id || null;
    return {
      data: [
        {
          id: workId,
          work: workId,
          subject: workData?.discipline_name || workData?.publication_kind_display || 'Переписка',
          status: workData?.status || 'chat',
          status_display: workData?.status_display || workData?.status,
          recipient,
          sender,
          work_title: workData?.discipline_name,
          work_publication_kind_display: workData?.publication_kind_display,
          work_guideline_subtype_display: workData?.guideline_subtype_display,
          work_training_form_display: workData?.training_form_display,
          work_year: workData?.year,
          work_author_display_name: workData?.profile_display_name,
          work_author_username: workData?.profile_username,
          created_at: messages[0]?.created_at || workData?.created_at,
          updated_at: messages[messages.length - 1]?.created_at || workData?.updated_at,
          messages,
        },
      ],
    };
  }

  async getTask(taskId) {
    if (!taskId) throw new Error('taskId is required');
    const response = await this.listTasks({ work: taskId });
    const list = response?.data ?? response;
    const task =
      (Array.isArray(list) && list[0]) ||
      (Array.isArray(list?.results) && list.results[0]) ||
      list?.[0] ||
      list;
    return { data: task };
  }

  async createTask(payload = {}) {
    if (!payload?.work) {
      throw new Error('work is required to start chat');
    }
    const message = payload.message || payload.subject || '';
    if (message) {
      await this.postWorkChatMessage(payload.work, { content: message });
    }
    return this.listTasks({ work: payload.work });
  }

  async deleteTask() {
    return { data: {} };
  }

  async closeTask(taskId, payload = {}) {
    if (!taskId) return { data: {} };
    if (payload?.message) {
      await this.postWorkChatMessage(taskId, { content: payload.message });
    }
    return this.getTask(taskId);
  }

  async submitTaskForReview(taskId, payload = {}) {
    if (!taskId) return { data: {} };
    if (payload?.message) {
      await this.postWorkChatMessage(taskId, { content: payload.message });
    }
    return this.getTask(taskId);
  }

  async postTaskMessage(taskId, payload = {}) {
    if (!taskId) throw new Error('taskId is required');
    return this.postWorkChatMessage(taskId, payload);
  }

  async updateTask(taskId, payload = {}) {
    if (!taskId) throw new Error('taskId is required');
    if (payload?.message) {
      await this.postWorkChatMessage(taskId, { content: payload.message });
    }
    return this.getTask(taskId);
  }

  async listTaskMessages(taskId) {
    if (!taskId) throw new Error('taskId is required');
    return this.listWorkChatMessages(taskId);
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

  async deleteWork(workId) {
    if (!workId) {
      throw new Error('workId is required');
    }
    return apiClient.delete(`${this.base.works}${workId}/`);
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
