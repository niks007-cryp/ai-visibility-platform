const BASE_URL = '/api/v1';

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
      throw new Error(err.detail || 'Failed to trigger analysis job');
    }
    return res.json();
  },

  async getJob(jobId: string): Promise<AnalysisJob> {
    const res = await fetch(`${BASE_URL}/jobs/${jobId}`);
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
};
