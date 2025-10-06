
class CustomImage extends Image {
  constructor(file) {
    super();
    this.file = file;
    this.src = URL.createObjectURL(file);
    this.hash = null;
    this.ready = this.generateHash();
  }

  async generateHash() {
    try {
      const arrayBuffer = await this.file.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      this.hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return this.hash;
    } catch (error) {
      console.error('Hash generation failed:', error);
      this.hash = 'fallback_' + this.file.name + '_' + this.file.size;
      return this.hash;
    }
  }

  data() {
    return {
      file: this.file,
      src: this.src,
      hash: this.hash
    };
  }
}

export { CustomImage };
