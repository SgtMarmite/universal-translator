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
	let mounted = $state(false);

	onMount(async () => {
		mounted = true;
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

<div class="page" class:visible={mounted}>
	<div class="noise"></div>

	<main>
		<div class="container">
			<header>
				<div class="logo-mark">
					<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="12" cy="12" r="10" />
						<path d="M2 12h20" />
						<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
					</svg>
				</div>
				<h1>Universal Translator</h1>
				<p class="subtitle">Translate documents. Preserve formatting. Any language.</p>
			</header>

			{#if session}
				<div class="card">
					<DropZone onFileDrop={handleFileDrop} formats={session.formats} />

					<div class="divider"></div>

					<LanguageSelect
						languages={session.languages}
						bind:sourceLang
						bind:targetLang
					/>

					<Instructions bind:instructions />

					{#if uploading}
						<div class="status-msg uploading">
							<div class="spinner"></div>
							Uploading...
						</div>
					{/if}

					{#if error}
						<div class="status-msg error">{error}</div>
					{/if}
				</div>

				<JobList {jobs} onRefresh={refreshJobs} />
			{:else}
				<div class="loading">
					<div class="spinner"></div>
				</div>
			{/if}

			<footer>
				<span class="provider-badge">LLM: Azure OpenAI</span>
			</footer>
		</div>
	</main>
</div>

<style>
	:root {
		--bg-deep: #0c0c14;
		--bg-card: rgba(18, 18, 30, 0.7);
		--bg-input: rgba(28, 28, 48, 0.6);
		--border: rgba(255, 255, 255, 0.06);
		--border-hover: rgba(255, 255, 255, 0.12);
		--text-primary: #eaeaf0;
		--text-secondary: #7a7a96;
		--text-muted: #4e4e6a;
		--accent: #e8a846;
		--accent-dim: rgba(232, 168, 70, 0.15);
		--accent-glow: rgba(232, 168, 70, 0.08);
		--danger: #e85555;
		--success: #5ae8a0;
		--radius: 16px;
		--radius-sm: 10px;
		--font-display: 'Sora', sans-serif;
		--font-body: 'DM Sans', sans-serif;
	}

	:global(*) {
		box-sizing: border-box;
	}

	:global(body) {
		margin: 0;
		font-family: var(--font-body);
		background: var(--bg-deep);
		color: var(--text-primary);
		min-height: 100vh;
		-webkit-font-smoothing: antialiased;
	}

	.page {
		opacity: 0;
		transition: opacity 0.6s ease;
	}

	.page.visible {
		opacity: 1;
	}

	.noise {
		position: fixed;
		inset: 0;
		z-index: 0;
		pointer-events: none;
		opacity: 0.03;
		background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
		background-repeat: repeat;
		background-size: 256px;
	}

	main {
		position: relative;
		z-index: 1;
		min-height: 100vh;
		display: flex;
		justify-content: center;
		padding: 3rem 1.25rem 2rem;
	}

	.container {
		width: 100%;
		max-width: 580px;
		display: flex;
		flex-direction: column;
		gap: 1.75rem;
	}

	header {
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.logo-mark {
		color: var(--accent);
		margin-bottom: 0.25rem;
	}

	h1 {
		font-family: var(--font-display);
		font-size: 1.75rem;
		font-weight: 700;
		margin: 0;
		letter-spacing: -0.03em;
		color: var(--text-primary);
	}

	.subtitle {
		color: var(--text-secondary);
		margin: 0;
		font-size: 0.95rem;
		font-weight: 400;
		letter-spacing: 0.01em;
	}

	.card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 1.75rem;
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}

	.divider {
		height: 1px;
		background: var(--border);
		margin: 0.25rem 0;
	}

	.status-msg {
		font-size: 0.85rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 0.85rem;
		border-radius: var(--radius-sm);
	}

	.status-msg.uploading {
		color: var(--accent);
		background: var(--accent-dim);
	}

	.status-msg.error {
		color: var(--danger);
		background: rgba(232, 85, 85, 0.1);
	}

	.spinner {
		width: 14px;
		height: 14px;
		border: 2px solid transparent;
		border-top-color: currentColor;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}

	.loading {
		display: flex;
		justify-content: center;
		padding: 3rem 0;
		color: var(--text-muted);
	}

	.loading .spinner {
		width: 24px;
		height: 24px;
	}

	footer {
		display: flex;
		justify-content: center;
		padding-top: 0.5rem;
	}

	.provider-badge {
		font-size: 0.7rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-family: var(--font-display);
		font-weight: 400;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
