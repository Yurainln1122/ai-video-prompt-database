# AI 视频提示词数据库使用指南

## 1. 先认识这些文件

| 文件 | 用途 | 推荐使用场景 |
|---|---|---|
| `AI视频提示词数据库.sqlite` | 完整主数据库 | 精确筛选、全文检索、程序调用 |
| `AI视频提示词数据库.md` | 数据库概览与重点案例 | 快速阅读、查看 X 视频反推提示词 |
| `AI视频提示词数据库_总表.csv` | 每条提示词占一行 | Excel、飞书、Notion、人工整理 |
| `AI视频提示词数据库_分镜.csv` | 每个分镜占一行 | 分镜生成、时间轴管理、批量调用模型 |
| `AI视频提示词数据库.json` | 完整结构化数据 | 自动化工作流、脚本、API 调用 |
| `tools/build_ai_video_prompt_database.py` | 数据库构建脚本 | 修改基础数据后重新生成全部文件 |

如果只是找提示词，先打开 `AI视频提示词数据库.md` 或总表 CSV。需要组合条件、全文搜索或自动化时，再使用 SQLite。

## 2. 一条提示词包含什么

`prompts` 表中的主要字段如下：

| 字段 | 含义 |
|---|---|
| `title` | 提示词名称 |
| `category` | 视频类型，如搞笑短视频、奇幻动作、概念 VFX |
| `aspect_ratio` | 画幅，如 `9:16`、`16:9` |
| `duration_sec` | 建议时长 |
| `resolution` | 建议分辨率 |
| `style_summary` | 整体视觉风格 |
| `scene_summary` | 场景和环境 |
| `subject_summary` | 主要人物或角色 |
| `core_mechanic` | 视频最核心的动作或视觉机制 |
| `camera_language` | 景别、机位、运动方式和剪辑语言 |
| `lighting_color` | 灯光和色彩设计 |
| `audio_design` | 环境声、动作声和喜剧音效 |
| `continuity_rules` | 角色、空间、服装和物理连续性要求 |
| `master_prompt` | 可直接修改使用的完整提示词 |
| `negative_prompt` | 应明确禁止的问题 |
| `reference_image_prompt` | 角色或场景参考图提示词 |
| `recommended_models` | 建议使用的模型 |
| `prompt_origin` | 原文或反推稿的来源性质 |
| `quality_notes` | 数据冲突、推断范围等注意事项 |

`shots` 表保存每条提示词的分镜，包括开始时间、结束时间、画面动作、镜头、音效和连续性要求。

## 3. 最简单的使用方法

### 方法 A：直接复制完整提示词

1. 打开 `AI视频提示词数据库.md` 或 `AI视频提示词数据库_总表.csv`。
2. 根据题材、画幅和时长选择一条记录。
3. 复制 `master_prompt`。
4. 替换人物、场景、动作、时长等变量。
5. 将 `negative_prompt` 一并提交给支持负面提示词的模型；不支持时，将它改写成“全片禁止……”并追加到正文末尾。
6. 如果平台一次只能生成 5–10 秒，按照分镜表逐段生成，不要把长时间轴强行塞进一次生成。

### 方法 B：按分镜生成

以提示词 ID 4“单指局部时间冻结”为例：

1. 先读取 `prompts` 中的风格、人物、场景和连续性规则。
2. 按 `shots` 表顺序生成 7 个片段。
3. 每个分镜都重复必要的角色和场景锁定信息。
4. 前一个分镜的结束姿态应写入下一个分镜的开头。
5. 最后再进行剪辑、音效和节奏调整。

推荐的单分镜组合方式：

```text
固定设定
+ 当前分镜的 visual_action
+ 当前分镜的 camera
+ 当前分镜的 audio
+ 当前分镜的 continuity
+ 全局 negative_prompt
```

## 4. 如何选择数据库中的模板

### 做竖屏搞笑视频

选择：

- ID 2：水豚噜噜厨房倒盐恶作剧
- ID 3：山地烧烤 Vlog 猫头鹰偷肉

这两条模板适合复用“真人实拍环境 + 二维贴纸角色 + 四段喜剧因果”的结构。可以替换角色和食物，但应保留：

- 真人元素与二维角色的材质边界；
- 固定角色造型；
- 明确的捣乱、惩罚、反应、收尾；
- 每个动作的精确时间段；
- 禁止角色突然 3D 化、漂移或穿模。

### 做电影级动作视频

选择 ID 1“奇幻海盗舰队大战利维坦”。

长提示词最好拆成多个镜头生成。每一段都重复船长外形、旗舰颜色、巨兽尺寸和风暴色板，避免角色、船只数量和空间关系跳变。

### 做概念 VFX 或特殊物理效果

选择 ID 4“单指局部时间冻结”。

重点不是“时间冻结”这个名词，而是精确写清：

