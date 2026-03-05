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
		<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
			<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
			<polyline points="17 8 12 3 7 8" />
			<line x1="12" y1="3" x2="12" y2="15" />
		</svg>
		<p class="drop-text">Drop a file here or click to browse</p>
		<p class="drop-formats">
			{Object.values(formats).join(' / ')}
		</p>
	</div>
</div>

<style>
	.drop-zone {
		border: 2px dashed #4a5568;
		border-radius: 12px;
		padding: 3rem 2rem;
		text-align: center;
		cursor: pointer;
		transition: all 0.2s ease;
		background: #1a1a2e;
	}

	.drop-zone:hover,
	.drop-zone.dragging {
		border-color: #667eea;
		background: #1a1a3e;
	}

	.drop-content {
		color: #a0aec0;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
	}

	.drop-text {
		font-size: 1.1rem;
		margin: 0;
	}

	.drop-formats {
		font-size: 0.85rem;
		color: #718096;
		margin: 0;
	}
</style>
