import type { SessionInfo, Job, TranslateResponse } from './types';

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE}${path}`, {
		credentials: 'include',
		...options
	});
	if (!res.ok) {
		const body = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(body.detail || 'Request failed');
	}
	return res.json();
}

export async function getSession(): Promise<SessionInfo> {
	return request<SessionInfo>('/session');
}

export async function uploadFile(
	file: File,
	sourceLang: string,
	targetLang: string,
	instructions: string
): Promise<TranslateResponse> {
	const form = new FormData();
	form.append('file', file);
	form.append('source_lang', sourceLang);
	form.append('target_lang', targetLang);
	form.append('instructions', instructions);

	return request<TranslateResponse>('/translate', {
		method: 'POST',
		body: form
	});
}

export async function getJobs(): Promise<Job[]> {
	const res = await request<{ jobs: Job[] }>('/jobs');
	return res.jobs;
}

export async function deleteJob(jobId: string): Promise<void> {
	await request(`/jobs/${jobId}`, { method: 'DELETE' });
}

export function getDownloadUrl(jobId: string): string {
	return `${BASE}/jobs/${jobId}/download`;
}

export async function uploadGlossary(file: File): Promise<void> {
	const form = new FormData();
	form.append('file', file);
	await request('/glossary', { method: 'POST', body: form });
}

export async function deleteGlossary(): Promise<void> {
	await request('/glossary', { method: 'DELETE' });
}
