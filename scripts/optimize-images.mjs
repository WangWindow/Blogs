#!/usr/bin/env node
/**
 * 图片优化脚本
 *
 * 功能：
 * - 检测 posts 目录下所有 jpg/png/gif/jpeg 图片
 * - 使用 sharp 转换为 WebP 格式并优化大小
 * - 更新 Markdown 中的图片引用（封面、![](xxx) 语法、HTML img 标签）
 * - 只有转换成功才更新引用，失败则保持原引用
 * - 使用 -> 符号显示转换和引用更新日志
 */

import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.join(__dirname, "..");
const POSTS_DIR = path.join(ROOT_DIR, "posts");
const UPLOADS_DIR = path.join(ROOT_DIR, "uploads");

// 图片扩展名正则
const IMAGE_EXTENSIONS = /\.(jpe?g|png|gif)$/i;

// 智能压缩质量策略
function getQuality(fileSizeBytes) {
  const sizeMB = fileSizeBytes / (1024 * 1024);
  if (sizeMB > 2) return 65;
  if (sizeMB > 1) return 70;
  if (sizeMB > 0.5) return 80;
  return 85;
}

// 格式化文件大小
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
}

// 判断路径是否存在
async function exists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

// 递归收集所有图片文件
async function findImages(dir) {
  const images = [];

  async function walk(currentDir) {
    const entries = await fs.readdir(currentDir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        await walk(fullPath);
      } else if (IMAGE_EXTENSIONS.test(entry.name)) {
        const stats = await fs.stat(fullPath);
        images.push({
          path: fullPath,
          relativePath: path.relative(ROOT_DIR, fullPath),
          size: stats.size,
          name: entry.name,
        });
      }
    }
  }

  await walk(dir);
  return images;
}

// 递归收集所有 Markdown 文件
async function findMarkdownFiles(dir) {
  const mdFiles = [];

  async function walk(currentDir) {
    const entries = await fs.readdir(currentDir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        await walk(fullPath);
      } else if (entry.name.endsWith(".md") || entry.name.endsWith(".mdx")) {
        mdFiles.push(fullPath);
      }
    }
  }

  await walk(dir);
  return mdFiles;
}

// 使用 Sharp 转换图片为 WebP
async function convertToWebp(imagePath, quality) {
  const webpPath = imagePath.replace(IMAGE_EXTENSIONS, ".webp");

  let sharp;
  try {
    sharp = (await import("sharp")).default;
  } catch {
    return { success: false, error: "sharp 模块未安装" };
  }

  try {
    await sharp(imagePath)
      .webp({ quality, effort: 4 })
      .toFile(webpPath);

    const webpStats = await fs.stat(webpPath);
    return { success: true, webpPath, newSize: webpStats.size };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

// 解析图片路径（处理 URL 编码）
function resolveImagePath(mdDir, imgRef) {
  if (/^https?:\/\//i.test(imgRef) || /^data:/i.test(imgRef)) {
    return null;
  }

  // 去掉开头的 ./ 如果有
  let cleanRef = imgRef;
  if (cleanRef.startsWith("./")) {
    cleanRef = cleanRef.slice(2);
  }
  // URL 解码
  try {
    cleanRef = decodeURIComponent(cleanRef);
  } catch {
    // 如果解码失败，使用原始路径
  }

  if (cleanRef.startsWith("/")) {
    return path.join(ROOT_DIR, cleanRef.replace(/^\/+/, ""));
  }

  return path.resolve(mdDir, cleanRef);
}

// 获取图片引用的 webp 版本路径
function getWebpRef(imgRef) {
  return imgRef.replace(/\.(jpe?g|png|gif)$/i, ".webp");
}

// 更新 Markdown 文件中的图片引用（仅替换成功转换的）
async function updateMarkdownReferences(mdFiles, convertedSet) {
  const refLogs = [];
  let totalRefs = 0;
  let updatedRefs = 0;

  for (const mdPath of mdFiles) {
    const mdDir = path.dirname(mdPath);
    const mdRelPath = path.relative(POSTS_DIR, mdPath);
    let content = await fs.readFile(mdPath, "utf-8");
    let modified = false;
    const fileRefLogs = [];

    // 定义各种图片引用的匹配模式
    const patterns = [
      // Markdown 图片: ![alt](path.ext)
      {
        regex: /!\[([^\]]*)\]\(([^)]+\.(jpe?g|png|gif))\)/gi,
        getRef: (match) => match[2],
        replace: (match, webpRef) => `![${match[1]}](${webpRef})`,
      },
      // frontmatter cover: cover: "./path.ext" 或 cover: "path.ext"
      {
        regex: /^(cover:\s*["']?)([^"'\n]+\.(jpe?g|png|gif))(["']?\s*)$/gim,
        getRef: (match) => match[2],
        replace: (match, webpRef) => `${match[1]}${webpRef}${match[4]}`,
      },
      // HTML img 标签: <img src="path.ext">
      {
        regex: /<img([^>]*)\ssrc=["']([^"']+\.(jpe?g|png|gif))["']([^>]*)>/gi,
        getRef: (match) => match[2],
        replace: (match, webpRef) => `<img${match[1]} src="${webpRef}"${match[4]}>`,
      },
    ];

    for (const pattern of patterns) {
      const matches = [...content.matchAll(pattern.regex)];
      for (const match of matches) {
        totalRefs++;
        const imgRef = pattern.getRef(match);
        const imgFullPath = resolveImagePath(mdDir, imgRef);

        if (!imgFullPath) {
          continue;
        }

        // 检查这个图片是否成功转换
        if (convertedSet.has(imgFullPath)) {
          const webpRef = getWebpRef(imgRef);
          const original = match[0];
          const replacement = pattern.replace(match, webpRef);
          content = content.replace(original, replacement);
          modified = true;
          updatedRefs++;
          fileRefLogs.push(`   ${imgRef} -> ${webpRef}`);
        }
      }
    }

    if (modified) {
      await fs.writeFile(mdPath, content, "utf-8");
      if (fileRefLogs.length > 0) {
        refLogs.push(`📄 ${mdRelPath}`);
        refLogs.push(...fileRefLogs);
      }
    }
  }

  return { refLogs, totalRefs, updatedRefs };
}

