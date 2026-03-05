<script lang="ts">
	let {
		languages,
		sourceLang = $bindable('auto'),
		targetLang = $bindable('english')
	}: {
		languages: string[];
		sourceLang: string;
		targetLang: string;
	} = $props();

	function capitalize(s: string): string {
		return s.charAt(0).toUpperCase() + s.slice(1);
	}

	function swap() {
		if (sourceLang === 'auto') return;
		const tmp = sourceLang;
		sourceLang = targetLang;
		targetLang = tmp;
	}
</script>

<div class="language-select">
	<div class="select-group">
		<label for="source-lang">From</label>
		<select id="source-lang" bind:value={sourceLang}>
			{#each languages as lang}
				<option value={lang}>
					{lang === 'auto' ? 'Auto-detect' : capitalize(lang)}
				</option>
			{/each}
		</select>
	</div>

	<button class="swap-btn" onclick={swap} title="Swap languages" disabled={sourceLang === 'auto'}>
		<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
			<path d="M7 16l-4-4 4-4" />
			<path d="M17 8l4 4-4 4" />
			<path d="M3 12h18" />
		</svg>
	</button>

	<div class="select-group">
		<label for="target-lang">To</label>
		<select id="target-lang" bind:value={targetLang}>
			{#each languages.filter((l) => l !== 'auto') as lang}
				<option value={lang}>{capitalize(lang)}</option>
			{/each}
		</select>
	</div>
</div>

<style>
	.language-select {
		display: flex;
		align-items: end;
		gap: 0.75rem;
	}

	.select-group {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		flex: 1;
	}

	label {
		font-size: 0.65rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-family: var(--font-display);
		font-weight: 400;
	}

	select {
		padding: 0.6rem 0.75rem;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
		background: var(--bg-input);
		color: var(--text-primary);
		font-size: 0.9rem;
		font-family: var(--font-body);
		cursor: pointer;
		width: 100%;
		appearance: none;
		-webkit-appearance: none;
		background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%237a7a96' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 0.75rem center;
		padding-right: 2rem;
		transition: border-color 0.2s;
	}

	select:focus {
		outline: none;
		border-color: var(--accent);
	}

	select:hover {
		border-color: var(--border-hover);
	}

	.swap-btn {
		background: none;
		border: 1px solid var(--border);
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.55rem;
		border-radius: var(--radius-sm);
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
		flex-shrink: 0;
	}

	.swap-btn:hover:not(:disabled) {
		border-color: var(--accent);
		color: var(--accent);
	}

	.swap-btn:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}
</style>
