<script lang="ts">
	import type { Job } from '$lib/types';
	import { getDownloadUrl, deleteJob } from '$lib/api';

	let { job, onRemove }: { job: Job; onRemove: () => void } = $props();

	const statusColors: Record<string, string> = {
		queued: '#ecc94b',
		processing: '#667eea',
		completed: '#68d391',
		failed: '#fc8181'
	};

	const statusLabels: Record<string, string> = {
		queued: 'Queued',
		processing: 'Translating...',
		completed: 'Done',
		failed: 'Failed'
	};

	async function handleRemove() {
		await deleteJob(job.job_id);
		onRemove();
	}
</script>

<div class="job-item">
	<div class="job-info">
		<span class="job-filename">{job.filename}</span>
		<span class="job-status" style="color: {statusColors[job.status]}">
			{statusLabels[job.status]}
		</span>
	</div>

	<div class="job-actions">
		{#if job.status === 'completed'}
			<a href={getDownloadUrl(job.job_id)} class="download-btn" download>Download</a>
		{/if}
		{#if job.error}
			<span class="error-text" title={job.error}>Error</span>
		{/if}
		<button class="remove-btn" onclick={handleRemove} title="Remove">&#10005;</button>
	</div>

	{#if job.status === 'processing'}
		<div class="progress-bar">
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
		padding: 0.75rem 1rem;
		background: #2d3748;
		border-radius: 8px;
		gap: 0.5rem;
	}

	.job-info {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.job-filename {
		color: #e2e8f0;
		font-size: 0.95rem;
	}

	.job-status {
		font-size: 0.85rem;
		font-weight: 500;
	}

	.job-actions {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.download-btn {
		padding: 0.35rem 0.75rem;
		border-radius: 6px;
		background: #667eea;
		color: white;
		text-decoration: none;
		font-size: 0.85rem;
		transition: background 0.2s;
	}

	.download-btn:hover {
		background: #5a67d8;
	}

	.error-text {
		color: #fc8181;
		font-size: 0.8rem;
		cursor: help;
	}

	.remove-btn {
		background: none;
		border: none;
		color: #718096;
		cursor: pointer;
		font-size: 1rem;
		padding: 0.2rem;
	}

	.remove-btn:hover {
		color: #fc8181;
	}

	.progress-bar {
		width: 100%;
		height: 3px;
		background: #4a5568;
		border-radius: 2px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: #667eea;
		border-radius: 2px;
		animation: indeterminate 1.5s ease-in-out infinite;
	}

	@keyframes indeterminate {
		0% {
			width: 0%;
			margin-left: 0%;
		}
		50% {
			width: 60%;
			margin-left: 20%;
		}
		100% {
			width: 0%;
			margin-left: 100%;
		}
	}
</style>
