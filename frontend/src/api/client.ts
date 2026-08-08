const PRODUCTION_RAILWAY_URL = 'https://ai-visibility-platform-production-4b8b.up.railway.app';

const getBaseUrl = (): string => {
  const rawUrl = import.meta.env.VITE_API_URL || '';
  const cleanUrl = rawUrl.trim().replace(/\/+$/, '');
  if (cleanUrl) return `${cleanUrl}/api/v1`;

  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') {
      return '/api/v1';
    }
  }
  return `${PRODUCTION_RAILWAY_URL}/api/v1`;
};

const BASE_URL = getBaseUrl();

export interface Project {
  id: string;
  name: string;
  domain: string;
  created_at: string;
}

export interface AnalysisJob {
  id: string;
  project_id: string;
  status: 'Pending' | 'Queued' | 'Running' | 'Completed' | 'Failed' | 'Cancelled';
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobReport {
  job_id: string;
  project_id: string;
  project_name: string;
  target_domain: string;
  job_status: string;
  provider_name: string;
  prompt: string;
  raw_response: string;
  mentioned: boolean;
  raw_citations: string[];
  matched_snippets: string[];
  extracted_brand_mentions: string[];
  created_at: string;
}

export interface ContradictionDetail {
  mentioned_prompt_id: string;
  mentioned_prompt_category: string;
  omitted_prompt_id: string;
  omitted_prompt_category: string;
  description: string;
}

export interface EvaluationSummary {
  job_id: string;
  total_prompts: number;
  successful_executions: number;
  mentioned_count: number;
  mention_rate: number;
  provider_count: number;
  prompt_categories_tested: string[];
  consistency_percentage: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  contradictions: ContradictionDetail[];
  generated_at: string;
}

export const api = {
  async createProject(name: string, url: string): Promise<Project> {
    const res = await fetch(`${BASE_URL}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, url }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to create project' }));
      if (res.status === 409) {
        try {
          const listRes = await fetch(`${BASE_URL}/projects`);
          if (listRes.ok) {
            const projects: Project[] = await listRes.json();
            const host = url.replace(/https?:\/\//i, '').replace(/\/.*$/, '').replace('www.', '').toLowerCase();
            const match = projects.find(p => p.domain.toLowerCase() === host || host.includes(p.domain.toLowerCase()));
            if (match) return match;
          }
        } catch {
          // Fall through
        }
      }
      throw new Error(err.detail || 'Failed to create project');
    }
    return res.json();
  },

  async triggerJob(projectId: string): Promise<AnalysisJob> {
    const res = await fetch(`${BASE_URL}/projects/${projectId}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to trigger analysis job' }));
      if (res.status === 409) {
        try {
          const jobs = await this.listJobsForProject(projectId);
          const active = jobs.find(j => j.status === 'Pending' || j.status === 'Running' || j.status === 'Queued');
          if (active) return active;
          if (jobs.length > 0) return jobs[0];
        } catch {
          // Fall through
        }
      }
      throw new Error(err.detail || 'Failed to trigger analysis job');
    }
    return res.json();
  },

  async getJob(jobId: string): Promise<AnalysisJob> {
    const res = await fetch(`${BASE_URL}/jobs/${jobId}?_t=${Date.now()}`, {
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
      },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch job status' }));
      throw new Error(err.detail || 'Failed to fetch job status');
    }
    return res.json();
  },

  async executeJob(jobId: string, prompt?: string, providerName?: string): Promise<any> {
    const params = new URLSearchParams();
    if (prompt) params.append('prompt', prompt);
    if (providerName) params.append('provider_name', providerName);

    const res = await fetch(`${BASE_URL}/jobs/${jobId}/execute?${params.toString()}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to execute job' }));
      throw new Error(err.detail || 'Failed to execute job');
    }
    return res.json();
  },

  async getJobReport(jobId: string): Promise<JobReport> {
    const res = await fetch(`${BASE_URL}/jobs/${jobId}/report`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch job report' }));
      throw new Error(err.detail || 'Failed to fetch job report');
    }
    return res.json();
  },

  async getEvaluationSummary(jobId: string): Promise<EvaluationSummary> {
    const res = await fetch(`${BASE_URL}/jobs/${jobId}/evaluation`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch evaluation summary' }));
      throw new Error(err.detail || 'Failed to fetch evaluation summary');
    }
    return res.json();
  },

  async listProjects(): Promise<Project[]> {
    const res = await fetch(`${BASE_URL}/projects`);
    if (!res.ok) {
      throw new Error('Failed to fetch projects list');
    }
    return res.json();
  },

  async listJobsForProject(projectId: string): Promise<AnalysisJob[]> {
    const res = await fetch(`${BASE_URL}/projects/${projectId}/jobs`);
    if (!res.ok) {
      throw new Error('Failed to fetch jobs for project');
    }
    return res.json();
  },
};
