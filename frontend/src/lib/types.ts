export interface SessionInfo {
	session_active: boolean;
	formats: Record<string, string>;
	languages: string[];
	has_session: boolean;
}

export interface ReviewResult {
	score: number;
	status: 'ok' | 'warning' | 'error';
	issues: ReviewIssue[];
	summary: string;
}

export interface ReviewIssue {
	segment_index: number;
	type: 'terminology' | 'untranslated' | 'mistranslation' | 'formatting';
	detail: string;
}

export interface Job {
	job_id: string;
	status: 'processing' | 'completed' | 'failed';
	filename: string;
	error: string | null;
	review: ReviewResult | null;
}
