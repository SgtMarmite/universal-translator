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

	<span class="arrow">&#8594;</span>

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
		gap: 1rem;
		justify-content: center;
	}

	.select-group {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	label {
		font-size: 0.8rem;
		color: #a0aec0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	select {
		padding: 0.6rem 1rem;
		border-radius: 8px;
		border: 1px solid #4a5568;
		background: #2d3748;
		color: #e2e8f0;
		font-size: 0.95rem;
		min-width: 160px;
		cursor: pointer;
	}

	select:focus {
		outline: none;
		border-color: #667eea;
	}

	.arrow {
		font-size: 1.5rem;
		color: #667eea;
		padding-bottom: 0.4rem;
	}
</style>
