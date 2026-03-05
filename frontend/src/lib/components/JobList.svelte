<script lang="ts">
	import type { Job } from '$lib/types';
	import JobItem from './JobItem.svelte';

	let { jobs, onRefresh }: { jobs: Job[]; onRefresh: () => void } = $props();
</script>

{#if jobs.length > 0}
	<div class="job-list">
		<h2>Translation Queue</h2>
		<div class="jobs">
			{#each jobs as job (job.job_id)}
				<JobItem {job} onRemove={onRefresh} />
			{/each}
		</div>
	</div>
{/if}

<style>
	.job-list {
		width: 100%;
	}

	h2 {
		color: #e2e8f0;
		font-size: 1.1rem;
		margin: 0 0 0.75rem 0;
		font-weight: 500;
	}

	.jobs {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
</style>
