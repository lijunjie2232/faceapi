import { ElMessage } from 'element-plus';

/**
 * Face API 工具类，封装了人脸识别相关功能
 */
export class FaceUtils {
  constructor() {
    this.faceapi = null;
    this.API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.MODELS_PATH = import.meta.env.VITE_FACE_API_MODELS_PATH || '/models';
  }

  /**
   * 加载face-api.js库和模型
   * @param {Function} onProgress - 进度回调函数，接收进度百分比参数
   * @returns {Promise<boolean>} 是否成功加载
   */
  async loadFaceApi(onProgress = null) {
    try {
      if (this.faceapi) {
        return true; // 已经加载过了
      }

      // 动态加载face-api.js
      const faceApiModule = await import('face-api.js');
      this.faceapi = faceApiModule;

      if (onProgress) onProgress(25);

      // 尝试从本地路径加载模型
      await this.loadModelsFromPath(this.MODELS_PATH);

      if (onProgress) onProgress(100);

      return true;
    } catch (error) {
      // console.error("Error loading face-api.js or models:", error);

      // 如果本地加载失败，尝试从CDN加载
      try {
        await this.loadModelsFromPath('https://raw.githubusercontent.com/justadudewhochacks/face-api.js/master/weights');

        if (onProgress) onProgress(100);

        return true;
      } catch (cdnError) {
        // console.error("Error loading models from CDN:", cdnError);
        ElMessage.error("Failed to load face detection models");
        return false;
      }
    }
  }

  /**
   * 从指定路径加载模型
   * @param {string} path - 模型路径
   */
  async loadModelsFromPath(path) {
    await this.faceapi.nets.tinyFaceDetector.loadFromUri(path);
  }

  /**
   * 获取人脸检测器选项
   * @returns {*} TinyFaceDetectorOptions实例
   */
  getFaceDetectorOptions() {
    return new this.faceapi.TinyFaceDetectorOptions();
  }

  /**
   * 执行人脸检测
   * @param {HTMLVideoElement|HTMLImageElement} input - 输入元素
   * @returns {Promise<Array>} 检测到的人脸数组
   */
  async detectFaces(input) {
    if (!this.faceapi) {
      // console.error("face-api.js not loaded");
      return [];
    }

    try {
      const detections = await this.faceapi.detectAllFaces(
        input,
        this.getFaceDetectorOptions()
      );
      return detections;
    } catch (error) {
      // console.error("Error during face detection:", error);
      return [];
    }
  }

  /**
   * 在canvas上绘制检测框
   * @param {HTMLCanvasElement} canvas - 画布元素
   * @param {Array} detections - 检测结果
   * @param {number} scaleX - X轴缩放比例
   * @param {number} scaleY - Y轴缩放比例
  //  * @param {boolean} isFlipped - 是否翻转
   */
  drawDetections(canvas, detections, scaleX = 1, scaleY = 1) {
    if (!canvas || !detections || detections.length === 0) return;

    const ctx = canvas.getContext('2d');

    // 清除画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    detections.forEach(detection => {
      const box = detection.box;

      // 缩放坐标
      let x = box.x * scaleX;
      let y = box.y * scaleY;
      const width = box.width * scaleX;
      const height = box.height * scaleY;

      // 如果翻转，则调整X坐标
      // if (isFlipped) {
      //   x = canvas.width - x - width;
      // }

      // 绘制椭圆形检测框
      this.drawEllipseWithGradient(ctx, x + width / 2, y + height / 2, width / 2, height / 2);
    });
  }

  /**
   * 绘制带渐变效果的椭圆
   * @param {CanvasRenderingContext2D} ctx - 画布上下文
   * @param {number} centerX - 中心X坐标
   * @param {number} centerY - 中心Y坐标
   * @param {number} radiusX - X轴半径
   * @param {number} radiusY - Y轴半径
   */
  drawEllipseWithGradient(ctx, centerX, centerY, radiusX, radiusY) {
    ctx.save();

    // 绘制绿色边框
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, Math.PI * 2);
    ctx.stroke();

    // 添加L形角标以提高可见性
    ctx.beginPath();

    // 左上角
    ctx.moveTo(centerX - radiusX, centerY - radiusY + 10);
    ctx.lineTo(centerX - radiusX, centerY - radiusY);
    ctx.lineTo(centerX - radiusX + 10, centerY - radiusY);

    // 右上角
    ctx.moveTo(centerX + radiusX - 10, centerY - radiusY);
    ctx.lineTo(centerX + radiusX, centerY - radiusY);
    ctx.lineTo(centerX + radiusX, centerY - radiusY + 10);

    // 左下角
    ctx.moveTo(centerX - radiusX, centerY + radiusY - 10);
    ctx.lineTo(centerX - radiusX, centerY + radiusY);
    ctx.lineTo(centerX - radiusX + 10, centerY + radiusY);

    // 右下角
    ctx.moveTo(centerX + radiusX - 10, centerY + radiusY);
    ctx.lineTo(centerX + radiusX, centerY + radiusY);
    ctx.lineTo(centerX + radiusX, centerY + radiusY - 10);

    ctx.stroke();

    // 在中心绘制一个小圆点
    ctx.beginPath();
    ctx.fillStyle = '#00ff00';
    ctx.arc(centerX, centerY, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  /**
   * 从视频捕获图像
   * @param {HTMLVideoElement} video - 视频元素
   * @param {boolean} flipEnabled - 是否翻转
   * @returns {string} 图片数据URL
   */
  captureImageFromVideo(video, flipEnabled = false) {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');

    if (flipEnabled) {
      tempCtx.translate(tempCanvas.width, 0);
      tempCtx.scale(-1, 1);
    }

    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    return tempCanvas.toDataURL('image/jpeg');
  }

  /**
   * 将图片数据URL转换为Blob
   * @param {string} imageDataUrl - 图片数据URL
   * @param {string} filename - 文件名
   * @returns {FormData} 包含图片的表单数据
   */
  imageToFormData(imageDataUrl, filename = 'image.jpg') {
    const formData = new FormData();

    const base64Data = imageDataUrl.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
      const slice = byteCharacters.slice(offset, offset + 512);
      const byteNumbers = new Array(slice.length);

      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }

      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }

    const blob = new Blob(byteArrays, { type: 'image/jpeg' });
    formData.append('image', blob, filename);

    return formData;
  }

  /**
   * 发送验证请求
   * @param {FormData} formData - 表单数据
   * @returns {Promise<any>} 验证响应
   */
  async verifyFace(formData) {
    // try {
    const response = await fetch(`${this.API_BASE_URL}/api/v1/face/verify`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
    // } catch (error) {
    //   console.error('Error during face verification:', error);
    //   throw error;
    // }
  }
}