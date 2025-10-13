
class CustomImage extends Image {
  constructor(fileOrUrl) {
    super();
    this.isFile = fileOrUrl instanceof File;
    this.isUrl = typeof fileOrUrl === 'string';
    
    if (this.isFile) {
      this.file = fileOrUrl;
      this.src = URL.createObjectURL(fileOrUrl);
      this.filename = fileOrUrl.name;
    } else if (this.isUrl) {
      this.file = null;
      this.src = fileOrUrl;
      this.filename = fileOrUrl.split('/').pop(); // Extract filename from URL
    } else {
      throw new Error('CustomImage constructor expects a File object or URL string');
    }
    
    this.hash = null;
    this.ready = this.generateHash();
  }

  async generateHash() {
    try {
      if (this.isFile) {
        // Generate hash from file content for uploaded files
        const arrayBuffer = await this.file.arrayBuffer();
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        this.hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      } else if (this.isUrl) {
        // For existing images from API, use filename as hash (much faster)
        // No need to download entire image just for deduplication
        this.hash = 'existing_' + this.filename;
      }
      return this.hash;
    } catch (error) {
      console.error('Hash generation failed:', error);
      // Fallback hash based on filename for URLs, or file properties for Files
      if (this.isFile) {
        this.hash = 'fallback_' + this.file.name + '_' + this.file.size;
      } else {
        this.hash = 'fallback_' + this.filename;
      }
      return this.hash;
    }
  }

  data() {
    return {
      file: this.file,
      src: this.src,
      hash: this.hash,
      filename: this.filename
    };
  }
}

export { CustomImage };