1. 哪一帧触发；
2. 只冻结哪个对象；
3. 冻结对象的哪些细节必须完全停止；
4. 哪些背景元素必须继续运动；
5. 相机是否继续移动；
6. 持续多久；
7. 如何恢复原来的速度、重心和惯性。

## 5. 用 SQLite 检索

可以用 DB Browser for SQLite、DBeaver、DataGrip、VS Code SQLite 扩展或程序代码打开：

`AI视频提示词数据库.sqlite`

### 查看全部条目

```sql
SELECT *
FROM prompt_catalog
ORDER BY id;
```

### 查找所有竖屏视频

```sql
SELECT id, title, category, duration_sec
FROM prompts
WHERE aspect_ratio = '9:16';
```

### 查找 10 秒以内的搞笑视频

```sql
SELECT id, title, style_summary, core_mechanic
FROM prompts
WHERE duration_sec <= 10
  AND category LIKE '%搞笑%';
```

### 查看某条提示词的完整正文

```sql
SELECT title, master_prompt, negative_prompt
FROM prompts
WHERE id = 4;
```

### 查看某条提示词的分镜

```sql
SELECT
    shot_index,
    start_sec,
    end_sec,
    title,
    visual_action,
    camera,
    audio,
    continuity
FROM shots
WHERE prompt_id = 4
ORDER BY shot_index;
```

### 按标签检索

```sql
SELECT DISTINCT p.id, p.title
FROM prompts p
JOIN prompt_tags pt ON pt.prompt_id = p.id
JOIN tags t ON t.id = pt.tag_id
WHERE t.name IN ('2D贴纸', 'POV', '9:16')
ORDER BY p.id;
```

### 全文检索

数据库已创建 FTS5 全文检索表：

```sql
SELECT rowid, title, style_summary
FROM prompt_fts
WHERE prompt_fts MATCH '时间冻结';
```

也可以检索多个概念：

```sql
SELECT rowid, title
FROM prompt_fts
WHERE prompt_fts MATCH '搞笑 OR 海盗 OR 物理一致性';
```

## 6. CSV 和 JSON 怎么用

### CSV

两个 CSV 都采用 UTF-8 BOM 编码，可直接用 Excel 打开：

- 总表适合筛选和批量编辑；
- 分镜表适合制作镜头清单和生成任务队列。

注意：直接修改 CSV 不会自动同步回 SQLite。

### JSON

JSON 中每条 `prompt` 都带有自己的 `tags` 和 `shots`，适合：

- 自动拼接分镜提示词；
- 接入模型 API；
- 构建网页搜索工具；
- 导入向量数据库；
- 批量生成任务。

基本结构：

```json
{
  "sources": [],
  "prompts": [
    {
      "title": "提示词标题",
      "master_prompt": "完整提示词",
      "negative_prompt": "负面提示词",
      "tags": [],
      "shots": []
    }
  ]
}
```

## 7. 如何修改现有提示词

临时使用时，可以直接复制 `master_prompt` 后修改，不必改数据库。

需要永久保存修改时，推荐修改：

`tools/build_ai_video_prompt_database.py`

然后重新运行构建脚本。不要只修改生成后的 SQLite、CSV、JSON 或索引文件，因为下次重建时这些修改会被覆盖。

在 PowerShell 中运行：

```powershell
& 'C:\Users\25748\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\25748\Desktop\ai视频提示词\tools\build_ai_video_prompt_database.py'
```

脚本会重新生成：

- SQLite 主库；
- 提示词总表 CSV；
- 分镜 CSV；
- JSON；
- Markdown 数据库索引。

脚本重建生成文件时，不会覆盖原始的 `搞笑做饭提示词.txt`、`山地烧烤vlog提示词.txt` 和 `海盗舰队与巨兽激战提示词.md`。

## 8. 添加新提示词的推荐规范

新增记录时至少填写：

```text
标题：
分类：
画幅：
时长：
分辨率：
风格：
固定场景：
固定角色：
核心动作或视觉机制：
时间轴：
镜头语言：
灯光和色彩：
音效：
连续性规则：
负面提示词：
来源：
```

高质量提示词应优先写清动作因果与连续性，不要只堆砌“8K、电影级、杰作”等质量词。

建议把提示词分成三层：

1. **固定层**：人物、服装、场景、画幅、材质和色板；
2. **时间层**：每个时间段发生的动作；
3. **约束层**：哪些内容不能变化、不能出现或必须继续运动。

## 9. 数据质量注意事项

- 海盗视频原文时间轴为 0–15 秒，但末尾写有“10s”；数据库按 15 秒时间轴记录。
- `海盗舰队与巨兽激战提示词.txt` 是空文件，没有作为独立记录导入。
- X 视频条目是依据帖子、视频封面和播放器元数据整理的可复用反推稿，不是作者公开的原始提示词。
- `prompt_origin` 和 `quality_notes` 字段用于区分原文、结构化整理和反推内容，使用时不要删除这些来源说明。

