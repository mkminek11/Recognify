
class CustomImage extends Image {
  constructor(fileOrUrl, id = null, imageData = null) {
    /*
    Constructor:
    - fileOrUrl: File object or URL string
    - id: optional identifier
    - imageData: optional metadata object with properties like label, slide, id
    */
    super();
    this.isFile = fileOrUrl instanceof File;
    this.isUrl = typeof fileOrUrl === 'string';
    
    if (id) {
      this.id = id;
    } else if (imageData && imageData.id) {
      this.id = imageData.id;
    } else if (this.isUrl) {
      this.id = this.extractIdFromUrl(fileOrUrl);
    } else {
      this.id = this.generateId();
    }
    
    if (this.isFile) {
      this.file = fileOrUrl;
      this.src = URL.createObjectURL(fileOrUrl);
      this.filename = fileOrUrl.name;
    } else if (this.isUrl) {
      this.file = null;
      this.src = fileOrUrl;
      this.filename = fileOrUrl.split('/').pop();

      if (imageData) {
        this.label = imageData.label || '';
        this.slide = imageData.slide || '';
      }
    } else {
      throw new Error('CustomImage constructor expects a File object or URL string');
    }
    
    this.hash = null;
    this.ready = this.generateHash();
  }

  extractIdFromUrl(url) {
    const match = url.match(/\/api\/draft\/(\d+)\/image\//);
    if (match) {
      return `draft_${match[1]}_${this.filename}`;
    }
    return this.generateId();
  }

  generateId() {
    return 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  async generateHash() {
    try {
      if (this.isFile) {
        const arrayBuffer = await this.file.arrayBuffer();
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        this.hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      } else if (this.isUrl) {
        this.hash = 'existing_' + this.filename;
      }
      return this.hash;
    } catch (error) {
      console.error('Hash generation failed:', error);
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
      id: this.id
    };
  }
}

export { CustomImage };
