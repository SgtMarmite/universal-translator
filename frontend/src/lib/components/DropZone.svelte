<script lang="ts">
	let { onFileDrop, formats }: { onFileDrop: (file: File) => void; formats: Record<string, string> } = $props();

	let isDragging = $state(false);
	let fileInput: HTMLInputElement;

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		const file = e.dataTransfer?.files[0];
		if (file) onFileDrop(file);
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave() {
		isDragging = false;
	}

	function handleClick() {
		fileInput.click();
	}

	function handleFileSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) onFileDrop(file);
		target.value = '';
	}

	const acceptExtensions = $derived(Object.keys(formats).join(','));
	const formatTags = $derived(Object.entries(formats).map(([ext, name]) => ({ ext, name })));
</script>

<div
	class="drop-zone"
	class:dragging={isDragging}
	ondrop={handleDrop}
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	onclick={handleClick}
	role="button"
	tabindex="0"
>
	<input
		bind:this={fileInput}
		type="file"
		accept={acceptExtensions}
		onchange={handleFileSelect}
		hidden
	/>
	<div class="drop-content">
		<div class="icon-ring">
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
				<polyline points="17 8 12 3 7 8" />
				<line x1="12" y1="3" x2="12" y2="15" />
			</svg>
		</div>
		<p class="drop-text">Drop a file here or <span class="browse">browse</span></p>
		<div class="format-tags">
			{#each formatTags as { ext, name }}
				<span class="tag">{ext}</span>
			{/each}
		</div>
	</div>
</div>

<style>
	.drop-zone {
		border: 1.5px dashed var(--border-hover);
		border-radius: var(--radius-sm);
		padding: 2.5rem 1.5rem;
		text-align: center;
		cursor: pointer;
		transition: all 0.25s ease;
		background: transparent;
		position: relative;
	}

	.drop-zone:hover,
	.drop-zone.dragging {
		border-color: var(--accent);
		background: var(--accent-glow);
	}

	.drop-zone.dragging {
		transform: scale(1.01);
	}

	.drop-content {
		color: var(--text-secondary);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
	}

	.icon-ring {
		width: 48px;
		height: 48px;
		border-radius: 50%;
		border: 1.5px solid var(--border-hover);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-muted);
		transition: all 0.25s ease;
	}

	.drop-zone:hover .icon-ring {
		border-color: var(--accent);
		color: var(--accent);
		box-shadow: 0 0 20px var(--accent-glow);
	}

	.drop-text {
		font-size: 0.9rem;
		margin: 0;
		color: var(--text-secondary);
	}

	.browse {
		color: var(--accent);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.format-tags {
		display: flex;
		gap: 0.35rem;
		flex-wrap: wrap;
		justify-content: center;
	}

	.tag {
		font-size: 0.65rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		padding: 0.2rem 0.5rem;
		border-radius: 4px;
		background: var(--bg-input);
		color: var(--text-muted);
		font-family: var(--font-display);
		font-weight: 400;
	}
</style>
