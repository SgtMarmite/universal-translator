<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { SessionInfo, Job } from '$lib/types';
	import { getSession, uploadFile, getJobs } from '$lib/api';
	import DropZone from '$lib/components/DropZone.svelte';
	import LanguageSelect from '$lib/components/LanguageSelect.svelte';
	import Instructions from '$lib/components/Instructions.svelte';
	import JobList from '$lib/components/JobList.svelte';

	let session = $state<SessionInfo | null>(null);
	let jobs = $state<Job[]>([]);
	let sourceLang = $state('auto');
	let targetLang = $state('english');
	let instructions = $state('');
	let uploading = $state(false);
	let error = $state<string | null>(null);
	let pollInterval: ReturnType<typeof setInterval>;

	onMount(async () => {
		session = await getSession();
		await refreshJobs();
		pollInterval = setInterval(refreshJobs, 2000);
	});

	onDestroy(() => {
		if (pollInterval) clearInterval(pollInterval);
	});

	async function refreshJobs() {
		try {
			jobs = await getJobs();
		} catch {
			// session not ready yet
		}
	}

	async function handleFileDrop(file: File) {
		if (!session) return;

		const ext = '.' + file.name.split('.').pop()?.toLowerCase();
		if (!session.formats[ext]) {
			error = `Unsupported format: ${ext}`;
			return;
		}

		error = null;
		uploading = true;

		try {
			await uploadFile(file, sourceLang, targetLang, instructions);
			await refreshJobs();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Upload failed';
		} finally {
			uploading = false;
		}
	}
</script>

<main>
	<div class="container">
		<header>
			<h1>Universal Translator</h1>
			<p class="subtitle">Drop a file, pick your languages, get it translated.</p>
		</header>

		{#if session}
			<div class="upload-section">
				<DropZone onFileDrop={handleFileDrop} formats={session.formats} />

				<LanguageSelect
					languages={session.languages}
					bind:sourceLang
					bind:targetLang
				/>

				<Instructions bind:instructions />

				{#if uploading}
					<p class="uploading">Uploading...</p>
				{/if}

				{#if error}
					<p class="error">{error}</p>
				{/if}
			</div>

			<div class="queue-section">
				<JobList {jobs} onRefresh={refreshJobs} />
			</div>
		{:else}
			<p class="loading">Loading...</p>
		{/if}
	</div>
</main>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		background: #0f0f23;
		color: #e2e8f0;
		min-height: 100vh;
	}

	main {
		min-height: 100vh;
		display: flex;
		justify-content: center;
		padding: 2rem 1rem;
	}

	.container {
		width: 100%;
		max-width: 640px;
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	header {
		text-align: center;
	}

	h1 {
		font-size: 2rem;
		font-weight: 700;
		margin: 0;
		background: linear-gradient(135deg, #667eea, #764ba2);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		color: #718096;
		margin: 0.5rem 0 0 0;
		font-size: 1rem;
	}

	.upload-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.25rem;
	}

	.queue-section {
		width: 100%;
	}

	.uploading {
		color: #667eea;
		font-size: 0.9rem;
		margin: 0;
	}

	.error {
		color: #fc8181;
		font-size: 0.9rem;
		margin: 0;
	}

	.loading {
		text-align: center;
		color: #718096;
	}
</style>
