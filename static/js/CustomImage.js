

export class CustomImage extends Image {
  constructor(data, id = null) {
    super();
    this.data = data;
    this.dbid = id || this.generateId();
    this.ready = this.generateHash();
  }

  generateId() {
    return 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  extractIdFromUrl(url) {
    const match = url.match(/\/api\/draft\/(\d+)\/image\//);  
    return match ? `draft_${match[1]}_${this.filename}` : this.generateId();
  }

  async generateHash() {
    /* Generate a hash for the image from data URL */
    try {
      const response = await fetch(this.data);
      const blob = await response.blob();
      const arrayBuffer = await blob.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      this.hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return this.hash;
    } catch (error) {
      console.error('Hash generation failed:', error);
      this.hash = 'fallback_' + this.data;
      return this.hash;
    }
  }

  static fromFile(file, id = null) {
    /* Create CustomImage from File object */
    return new CustomImage(URL.createObjectURL(file), id);
  }

  static async fromUrl(url, id = null) {
    /* Create CustomImage from URL string */
    const response = await fetch(url);
    const blob = await response.blob();
    return new CustomImage(URL.createObjectURL(blob), id);
  }
}
