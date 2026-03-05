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

<div class="instructions-section">
	<button class="toggle" onclick={() => (expanded = !expanded)}>
		{expanded ? '&#9660;' : '&#9654;'} Custom Instructions
	</button>

	{#if expanded}
		<div class="instructions-content">
			<textarea
				bind:value={instructions}
				placeholder="e.g., Use formal tone. Translate 'Firma' as 'Acme Corp'. Keep technical terms in English."
				rows="3"
			></textarea>

			<div class="glossary-section">
				<div class="glossary-row">
					<button class="glossary-btn" onclick={() => glossaryInput.click()}>
						Upload Glossary CSV
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
						<button class="remove-btn" onclick={handleRemoveGlossary}>&#10005;</button>
					{/if}
				</div>
				<p class="glossary-hint">CSV format: source_term,target_term</p>
			</div>
		</div>
	{/if}
</div>

<style>
	.instructions-section {
		width: 100%;
	}

	.toggle {
		background: none;
		border: none;
		color: #a0aec0;
		cursor: pointer;
		font-size: 0.9rem;
		padding: 0.5rem 0;
	}

	.toggle:hover {
		color: #e2e8f0;
	}

	.instructions-content {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-top: 0.5rem;
	}

	textarea {
		width: 100%;
		padding: 0.75rem;
		border-radius: 8px;
		border: 1px solid #4a5568;
		background: #2d3748;
		color: #e2e8f0;
		font-size: 0.9rem;
		resize: vertical;
		font-family: inherit;
	}

	textarea:focus {
		outline: none;
		border-color: #667eea;
	}

	.glossary-section {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.glossary-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.glossary-btn {
		padding: 0.4rem 0.8rem;
		border-radius: 6px;
		border: 1px solid #4a5568;
		background: #2d3748;
		color: #e2e8f0;
		cursor: pointer;
		font-size: 0.85rem;
	}

	.glossary-btn:hover {
		border-color: #667eea;
	}

	.glossary-name {
		color: #68d391;
		font-size: 0.85rem;
	}

	.remove-btn {
		background: none;
		border: none;
		color: #fc8181;
		cursor: pointer;
		font-size: 1rem;
		padding: 0;
	}

	.glossary-hint {
		font-size: 0.75rem;
		color: #718096;
		margin: 0;
	}
</style>
