// VideoSelector.js
const template = `
<div>
  <div 
      class="video-selector"
      @mousedown="startSelecting"
      @mousemove="onMouseMove"
      @mouseup="endSelecting"
      @mouseleave="endSelecting"
  >
    <video ref="video" :controls="false" :src="src" @loadedmetadata="handleLoadedMetadata">
      您的浏览器不支持视频标签。
    </video>
    <div
      class="selector"
      :style="selectorStyle"
    ></div>
  </div>
  <el-slider
      v-model="currentTime"
      :max="duration"
      :show-tooltip="false"
      @input="handleInput"
    >
  </el-slider>
</div>
`;

const styles = `
.video-selector {
    position: relative;
    width: 356px;
    height: auto;
    overflow: hidden;
    line-height: 0;
  }
  video {
    width: 350px;
    height: auto;
    position: relative;
    border: 3px solid #333;
  }
  .selector {
    position: absolute;
    border: 2px solid red;
    z-index: 100000;
  }
`;

const VideoSelector = {
  name: 'VideoSelector',
  props: {
    src: {
      type: String,
      required: true
    },
    value: {
      type: Array,
      default: () => [0, 0, 0, 0]
    },
    videoSize: {
      type: Object,
      default: () => ({ width: 0, height: 0 })
    }
  },
  data() {
    return {
      isSelecting: false,
      start: { x: 0, y: 0 },
      end: { x: 0, y: 0 },
      videoSize: { width: 0, height: 0 },
      componentStyles: styles,
      currentTime: 0,
      duration: 0
    };
  },
  computed: {
    selectorStyle() {
      if (!this.isSelecting) {

      }
      return {
        display: 'block',
        left: Math.min(this.start.x, this.end.x) + 'px',
        top: Math.min(this.start.y, this.end.y) + 'px',
        width: Math.abs(this.end.x - this.start.x) + 'px',
        height: Math.abs(this.end.y - this.start.y) + 'px',
        zIndex: 100000,
      };
    }
  },
  mounted() {
    const styleElement = document.createElement('style');
    styleElement.type = 'text/css';
    styleElement.innerHTML = this.componentStyles;
    document.head.appendChild(styleElement);
    this.$refs.video.addEventListener('loadedmetadata', this.setDuration);
  },
  beforeDestroy() {
    this.$refs.video.removeEventListener('loadedmetadata', this.setDuration);
  },
  methods: {
    handleLoadedMetadata() {
      this.videoSize.width = this.$refs.video.videoWidth;
      this.videoSize.height = this.$refs.video.videoHeight;
      // 传递给props 的videoSize
      this.$emit('video-size', this.videoSize);
      this.$emit('input', [0, 0, 0, 0]);
      this.start = { x: 0, y: 0}
      this.end = { x: 0, y: 0}
    },
    handleInput(val){
      const currentTime = val || 0;
      this.currentTime = currentTime;
      this.$refs.video.currentTime = currentTime;
      this.$emit('upcurrenttime', this.currentTime);

    },
    setDuration() {
      const duration = this.$refs.video.duration;
      this.duration = duration;
    },
    getCursorPosition(event) {
      const rect = this.$refs.video.getBoundingClientRect();
      return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      };
    },
    startSelecting(event) {
      this.isSelecting = true;
      this.start = this.end = this.getCursorPosition(event);
    },
    onMouseMove(event) {
      if (this.isSelecting) {
        this.end = this.getCursorPosition(event);
      }
    },
    endSelecting() {
      if (this.isSelecting) {
        this.isSelecting = false;
        // 缩放比例
        const scaleX = this.videoSize.width / 350;
        const videoRect = this.$refs.video.getBoundingClientRect();
        // 取整数
        // const relativeStartX = this.start.x * scaleX;
        // const relativeStartY = this.start.y * scaleX;
        // const relativeEndX = this.end.x * scaleX;
        // const relativeEndY = this.end.y * scaleX;
        const relativeStartX = Math.min(Math.max(0, Math.floor(this.start.x * scaleX)), this.videoSize.width);
        const relativeStartY = Math.min(Math.max(0, Math.floor(this.start.y * scaleX)), this.videoSize.height);
        const relativeEndX = Math.min(Math.max(0, Math.floor(this.end.x * scaleX)), this.videoSize.width);
        const relativeEndY = Math.min(Math.max(0, Math.floor(this.end.y * scaleX)), this.videoSize.height);
        this.$emit('input', [relativeStartX, relativeStartY, relativeEndX, relativeEndY]);
      }
    }
  },
  template: template,
  styles: styles
};
