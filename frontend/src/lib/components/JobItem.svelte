<script lang="ts">
	import type { Job } from '$lib/types';
	import { getDownloadUrl, deleteJob } from '$lib/api';

	let { job, onRemove }: { job: Job; onRemove: () => void } = $props();

	const statusConfig: Record<string, { color: string; label: string; icon: string }> = {
		queued: { color: 'var(--text-muted)', label: 'Queued', icon: 'M12 6v6l4 2' },
		processing: { color: 'var(--accent)', label: 'Translating', icon: 'M12 6v6l4 2' },
		completed: { color: 'var(--success)', label: 'Done', icon: 'M20 6L9 17l-5-5' },
		failed: { color: 'var(--danger)', label: 'Failed', icon: 'M18 6L6 18M6 6l12 12' },
	};

	const config = $derived(statusConfig[job.status] || statusConfig.queued);

	async function handleRemove() {
		await deleteJob(job.job_id);
		onRemove();
	}
</script>

<div class="job-item" class:completed={job.status === 'completed'}>
	<div class="job-left">
		<div class="status-dot" style="background: {config.color}"></div>
		<div class="job-meta">
			<span class="job-filename">{job.filename}</span>
			<span class="job-status" style="color: {config.color}">{config.label}</span>
		</div>
	</div>

	<div class="job-actions">
		{#if job.status === 'completed'}
			<a href={getDownloadUrl(job.job_id)} class="download-btn" download>
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="7 10 12 15 17 10" />
					<line x1="12" y1="15" x2="12" y2="3" />
				</svg>
				Download
			</a>
		{/if}
		{#if job.error}
			<span class="error-text" title={job.error}>Error</span>
		{/if}
		<button class="remove-btn" onclick={handleRemove} title="Remove">
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
				<path d="M18 6L6 18M6 6l12 12" />
			</svg>
		</button>
	</div>

	{#if job.status === 'processing'}
		<div class="progress-track">
			<div class="progress-fill"></div>
		</div>
	{/if}
</div>

<style>
	.job-item {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		padding: 0.7rem 0.9rem;
		background: var(--bg-input);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		gap: 0.5rem;
		transition: border-color 0.2s;
	}

	.job-item.completed {
		border-color: rgba(90, 232, 160, 0.15);
	}

	.job-left {
		display: flex;
		align-items: center;
		gap: 0.65rem;
		min-width: 0;
	}

	.status-dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.job-meta {
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
		min-width: 0;
	}

	.job-filename {
		color: var(--text-primary);
		font-size: 0.88rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.job-status {
		font-size: 0.72rem;
		font-family: var(--font-display);
		font-weight: 400;
		letter-spacing: 0.03em;
		text-transform: uppercase;
		white-space: nowrap;
	}

	.job-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.download-btn {
		padding: 0.3rem 0.65rem;
		border-radius: 6px;
		background: var(--accent);
		color: var(--bg-deep);
		text-decoration: none;
		font-size: 0.78rem;
		font-weight: 500;
		font-family: var(--font-body);
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.3rem;
	}

	.download-btn:hover {
		filter: brightness(1.1);
		transform: translateY(-1px);
	}

	.error-text {
		color: var(--danger);
		font-size: 0.75rem;
		cursor: help;
	}

	.remove-btn {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.15rem;
		display: flex;
		transition: color 0.2s;
	}

	.remove-btn:hover {
		color: var(--danger);
	}

	.progress-track {
		width: 100%;
		height: 2px;
		background: var(--border);
		border-radius: 1px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: var(--accent);
		border-radius: 1px;
		animation: indeterminate 1.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
	}

	@keyframes indeterminate {
		0% { width: 0%; margin-left: 0%; }
		50% { width: 50%; margin-left: 25%; }
		100% { width: 0%; margin-left: 100%; }
	}
</style>