// 主函数
async function main() {
  console.log("🖼️  图片优化脚本启动");
  console.log("=".repeat(60));

  // 查找所有图片
  console.log("\n📂 扫描图片文件...");
  const scanDirs = [POSTS_DIR, UPLOADS_DIR];
  const images = [];

  for (const dir of scanDirs) {
    if (!(await exists(dir))) {
      continue;
    }
    const dirImages = await findImages(dir);
    images.push(...dirImages);
  }

  if (images.length === 0) {
    console.log("✅ 没有找到需要处理的图片文件");
    return;
  }

  console.log(`   找到 ${images.length} 个图片文件\n`);

  // 处理结果
  const convertedSet = new Set();
  let successCount = 0;
  let failCount = 0;
  let skippedCount = 0;
  let totalOriginalSize = 0;
  let totalNewSize = 0;

  // 转换图片
  console.log("🔄 转换图片为 WebP...\n");

  for (const image of images) {
    const quality = getQuality(image.size);
    const result = await convertToWebp(image.path, quality);

    if (result.success) {
      const savedPercentValue = ((image.size - result.newSize) / image.size) * 100;
      const savedPercent = savedPercentValue.toFixed(1);
      const webpRelPath = path.relative(ROOT_DIR, result.webpPath);

      if (result.newSize >= image.size) {
        await fs.unlink(result.webpPath);
        console.log(
          `   ⏭️  ${image.relativePath} (跳过: ${formatSize(result.newSize)} >= ${formatSize(image.size)})`
        );
        skippedCount++;
        continue;
      }

      console.log(
        `   ✅ ${image.relativePath} -> ${webpRelPath} (${formatSize(image.size)} -> ${formatSize(result.newSize)}, -${savedPercent}%)`
      );

      convertedSet.add(image.path);
      totalOriginalSize += image.size;
      totalNewSize += result.newSize;
      successCount++;

      // 删除原始文件
      await fs.unlink(image.path);
    } else {
      console.log(`   ❌ ${image.relativePath} (失败: ${result.error})`);
      failCount++;
    }
  }

  // 更新 Markdown 引用
  console.log("\n📝 更新 Markdown 引用...\n");
  const mdFiles = await findMarkdownFiles(ROOT_DIR);
  const { refLogs, totalRefs, updatedRefs } = await updateMarkdownReferences(mdFiles, convertedSet);

  if (refLogs.length > 0) {
    for (const log of refLogs) {
      console.log(`   ${log}`);
    }
  } else {
    console.log("   没有需要更新的引用");
  }

  // 打印总结
  console.log("\n" + "=".repeat(60));
  console.log("📊 处理总结\n");

  const savedSize = totalOriginalSize - totalNewSize;
  const savedPercent = totalOriginalSize > 0
    ? ((savedSize / totalOriginalSize) * 100).toFixed(1)
    : 0;

  console.log(`   图片转换: ${successCount} 成功, ${failCount} 失败`);
  console.log(`   引用更新: ${updatedRefs}/${totalRefs} 个`);
  console.log();
  console.log(`   原始大小: ${formatSize(totalOriginalSize)}`);
  console.log(`   新的大小: ${formatSize(totalNewSize)}`);
  console.log(`   节省空间: ${formatSize(savedSize)} (${savedPercent}%)`);
  console.log();

  if (failCount > 0) {
    console.log("⚠️  部分图片转换失败，对应引用保持不变");
    process.exit(1);
  }

  console.log("✅ 所有图片处理完成！\n");
}

main().catch((err) => {
  console.error("❌ 脚本执行失败:", err);
  process.exit(1);
});
