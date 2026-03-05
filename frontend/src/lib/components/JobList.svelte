<script lang="ts">
	import type { Job } from '$lib/types';
	import JobItem from './JobItem.svelte';

	let { jobs, onRefresh }: { jobs: Job[]; onRefresh: () => void } = $props();
</script>

{#if jobs.length > 0}
	<div class="job-list">
		<h2>Queue</h2>
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
		color: var(--text-muted);
		font-size: 0.7rem;
		margin: 0 0 0.6rem 0;
		font-weight: 400;
		font-family: var(--font-display);
		text-transform: uppercase;
		letter-spacing: 0.12em;
	}

	.jobs {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
</style>
