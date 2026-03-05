export interface SessionInfo {
	session_active: boolean;
	formats: Record<string, string>;
	languages: string[];
	has_session: boolean;
}

export interface Job {
	job_id: string;
	status: 'queued' | 'processing' | 'completed' | 'failed';
	filename: string;
	error: string | null;
}

export interface TranslateResponse {
	job_id: string;
	task_id: string;
	filename: string;
	status: string;
}
