#!/usr/bin/env node
/**
 * ============================================================
 * 文件说明书 (File Manual)
 * ============================================================
 * 核心功能 (Core Function)
 * 即刻发布工具适配层，负责认证、搜索频道、上传图片和发布动态。
 *
 * 输入 (Input)
 * - 命令行参数: login / whoami / search-topic / upload-image / publish-json
 * - 环境变量: JIKE_PHONE, JIKE_PASSWORD
 * - payload.json: 发布内容、图片列表、频道 ID、同步配置
 *
 * 输出 (Output)
 * - stdout: JSON 格式的执行结果
 * - 本地 token 缓存: .jike-tokens.json
 *
 * 定位 (Position)
 * content-publisher 的即刻底层适配器，由 Python 发布器通过 subprocess 调用。
 *
 * 依赖 (Dependency)
 * - Node.js 18+ 的原生 fetch / FormData / Blob
 * - 即刻移动端接口: users/profile, users/topics/search, upload/token, originalPosts/create
 *
 * 维护规则 (Maintenance Rules)
 * 1. 每次修改代码逻辑后，必须检查并更新上述信息。
 * 2. 禁止修改或删除本【维护规则】章节的内容。
 * ============================================================
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const BASE_DIR = path.dirname(fileURLToPath(import.meta.url));
const BASE_URL = 'https://api.ruguoapp.com';
const TOKEN_FILE = path.join(BASE_DIR, '.jike-tokens.json');

const DEVICE_ID = '4653BFCE-9D54-471C-809C-422AC240DA7B';
const IDFV = '5C5FC6BB-F6E6-4689-BB5A-E88763186C55';
const UA = 'jike/7.34.0 (com.ruguoapp.jike; build:2225; iOS 15.5.0) Alamofire/5.4.3';

function printJson(payload, exitCode = 0) {
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(exitCode);
}

function fail(message, extra = {}, exitCode = 1) {
  printJson({ status: 'error', message, ...extra }, exitCode);
}

function baseHeaders(accessToken) {
  const headers = {
    'Content-Type': 'application/json',
    'User-Agent': UA,
    'x-jike-device-id': DEVICE_ID,
    'x-jike-device-properties': JSON.stringify({ idfv: IDFV }),
    'App-Version': '7.34.0',
    bundleid: 'com.ruguoapp.jike',
    manufacturer: 'Apple',
    os: 'ios',
    'os-version': 'Version 14.7',
  };
  if (accessToken) headers['x-jike-access-token'] = accessToken;
  return headers;
}

function loadTokens() {
  try {
    return fs.existsSync(TOKEN_FILE)
      ? JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf-8'))
      : null;
  } catch {
    return null;
  }
}

function saveTokens(tokens) {
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokens, null, 2));
  fs.chmodSync(TOKEN_FILE, 0o600);
}

async function apiGet(endpoint, token) {
  const resp = await fetch(`${BASE_URL}/${endpoint}`, {
    headers: baseHeaders(token),
  });
  return { status: resp.status, data: await resp.json(), headers: resp.headers };
}

async function apiPost(endpoint, body, token) {
  const resp = await fetch(`${BASE_URL}/${endpoint}`, {
    method: 'POST',
    headers: baseHeaders(token),
    body: JSON.stringify(body),
  });
  return { status: resp.status, data: await resp.json(), headers: resp.headers };
}

async function doLogin(phone, password) {
  const resp = await fetch(`${BASE_URL}/1.0/users/loginWithPhoneAndPassword`, {
    method: 'POST',
    headers: baseHeaders(),
    body: JSON.stringify({
      areaCode: '+86',
      mobilePhoneNumber: phone,
      password,
    }),
  });

  return {
    status: resp.status,
    accessToken: resp.headers.get('x-jike-access-token'),
    refreshToken: resp.headers.get('x-jike-refresh-token'),
    data: await resp.json(),
  };
}

async function doRefresh(refreshToken) {
  const headers = baseHeaders();
  headers['x-jike-refresh-token'] = refreshToken;
  const resp = await fetch(`${BASE_URL}/app_auth_tokens.refresh`, {
    method: 'POST',
    headers,
  });
  return {
    status: resp.status,
    accessToken: resp.headers.get('x-jike-access-token'),
    refreshToken: resp.headers.get('x-jike-refresh-token'),
  };
}

async function getToken() {
  const phone = process.env.JIKE_PHONE || '';
  const password = process.env.JIKE_PASSWORD || '';
  let tokens = loadTokens();

  if (tokens?.accessToken) {
    const current = await apiGet('1.0/users/profile?username=', tokens.accessToken);
    if (current.status === 200) return tokens.accessToken;
  }

  if (tokens?.refreshToken) {
    const refreshed = await doRefresh(tokens.refreshToken);
    if (refreshed.accessToken) {
      saveTokens({
        accessToken: refreshed.accessToken,
        refreshToken: refreshed.refreshToken || tokens.refreshToken,
        updatedAt: new Date().toISOString(),
      });
      return refreshed.accessToken;
    }
  }

  if (!phone || !password) {
    fail('即刻未登录，且缺少 JIKE_PHONE / JIKE_PASSWORD 环境变量', { needs_login: true });
  }

  const login = await doLogin(phone, password);
  if (!login.accessToken) {
    fail('即刻登录失败', { http_status: login.status, data: login.data });
  }

  saveTokens({
    accessToken: login.accessToken,
    refreshToken: login.refreshToken,
    updatedAt: new Date().toISOString(),
  });
  return login.accessToken;
}

async function uploadImage(imagePath, token) {
  if (!fs.existsSync(imagePath)) {
    throw new Error(`图片不存在: ${imagePath}`);
  }

  const imageBuffer = fs.readFileSync(imagePath);
  const md5 = crypto.createHash('md5').update(imageBuffer).digest('hex');
  const tokenResult = await apiGet(`1.0/upload/token?md5=${md5}`, token);

  if (tokenResult.status !== 200 || !tokenResult.data?.uptoken) {
    throw new Error(`获取上传凭证失败: HTTP ${tokenResult.status}`);
  }

  const ext = path.extname(imagePath).toLowerCase();
  const mimeMap = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.gif': 'image/gif',
  };

  const formData = new FormData();
  formData.append('file', new Blob([imageBuffer], { type: mimeMap[ext] || 'image/jpeg' }), `image${ext}`);
  formData.append('token', tokenResult.data.uptoken);

  const uploadResp = await fetch('https://upload.qiniup.com/', {
    method: 'POST',
    body: formData,
  });
  const uploadResult = await uploadResp.json();
  if (!uploadResult.key) {
    throw new Error(`图片上传失败: ${JSON.stringify(uploadResult)}`);
  }

  return uploadResult.key;
}

async function cmdLogin() {
  const phone = process.argv[3] || process.env.JIKE_PHONE;
  const password = process.argv[4] || process.env.JIKE_PASSWORD;
  if (!phone || !password) {
    fail('用法: node jike_toolkit.mjs login <手机号> <密码>');
  }

  const login = await doLogin(phone, password);
  if (!login.accessToken) {
    fail('登录失败', { http_status: login.status, data: login.data });
  }

  saveTokens({
    accessToken: login.accessToken,
    refreshToken: login.refreshToken,
    updatedAt: new Date().toISOString(),
  });

  printJson({
    status: 'success',
    message: '登录成功',
    user: {
      screenName: login.data?.user?.screenName || '',
      username: login.data?.user?.username || '',
      id: login.data?.user?.id || '',
    },
  });
}

async function cmdWhoami() {
  const token = await getToken();
  const result = await apiGet('1.0/users/profile?username=', token);
  const user = result.data?.user;
  if (result.status !== 200 || !user) {
    fail('获取当前用户失败', { http_status: result.status, data: result.data });
  }

  printJson({
    status: 'success',
    user: {
      screenName: user.screenName || '',
      username: user.username || '',
      id: user.id || '',
      briefIntro: user.briefIntro || user.bio || '',
    },
  });
}

async function cmdSearchTopic() {
  const keyword = process.argv[3];
  if (!keyword) fail('用法: node jike_toolkit.mjs search-topic "关键词"');

  const token = await getToken();
  const result = await apiPost('1.0/users/topics/search', {
    type: 'ALL',
    keywords: keyword,
    onlyUserPostEnabled: true,
    limit: 15,
  }, token);

  if (result.status !== 200) {
    fail('搜索频道失败', { http_status: result.status, data: result.data });
  }

  const topics = (result.data?.data || []).map((topic) => ({
    id: topic.id || '',
    name: topic.content || topic.text || '',
    subscribersCount: topic.subscribersCount || 0,
    briefIntro: topic.briefIntro || '',
  }));

  printJson({
    status: 'success',
    query: keyword,
    total: topics.length,
    topics,
  });
}

async function cmdUploadImage() {
  const imagePath = process.argv[3];
  if (!imagePath) fail('用法: node jike_toolkit.mjs upload-image /path/to/image.jpg');

  const token = await getToken();
  const key = await uploadImage(imagePath, token);
  printJson({
    status: 'success',
    imagePath,
    key,
  });
}

async function cmdPublishJson() {
  const payloadPath = process.argv[3];
  if (!payloadPath) fail('用法: node jike_toolkit.mjs publish-json /path/to/payload.json');
  if (!fs.existsSync(payloadPath)) fail(`payload 文件不存在: ${payloadPath}`);

  const payload = JSON.parse(fs.readFileSync(payloadPath, 'utf-8'));
  const content = payload.content || '';
  const images = Array.isArray(payload.images) ? payload.images : [];
  const topicId = payload.topicId || '';
  const syncToPersonalUpdate = payload.syncToPersonalUpdate !== false;

  if (!content.trim()) fail('发布内容不能为空');

  const token = await getToken();
  const pictureKeys = [];

  for (const imagePath of images) {
    try {
      const key = await uploadImage(imagePath, token);
      pictureKeys.push(key);
    } catch (error) {
      fail('上传图片失败', {
        imagePath,
        detail: error instanceof Error ? error.message : String(error),
      });
    }
  }

  const requestBody = {
    content,
    pictureKeys,
    syncToPersonalUpdate,
  };
  if (topicId) requestBody.submitToTopic = topicId;

  const result = await apiPost('1.0/originalPosts/create', requestBody, token);
  if (result.status !== 200 || !result.data?.data) {
    fail('发布动态失败', { http_status: result.status, data: result.data });
  }

  const post = result.data.data;
  printJson({
    status: 'success',
    post: {
      id: post.id || '',
      url: post.id ? `https://web.okjike.com/originalPost/${post.id}` : '',
      topicId: topicId || '',
      pictureKeys,
      syncToPersonalUpdate,
    },
  });
}

async function main() {
  const command = process.argv[2];
  try {
    switch (command) {
      case 'login':
        await cmdLogin();
        break;
      case 'whoami':
        await cmdWhoami();
        break;
      case 'search-topic':
        await cmdSearchTopic();
        break;
      case 'upload-image':
        await cmdUploadImage();
        break;
      case 'publish-json':
        await cmdPublishJson();
        break;
      default:
        fail('未知命令', {
          supported: ['login', 'whoami', 'search-topic', 'upload-image', 'publish-json'],
        });
    }
  } catch (error) {
    fail(
      error instanceof Error ? error.message : String(error),
      { stack: error instanceof Error ? error.stack : '' }
    );
  }
}

await main();
