const languages = [
  "英语",
  "中文",
  "日语",
  "韩语",
  "法语",
  "德语",
  "泰语",
  "俄语",
  "意大利语",
  "西班牙语",
  "葡萄牙语",
  "阿拉伯语",
  "波斯语",
  "土耳其语",
  "印尼语",
  "越南语",
  "马来语",
  "印地语",
]

const srttemplate = `
<div>
  <div v-if="showUploader">
    <el-form>
      <el-form-item label="翻译语种">
        <el-select size="small" v-model="language" placeholder="请选择翻译语种">
          <el-option
            v-for="item in languages"
            :key="item"
            :label="item"
            :value="item">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="翻译方式">
        <el-radio-group v-model="translateType">
          <el-radio label="gpt">有风模型翻译</el-radio>
          <el-radio label="baidu">百度翻译</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="文件">
        <el-button size="small" type="primary" @click="selectSrtFile('Srt Files (*.srt)')">选择SRT文件</el-button>
      </el-form-item>
    </el-form>

  </div>
  <el-pagination
  v-if="captions.length > 0"
  @current-change="handleCurrentChange"
  :current-page="currentPage"
  :page-size="10"
  layout="total, prev, pager, next"
  :total="captions.length"
  :small="true"
></el-pagination>
  <el-table 
    v-if="captions.length > 0" 
    :data="selectedCaption"
    size="small"
    class="small-font"
    v-loading="loading"
  >
    <el-table-column width="60px" prop="index" label="序号"></el-table-column>
    <el-table-column width="100px" prop="startTime" label="时间"></el-table-column>
    <el-table-column width="300px" prop="text" label="字幕语本"></el-table-column>
    <el-table-column width="300px" class-name="result-table" prop="translateText" label="翻译结果">
    <template slot="header" slot-scope="scope">
        <el-button type="primary"  size="mini" v-show="outputPath !== ''" @click="openOutput">打开输出目录</el-button>
    </template>
  </el-table>
  <el-button :disabled="loading" v-if="showUploader && inputPath" class="submit-btn" @click="translateFile" type="primary">开始翻译</el-button>
</div>
`;

const style = `
.small-font { 
  font-size: 12px;
}
.result-table {
  background-color: #fffff0;
}
.submit-btn {
  margin-top: 20px;
}
`
const SrtReader = {
  name: 'SrtReader',
  data() {
    return {
      inputPath: "",
      outputPath: "",
      captions: [],
      selectedCaption: [],
      currentPage: 1,
      loading: false,
      componentStyles: style,
      language: "英语",
      translateType: "gpt",
      languages: languages
    };
  },
  props: {
    uid: {
      type: String,
      required: true
    },
    outputPath: {
      type: String,
      required: false,
      default: () => ''
    },
    inputPath: {
      type: String,
      default: () => ''
    },
    showUploader: {
      type: Boolean,
      default: () => true
    }
  },
  mounted() {
    const styleElement = document.createElement('style');
    styleElement.type = 'text/css';
    styleElement.innerHTML = this.componentStyles;
    document.head.appendChild(styleElement);
  },
  created() {
    // 判断 props 的inputPath 是否为 “” 空字符串 和 data中的inputPath
    if (this.inputPath !== "") {
      this.getSrt();
    }
  },
  methods: {
    selectSrtFile(fileType) {
      axios.get('http://127.0.0.1:8001/select-file/', {
        params: {
          file_types: fileType
        }
      }).then(response => {
        filepath = response.data.filepath
        if (filepath) {
          this.$emit("input-path", filepath);
          this.$emit("output-path", "");
          this.inputPath = filepath;
          this.outputPath = "";
          this.getSrt();
          this.$message("选择文件成功")
        } else {
          this.$message.error("选择文件取消")
        }

      }).catch(error => {
        this.$message.error("选择文件失败")
      });
    },
    translateFile() {
      that = this;
      // this.loading = true;
      axios.post('http://127.0.0.1:8001/translate/', {
        user_id: this.uid,
        input_path: this.inputPath,
        language: this.language,
        t_type: this.translateType,
      }).then(response => {
        data = response.data;
        that.loading = true;
        if (data.code === 200) {
          this.$message("开始翻译")
          that.translateId = data.id;


          // setInterval(function() {
          //   axios.get('http://127.0.0.1:8001:translate-status/', {
          //     id: that.translateId,
          //   }).then(response => {
          //     data = response.data;
          //     if (data.code === 200) {
          //       that.outputPath = data.filename;
          //       that.getSrt();
          //       that.$message("翻译成功")
          //       this.loading = false;
          //     } else {
          //       that.$message.error("翻译失败")
          //       this.loading = false;
          //     }
          //   }).catch(error => {});
          // }, 1000);
          // 周期性查询翻译状态 直到翻译完成结束轮训
          let interval = setInterval(function () {
            console.log(that.translateId);
            axios.get('http://127.0.0.1:8001/translate-status/', {
              params: {
                id: that.translateId,
              }
            }).then(response => {
              data = response.data;
              if (data.code === 200) {
                if (data.status === 'finished') {
                  that.outputPath = data.filename;
                  that.getSrt();
                  that.$message("翻译成功")
                  that.loading = false;
                  clearInterval(interval);
                }

                if (data.status === 'failed') {
                  that.$message.error("翻译失败")
                  that.loading = false;
                  clearInterval(interval);
                }
              } else {
                that.$message.error("翻译失败")
                that.loading = false;
                clearInterval(interval);
              }
            }
            ).catch(error => {
              this.$message.error("翻译失败")
             });
          }, 1000);

        } else {
          console.log(data);
          this.$message.error("翻译失败")
        }
      }).catch(error => {
        console.log(error);
        this.$message.error("翻译失败")
        this.loading = false;
 });
    },
    handleSizeChange(event) {
      console.log(event);
      this.currentPage = 1;
    },
    handleCurrentChange(event) {
      console.log(event);
      this.currentPage = event;
      this.selectedCaption = this.captions.slice((event - 1) * 10, event * 10);
    },
    getSrt() {
      axios.post('http://127.0.0.1:8001/get-srt/', {
        input_path: this.inputPath,
        output_path: this.outputPath
      }).then(response => {
        this.captions = response.data.captions;
        this.selectedCaption = this.captions.slice(0, 10);
      }).catch(error => { });
    },
    openOutput() {
      axios.get('http://127.0.0.1:8001/open-filepath/', {
        params: {
          filepath: this.outputPath
        }
      }).then(response => {
        code = response.data.code
        if (code === 200) {
          this.$message("目录打开成功")
        } else {
          this.$message("目录打开失败")
        }
      }).catch(error => {
        this.$message("目录打开失败")
      })
    },
    parseSrt(srtContent) {
      let index = 1;
      this.captions = [];
      const lines = srtContent.split('\n');
      let caption = {};
      for (let i = 0; i < lines.length; i++) {
        let linenum = i + 1;
        const line = lines[i].trim();
        console.log(line, linenum, linenum % 4);
        if (linenum % 4 === 1) {
          if (caption.startTime && caption.endTime && caption.text) {
            caption.index = index;
            index++;
            this.captions.push(caption);
          }
          caption = { text: '' };
        } else if (linenum % 4 === 2) {
          const times = line.split(' --> ');
          caption.startTime = times[0];
          caption.endTime = times[1];
        } else if (linenum % 4 === 3) {
          caption.text = line;
        }
      }
      if (caption.startTime && caption.endTime && caption.text) {
        this.captions.push(caption);
      }
    }
  },
  template: srttemplate
};
