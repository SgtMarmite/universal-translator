<script lang="ts">
	import { uploadGlossary, deleteGlossary } from '$lib/api';

	let {
		instructions = $bindable('')
	}: {
		instructions: string;
	} = $props();

	let expanded = $state(false);
	let glossaryStatus = $state<string | null>(null);
	let glossaryInput: HTMLInputElement;

	async function handleGlossaryUpload(e: Event) {
		const target = e.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		try {
			await uploadGlossary(file);
			glossaryStatus = file.name;
		} catch (err) {
			glossaryStatus = null;
			alert(err instanceof Error ? err.message : 'Failed to upload glossary');
		}
		target.value = '';
	}

	async function handleRemoveGlossary() {
		await deleteGlossary();
		glossaryStatus = null;
	}
</script>

<button class="toggle" onclick={() => (expanded = !expanded)}>
	<svg
		class="chevron"
		class:open={expanded}
		width="12" height="12"
		viewBox="0 0 12 12"
		fill="none"
		stroke="currentColor"
		stroke-width="1.5"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		<path d="M4 4.5L6 6.5L8 4.5" />
	</svg>
	Custom instructions
</button>

{#if expanded}
	<div class="instructions-content">
		<textarea
			bind:value={instructions}
			placeholder="e.g., Use formal tone. Translate 'Firma' as 'Acme Corp'. Keep technical terms in English."
			rows="3"
		></textarea>

		<div class="glossary-row">
			<button class="glossary-btn" onclick={() => glossaryInput.click()}>
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
					<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
					<polyline points="14 2 14 8 20 8" />
				</svg>
				Upload glossary
			</button>
			<input
				bind:this={glossaryInput}
				type="file"
				accept=".csv"
				onchange={handleGlossaryUpload}
				hidden
			/>
			{#if glossaryStatus}
				<span class="glossary-name">{glossaryStatus}</span>
				<button class="remove-btn" onclick={handleRemoveGlossary} title="Remove glossary">
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
						<path d="M18 6L6 18M6 6l12 12" />
					</svg>
				</button>
			{:else}
				<span class="glossary-hint">CSV: source_term, target_term</span>
			{/if}
		</div>
	</div>
{/if}

<style>
	.toggle {
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		font-size: 0.8rem;
		font-family: var(--font-display);
		font-weight: 400;
		padding: 0.4rem 0;
		display: flex;
		align-items: center;
		gap: 0.4rem;
		letter-spacing: 0.02em;
		transition: color 0.2s;
	}

	.toggle:hover {
		color: var(--text-secondary);
	}

	.chevron {
		transition: transform 0.2s ease;
	}

	.chevron.open {
		transform: rotate(0deg);
	}

	.chevron:not(.open) {
		transform: rotate(-90deg);
	}

	.instructions-content {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		animation: slideDown 0.2s ease;
	}

	textarea {
		width: 100%;
		padding: 0.7rem 0.85rem;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
		background: var(--bg-input);
		color: var(--text-primary);
		font-size: 0.85rem;
		resize: vertical;
		font-family: var(--font-body);
		line-height: 1.5;
		transition: border-color 0.2s;
	}

	textarea::placeholder {
		color: var(--text-muted);
	}

	textarea:focus {
		outline: none;
		border-color: var(--accent);
	}

	.glossary-row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}

	.glossary-btn {
		padding: 0.4rem 0.7rem;
		border-radius: 6px;
		border: 1px solid var(--border);
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		font-size: 0.78rem;
		font-family: var(--font-body);
		display: flex;
		align-items: center;
		gap: 0.35rem;
		transition: all 0.2s;
		white-space: nowrap;
	}

	.glossary-btn:hover {
		border-color: var(--accent);
		color: var(--accent);
	}

	.glossary-name {
		color: var(--success);
		font-size: 0.78rem;
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

	.glossary-hint {
		font-size: 0.72rem;
		color: var(--text-muted);
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
