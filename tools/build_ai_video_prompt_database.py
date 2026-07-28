from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "AI视频提示词数据库.sqlite"
PROMPTS_CSV = ROOT / "AI视频提示词数据库_总表.csv"
SHOTS_CSV = ROOT / "AI视频提示词数据库_分镜.csv"
JSON_PATH = ROOT / "AI视频提示词数据库.json"
BROWSER_DATA_PATH = ROOT / "database-data.js"
INDEX_PATH = ROOT / "AI视频提示词数据库.md"

X_URL = "https://x.com/andy_neon_/status/2080767882250842191"
X_POST = (
    "ONE FINGER TAP FREEZES A PERSON MID-MOTION. EVERYTHING AROUND THEM KEEPS MOVING. "
    "Not the whole world. Just the target—locked in place, real physics holding, while the "
    "frame around them stays completely alive. Claude structured the sequence first—the exact "
    "moment the tap lands, what freezes, what keeps moving, how long the hold lasts—before "
    "Seedance 2.0 rendered it frame by frame. Under 10 minutes of render time. $12 in tokens. "
    "No compositing team. No post-production pass. No green screen."
)
RESTAURANT_X_URL = "https://x.com/YangOnchain/status/2080727499894645240"
RESTAURANT_X_POST = (
    "100天AI玩法学习，第6天。今天挑战的是：不用请托，只用AI给商家拍外国人探店！"
    "另外我也会做skill了！杨哥玩了3个月AI进步了啊！！"
)
SHOOTING_GALLERY_X_URL = "https://x.com/manaimovie/status/2080268691430928644"
SHOOTING_GALLERY_X_POST = "🎯射的では大物を狙うべからず🧸"
ANIMATION_STYLES_X_URL = "https://x.com/sebatheepan/status/2080687176581259596"
ANIMATION_STYLES_IMAGE_POST_URL = "https://x.com/sebatheepan/status/2080687180532342996"
ANIMATION_STYLES_VIDEO_POST_URL = "https://x.com/sebatheepan/status/2080687185150271772"
ANIMATION_STYLES_X_POST = (
    "I’m testing 100 animation styles by giving each one the same challenge: create an original "
    "character, a world, and a complete 15-second story.\n\nPilot batch: graphite, pinscreen, "
    "particle flow, and cel-banded CGI.\n\nFour styles. Four micro-short. One minute ↓"
)
STARBUCKS_ANIME_X_URL = "https://x.com/noorwithwifi/status/2080914390782779861"
STARBUCKS_ANIME_PROMPT = (
    "Create a 35-second anime/Ghibli-inspired 2D commercial for Starbucks Bottled Coffee "
    "featuring a young man enjoying a bright morning in the city. He picks up a Starbucks "
    "Caffè Latte from a convenience store, takes a refreshing sip, then works and socializes "
    "with friends in a cozy café while using his laptop and notebook. Warm sunlight, soft "
    "colors, expressive character animation, and upbeat acoustic music create a cheerful, "
    "inspiring atmosphere. End with a close-up of the Starbucks Caffè Latte bottles."
)
PHO_ANIME_X_URL = "https://x.com/noorwithwifi/status/2080998165013217284"
PHO_ANIME_PROMPT = (
    "Create a cinematic anime-style cooking video showing the outdoor preparation of authentic "
    "beef pho at a peaceful riverside campsite. Begin with slicing marbled beef, preparing "
    "ginger, onions, whole spices, fresh Thai basil, bean sprouts, and lime, then simmer beef "
    "bones, aromatics, and spices in a cast-iron pot over a crackling campfire to create a rich "
    "broth. Finally, place rice noodles in a ceramic bowl, top with thin beef slices, pour "
    "steaming broth to gently cook the meat, and finish with herbs, chili, red onion, and lime. "
    "Capture warm golden lighting, cozy camping vibes, detailed food close-ups, smooth "
    "transitions, and beautiful anime-inspired visuals."
)
COOKIES_MILK_ASMR_X_URL = "https://x.com/AIwithSynthia/status/2081581375790948730"
COOKIES_MILK_STORYBOARD_PROMPT = """Create a premium 16:9 storyboard infographic for a Cookies & Milk ASMR commercial on a clean white background with a modern creative agency layout. Add the title "STORYBOARD – COOKIES & MILK – ASMR SNACK EXPERIENCE" and info boxes for Duration: 15 Seconds, Style: POV Hands ASMR, Audience: 16–35, Audio: Wrapper • Crunch • Milk Pouring • Glass Tap. Arrange 6 storyboard panels (3×2) with numbered badges and timestamps. Show: (1) cookie box introduction (HELLO!), (2) wrapper opening (CRINKLE~), (3) milk pouring (POUR~), (4) cookie dipping (DIP!), (5) cookie breaking with crumbs (CRUNCH!), (6) final hero shot with cookies, milk, and thumbs-up (YUM!). Include VISUAL, ACTION, and DIALOGUE below each panel. Use realistic food photography, warm wooden table, soft natural lighting, shallow depth of field, handwritten doodle effects, rounded panel borders, elegant brown accents, and a polished client-pitch presentation."""
COOKIES_MILK_VIDEO_PROMPT = """Create an ultra-realistic 15-second premium ASMR food commercial featuring only POV hands throughout the entire sequence. No faces visible. Cozy morning kitchen aesthetic with a warm wooden tabletop, soft natural window light, shallow depth of field, realistic food textures, cinematic macro photography, and luxury commercial color grading.
Throughout the video, add playful hand-drawn white doodle text and arrows that naturally animate into the scene, just like a modern food reel. The doodles should appear briefly beside the action, following the product, then fade away. No subtitles, captions, logos, or other text besides these doodle effects.
0:00–0:02.5
A premium chocolate chip cookie box and a chilled glass bottle of milk rest on a wooden table. Hands slide into frame and gently rotate the box. Animated doodles appear: "HELLO!", "HI!", small sparkles and arrows pointing toward the box.
0:02.5–0:05
Hands slowly tear open the cookie wrapper. Crisp ASMR crinkle fills the room. Animated doodles: "CRINKLE~", "OPEN!", "WOW!" with playful motion lines.
0:05–0:07.5
Fresh cold milk pours into a clear glass in slow motion. Creamy splashes, bubbles, and condensation glisten. Animated doodles: "POUR~", "FRESH!", tiny droplets and splash illustrations.
0:07.5–0:10
One cookie is lifted and slowly dipped into the milk. Milk drips gently back into the glass. Animated doodles: "DIP!", "SOFT!", hearts and curved arrows following the cookie.
0:10–0:12.5
Macro shot of the cookie breaking in half. Chocolate stretches slightly while crumbs fall in slow motion. Animated doodles: "CRUNCH!", "YUM!", "MMM!" with tiny stars and crumb illustrations.
0:12.5–0:15
Hero shot of the cookie box, stacked cookies, and glass of milk beautifully arranged together. A hand places the final cookie onto the plate and gives a thumbs-up. Camera slowly pushes in. Animated doodles: "PERFECT!", "BEST!", "ENJOY!", surrounded by soft sparkles and hand-drawn stars.
Audio: Natural ASMR only—cardboard tapping, wrapper crinkles, milk pouring, glass clinks, cookie dipping, crunchy bites, falling crumbs, soft tabletop taps, and quiet room ambience. No background music, no subtitles, no logos, no watermarks, and no on-screen text other than the animated doodle words. Premium food commercial cinematography, realistic food physics, macro close-ups, physically accurate lighting, photorealistic 4K HDR, 16:9, 24 fps."""
COFFEE_LIGHTHOUSE_X_URL = "https://x.com/icreatelife/status/2081740528173924586"
COFFEE_LIGHTHOUSE_X_POST = "May your coffee taste great today!\nHappy Monday!"


def read_utf8(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8").strip()


def split_pirate_prompt(text: str) -> tuple[str, str]:
    match = re.search(
        r"\*\*视频提示词：\*\*\s*(.*?)\s*\*\*生图提示词：\*\*\s*(.*)",
        text,
        flags=re.S,
    )
    if not match:
        return text, ""
    return match.group(1).strip(), match.group(2).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def shot(
    index: int,
    start: float,
    end: float,
    title: str,
    visual_action: str,
    camera: str,
    audio: str = "",
    continuity: str = "",
) -> dict:
    return {
        "shot_index": index,
        "start_sec": start,
        "end_sec": end,
        "title": title,
        "visual_action": visual_action,
        "camera": camera,
        "audio": audio,
        "continuity": continuity,
    }


def build_records() -> tuple[list[dict], list[dict]]:
    pirate_source = read_utf8("海盗舰队与巨兽激战提示词.md")
    pirate_video, pirate_image = split_pirate_prompt(pirate_source)
    capybara = read_utf8("搞笑做饭提示词.txt")
    owl = read_utf8("山地烧烤vlog提示词.txt")

    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    sources = [
        {
            "id": 1,
            "source_type": "local_md",
            "title": "海盗舰队与巨兽激战提示词",
            "locator": "海盗舰队与巨兽激战提示词.md",
            "accessed_at": now,
            "verification": "full_text",
            "notes": "包含视频提示词与生图提示词；时间轴为 0–15 秒，但原文末尾另写 10s，存在时长冲突。",
            "sha256": sha256_text(pirate_source),
            "raw_excerpt": pirate_source,
        },
        {
            "id": 2,
            "source_type": "local_txt",
            "title": "搞笑做饭提示词",
            "locator": "搞笑做饭提示词.txt",
            "accessed_at": now,
            "verification": "full_text",
            "notes": "10 秒、9:16、真人实拍与二维贴纸合成。",
            "sha256": sha256_text(capybara),
            "raw_excerpt": capybara,
        },
        {
            "id": 3,
            "source_type": "local_txt",
            "title": "山地烧烤 Vlog 提示词",
            "locator": "山地烧烤vlog提示词.txt",
            "accessed_at": now,
            "verification": "full_text",
            "notes": "10 秒、竖屏、真人实拍与二维贴纸合成。",
            "sha256": sha256_text(owl),
            "raw_excerpt": owl,
        },
        {
            "id": 4,
            "source_type": "x_video",
            "title": "单指局部时间冻结",
            "locator": X_URL,
            "accessed_at": now,
            "verification": "page_text_poster_video_metadata",
            "notes": (
                "页面确认：1920×1080 横屏、约 43.285 秒。封面为强日照城市广场，前景鸽群，"
                "背景游客与纪念性喷泉/建筑。作者未公开完整原始提示词；数据库中的提示词为"
                "依据视频页面、封面与帖文说明反推的可复用版本。"
            ),
            "sha256": sha256_text(X_POST),
            "raw_excerpt": X_POST,
        },
        {
            "id": 5,
            "source_type": "x_video",
            "title": "AI 外国人探店：暖色串烧餐厅广告",
            "locator": RESTAURANT_X_URL,
            "accessed_at": now,
            "verification": "page_text_poster_video_metadata",
            "notes": (
                "页面确认：1280×720 横屏、约 15.168 秒。帖子主题为不用真人请托、"
                "只用 AI 为商家制作外国人探店短片；可见画面为暖色餐厅环境中的烤串英雄镜头。"
                "作者未公开完整原始提示词，数据库内容为可复用反推版本。"
            ),
            "sha256": sha256_text(RESTAURANT_X_POST),
            "raw_excerpt": RESTAURANT_X_POST,
        },
        {
            "id": 6,
            "source_type": "x_video",
            "title": "夏祭射击摊：大熊奖品反弹与友情代打",
            "locator": SHOOTING_GALLERY_X_URL,
            "accessed_at": now,
            "verification": "page_text_full_video_frames_metadata",
            "notes": (
                "页面与媒体元数据确认：横屏 3760×2160、约 25.708 秒。已读取完整视频并按逐秒画面核对："
                "三名浴衣少女在黄昏夏祭射击摊，金发女孩先击倒小盒奖品，随后瞄准泰迪熊；"
                "软木塞被熊的柔软腹部弹回并撞到她额头，蓝发同伴接枪命中，最后把熊送给她。"
                "作者未公开完整原始提示词，数据库内容为依据帖文、完整画面与媒体规格反推的可复用版本。"
            ),
            "sha256": sha256_text(SHOOTING_GALLERY_X_POST),
            "raw_excerpt": SHOOTING_GALLERY_X_POST,
        },
        {
            "id": 7,
            "source_type": "x_video_thread",
            "title": "100 种动画风格试验：首批四个 15 秒微短片",
            "locator": ANIMATION_STYLES_X_URL,
            "accessed_at": now,
            "verification": "author_full_prompts_reference_prompts_full_video_frames_metadata",
            "notes": (
                "主视频为 1080×1920 竖屏合辑、60.3 秒，包含四个约 15 秒微短片："
                "graphite、pinscreen、particle flow、cel-banded CGI。作者在后续两条回复中"
                "公开了四份 16:9 角色与世界设定图提示词，以及四份 Seedance 2.0 完整视频提示词。"
                f"生图原文：{ANIMATION_STYLES_IMAGE_POST_URL}；视频原文：{ANIMATION_STYLES_VIDEO_POST_URL}。"
            ),
            "sha256": sha256_text(
                ANIMATION_STYLES_X_POST
                + ANIMATION_STYLES_IMAGE_POST_URL
                + ANIMATION_STYLES_VIDEO_POST_URL
            ),
            "raw_excerpt": ANIMATION_STYLES_X_POST,
        },
        {
            "id": 8,
            "source_type": "x_video",
            "title": "Seedance 2.0 日系二维瓶装咖啡城市晨间广告",
            "locator": STARBUCKS_ANIME_X_URL,
            "accessed_at": now,
            "verification": "author_full_prompt_video_metadata_thumbnail",
            "notes": (
                "作者在帖子正文中公开了完整英文 prompt，并注明使用 Seedance 2.0。"
                "原 prompt 要求 35 秒，公开视频媒体元数据为 31.201 秒、720×810（8:9）。"
                "内容结构为城市明亮早晨、便利店取瓶装拿铁、饮用、咖啡馆工作与朋友社交、"
                "最终产品瓶特写。数据库保留作者原文，并按实际媒体时长整理分镜。"
            ),
            "sha256": sha256_text(STARBUCKS_ANIME_PROMPT),
            "raw_excerpt": "Made with Seedance 2.0\n\nPrompt:\n\n" + STARBUCKS_ANIME_PROMPT,
        },
        {
            "id": 9,
            "source_type": "x_video",
            "title": "Seedance 2.0 河畔露营牛肉河粉烹饪动画",
            "locator": PHO_ANIME_X_URL,
            "accessed_at": now,
            "verification": "author_full_prompt_video_metadata_thumbnail",
            "notes": (
                "作者在帖子正文中公开完整英文 prompt，并注明使用 Seedance 2.0。"
                "公开视频媒体元数据为 12.5 秒、1280×720（16:9）。内容依次包含切大理石纹牛肉、"
                "准备姜、洋葱、整粒香料、泰国罗勒、豆芽和青柠；篝火铸铁锅熬制牛骨香料汤；"
                "米粉入碗、铺薄牛肉片、浇滚汤烫熟，最后以香草、辣椒、红洋葱和青柠装饰。"
            ),
            "sha256": sha256_text(PHO_ANIME_PROMPT),
            "raw_excerpt": "Made with Seedance 2.0\n\nPrompt:\n\n" + PHO_ANIME_PROMPT,
        },
        {
            "id": 10,
            "source_type": "x_video",
            "title": "GPT Image 2 + Seedance 曲奇牛奶 POV ASMR 广告",
            "locator": COOKIES_MILK_ASMR_X_URL,
            "accessed_at": now,
            "verification": "author_storyboard_prompt_author_video_prompt_video_metadata",
            "notes": (
                "作者在帖子正文中公开完整分镜板提示词与完整视频提示词，并注明使用 GPT Image 2、"
                "Seedance 和 Pollo AI。原提示词要求 15 秒、16:9、4K HDR、24 fps；公开视频"
                "媒体元数据为 14.778 秒、1076×1330（竖向约 4:5）。视频结构为曲奇盒介绍、"
                "拆包装、倒牛奶、蘸曲奇、掰开曲奇和产品英雄镜头，全程只有 POV 双手与自然 ASMR。"
            ),
            "sha256": sha256_text(
                COOKIES_MILK_STORYBOARD_PROMPT + COOKIES_MILK_VIDEO_PROMPT
            ),
            "raw_excerpt": (
                "ASMR of Cookies and Milk created on @itsPolloAI\n\n"
                "GPT Image 2 and Seedance\n\nStoryboard Prompt:\n\n"
                + COOKIES_MILK_STORYBOARD_PROMPT
                + "\n\nVideo:\n\n"
                + COOKIES_MILK_VIDEO_PROMPT
            ),
        },
        {
            "id": 11,
            "source_type": "x_video",
            "title": "咖啡杯里的灯塔海洋：云海微缩梦境",
            "locator": COFFEE_LIGHTHOUSE_X_URL,
            "accessed_at": now,
            "verification": "page_text_video_frames_metadata",
            "notes": (
                "作者帖文仅写“May your coffee taste great today! Happy Monday!”，未公开生成模型或"
                "原始提示词。媒体元数据为 10.041 秒、832×1104（竖向约 3:4）。已核对开场、"
                "4 秒、7 秒与结尾画面：透明玻璃杯悬置于厚重云海/奶泡之中，杯内是青绿色微缩"
                "海洋与暖光灯塔；浪峰持续围绕灯塔起伏、破碎和重组，灯塔光束扫过水面。数据库"
                "内容为依据帖子、关键帧与媒体规格反推的可复用版本，并非作者原始提示词。"
            ),
            "sha256": sha256_text(COFFEE_LIGHTHOUSE_X_POST),
            "raw_excerpt": COFFEE_LIGHTHOUSE_X_POST,
        },
    ]

    x_master = """生成一段约 43 秒、16:9 横屏、1920×1080 的超写实城市街头短片。场景是正午强日照下的欧洲城市广场：浅色石板地面，前景有一群正在啄食、走动和振翅的鸽子，背景游客持续穿行，有人推婴儿车、交谈、坐在纪念性喷泉或台阶旁，历史建筑立面清晰可见。使用自然手持或稳定器跟拍，真实手机/纪录片摄影质感，硬朗日光与清晰长阴影，连续空间关系。

核心效果是“局部时间冻结”，不是全画面定格。先用数秒建立完全正常、充满细微运动的广场。镜头靠近一名正在自然行走或转身的目标人物，拍摄者的一只手从镜头前景伸入，食指准确轻触目标。接触的精确一帧，只有被触碰的人物瞬间冻结在动作中：脚停在迈步中段，手臂、衣物、头发、表情和身体重心全部像被真实物理约束锁住；目标不能漂移、抖动、变形或继续呼吸式摆动。触碰者的手可以离开。

冻结期间，除目标外的一切保持正常时间和真实物理：鸽群继续啄食、行走、起飞和投下移动阴影；背景行人从目标前后穿过；婴儿车继续前进；远处人物继续交谈；阳光、风吹衣角和城市环境保持活跃。镜头缓慢横移并绕目标形成视差，清楚证明这是一个被局部锁定的人，而不是整帧暂停。冻结保持数秒，画面不使用魔法光效、发光描边、粒子爆炸或绿幕痕迹。

随后食指再次轻触同一目标，人物从被冻结的精确姿态无缝恢复原有动量，继续未完成的步伐或转身；动作速度、重心与衣物惯性自然衔接，周围世界从未中断。结尾用一个稍宽镜头让目标融回人群，鸽子继续活动。

节奏结构：先建立活世界，再清楚展示触碰触发点，再长时间证明“目标冻结、环境继续”，最后二次触碰释放。电影级真实感，连续镜头优先，真实人体、真实鸽群动力学、自然景深、稳定身份与服装一致性。"""

    restaurant_master = """生成一支约 15 秒、16:9 横屏的电影感餐饮探店广告。核心概念：不用真人请托，用 AI 生成一名自然可信的外国游客完成一次中国串烧餐厅探店。全片保持同一个人物：约 30 岁的外国男性旅行者，短棕发、浅色亚麻衬衫、深色休闲裤，表情友善克制，脸型、发型、服装、身高和肤色全程一致。环境是一家温暖、有烟火气的木质串烧餐厅，琥珀色吊灯、深色木桌、开放式烤台、轻微炭火烟雾与暖色背景散景。

[00:00-00:02.5] 用简洁的餐厅入口或门头建立镜头开场。外国游客从街边走近并自然进入餐厅，动作像真实旅行 Vlog，不看镜头摆拍。相机使用稳定器轻跟拍，迅速建立“外国游客探店”的人物身份和地点。

[00:02.5-00:05.5] 游客坐到木质吧台旁，与店员自然点头交流，观察菜单和开放式烤台。使用肩后中景与正侧面中近景快速切换，保持视线和空间方向一致。表演克制，不夸张大笑，不做网红式指镜头动作。

[00:05.5-00:09] 切入高食欲感制作蒙太奇：肉串在炭火上翻面，油脂滋滋冒泡，孜然与辣椒粉落下，火焰短促跃起，刷酱形成晶亮焦化表面。使用微距特写、浅景深、低角度掠过烤架和一次短促慢动作；油脂、烟雾、火焰与香料遵守真实物理。

[00:09-00:12.5] 烤串上桌，游客拿起一串自然品尝，先感受味道，再露出真实而含蓄的惊喜反应，轻轻点头表示认可。中近景保持人物脸部与食物同框，再补一个手持烤串和焦化纹理的特写。咀嚼动作自然，手指结构正确，竹签不穿透手掌或面部。

[00:12.5-00:15.168] 以菜品英雄镜头收尾：多串焦香烤肉整齐铺在深色陶盘中，搭配烤青椒、蒜瓣或少量蔬菜，放在深色木桌上；镜头从低角度缓慢横移并轻微推近，前景肉串油亮、孜然颗粒和焦边清晰，背景是虚化的暖色餐厅灯光与烤台火光。停留足够时间形成商用封面，不生成随机品牌文字。

整体风格：高端但真实的本地餐饮广告 × 外国游客旅行 Vlog × 美食微距摄影。色彩为暖琥珀、焦糖棕、炭火橙与深木色；高光不过曝，食物保持真实质感。剪辑节奏先人物、再制作、再品尝、最后菜品英雄镜头，镜头之间动作与视线连续。声音设计包括门店环境底噪、炭火滋滋声、撒料声、盘子落桌声和克制的轻快旅行音乐，最后英雄镜头突出烤串滋滋声。"""

    shooting_gallery_master = """生成一段约 25.7 秒、16:9 横屏、日系二维动画质感的夏祭轻喜剧短片。时间是黄昏入夜前，紫粉色天空与远山作背景，射击摊悬挂一排暖黄色纸灯笼，木制奖品架摆满粉、紫、奶油黄与薄荷绿的马卡龙、写有数字“2”的小盒和一只奶油色泰迪熊。画面采用柔和赛璐璐上色、细腻线稿、浅景深与温暖灯笼光，保持手绘动画的柔软质感。

全片锁定三名少女：主角是娇小的浅金色短发女孩，侧后方系蓝色小发带，穿淡黄色花纹浴衣与蓝色腰带；粉色高马尾少女穿红色樱花浴衣；蓝色短发少女穿深蓝花纹浴衣，手里拿一串红色三色丸子。三人的发型、浴衣花纹、腰带颜色、身高差、脸型和站位关系在所有镜头中保持一致。道具是一把木制软木塞射击枪，枪管、枪托和软木塞尺寸稳定。

[00:00-00:04.5] 从枪管主观近景切到摊位侧面中景。浅金发女孩在两位同伴注视下端枪瞄准下层一排数字盒，扣动扳机；软木塞沿清楚的直线飞出，连续带倒数个轻小纸盒，盒子依次倾斜、翻落，形成干净的多米诺式物理反应。穿插奖品架正面镜头，保证射击方向与盒子倒落方向一致。

[00:04.5-00:06.5] 中近景表现女孩因命中小奖品而自信微笑，随即抬高枪口，把目标转向上层马卡龙之间的奶油色泰迪熊。镜头从她的眼神切到泰迪熊，建立新的瞄准关系。

[00:06.5-00:10.5] 用夸张但物理清楚的喜剧特写展示第一次挑战大熊：软木塞撞进泰迪熊柔软的绒毛腹部，表面明显凹陷并把能量弹回；软木塞反向飞回，轻轻撞到女孩额头。切回她的反应特写，额头出现红色二维旋涡形怒气符号，她惊讶又不服气。泰迪熊保持原位，没有被第一枪击倒。

[00:10.5-00:16.5] 女孩再次认真举枪，两位同伴与她同框：粉发少女温柔鼓励，蓝发少女安静观察。使用正面中景、枪口与眼睛的紧张特写，再回到三人中景。女孩屏息瞄准但仍难以撼动泰迪熊，随后蓝发少女从她手中平稳接过木枪。

[00:16.5-00:19.5] 蓝发少女冷静完成一次准确射击。切到奖品架正面：软木塞命中泰迪熊腹部中心，留下清楚的圆形命中点，熊随后失去平衡向前翻倒。动作顺序必须是“命中—短暂停顿—翻倒”，马卡龙和周围奖品只发生轻微碰撞，不凭空跳动。

[00:19.5-00:22.5] 从三人背面中景切到正面。摊主的手从画面左侧递出赢得的泰迪熊，蓝发少女先接过，再把熊送到浅金发女孩怀里。女孩从失落转为惊喜，双手抱紧玩偶；粉发少女微笑看着她们。

[00:22.5-00:25.7] 三名少女并肩离开射击摊。蓝发少女继续拿着红色丸子，浅金发女孩抱着泰迪熊走在两人之间或稍后方。最后切近女孩的脸与熊，她闭眼露出满足笑容，以暖灯笼与奖品架虚化背景收尾。

镜头语言：枪管主观近景、摊位正面与侧面中景、软木塞飞行特写、柔软绒毛受击微距、额头反应特写、三人关系中景、领奖背面镜头、温暖笑容近景。剪辑节奏清楚，动作轴线统一，软木塞飞行、反弹、命中和泰迪熊翻倒遵守连续物理。声音可包含夏祭人群底噪、远处铃鼓与摊位声、软木枪“噗”的轻响、纸盒翻落声、软木塞弹回的滑稽音、泰迪熊落架的闷响和温柔轻快的日系配乐。"""

    mira_image = """Asset type: 16:9 animation production character-and-world sheet
Primary request: Create a clean landscape production sheet for an original character named Mira Quill in graphite motion-study animation.
Subject: Mira Quill, a slim adult wind-archive courier with a short asymmetrical bob, angular oval face, long split-tail field coat, narrow trousers, ankle boots and compact satchel. Original design, no resemblance to an existing character.
Style/medium: graphite on warm animation paper, visible construction lines, soft smudging, erased highlights, controlled line boil implied in the action strip, selective muted ochre accents.
Layout: one large full-body three-quarter hero; smaller front, side and back views; head close-up with neutral and curious expressions; three-step walk silhouette strip; Aeroseed prop callout; wide archive-courtyard environment panel; stone and paper-streamer material details; four-value palette.
Environment: open wind-worn archive courtyard with high arches, paper streamers and stone paving.
Text (verbatim): "AS-004  MIRA QUILL"
Constraints: landscape 16:9, full bodies visible, generous margins, consistent face and clothing across every view, one character only, exact same satchel and coat, no photorealism, no colour except muted ochre accent, no logos, no watermark, no extra text."""

    mira_video = """AS-004 — Mira Quill: “Draw the Way”

@ Image1 controls MIRA's original identity, face, asymmetrical bob, split-tail coat, satchel, proportions, Aeroseed, graphite-on-warm-paper medium, ochre accent and archive architecture. Use it as identity, style, prop and world reference only; do not reproduce the sheet layout, white background, panels, labels or text. Preserve MIRA and her wardrobe across every cut.

Create one fast 15-second micro-story with five explicit cuts. Graphite animation on warm paper: visible construction lines, purposeful contour boil, smears, erased highlights and animation on twos.

Shot 1 (2s): Extreme close-up—the courtyard floor erases itself into a white void racing toward MIRA's boot; rapid pencil-scratch push-in; sharp eraser hiss.
Shot 2 (3s): Wide lateral track—MIRA sprints left-to-right as arches and paper streamers vanish behind her in sweeping erased strokes; coat and satchel follow through; urgent dry percussion.
Shot 3 (3s): Medium profile—at the broken edge MIRA skids, swings the satchel forward, and the ochre Aeroseed bursts free; camera stops with her; scrape, heartbeat, bright chime.
Shot 4 (4s): Low-angle tracking—MIRA leaps as the Aeroseed draws one bold graphite line through empty space; the line thickens into a bridge beneath each landing foot and redraws the courtyard outward in fast construction passes; percussion peaks.
Shot 5 (3s): Crane back to wide—MIRA lands in a stable three-quarter pose while the final arch sketches itself complete and loose graphite birds lift from the page; music resolves on one pencil tap.

One character, no dialogue, no photorealism or 3D, no face drift, no costume change, no extra limbs, no generated text. End on a complete readable hero frame."""

    orin_image = """Use case: infographic-diagram
Asset type: 16:9 animation production character-and-world sheet
Primary request: Create a clean landscape production sheet for an original character named Orin Vale rendered as physical pinscreen shadow relief.
Subject: Orin Vale, a sturdy adult nocturnal signal keeper with short swept hair, strong profile, high collar, asymmetric shoulder cape, long tapered gloves, broad cropped trousers and heavy boots. Original design.
Style/medium: physical pinscreen relief made from thousands of pin-tip shadows, oblique side lighting, embossed monochrome gradients, velvety black-to-white stipple, no charcoal or pencil texture.
Layout: one large full-body three-quarter hero; smaller front, side and back relief views; profile head close-up with calm and curious expressions; three-step walk silhouette strip; raised-light Aeroseed callout; wide terraced night-plaza environment panel; pin-depth and shadow-ripple detail; four-value grayscale palette.
Environment: terraced nocturnal plaza with arched signal towers and rolling relief fog.
Text (verbatim): "AS-058  ORIN VALE"
Constraints: landscape 16:9, full bodies visible, generous margins, consistent profile, cape and boots in every view, one character only, strict monochrome, unmistakable pinscreen texture, no colour, no text except the exact title, no logos, no watermark."""

    orin_video = """AS-058 — Orin Vale: “The Last Signal”

@ Image1 controls ORIN's original identity, profile, high collar, asymmetric cape, gloves, boots, Aeroseed, terraced signal plaza and physical pinscreen relief. Use it as identity, style, prop and world reference only; do not reproduce the sheet layout, white background, panels, labels or text. Preserve ORIN's silhouette across every cut.

Create one tense 15-second micro-story with five explicit cuts. Strict monochrome physical pinscreen: thousands of pin-tip shadows, fixed oblique side light, embossed depth and velvety black-to-white gradients.

Shot 1 (2s): Macro—a luminous signal tower collapses into flat black pin depth; locked camera, pins retract in a fast circular chain; metallic pin whisper and one alarm knock.
Shot 2 (3s): Extreme wide—the black relief tide races across the terraces extinguishing towers toward ORIN; high-angle pan follows the tide, not the character; low drum pulse grows.
Shot 3 (3s): Medium low angle—ORIN steps in front of the final beacon, plants both boots, and raises the white Aeroseed to shoulder height; slow push-in ends on his resolved profile; cape settles, bass hit.
Shot 4 (4s): Overhead—the Aeroseed releases three concentric pressure rings; pins rise behind each ring, reversing the black tide and rebuilding stairs, arches and fog in luminous relief; camera remains overhead; tactile rolling thunder moves in stereo.
Shot 5 (3s): Wide profile—the last tower snaps upright and throws a white beam across the plaza; ORIN lowers his arm as relief fog parts around him; restrained brass note and final pin click.

One character, no dialogue, no colour, no pencil, charcoal, smoke simulation or CGI gloss, no face drift, no costume change, no generated text. Keep side-light direction physically consistent and end on a readable silhouette."""

    kade_image = """Asset type: 16:9 animation production character-and-world sheet
Primary request: Create a clean landscape production sheet for an original character named Kade Flux in ink-contour cel-banded CGI.
Subject: Kade Flux, an athletic adult urban wind-grid mechanic with swept dark hair, clean graphic facial planes, angular cropped jacket, one asymmetric shoulder panel, tapered utility trousers and sturdy boots. Original design, not a superhero.
Style/medium: non-photorealistic stylized 3D, two-to-four cel-shaded light bands, variable dark ink contours, flat graphic shadow shapes, pale stone surfaces with teal and amber accents, no realistic skin shading.
Layout: one large full-body three-quarter hero; smaller front, side and back views; head close-up with neutral and alert-curious expressions; three-step walk/action silhouette strip; amber Aeroseed with two teal orbit rings; wide modular rooftop wind-plaza environment panel; line-weight and cel-shadow detail; four-colour palette.
Environment: modular rooftop plaza with geometric turbines, suspended rings and block architecture.
Text (verbatim): "AS-061  KADE FLUX"
Constraints: landscape 16:9, full bodies visible, generous margins, identical jacket, face and proportions across every view, one character only, stable dark contours, no photorealism, no glossy plastic skin, no brand marks, no watermark, no extra text."""

    kade_video = """AS-061 — Kade Flux: “Restart the Sky”

@ Image1 controls KADE's original identity, swept hair, angular jacket, amber shoulder panel, trousers, boots, Aeroseed, teal-and-amber palette and rooftop wind plaza. Use it as identity, style, prop and world reference only; do not reproduce the sheet layout, white background, panels, labels or text. Preserve KADE's face, contour design and wardrobe across every cut.

Create one propulsive 15-second micro-story with five explicit cuts. Non-photoreal 3D with stable variable-width ink contours, two-to-four cel-light bands, graphic shadows and angular held poses punctuated by short motion bursts.

Shot 1 (2s): Extreme close-up—a turbine ring fractures and amber power arcs toward camera; snap zoom ends on the crack; electric pop and immediate drum hit.
Shot 2 (3s): Wide 24mm lateral track—KADE races left-to-right across the rooftop while the dead turbine collapses behind him in clean geometric pieces; one action pose per beat, teal speed accents.
Shot 3 (3s): Ground-level medium—KADE drops into one controlled knee slide beneath a falling ring and catches the hovering Aeroseed against his forearm guard; camera tracks with the slide and stops at contact; metal scrape, syncopated hit.
Shot 4 (4s): Rising three-quarter shot—KADE redirects the Aeroseed into the turbine core; one amber shock pulse travels through every suspended ring as cel bands switch from shadow to teal light across the skyline; camera cranes with the energy path; synth rises.
Shot 5 (3s): Low hero wide—the turbine locks into rotation behind KADE, wind snaps his jacket once, and the city lights answer in graphic bands; hold the final half-second on a clean silhouette; turbine thrum and decisive two-note finish.

One character, no dialogue, no photoreal skin, glossy plastic, contour crawl, face drift, costume change, extra fingers or generated text. Every cut must end after its action lands."""

    nia_image = """Asset type: 16:9 animation production character-and-world sheet
Primary request: Create a clean landscape production sheet for an original character named Nia Vector in coherent particle-flow animation.
Subject: Nia Vector, a tall adult flow-field cartographer with rounded bob, simple luminous eyes, short structured cape, fitted tunic, wide cuffs and slim boots. Her body is a stable readable silhouette constructed from thousands of cyan and muted-violet luminous particles with denser points around the face and hands.
Style/medium: coherent point-cloud animation concept, force-driven particle currents, controlled density, soft alpha trails, dark spatial background, gold-white Aeroseed, no chaotic noise.
Layout: one large full-body three-quarter hero; smaller front, side and back particle silhouettes; head close-up with neutral and curious expressions; three-step walk/action silhouette strip; dense gold-white Aeroseed with two cyan particle arcs; wide flow-field environment panel; particle-density and current-path detail; four-colour palette.
Environment: midnight spatial field with flowing contour lines, sparse pylons and organized particle currents.
Text (verbatim): "AS-096  NIA VECTOR"
Constraints: landscape 16:9, full bodies visible, generous margins, same cape, face silhouette and colour-density pattern in every view, one character only, particles must form a legible body, no explosion, no random debris, no photoreal human skin, no logos, no watermark, no extra text."""

    nia_video = """AS-096 — Nia Vector: “Map the Storm”

@ Image1 controls NIA's original identity, rounded bob, luminous eyes, structured cape, tunic, cuffs, boots, cyan-violet density pattern, gold-white Aeroseed and flow-field world. Use it as identity, style, prop and world reference only; do not reproduce the sheet layout, white background, panels, labels or text. Keep her face and torso densely legible across every cut.

Create one escalating 15-second micro-story with five explicit cuts. Coherent point-cloud animation: force-driven advection, organized contour currents, controlled density shifts and soft trails; particles always follow readable vector paths.

Shot 1 (2s): Macro—the gold Aeroseed flickers as a violent cyan current bends backward and tears a dark hole through the map; rapid rack focus from seed to rupture; granular crack and sub-bass drop.
Shot 2 (3s): Extreme wide—the particle storm funnels toward the pylons and strips their outer points away; camera dives along one contour line toward NIA; accelerating airy pulse.
Shot 3 (3s): Medium frontal—NIA braces, opens both arms, and deliberately releases only her cape edge and outer silhouette into two controlled streams; slow push-in ends on her stable eyes; sound briefly drops to a heartbeat.
Shot 4 (4s): Overhead orbit—the two streams wrap the storm, bend its vector path into a luminous spiral, and pull the dark rupture closed; NIA's face and torso remain intact; granular crescendo circles in stereo.
Shot 5 (3s): Crane up—the streams rejoin NIA completely as thousands of ground particles illuminate into a vast city-map constellation beneath her; she turns into a clear three-quarter hero silhouette; warm chime and deep resolved pulse.

One character, no dialogue, no explosion, random debris, chaotic noise, face dissolution, missing limbs, colour drift, costume change or generated text. Finish fully reassembled with no loose particles crossing the face."""

    starbucks_anime_video = STARBUCKS_ANIME_PROMPT
    pho_anime_video = PHO_ANIME_PROMPT
    cookies_milk_storyboard = COOKIES_MILK_STORYBOARD_PROMPT
    cookies_milk_video = COOKIES_MILK_VIDEO_PROMPT
    coffee_lighthouse_master = """生成一段约 10 秒、3:4 竖幅的超现实电影感微缩景观视频。主体是一只透明、厚壁、带圆形把手的玻璃咖啡杯，完整居中悬置在无边的白灰色云海与细密奶泡之间。杯中不是普通咖啡，而是一片深邃通透的青绿色微缩海洋；杯壁必须保持稳定、可见折射、焦散与水下纹理。海面中央始终只有一座奶白色圆柱灯塔，红棕色塔顶，底部立在极小的暗色礁石上，塔灯发出温暖琥珀光并缓慢扫过水面。

[00:00-00:02.5] 从略高的正面中近景建立完整玻璃杯。左侧海面升起一堵比例夸张但细节真实的卷浪，浪尖翻白并朝灯塔弯曲；灯塔位于杯内偏右，暖灯与冷青海水形成强烈对比。镜头极缓慢推近，云层像浓密奶泡一样在杯底和远景轻柔流动。

[00:02.5-00:05] 海浪沿杯口绕行并暂时回落成旋涡，水面反射灯塔双向扫动的金色光束。镜头轻微横移和下沉，让透明杯壁的折射、水线、气泡与水下流动更清晰。灯塔结构、杯把方向与杯体尺寸保持不变。

[00:05-00:07.5] 灯塔与小礁石逐渐成为画面视觉中心，海面短暂舒展后再次聚集能量。灯光横向扫过云层和波纹，水面形成明亮金色反射带；镜头缓慢环绕几度，制造微缩世界的立体视差，但不切换场景。

[00:07.5-00:10.041] 新一轮高浪从杯内后侧抬升，卷过灯塔周围并在杯口边缘炸成细碎水花；浪体不能溢出成无规则洪水，必须始终像被杯中微缩物理约束。结尾停在灯塔仍然清晰、浪峰形成优美弧线、暖光穿透水雾的英雄画面。

整体风格：超现实微缩摄影、梦境咖啡意象、宏观食物广告质感与海洋电影摄影融合；真实玻璃折射、体积云、体积光、细腻水花、动态焦散、浅景深、柔和胶片颗粒、冷青与暖金互补调色。镜头运动稳定舒缓，所有形变连续，无硬切、无文字、无人物、无品牌。声音可使用低沉而柔和的海浪拍击、细小水滴、远风、极轻灯塔机械转动声与克制的梦幻氛围音，无对白。"""
    coffee_lighthouse_image = """超现实微缩摄影，一只透明厚壁玻璃咖啡杯完整居中，圆形金色玻璃把手朝右，杯子悬置在无边白灰色云海与细密奶泡之中；杯内盛着通透的青绿色微缩海洋，一座奶白色圆柱灯塔立在小型暗色礁石上，红棕色塔顶发出温暖琥珀光束；一堵高细节卷浪沿杯口弯曲，白色浪花在灯塔旁飞溅，水下焦散、玻璃折射、冷凝高光和金色反射带清晰可见。冷青海水与暖金灯光互补，电影级体积云与体积光，微距镜头，浅景深，精致梦境广告质感，写实水体物理，3:4 竖幅，无人物、无文字、无品牌、无水印。"""

    prompts = [
        {
            "id": 1,
            "source_id": 1,
            "slug": "fantasy-pirate-fleet-vs-leviathan",
            "title": "奇幻海盗舰队大战利维坦",
            "category": "电影级奇幻动作 / Boss 战",
            "language": "zh-CN",
            "aspect_ratio": "16:9",
            "duration_sec": 15.0,
            "resolution": "4K",
            "style_summary": "奇幻海盗 × 巨型 Boss 战 × AAA 电影级海战 CG",
            "scene_summary": "暴风雨深海、五艘木制战舰、磷光巨兽、巨浪与闪电。",
            "subject_summary": "粉色卷发、黑金三角帽、酒红长裙的海盗女船长，对抗山脉般的利维坦。",
            "core_mechanic": "绳索摆荡与细剑的敏捷战斗，对抗巨兽冲撞、撕咬、翻滚和倾覆。",
            "camera_language": "低角度、甲板追踪、摆动主观视角、脊背跟拍、翻覆全景、横向追踪、闪电定格。",
            "lighting_color": "铅黑风暴天、深绿海洋、磷光绿、酒红与金色、橙色炮火、蓝白闪电。",
            "audio_design": "暴雨、巨浪、木船断裂、炮火齐射、巨兽咆哮、绳索与帆布声。",
            "continuity_rules": "船长外形、服装、武器严格一致；海洋与船体破坏遵守重量感和流体动力学。",
            "master_prompt": pirate_video,
            "negative_prompt": "角色换装或变脸，船只数量无故变化，巨兽尺寸漂移，海水像固体或烟雾，低重量感，静态海面，穿模，额外肢体，低清晰度，水印，logo。",
            "reference_image_prompt": pirate_image,
            "recommended_models": "Seedance 2.0 / Veo / Kling / Sora（按平台拆分为多镜头生成）",
            "prompt_origin": "local_source_full_text",
            "quality_notes": "原文时间轴为 15 秒，但结尾写 10s；数据库按时间轴记录 15 秒。",
            "tags": ["奇幻", "海盗", "巨兽", "Boss战", "海战", "动作", "CG", "16:9", "角色一致性", "流体物理"],
            "shots": [
                shot(1, 0, 3, "巨兽破海毁舰", "巨兽拖着水墙冲出海面，咬断侧翼护卫舰；船长抓断绳摆荡离舰。", "从巨兽低角度切到倾斜甲板追踪，再沿摆荡弧线跟随。", "巨浪、木船断裂、帆索绷紧。", "船长造型与旗舰方位保持一致。"),
                shot(2, 3, 6, "索具追逐与舷炮齐射", "船长在横桁、前桅和帆索间疾驰，巨兽三次撕咬落空，舷炮轰击颈部。", "摇摆视角与横向跟踪交替，加入逆光轮廓。", "炮火齐射、帆布撕裂、巨兽尖啸。", "动作路径可追踪，三次攻击因果清晰。"),
                shot(3, 6, 9, "登上巨兽", "船长落上巨兽颈部鳞片，奔跑刺击、侧滚并刺入骨冠底部，随后借绳荡回船。", "手持脊背跟拍，随巨兽翻滚，末尾快速拉远。", "鳞片摩擦、绿色磷光爆裂、咆哮。", "细剑位置、鳞片损伤和绳索来源连续。"),
                shot(4, 9, 12, "水下伏击与逃亡", "巨兽从另一侧跃出并掀翻两舰，旗舰掠过漩涡和暗礁逃向风暴。", "破坏全景后横向追踪舰队航线。", "短暂死寂后爆发水下冲击、船体折断。", "舰队剩余船只数量与受损状态延续。"),
                shot(5, 12, 15, "冲入风暴眼", "旗舰冲入雷云，巨兽从船尾逼近；船长举剑，舰队齐射，闪电中定格。", "船尾楼中景逐步拉远，最终闪电定格。", "雷鸣、炮火、海浪与命令声叠加。", "高潮延续追逐，不突然切换地点。"),
            ],
        },
        {
            "id": 2,
            "source_id": 2,
            "slug": "capybara-kitchen-salt-prank",
            "title": "水豚噜噜厨房倒盐恶作剧",
            "category": "真人实拍 + 2D 贴纸荒诞喜剧",
            "language": "zh-CN",
            "aspect_ratio": "9:16",
            "duration_sec": 10.0,
            "resolution": "8K",
            "style_summary": "真实厨房 POV 与扁平二维贴纸角色合成，快速硬切喜剧。",
            "scene_summary": "居家厨房、黑铁锅、牛肉青菜、白瓷砖、自然侧光。",
            "subject_summary": "头顶小橘子的二维水豚噜噜与真人双手。",
            "core_mechanic": "整罐倒盐 → 锅铲敲头 → 爆哭塞盐 → 齁到纸片式倒地。",
            "camera_language": "手机广角、第一人称俯拍、中近景、轻微手持晃动、四段快速硬切。",
            "lighting_color": "真实柔和自然侧光；2D 角色使用扁平色块、粗黑描边和白色贴纸边。",
            "audio_design": "滋滋声、盐粒沙沙声、Duang、卡通爆哭、咕咚、倒地和灵魂升天音效。",
            "continuity_rules": "厨房方向、灶台、角色位置、头身比、服装、色板和描边宽度全程锁定。",
            "master_prompt": capybara,
            "negative_prompt": "水豚变成 3D 玩偶，贴纸接受真实立体重打光，角色漂移闪烁，服装变化，盐像液体或烟雾，锅铲穿透面部，真实伤害或血腥，多余肢体，空间跳变。",
            "reference_image_prompt": "",
            "recommended_models": "Seedance 2.0 / Kling / Veo（建议提供角色参考图）",
            "prompt_origin": "local_source_full_text",
            "quality_notes": "完整时间轴与连续性约束齐全。",
            "tags": ["搞笑", "厨房", "POV", "真人实拍", "2D贴纸", "水豚", "9:16", "角色一致性", "短视频"],
            "shots": [
                shot(1, 0, 3, "整罐倒盐", "水豚把整罐真实白盐倒入翻炒牛肉和青菜的铁锅，堆成盐山。", "第一人称俯视中近景。", "滋滋声、盐粒沙沙声。", "盐粒遵守真实颗粒、重力和碰撞。"),
                shot(2, 3, 5, "夺罐敲头", "真人夺走盐罐并用锅铲轻敲一次，二维红色肿包弹出。", "同方向稍近构图，快速硬切。", "金属 Duang 与弹簧音。", "小橘子保留，肿包位于其旁边。"),
                shot(3, 5, 8, "爆哭与塞盐", "二维蓝色泪水喷泉；真人铲起盐和青菜送到嘴前，水豚腮帮鼓起。", "保持同一构图。", "爆哭、刮盐、啵。", "锅铲不穿透角色，泪水保持 2D。"),
                shot(4, 8, 10, "齁到倒地", "水豚脸红、褪白、X 眼，纸片式后仰倒下，星星与灵魂白烟出现。", "末 0.3 秒定格。", "咕咚、咯噔、咚、滑稽收尾音。", "橘子和肿包保留，褪白不改变角色结构。"),
            ],
        },
        {
            "id": 3,
            "source_id": 3,
            "slug": "mountain-bbq-owl-sticker-vlog",
            "title": "山地烧烤 Vlog：猫头鹰偷肉",
            "category": "户外 Vlog + 2D 贴纸搞笑短视频",
            "language": "zh-CN",
            "aspect_ratio": "9:16",
            "duration_sec": 10.0,
            "resolution": "8K",
            "style_summary": "真实高海拔露营与平面剪纸猫头鹰形成强反差。",
            "scene_summary": "日落山地营地、石烤架、木炭、牛肉、群山、松树和薄雾。",
            "subject_summary": "只有牛肉三分之一大小的二维猫头鹰咕咕与逼真人手。",
            "core_mechanic": "偷肉 → 被敲出肿包 → 生气跺脚 → 扑向手并啄击。",
            "camera_language": "第一人称俯视、手持微抖、竖屏 Vlog、四段紧凑动作。",
            "lighting_color": "温暖落日与火红木炭；角色保持无真实重打光的二维平面纹理。",
            "audio_design": "木炭滋滋、撕肉、咚、弹簧、哼、跺脚、啄击与翅膀拍击。",
            "continuity_rules": "露营地、烤架、牛肉、人手入口方向、角色尺寸、贴纸质感和肿包连续。",
            "master_prompt": owl,
            "negative_prompt": "猫头鹰变成真实动物或 3D 玩偶，角色尺寸漂移，真实光照重塑贴纸，穿模，手部畸形，真实伤害或血腥，背景跳变，肉与油花失去物理重量，额外翅膀或脚。",
            "reference_image_prompt": "",
            "recommended_models": "Seedance 2.0 / Kling / Veo（建议提供角色参考图）",
            "prompt_origin": "local_source_full_text",
            "quality_notes": "原提示词为单段长文本，数据库已拆成四条分镜。",
            "tags": ["搞笑", "山地", "烧烤", "Vlog", "POV", "真人实拍", "2D贴纸", "猫头鹰", "9:16", "短视频"],
            "shots": [
                shot(1, 0, 3, "猫头鹰偷肉", "猫头鹰跳上烤架边缘，撕下一大块熟牛肉塞进口中，肉屑和油花飞溅。", "第一人称俯视。", "木炭滋滋、兴奋叫声、撕肉声。", "角色仅为牛肉约三分之一大小。"),
                shot(2, 3, 5, "指关节敲头", "真人手轻敲猫头鹰脑袋，红色二维肿包弹出，身体上下弹跳。", "同一空间关系的近景。", "清脆咚声与弹簧声。", "无真实伤害，肿包后续保留。"),
                shot(3, 5, 7, "生气跺脚", "猫头鹰捂包、鼓腮、撅嘴、羽毛竖起并纸片式跺脚。", "保持构图，突出表情。", "哼声与咚咚跺脚。", "嘴里仍有少量肉丝。"),
                shot(4, 7, 10, "攻击真人手", "眼中闪火，猫头鹰扑到手上啄手指并拍打手背，最终定格。", "近距离动作跟随。", "快速叫声、啄击、拍翅与冲击音。", "贴纸粘附关系稳定，红色肿包仍在。"),
            ],
        },
        {
            "id": 4,
            "source_id": 4,
            "slug": "localized-time-freeze-city-square",
            "title": "单指局部时间冻结：城市广场",
            "category": "超写实概念 VFX / 时间操控",
            "language": "zh-CN",
            "aspect_ratio": "16:9",
            "duration_sec": 43.285,
            "resolution": "1920×1080",
            "style_summary": "自然日光城市纪录片质感，无后期痕迹的局部时间冻结。",
            "scene_summary": "强日照欧洲城市广场，石板地、鸽群、游客、婴儿车、纪念性喷泉与历史建筑。",
            "subject_summary": "前景食指触碰一名移动中的行人；只有目标人物被冻结。",
            "core_mechanic": "单指触碰精确触发局部冻结；目标保持物理锁定，周围世界继续；二次触碰无缝释放。",
            "camera_language": "广场建立镜头、近距离触发、持续跟拍与绕行视差、稍宽收尾；连续镜头优先。",
            "lighting_color": "正午自然硬光，高反差、清晰长阴影、真实石材与肤色。",
            "audio_design": "真实城市环境音、鸽群振翅与脚步；触碰可用极轻微低频提示，避免魔法音效。",
            "continuity_rules": "只有目标冻结；目标身份、服装、姿势和接触点锁定；其他行人、鸽子、阴影和相机持续运动。",
            "master_prompt": x_master,
            "negative_prompt": "全世界一起冻结，整帧定格，背景行人或鸽子停止，目标在冻结期漂移、眨眼或衣物摆动，慢动作代替冻结，跳切，镜头锁死，魔法光圈，发光描边，粒子爆炸，绿幕边缘，人物变脸，服装变化，肢体变形，重复行人或鸽子。",
            "reference_image_prompt": "",
            "recommended_models": "Seedance 2.0（作者说明所用模型）",
            "prompt_origin": "reconstructed_from_page_and_visual_evidence",
            "quality_notes": "不是作者公开原始提示词；依据帖文、封面与播放器元数据反推，场景事实与效果机制已核对。",
            "tags": ["时间冻结", "局部特效", "城市广场", "鸽子", "真人实拍", "VFX", "Seedance 2.0", "16:9", "连续镜头", "物理一致性"],
            "shots": [
                shot(1, 0, 7, "建立活着的广场", "鸽群啄食和走动，游客、婴儿车与远处人物持续穿行，建立正常时间。", "自然手持广角建立镜头，缓慢前进。", "脚步、城市底噪、鸽叫和振翅。", "所有可见元素先有明确运动，便于后续对比。"),
                shot(2, 7, 13, "锁定目标与伸手", "镜头靠近一名正在行走或转身的目标，食指从前景伸入并对准目标。", "从广角过渡到中近景，保持目标与背景同框。", "环境音持续。", "目标身份、服装和运动方向清晰。"),
                shot(3, 13, 15, "触碰精确触发", "指尖接触的精确一帧，只有目标停在动作中段，身体重心和衣物同时锁定。", "稳定展示接触点，不用硬切。", "可加入极轻微低频触发音。", "禁止全画面暂停；背景运动连续。"),
                shot(4, 15, 29, "证明局部冻结", "目标完全静止；鸽子继续走动或起飞，行人从前后穿过，婴儿车继续移动。", "缓慢横移并绕目标形成视差。", "城市与鸽群声音不间断。", "目标不眨眼、不漂移、不呼吸式摆动；其他一切正常。"),
                shot(5, 29, 36, "长时间物理保持", "从另一角度观察被冻结姿态，移动阴影和穿行人群进一步证明时间只锁定目标。", "中景绕行后轻微拉近细节。", "真实环境音。", "接触后姿态、衣褶和发丝精确保持。"),
                shot(6, 36, 40, "二次触碰释放", "食指再次触碰，目标从精确冻结姿势恢复原有速度和未完成动作。", "镜头保持连续，清楚看到动量恢复。", "轻微释放提示音后环境音不变。", "不能瞬移或从新姿势重新开始。"),
                shot(7, 40, 43.285, "融回人群", "目标继续离开或融入人群，鸽子仍在活动，广场保持自然。", "稍宽收尾镜头。", "自然城市声收尾。", "不加入解释性文字或魔法残留。"),
            ],
        },
        {
            "id": 5,
            "source_id": 5,
            "slug": "ai-foreign-diner-warm-skewer-restaurant",
            "title": "AI 外国人探店：暖色串烧餐厅广告",
            "category": "AI 商业广告 / 餐饮探店",
            "language": "zh-CN",
            "aspect_ratio": "16:9",
            "duration_sec": 15.168,
            "resolution": "1280×720",
            "style_summary": "电影感餐饮广告 × 外国游客旅行 Vlog × 暖色美食微距摄影。",
            "scene_summary": "暖色木质串烧餐厅、开放式烤台、炭火烟雾、深色木桌与烤串英雄盘。",
            "subject_summary": "同一名短棕发、浅色亚麻衬衫的外国男性旅行者，自然完成进店、点单与品尝。",
            "core_mechanic": "用 AI 虚拟探店人物串联门店空间、炭火制作、真实品尝反应和菜品英雄镜头。",
            "camera_language": "稳定器跟拍、肩后中景、人物与食物同框、微距制作蒙太奇、低角度菜品横移推近。",
            "lighting_color": "暖琥珀吊灯、焦糖棕与炭火橙，深木色背景和柔和散景，高光不过曝。",
            "audio_design": "门店环境声、炭火滋滋、撒料、刷酱、盘子落桌和克制的轻快旅行音乐。",
            "continuity_rules": "外国游客脸型、发型、服装与体型严格一致；餐厅方位、桌面、餐盘和烤串数量连续。",
            "master_prompt": restaurant_master,
            "negative_prompt": "人物换脸、年龄或国籍特征漂移、服装变化、假笑和夸张表演、手指畸形、竹签穿模、咀嚼异常、食物塑料感、油脂像胶水、烟雾穿透人物、火焰无物理来源、餐厅空间跳变、盘中烤串数量突变、随机品牌字、乱码字幕、水印、logo、过度磨皮、过曝高光。",
            "reference_image_prompt": "",
            "recommended_models": "Seedance 2.0 / Kling / Veo（建议锁定人物参考图与菜品参考图）",
            "prompt_origin": "reconstructed_from_page_and_visual_evidence",
            "quality_notes": "作者未公开完整原始提示词；人物探店流程为依据帖子主题构建的可复用广告结构，视频规格与烤串英雄画面已核对。",
            "tags": ["餐饮广告", "外国人探店", "AI演员", "串烧", "烤串", "美食微距", "旅行Vlog", "真人实拍", "16:9", "角色一致性", "商业短片"],
            "shots": [
                shot(1, 0, 2.5, "进入餐厅", "同一名外国游客从街边走近并自然进入串烧餐厅。", "稳定器中广角轻跟拍。", "街道与门店环境声、轻快音乐起。", "人物外形和服装首次锁定。"),
                shot(2, 2.5, 5.5, "观察与点单", "游客坐在木质吧台旁，观察菜单和开放式烤台，与店员自然点头交流。", "肩后中景与正侧面中近景。", "低声交谈与餐厅底噪。", "保持餐厅方向、视线和座位一致。"),
                shot(3, 5.5, 9, "炭火制作蒙太奇", "肉串翻面、油脂冒泡、撒孜然辣椒、刷酱并短促起火，形成焦化表面。", "微距特写、浅景深、低角度掠过烤架。", "炭火滋滋、撒料和刷酱声。", "食物与火焰遵守真实物理。"),
                shot(4, 9, 12.5, "品尝与认可", "烤串上桌，游客自然品尝，停顿后露出含蓄惊喜并轻轻点头。", "人物与食物同框中近景，补手部和烤串特写。", "盘子落桌、轻微咀嚼与环境声。", "脸部、手指、竹签和咀嚼动作稳定。"),
                shot(5, 12.5, 15.168, "烤串英雄镜头", "焦香肉串铺满深色陶盘，搭配青椒和蒜瓣；油亮焦边与香料颗粒清晰。", "低角度缓慢横移并轻推近，暖色背景散景。", "突出滋滋声，音乐简洁收尾。", "餐盘、桌面和食物形态保持稳定，不生成文字。"),
            ],
        },
        {
            "id": 6,
            "source_id": 6,
            "slug": "anime-summer-festival-shooting-gallery-teddy-bear",
            "title": "夏祭射击摊：大熊奖品反弹与友情代打",
            "category": "日系动漫短片 / 夏祭轻喜剧",
            "language": "zh-CN",
            "aspect_ratio": "16:9",
            "duration_sec": 25.708,
            "resolution": "3760×2160",
            "style_summary": "柔和赛璐璐日系动画 × 黄昏夏祭 × 射击摊物理笑点 × 少女友情。",
            "scene_summary": "紫粉黄昏、暖黄纸灯笼、木制射击摊、马卡龙与数字盒奖品、奶油色泰迪熊。",
            "subject_summary": "浅金短发黄浴衣女孩挑战泰迪熊；粉发红浴衣与蓝发深蓝浴衣同伴在旁，蓝发少女最终代打获胜。",
            "core_mechanic": "先击倒轻小盒建立能力，再让软木塞被大熊腹部弹回撞额头，最后由同伴精准命中并把熊送给主角。",
            "camera_language": "枪管主观近景、摊位正侧中景、软木塞飞行与绒毛受击特写、表情反应、领奖背面镜头、拥抱收尾近景。",
            "lighting_color": "紫粉暮空、暖黄灯笼、低饱和浴衣与粉紫奶油色奖品，柔和轮廓光和浅景深。",
            "audio_design": "夏祭人群底噪、轻快日系配乐、软木枪轻响、纸盒翻落、弹回滑稽音、玩偶落架闷响。",
            "continuity_rules": "三名少女的发型、浴衣花纹、身高差和站位稳定；木枪与软木塞尺寸一致；射击轴线、反弹方向、奖品位置和交接顺序连续。",
            "master_prompt": shooting_gallery_master,
            "negative_prompt": "真人实拍，3D 玩偶质感，角色换脸或年龄漂移，发色变化，浴衣花纹与腰带颜色改变，角色身高忽高忽低，额外人物突然出现，枪械变成真枪，木枪尺寸漂移，软木塞消失或瞬移，射击轴线错乱，软木塞无接触穿透泰迪熊，反弹方向不符合入射方向，熊未命中就翻倒，奖品架和马卡龙跳变，盒子无重力漂浮，泰迪熊颜色或大小变化，手指畸形，道具穿模，过度暴力，血腥，强烈魔法特效，乱码字幕，水印，logo。",
            "reference_image_prompt": "日系二维动画角色设定与夏祭场景参考，16:9。三名少女并排站在黄昏射击摊前：娇小浅金短发女孩穿淡黄色花纹浴衣配蓝色腰带；粉色高马尾少女穿红色樱花浴衣；蓝色短发少女穿深蓝花纹浴衣并拿红色三色丸子。背景有暖黄纸灯笼、木制奖品架、粉紫奶油色马卡龙、数字盒和奶油色泰迪熊。柔和赛璐璐上色，清晰正面全身比例，服装花纹与配色可锁定，无文字、无水印。",
            "recommended_models": "Seedance 2.0 / Kling / Veo（建议提供三人角色设定图并分镜生成）",
            "prompt_origin": "reconstructed_from_page_and_full_video_evidence",
            "quality_notes": "不是作者公开原始提示词；依据帖子正文、完整视频、逐秒抽帧与媒体元数据反推。媒体 API 时长 25.708 秒，解码帧时长约 25.583 秒。",
            "tags": ["日系动画", "夏祭", "射击摊", "浴衣", "少女友情", "泰迪熊", "软木枪", "物理喜剧", "赛璐璐", "16:9", "角色一致性"],
            "shots": [
                shot(1, 0, 4.5, "击倒轻小奖品", "浅金发女孩瞄准下层数字盒，软木塞带倒多个纸盒，盒子依次倾斜翻落。", "枪管主观近景、三人侧面中景与奖品架正面镜头。", "软木枪轻响、纸盒连续翻落、夏祭底噪。", "射击方向与盒子倒落方向一致，奖品架结构不变。"),
                shot(2, 4.5, 6.5, "自信转向大熊", "女孩因命中微笑，抬高枪口锁定上层马卡龙之间的泰迪熊。", "表情中近景切泰迪熊瞄准关系镜头。", "轻快配乐持续，环境声不间断。", "泰迪熊位置、大小和周围马卡龙布局锁定。"),
                shot(3, 6.5, 10.5, "软木塞反弹撞额头", "软木塞压入熊的柔软腹部后弹回，轻撞女孩额头；她出现红色旋涡怒气符号。", "绒毛受击微距、反向飞行特写、女孩反应特写。", "命中噗声、弹回滑稽音和轻微碰头声。", "熊第一枪不倒；反弹方向必须与入射轴线相反。"),
                shot(4, 10.5, 16.5, "再次挑战与同伴接枪", "女孩不服气地重新瞄准，两位同伴同框；尝试后蓝发少女平稳接过木枪。", "正面三人中景、眼睛与枪身紧张特写。", "短暂停顿、配乐蓄势、摊位环境声。", "角色站位、浴衣与木枪外形连续，交接动作清楚。"),
                shot(5, 16.5, 19.5, "蓝发少女精准代打", "蓝发少女冷静射中熊腹中心，出现圆形命中点，泰迪熊停顿后向前翻倒。", "奖品架正面中景与命中近景。", "软木枪声、命中闷声、玩偶落架声。", "严格按命中、停顿、翻倒顺序；周围奖品只轻微受扰。"),
                shot(6, 19.5, 22.5, "领奖并送给主角", "摊主递出泰迪熊，蓝发少女接过后送到浅金发女孩怀里，粉发少女微笑见证。", "三人背面中景切正面关系镜头。", "人群底噪、温柔配乐上扬。", "玩偶从摊主到蓝发少女再到主角，交接顺序不可跳变。"),
                shot(7, 22.5, 25.708, "抱熊满足收尾", "三人并肩离开，浅金发女孩抱紧泰迪熊，最后闭眼露出满足笑容。", "并肩中景后切女孩与熊的温暖近景。", "轻快温柔配乐与远处夏祭声收尾。", "蓝发少女仍拿红色丸子；女孩始终抱着同一只熊。"),
            ],
        },
        {
            "id": 7,
            "source_id": 7,
            "slug": "as-004-mira-quill-draw-the-way",
            "title": "AS-004 Mira Quill：Draw the Way",
            "category": "实验动画 / 石墨运动研究",
            "language": "en",
            "aspect_ratio": "16:9",
            "duration_sec": 15.0,
            "resolution": "16:9 源片（竖屏合辑 1080×1920）",
            "style_summary": "暖色动画纸上的石墨运动研究：结构线、擦除高光、轮廓抖动与赭色点缀。",
            "scene_summary": "风蚀档案庭院正在被白色虚空擦除，Mira 用 Aeroseed 画出桥梁并重建空间。",
            "subject_summary": "风之档案信使 Mira Quill：不对称短发、分叉长外套、窄裤、短靴与小型挎包。",
            "core_mechanic": "世界被橡皮擦除，赭色 Aeroseed 画出的石墨线变成承重桥梁并反向重绘庭院。",
            "camera_language": "极近景快速推入、横向追踪、中景侧面、低角度跟拍、起重机后拉大全景。",
            "lighting_color": "暖色动画纸、石墨灰、柔和涂抹与擦除高光，只保留低饱和赭色强调。",
            "audio_design": "橡皮擦嘶声、干涩急促打击乐、滑步刮擦、心跳、明亮提示音与铅笔落点声。",
            "continuity_rules": "Mira 的脸、发型、外套、挎包与比例跨镜头锁定；参考图只控制身份、风格、道具和世界，不复制设定表版式。",
            "master_prompt": mira_video,
            "negative_prompt": "One character only; no dialogue, no photorealism or 3D, no face drift, no costume change, no extra limbs, no generated text; do not reproduce the sheet layout, white background, panels, labels or text.",
            "reference_image_prompt": mira_image,
            "recommended_models": "Seedance 2.0（作者指定）",
            "prompt_origin": "author_published_full_prompt",
            "quality_notes": "作者在线程回复中公开了完整生图提示词与完整视频提示词；已按原文收录，并用合辑成片与媒体元数据核对。",
            "tags": ["Seedance 2.0", "石墨动画", "运动研究", "角色设定图", "微短片", "Aeroseed", "世界重建", "16:9", "五镜头", "作者原始提示词"],
            "shots": [
                shot(1, 0, 2, "庭院被擦除", "庭院地面化为白色虚空并冲向 Mira 的靴子。", "极近景，铅笔刮擦式快速推入。", "尖锐橡皮擦嘶声。", "石墨暖纸媒介稳定，擦除边界清楚。"),
                shot(2, 2, 5, "奔离消失区", "Mira 从左向右奔跑，拱门和纸飘带在身后被擦掉。", "宽幅横向跟拍。", "急促干涩打击乐。", "外套与挎包有连续跟随动作。"),
                shot(3, 5, 8, "释放 Aeroseed", "Mira 在断裂边缘滑停并甩出挎包，赭色 Aeroseed 飞出。", "中景侧面，镜头与角色同时停住。", "刮擦、心跳、明亮提示音。", "动作结束点和道具来源明确。"),
                shot(4, 8, 12, "画线成桥", "Mira 跃起，Aeroseed 画出粗石墨线；线在每次落脚下变成桥并向外重绘庭院。", "低角度跟拍。", "打击乐达到峰值。", "桥梁在脚落下前形成，重绘方向可读。"),
                shot(5, 12, 15, "庭院完成重建", "Mira 以稳定三分之四姿态落地，最后一座拱门完成，石墨鸟从纸面飞起。", "起重机后拉至大全景。", "音乐在一次铅笔轻点上解决。", "以完整可读英雄帧结束。"),
            ],
        },
        {
            "id": 8,
            "source_id": 7,
            "slug": "as-058-orin-vale-the-last-signal",
            "title": "AS-058 Orin Vale：The Last Signal",
            "category": "实验动画 / 针幕浮雕",
            "language": "en",
            "aspect_ratio": "16:9",
            "duration_sec": 15.0,
            "resolution": "16:9 源片（竖屏合辑 1080×1920）",
            "style_summary": "严格黑白的实体针幕阴影浮雕：针尖暗影、斜侧光、压印深度与丝绒灰阶。",
            "scene_summary": "夜间阶梯信号广场被黑色浮雕潮吞没，Orin 用 Aeroseed 压力环重建塔楼与雾。",
            "subject_summary": "夜间信号守护者 Orin Vale：强壮轮廓、高领、不对称肩披、长手套、阔短裤与重靴。",
            "core_mechanic": "三圈压力波使针体依次升起，逆转黑潮并恢复台阶、拱门、浮雕雾和信号塔。",
            "camera_language": "锁定微距、高角度跟潮平移、中低角度慢推、固定俯视、宽幅侧面结尾。",
            "lighting_color": "严格单色，固定斜侧光，黑到白的浮雕渐变与物理针幕阴影。",
            "audio_design": "金属针低语、警报敲击、低鼓脉冲、低音重击、环绕滚雷、克制铜管与针响。",
            "continuity_rules": "Orin 的侧脸、披肩和重靴跨切口一致；侧光方向物理一致；禁止用铅笔、炭笔或 CGI 光泽替代针幕。",
            "master_prompt": orin_video,
            "negative_prompt": "One character only; no dialogue, no colour, no pencil, charcoal, smoke simulation or CGI gloss, no face drift, no costume change, no generated text; keep side-light direction physically consistent; do not reproduce the sheet layout, labels or text.",
            "reference_image_prompt": orin_image,
            "recommended_models": "Seedance 2.0（作者指定）",
            "prompt_origin": "author_published_full_prompt",
            "quality_notes": "作者在线程回复中公开了完整生图提示词与完整视频提示词；已按原文收录，并用合辑成片与媒体元数据核对。",
            "tags": ["Seedance 2.0", "针幕动画", "浮雕", "黑白", "角色设定图", "微短片", "Aeroseed", "信号塔", "16:9", "作者原始提示词"],
            "shots": [
                shot(1, 0, 2, "信号塔熄灭", "一座发光信号塔塌成平黑针深，针体沿圆形链快速缩回。", "锁定微距。", "金属针低语与一次警报敲击。", "斜侧光和针幕材质固定。"),
                shot(2, 2, 5, "黑潮逼近", "黑色浮雕潮穿过阶梯熄灭塔楼并逼近 Orin。", "极大全景，高角度平移跟随黑潮。", "低鼓脉冲增强。", "镜头跟潮而非跟角色。"),
                shot(3, 5, 8, "守住最后信标", "Orin 站到最后信标前，双靴落定，把白色 Aeroseed 举到肩高。", "中低角度慢推，结束于坚定侧脸。", "披肩落定与低音重击。", "角色轮廓完整可读。"),
                shot(4, 8, 12, "压力环逆转黑潮", "Aeroseed 释放三圈压力环，针体随环升起并重建台阶、拱门和雾。", "固定俯视。", "有触感的滚雷环绕移动。", "三圈传播顺序和重建因果清楚。"),
                shot(5, 12, 15, "最后信号恢复", "最后塔楼竖起并投出白色光束，Orin 放下手臂，浮雕雾向两侧分开。", "宽幅侧面。", "克制铜管音与最终针响。", "以清楚稳定的侧面剪影结束。"),
            ],
        },
        {
            "id": 9,
            "source_id": 7,
            "slug": "as-096-nia-vector-map-the-storm",
            "title": "AS-096 Nia Vector：Map the Storm",
            "category": "实验动画 / 粒子流",
            "language": "en",
            "aspect_ratio": "16:9",
            "duration_sec": 15.0,
            "resolution": "16:9 源片（竖屏合辑 1080×1920）",
            "style_summary": "相干点云动画：力场驱动平流、有组织的等高流线、受控密度与柔和拖尾。",
            "scene_summary": "午夜流场地图被青色风暴撕开，Nia 释放外轮廓粒子改变向量路径并封闭裂口。",
            "subject_summary": "流场制图师 Nia Vector：圆短发、发光眼睛、结构短披风、束腰外衣、宽袖口与细靴。",
            "core_mechanic": "只释放披风边缘和身体外轮廓形成两股可控粒子流，包住风暴并把地面点云点亮成城市地图。",
            "camera_language": "微距移焦、沿等高线俯冲、正面慢推、头顶环绕、起重机上升。",
            "lighting_color": "深色空间背景，青色与低饱和紫色点云，金白 Aeroseed；脸和手部粒子更密。",
            "audio_design": "颗粒裂响、次低频下坠、加速空气脉冲、心跳、环绕颗粒高潮、温暖钟音与深沉收束。",
            "continuity_rules": "Nia 的脸和躯干在所有镜头中保持高密度可读；粒子沿明确向量运动；结尾完全重组且脸前无游离粒子。",
            "master_prompt": nia_video,
            "negative_prompt": "One character only; no dialogue, no explosion, random debris, chaotic noise, face dissolution, missing limbs, colour drift, costume change or generated text; no photoreal human skin; finish fully reassembled with no loose particles crossing the face.",
            "reference_image_prompt": nia_image,
            "recommended_models": "Seedance 2.0（作者指定）",
            "prompt_origin": "author_published_full_prompt",
            "quality_notes": "作者在线程回复中公开了完整生图提示词与完整视频提示词；已按原文收录，并用合辑成片与媒体元数据核对。",
            "tags": ["Seedance 2.0", "粒子流", "点云", "流场", "角色设定图", "微短片", "Aeroseed", "城市地图", "16:9", "作者原始提示词"],
            "shots": [
                shot(1, 0, 2, "地图被撕裂", "金色 Aeroseed 闪烁，青色激流反向弯曲并在地图中撕出黑洞。", "微距，从种子快速移焦至裂口。", "颗粒裂响与次低频下坠。", "裂口形成路径和流向可读。"),
                shot(2, 2, 5, "粒子风暴袭来", "风暴漏斗卷向塔柱，剥离其外层点云。", "极大全景，镜头沿一条等高线俯冲向 Nia。", "加速空气脉冲。", "粒子依照有组织的向量路径移动。"),
                shot(3, 5, 8, "释放外轮廓", "Nia 稳住身体、张开双臂，只把披风边缘和外轮廓释放为两股流。", "正面中景慢推，结束于稳定眼神。", "声音短暂降至心跳。", "脸和躯干保持完整高密度。"),
                shot(4, 8, 12, "改写风暴向量", "两股流包裹风暴，将其弯成发光螺旋并拉合黑色裂口。", "头顶环绕。", "颗粒高潮在立体声场中旋转。", "Nia 的脸和躯干始终不解体。"),
                shot(5, 12, 15, "点亮城市地图", "流体完全回到 Nia，地面数千粒子点亮为巨大城市地图，她转成三分之四英雄剪影。", "起重机上升。", "温暖钟音与深沉脉冲解决。", "完全重组，脸前没有游离粒子。"),
            ],
        },
        {
            "id": 10,
            "source_id": 7,
            "slug": "as-061-kade-flux-restart-the-sky",
            "title": "AS-061 Kade Flux：Restart the Sky",
            "category": "实验动画 / 墨线赛璐璐 CGI",
            "language": "en",
            "aspect_ratio": "16:9",
            "duration_sec": 15.0,
            "resolution": "16:9 源片（竖屏合辑 1080×1920）",
            "style_summary": "非写实三维：稳定可变宽墨线、二至四层赛璐璐光带、平面图形阴影与短促动作爆发。",
            "scene_summary": "模块化屋顶风力广场失去动力，Kade 把 Aeroseed 导入涡轮核心并重启整片城市天际线。",
            "subject_summary": "城市风网机械师 Kade Flux：深色后掠发、棱角短夹克、不对称肩片、工具裤与结实短靴。",
            "core_mechanic": "抓住悬浮 Aeroseed 后把它导入核心，一道琥珀冲击波依次穿过悬环并把城市光带从阴影切为青色。",
            "camera_language": "极近景变焦、24mm 横向跟拍、地面高度跟滑、中高位上升、低机位英雄大全景。",
            "lighting_color": "浅色石材、稳定深色轮廓、图形化阴影、青色与琥珀色强调光带。",
            "audio_design": "电弧爆响、即刻鼓击、金属刮擦、切分节拍、上升合成器、涡轮低鸣与两音收束。",
            "continuity_rules": "Kade 的脸、轮廓、夹克和比例跨镜头锁定；所有动作在切镜前落点；轮廓不爬动，皮肤无塑料光泽。",
            "master_prompt": kade_video,
            "negative_prompt": "One character only; no dialogue, no photoreal skin, glossy plastic, contour crawl, face drift, costume change, extra fingers or generated text; no photorealism; do not reproduce the sheet layout, white background, panels, labels or text.",
            "reference_image_prompt": kade_image,
            "recommended_models": "Seedance 2.0（作者指定）",
            "prompt_origin": "author_published_full_prompt",
            "quality_notes": "作者在线程回复中公开了完整生图提示词与完整视频提示词；已按原文收录，并用合辑成片与媒体元数据核对。",
            "tags": ["Seedance 2.0", "赛璐璐CGI", "墨线轮廓", "角色设定图", "微短片", "Aeroseed", "涡轮", "城市屋顶", "16:9", "作者原始提示词"],
            "shots": [
                shot(1, 0, 2, "涡轮环断裂", "涡轮环断裂，琥珀电能朝镜头弹射。", "极近景，快速变焦停在裂纹。", "电弧爆响与立即鼓击。", "断裂点和能量来源明确。"),
                shot(2, 2, 5, "穿越坍塌屋顶", "Kade 从左向右奔跑，失效涡轮在身后崩成干净几何块。", "24mm 宽幅横向跟拍。", "推进型打击乐。", "每一拍一个动作姿态，使用青色速度强调。"),
                shot(3, 5, 8, "滑跪接住种子", "Kade 在坠落圆环下完成一次受控膝滑，并用前臂护具接住 Aeroseed。", "地面高度中景，跟滑并在接触时停止。", "金属刮擦与切分重击。", "单一连贯滑行动作，手部和道具接触稳定。"),
                shot(4, 8, 12, "重启风力网络", "Kade 把 Aeroseed 导入核心，琥珀冲击波穿过所有悬环，城市赛璐璐光带由阴影切为青色。", "三分之四上升镜头，沿能量路径升高。", "合成器持续上升。", "冲击波传播顺序与照明切换同步。"),
                shot(5, 12, 15, "城市重新点亮", "涡轮在 Kade 身后锁定旋转，风吹动夹克一次，城市以图形光带回应。", "低机位英雄大全景，末 0.5 秒保持。", "涡轮低鸣与果断两音收尾。", "以清楚剪影结束，动作必须先落点。"),
            ],
        },
        {
            "id": 11,
            "source_id": 8,
            "slug": "seedance-anime-city-morning-bottled-coffee-commercial",
            "title": "日系二维城市晨间瓶装咖啡广告",
            "category": "日系二维商业动画 / 咖啡品牌广告",
            "language": "en",
            "aspect_ratio": "8:9",
            "duration_sec": 31.201,
            "resolution": "720×810",
            "style_summary": "温暖手绘日系二维商业动画：柔和配色、明亮晨光、富有表情的角色动作与轻快原声音乐。",
            "scene_summary": "城市清晨、便利店冷柜或货架、街头饮用、温馨咖啡馆工作与朋友社交，最后以瓶装拿铁产品特写收束。",
            "subject_summary": "一名年轻男性在明亮城市早晨购买瓶装拿铁，饮用后带着笔记本电脑和纸质笔记本进入咖啡馆工作并与朋友相聚。",
            "core_mechanic": "用“购买—第一口清爽体验—高效工作—朋友社交—产品英雄镜头”的生活方式叙事，把咖啡产品与积极晨间能量连接起来。",
            "camera_language": "城市建立镜头、便利店货架与取瓶近景、饮用中近景、咖啡馆桌面与人物关系镜头、产品瓶慢推英雄特写。",
            "lighting_color": "金色暖阳、柔和低饱和城市色彩、通透浅蓝与奶咖色，咖啡馆使用温暖木色和柔和窗光。",
            "audio_design": "轻快积极的原声吉他或尤克里里音乐，辅以城市晨间环境声、便利店冰柜声、开瓶与饮用声、咖啡馆谈笑声。",
            "continuity_rules": "年轻男性的脸、发型、服装与随身物品全程一致；同一瓶咖啡的瓶型、标签颜色和容量稳定；笔记本电脑与纸质笔记本的位置连续。",
            "master_prompt": starbucks_anime_video,
            "negative_prompt": "No photorealism, 3D CGI or live action; no character face drift, wardrobe change, extra fingers or deformed hands; no bottle shape changes, duplicate bottles before the final pack shot, warped labels, misspelled product text, random logos, flicker, inconsistent café layout, harsh neon lighting, gloomy mood or generated subtitles.",
            "reference_image_prompt": "",
            "recommended_models": "Seedance 2.0（作者注明）",
            "prompt_origin": "author_published_full_prompt",
            "quality_notes": "作者在帖子正文中公开了完整英文 prompt，数据库逐字保留；原文要求 35 秒，但公开视频媒体元数据为 31.201 秒、720×810，分镜按实际时长整理。",
            "tags": ["Seedance 2.0", "日系二维动画", "商业广告", "瓶装咖啡", "城市早晨", "便利店", "咖啡馆", "生活方式", "产品特写", "8:9", "作者原始提示词"],
            "shots": [
                shot(1, 0, 4, "明亮城市晨间", "年轻男性在阳光明媚的城市早晨出场，建立轻松积极的一天。", "城市宽景转人物中景，轻柔跟拍。", "轻快原声音乐与城市晨间环境声起。", "人物外形、服装和随身物品首次锁定。"),
                shot(2, 4, 9, "便利店取瓶装拿铁", "他进入便利店，从冷柜或货架拿起一瓶 Starbucks Caffè Latte。", "货架建立镜头、手部取瓶近景、人物与产品同框中景。", "店内底噪、冰柜轻响与取瓶声。", "手部结构正确，瓶型与标签完整清楚。"),
                shot(3, 9, 13, "清爽第一口", "回到明亮街头，他打开瓶盖并自然喝下一口，露出清爽满足的表情。", "侧面中近景配产品局部特写，暖阳形成柔和轮廓光。", "开瓶声、饮用声，音乐轻微上扬。", "饮用动作自然，瓶口不穿透面部，产品外观不变化。"),
                shot(4, 13, 20, "咖啡馆专注工作", "他坐在温馨咖啡馆，用笔记本电脑和纸质笔记本工作，瓶装咖啡放在桌面可见位置。", "窗边环境中景、肩后屏幕镜头、手写与键盘细节。", "轻快音乐、键盘与纸笔声、柔和咖啡馆底噪。", "电脑、笔记本、咖啡瓶与座位方位连续。"),
                shot(5, 20, 26.5, "与朋友轻松社交", "朋友来到桌边，几人自然交流、微笑并分享轻松的咖啡馆时刻。", "双人或小群组关系中景，轻微横移捕捉表情互动。", "自然谈笑声与积极原声音乐。", "主角身份和服装不漂移；新人物数量稳定。"),
                shot(6, 26.5, 31.201, "瓶装拿铁英雄镜头", "以多瓶 Starbucks Caffè Latte 的清晰近景结束，产品成为唯一视觉焦点。", "桌面产品英雄镜头，缓慢推近，背景柔和虚化。", "音乐形成明亮收束，可加入轻微瓶身落桌声。", "标签朝向统一、瓶型无变形，停留足够时间形成广告封面。"),
            ],
        },
        {
            "id": 12,
            "source_id": 9,
            "slug": "seedance-anime-riverside-camp-beef-pho-cooking",
            "title": "河畔露营牛肉河粉：金色篝火料理动画",
            "category": "日系二维美食动画 / 户外烹饪",
            "language": "en",
            "aspect_ratio": "16:9",
            "duration_sec": 12.5,
            "resolution": "1280×720",
            "style_summary": "电影感日系二维美食动画：河畔露营、金色暖光、篝火炊烟、细腻食材微距与顺滑转场。",
            "scene_summary": "宁静河畔露营地，以木质料理台、铸铁锅和篝火完成牛肉河粉的备料、熬汤、装碗、浇汤和装饰。",
            "subject_summary": "大理石纹牛肉、牛骨、姜、洋葱、整粒香料、泰国罗勒、豆芽、青柠、辣椒、红洋葱、米粉与陶瓷碗。",
            "core_mechanic": "用滚烫牛骨香料汤浇在米粉和薄切生牛肉上，让肉片在镜头前由红色自然变为柔嫩熟色，再以新鲜香草完成英雄碗。",
            "camera_language": "河畔建立镜头、俯拍备料、刀工微距、篝火铸铁锅近景、蒸汽慢推、浇汤特写与成品英雄环绕。",
            "lighting_color": "夕阳与篝火形成金色主光，河水使用柔和蓝绿反光；食材保持自然红、绿、白与暖棕色。",
            "audio_design": "河水、微风和鸟鸣底噪，刀切砧板声、香料落盘声、篝火噼啪、汤汁沸腾、浇汤声与轻柔温暖配乐。",
            "continuity_rules": "同一河畔营地、木桌、铸铁锅、陶瓷碗和食材组合保持连续；牛肉必须从薄切生肉经热汤逐渐变色，不瞬间替换；配料只在正确步骤出现。",
            "master_prompt": pho_anime_video,
            "negative_prompt": "No photoreal live action or glossy 3D CGI; no deformed hands, warped knife, floating ingredients, changing pot or bowl, duplicated utensils, instant ingredient teleportation, muddy or gelatinous broth, plastic-looking beef, noodles merging into a solid mass, steam without heat source, uncontrolled fire, incorrect garnish order, text, subtitles, logos, watermarks or flicker.",
            "reference_image_prompt": "",
            "recommended_models": "Seedance 2.0（作者注明）",
            "prompt_origin": "author_published_full_prompt",
            "quality_notes": "作者在帖子正文中公开完整英文 prompt，数据库逐字保留；公开视频媒体元数据为 12.5 秒、1280×720。原文未给分镜时间轴，数据库依据烹饪步骤整理为 7 段可执行镜头。",
            "tags": ["Seedance 2.0", "日系二维动画", "美食动画", "越南河粉", "牛肉河粉", "河畔露营", "篝火烹饪", "食材微距", "浇汤", "16:9", "作者原始提示词"],
            "shots": [
                shot(1, 0, 1.5, "河畔露营与食材建立", "金色晨昏光照亮宁静河畔营地，木桌摆着牛肉、香草、香料和蔬菜。", "宽幅环境建立后快速推向料理台。", "河水、微风、鸟鸣与轻柔音乐起。", "营地、木桌、铸铁锅和陶瓷碗的位置锁定。"),
                shot(2, 1.5, 3.3, "薄切牛肉与备料", "刀锋切开大理石纹牛肉，并快速展示姜、洋葱、整粒香料、泰国罗勒、豆芽和青柠。", "俯拍与极近景刀工蒙太奇，匹配切换食材。", "清脆刀切、砧板和香料落盘声。", "牛肉切片薄而连续，手指与刀具结构正确。"),
                shot(3, 3.3, 5.2, "牛骨香料入锅", "牛骨、姜、洋葱与整粒香料依次进入篝火上的铸铁锅。", "锅沿低角度近景转俯拍，跟随食材落入汤中。", "篝火噼啪、食材落锅与液体翻动声。", "每种食材只加入一次，铸铁锅外形不变。"),
                shot(4, 5.2, 7.2, "熬出浓郁清汤", "汤汁在篝火上稳定沸腾，金色蒸汽升起，牛骨与香料在清亮汤中缓慢翻滚。", "贴近锅面的慢推与蒸汽逆光特写。", "持续沸腾声与温暖配乐上扬。", "汤体保持清亮有流动性，火焰来自锅下篝火。"),
                shot(5, 7.2, 9, "米粉与薄牛肉装碗", "米粉放入陶瓷碗，薄牛肉片整齐铺在表面。", "碗内俯拍，米粉落下后切到牛肉铺放微距。", "米粉轻落和陶瓷轻响。", "同一陶瓷碗，牛肉仍呈自然生红色。"),
                shot(6, 9, 10.8, "滚汤烫熟牛肉", "滚烫清汤浇入碗中，蒸汽涌起，薄牛肉片沿浇汤路径逐渐由红转熟。", "浇汤超近景，跟随汤流横移并停在肉片变色处。", "清晰浇汤、蒸汽与轻微滋声。", "牛肉必须渐变受热，不瞬间换片；汤不溢出碗。"),
                shot(7, 10.8, 12.5, "香草装饰与英雄碗", "泰国罗勒、豆芽、辣椒、红洋葱和青柠完成装饰，热气中的牛肉河粉成为最终焦点。", "配料落点微距后轻微环绕成品英雄镜头。", "配料轻落声，音乐温暖收束。", "配料顺序清楚，成品碗完整稳定并留出封面停顿。"),
            ],
        },
        {
            "id": 13,
            "source_id": 10,
            "slug": "pov-cookies-milk-asmr-doodle-food-commercial",
            "title": "POV 曲奇蘸牛奶 ASMR：手绘涂鸦美食广告",
            "category": "写实美食广告 / POV ASMR",
            "language": "en",
            "aspect_ratio": "4:5",
            "duration_sec": 14.778,
            "resolution": "1076×1330",
            "style_summary": "超写实高端美食广告：温馨晨间厨房、POV 双手、电影级微距、慢动作食物物理与短暂白色手绘涂鸦。",
            "scene_summary": "暖色木桌上的巧克力曲奇盒、独立包装曲奇、冰牛奶瓶、透明玻璃杯与曲奇成品盘。",
            "subject_summary": "全片只出现同一双第一人称手，不露脸；依次转动曲奇盒、拆包装、倒牛奶、蘸曲奇、掰开曲奇并完成点赞。",
            "core_mechanic": "用包装摩擦、牛奶倾倒、蘸取滴落、曲奇断裂和碎屑坠落组成六段自然 ASMR，并以跟随动作的白色涂鸦词强化每个触感节点。",
            "camera_language": "桌面产品建立、手部近景、包装超近景、牛奶慢动作微距、蘸取跟随、断裂高速特写和末尾缓慢推近英雄镜头。",
            "lighting_color": "柔和自然窗光、暖木棕、奶白色、巧克力金棕与冷凝高光；浅景深和高端商业调色。",
            "audio_design": "仅自然 ASMR：纸盒轻敲、包装脆响、牛奶倾倒、玻璃轻碰、曲奇蘸取、清脆咬裂、碎屑落下、桌面轻拍与安静室内底噪；无背景音乐。",
            "continuity_rules": "只保留同一双 POV 手；曲奇盒、包装、牛奶瓶、玻璃杯、盘子和桌面位置连续；涂鸦词只在对应动作旁短暂出现并自然淡出。",
            "master_prompt": cookies_milk_video,
            "negative_prompt": "No faces visible; no background music, subtitles, captions, logos or watermarks; no on-screen text except the specified animated doodle words; no deformed hands or extra fingers, changing cookie box, duplicate glass, warped wrapper, impossible milk flow, floating crumbs, texture flicker, plastic-looking cookies, inconsistent tabletop or doodles that obscure the food.",
            "reference_image_prompt": cookies_milk_storyboard,
            "recommended_models": "GPT Image 2（分镜板）+ Seedance（视频）/ Pollo AI（作者工作流）",
            "prompt_origin": "author_published_full_prompt_and_storyboard",
            "quality_notes": "作者在正文中公开完整分镜板与视频提示词，数据库逐字保留。原提示词要求 15 秒、16:9、4K HDR、24 fps；公开视频实际为 14.778 秒、1076×1330，数据库以实际媒体规格归档，并将最后一镜收束到 14.778 秒。",
            "tags": ["Seedance", "GPT Image 2", "Pollo AI", "POV", "ASMR", "曲奇", "牛奶", "美食广告", "手绘涂鸦", "产品英雄镜头", "微距摄影", "4:5", "作者原始提示词"],
            "shots": [
                shot(1, 0, 2.5, "曲奇盒打招呼", "曲奇盒和冰牛奶瓶置于木桌，双手滑入画面并轻轻转动盒子；白色涂鸦 HELLO!、HI!、闪光和箭头出现。", "桌面产品建立镜头转手部近景，浅景深。", "纸盒轻敲、桌面轻触与安静房间底噪。", "不露脸；盒体、牛奶瓶与双手首次锁定。"),
                shot(2, 2.5, 5, "慢拆曲奇包装", "双手缓慢撕开曲奇包装；CRINKLE~、OPEN!、WOW! 和动态线条跟随撕口。", "包装超近景，镜头紧贴撕裂路径。", "突出清脆、层次丰富的包装摩擦声。", "包装从同一盒中取出，撕口和手指接触连续。"),
                shot(3, 5, 7.5, "慢动作倒牛奶", "冰牛奶倒入透明杯，飞溅、气泡和冷凝水在窗光中闪亮；POUR~、FRESH!、水滴涂鸦短暂出现。", "玻璃杯微距慢动作，跟随奶流轻微下移。", "牛奶倾倒与玻璃轻碰声。", "奶流遵守重力和流体物理，不穿透杯壁或溢出。"),
                shot(4, 7.5, 10, "曲奇蘸奶", "一块曲奇被缓慢浸入牛奶，再抬起让奶滴回杯中；DIP!、SOFT!、爱心与弧形箭头跟随曲奇。", "曲奇与液面同框的侧面近景，轻微跟随升降。", "蘸取、滴落和杯沿轻响。", "曲奇只软化不溶解，奶滴路径连续。"),
                shot(5, 10, 12.5, "掰开与碎屑慢落", "双手把曲奇掰成两半，巧克力轻微拉丝，碎屑慢动作落下；CRUNCH!、YUM!、MMM!、星星和碎屑涂鸦出现。", "断裂点极近景与短暂高速摄影。", "清脆断裂、碎屑落桌与近距离咀嚼质感声。", "双手结构正确，巧克力只轻微拉伸，碎屑受重力下落。"),
                shot(6, 12.5, 14.778, "产品英雄镜头与点赞", "曲奇盒、叠放曲奇和牛奶杯整齐成组，一只手放下最后一块曲奇并点赞；PERFECT!、BEST!、ENJOY! 与柔和星光环绕。", "低角度产品英雄构图，缓慢推近并停在清晰封面帧。", "曲奇落盘、玻璃轻响和桌面轻拍自然收尾。", "最终产品数量稳定，涂鸦不遮挡主体，手势完整可读。"),
            ],
        },
        {
            "id": 14,
            "source_id": 11,
            "slug": "surreal-coffee-cup-lighthouse-ocean",
            "title": "咖啡杯里的灯塔海洋：云海微缩梦境",
            "category": "超现实微缩景观 / 概念广告",
            "language": "zh-CN",
            "aspect_ratio": "3:4",
            "duration_sec": 10.041,
            "resolution": "832×1104",
            "style_summary": "超现实微缩摄影：透明咖啡杯、青绿色杯中海洋、暖光灯塔、云海奶泡与真实卷浪物理。",
            "scene_summary": "一只透明玻璃杯悬置在厚重白灰云海之中，杯内形成完整微缩海域，海浪围绕杯中灯塔循环起伏。",
            "subject_summary": "同一只厚壁透明玻璃杯、右侧圆形把手、单座奶白灯塔、红棕塔顶、小型暗礁、青绿色海水与云状奶泡。",
            "core_mechanic": "把咖啡杯稳定地变成一个受杯壁约束的微缩海洋，让卷浪、旋涡、水花与灯塔扫光持续演化，同时保持杯体和灯塔不漂移。",
            "camera_language": "略高正面中近景建立，极慢推近、数度横移与轻微环绕；依靠玻璃折射、浪峰和灯塔光束制造连续视差，无硬切。",
            "lighting_color": "冷青海水与暖琥珀灯塔光互补，白灰体积云包围杯体，金色反射穿透水雾；浅景深、柔和胶片颗粒与动态焦散。",
            "audio_design": "低沉柔和的海浪拍击、细碎水滴、远风、极轻灯塔机械转动与克制梦幻氛围音；无对白。",
            "continuity_rules": "杯体厚度、右侧把手、灯塔结构与礁石位置稳定；始终只有一座灯塔；海水和水花受杯中微缩物理约束，不能穿透杯壁或无规律溢出；云层连续缓慢流动。",
            "master_prompt": coffee_lighthouse_master,
            "negative_prompt": "No people, hands, spoon, saucer, coffee beans, text, subtitles, logos or watermarks; no extra lighthouse, changing cup handle, warped glass rim, opaque plastic cup, lighthouse scale drift, floating lighthouse, water penetrating the glass, uncontrolled flood, frozen wave, muddy water, random scene cuts, camera shake, flicker, duplicated objects or inconsistent cloud direction.",
            "reference_image_prompt": coffee_lighthouse_image,
            "recommended_models": "Seedance 2.0 / Veo 3.1 / Kling 3.0（复现建议；作者未注明模型）",
            "prompt_origin": "reverse_engineered_from_public_video_frames",
            "quality_notes": "作者未公开原始提示词或生成模型。数据库依据帖文、0 秒、4 秒、7 秒与结尾关键帧以及媒体元数据反推；实际视频为 10.041 秒、832×1104，按约 3:4 归档。",
            "tags": ["超现实", "微缩景观", "咖啡杯", "灯塔", "杯中海洋", "卷浪", "云海", "奶泡意象", "玻璃折射", "体积光", "概念广告", "3:4", "反推提示词"],
            "shots": [
                shot(1, 0, 2.5, "卷浪与灯塔建立", "透明杯悬在云海中，杯内青绿色巨浪从左侧卷起，暖光灯塔位于杯中偏右。", "略高正面中近景，极慢推近。", "低沉海浪、细小水花与远风。", "杯把始终朝右；单座灯塔、杯体和云海首次锁定。"),
                shot(2, 2.5, 5, "回浪与双向扫光", "卷浪沿杯口回落成旋涡，灯塔的暖金光束扫过水面并形成明亮反射。", "轻微横移和下沉，突出杯壁折射与水线。", "回浪、细碎水滴与极轻机械转动声。", "水体不得穿透杯壁，灯塔结构和比例不变。"),
                shot(3, 5, 7.5, "礁石灯塔英雄构图", "海面暂时舒展，灯塔与小礁石成为中心，扫光穿过云层与波纹。", "缓慢环绕数度并轻推，制造微缩视差。", "海面涌动减弱，梦幻氛围音轻微上扬。", "始终只有一座灯塔，礁石不漂移，云层方向连续。"),
                shot(4, 7.5, 10.041, "浪峰重组与暖光收束", "后侧海浪再次抬升并绕向灯塔，在杯口形成细碎白色水花，暖光穿透浪雾完成英雄帧。", "镜头稳定靠近后停顿，让卷浪弧线、灯塔和完整杯体同时可读。", "浪声增强后柔和收束，水滴与远风淡出。", "浪峰受杯内空间约束；结尾杯体、把手和灯塔必须清晰完整。"),
            ],
        },
    ]
    return sources, prompts


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    locator TEXT NOT NULL,
    accessed_at TEXT NOT NULL,
    verification TEXT NOT NULL,
    notes TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    raw_excerpt TEXT NOT NULL
);

CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    language TEXT NOT NULL,
    aspect_ratio TEXT NOT NULL,
    duration_sec REAL NOT NULL,
    resolution TEXT NOT NULL,
    style_summary TEXT NOT NULL,
    scene_summary TEXT NOT NULL,
    subject_summary TEXT NOT NULL,
    core_mechanic TEXT NOT NULL,
    camera_language TEXT NOT NULL,
    lighting_color TEXT NOT NULL,
    audio_design TEXT NOT NULL,
    continuity_rules TEXT NOT NULL,
    master_prompt TEXT NOT NULL,
    negative_prompt TEXT NOT NULL,
    reference_image_prompt TEXT NOT NULL,
    recommended_models TEXT NOT NULL,
    prompt_origin TEXT NOT NULL,
    quality_notes TEXT NOT NULL
);

CREATE TABLE shots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    shot_index INTEGER NOT NULL,
    start_sec REAL NOT NULL,
    end_sec REAL NOT NULL,
    title TEXT NOT NULL,
    visual_action TEXT NOT NULL,
    camera TEXT NOT NULL,
    audio TEXT NOT NULL,
    continuity TEXT NOT NULL,
    UNIQUE(prompt_id, shot_index)
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE prompt_tags (
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY(prompt_id, tag_id)
);

CREATE VIEW prompt_catalog AS
SELECT
    p.id,
    p.slug,
    p.title,
    p.category,
    p.aspect_ratio,
    p.duration_sec,
    p.resolution,
    p.style_summary,
    p.core_mechanic,
    p.recommended_models,
    p.prompt_origin,
    s.source_type,
    s.locator AS source_locator,
    GROUP_CONCAT(t.name, ' | ') AS tags
FROM prompts p
JOIN sources s ON s.id = p.source_id
LEFT JOIN prompt_tags pt ON pt.prompt_id = p.id
LEFT JOIN tags t ON t.id = pt.tag_id
GROUP BY p.id;
"""


def create_database(sources: list[dict], prompts: list[dict]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    source_cols = list(sources[0].keys())
    conn.executemany(
        f"INSERT INTO sources ({','.join(source_cols)}) VALUES ({','.join('?' for _ in source_cols)})",
        [[source[col] for col in source_cols] for source in sources],
    )

    prompt_cols = [key for key in prompts[0].keys() if key not in {"tags", "shots"}]
    conn.executemany(
        f"INSERT INTO prompts ({','.join(prompt_cols)}) VALUES ({','.join('?' for _ in prompt_cols)})",
        [[prompt[col] for col in prompt_cols] for prompt in prompts],
    )
    for prompt in prompts:
        for item in prompt["shots"]:
            conn.execute(
                """
                INSERT INTO shots
                (prompt_id, shot_index, start_sec, end_sec, title, visual_action, camera, audio, continuity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prompt["id"],
                    item["shot_index"],
                    item["start_sec"],
                    item["end_sec"],
                    item["title"],
                    item["visual_action"],
                    item["camera"],
                    item["audio"],
                    item["continuity"],
                ),
            )
        for tag in prompt["tags"]:
            conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag,))
            tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()[0]
            conn.execute(
                "INSERT OR IGNORE INTO prompt_tags(prompt_id, tag_id) VALUES (?, ?)",
                (prompt["id"], tag_id),
            )

    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE prompt_fts USING fts5(
                title, category, style_summary, scene_summary, subject_summary,
                core_mechanic, master_prompt, negative_prompt, tags
            )
            """
        )
        for prompt in prompts:
            conn.execute(
                """
                INSERT INTO prompt_fts
                (rowid, title, category, style_summary, scene_summary, subject_summary,
                 core_mechanic, master_prompt, negative_prompt, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prompt["id"],
                    prompt["title"],
                    prompt["category"],
                    prompt["style_summary"],
                    prompt["scene_summary"],
                    prompt["subject_summary"],
                    prompt["core_mechanic"],
                    prompt["master_prompt"],
                    prompt["negative_prompt"],
                    " ".join(prompt["tags"]),
                ),
            )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def export_csv(prompts: list[dict]) -> None:
    prompt_cols = [key for key in prompts[0].keys() if key != "shots"]
    with PROMPTS_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=prompt_cols)
        writer.writeheader()
        for prompt in prompts:
            row = {key: prompt[key] for key in prompt_cols}
            row["tags"] = " | ".join(prompt["tags"])
            writer.writerow(row)

    shot_cols = [
        "prompt_id",
        "prompt_title",
        "shot_index",
        "start_sec",
        "end_sec",
        "title",
        "visual_action",
        "camera",
        "audio",
        "continuity",
    ]
    with SHOTS_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=shot_cols)
        writer.writeheader()
        for prompt in prompts:
            for item in prompt["shots"]:
                writer.writerow(
                    {
                        "prompt_id": prompt["id"],
                        "prompt_title": prompt["title"],
                        **item,
                    }
                )


def export_json(sources: list[dict], prompts: list[dict]) -> None:
    payload = json.dumps(
        {
            "database_name": "AI视频提示词数据库",
            "version": "1.0.0",
            "sources": sources,
            "prompts": prompts,
        },
        ensure_ascii=False,
        indent=2,
    )
    JSON_PATH.write_text(payload, encoding="utf-8")
    BROWSER_DATA_PATH.write_text(
        f"window.AI_VIDEO_PROMPT_DB = {payload};",
        encoding="utf-8",
    )


def export_index(prompts: list[dict]) -> None:
    rows = "\n".join(
        f"| {p['id']} | {p['title']} | {p['category']} | {p['aspect_ratio']} | "
        f"{p['duration_sec']:g}s | {p['prompt_origin']} |"
        for p in prompts
    )
    x_prompt = prompts[3]["master_prompt"]
    text = f"""# AI 视频提示词数据库

本库把当前文件夹中的 3 份有效提示词与 8 个 X 视频来源统一整理为可检索结构；动画风格合辑按四个独立微短片拆分，因此共形成 14 条主提示词。主库是 SQLite，同时提供 UTF-8 BOM CSV、JSON 和本索引。

## 数据概览

| ID | 标题 | 分类 | 画幅 | 时长 | 来源性质 |
|---:|---|---|---|---:|---|
{rows}

共 {len(prompts)} 条主提示词、{sum(len(p['shots']) for p in prompts)} 条分镜、{len({tag for p in prompts for tag in p['tags']})} 个去重标签。

## 文件说明

- `AI视频提示词数据库.sqlite`：主数据库，含来源、提示词、分镜、标签及全文检索表。
- `AI视频提示词数据库_总表.csv`：一行一条提示词，适合 Excel、飞书或 Notion 导入。
- `AI视频提示词数据库_分镜.csv`：一行一个时间段分镜。
- `AI视频提示词数据库.json`：适合程序、自动化工作流和模型调用。
- `tools/build_ai_video_prompt_database.py`：可重复构建数据库的生成脚本。

## 核心表

- `sources`：来源、校验方式、内容哈希与原文。
- `prompts`：风格、场景、角色、核心机制、镜头、灯光、音频、连续性、完整提示词、负面提示词。
- `shots`：按时间段拆分的动作、镜头、音效和连续性。
- `tags` / `prompt_tags`：规范化标签。
- `prompt_catalog`：便于浏览的汇总视图。
- `prompt_fts`：SQLite FTS5 全文检索表（运行环境支持 FTS5 时创建）。

## 常用查询

```sql
-- 浏览全部条目
SELECT * FROM prompt_catalog ORDER BY id;

-- 找竖屏搞笑视频
SELECT title, duration_sec, style_summary
FROM prompts
WHERE aspect_ratio = '9:16' AND category LIKE '%搞笑%';

-- 查看一个条目的完整分镜
SELECT shot_index, start_sec, end_sec, title, visual_action, camera
FROM shots
WHERE prompt_id = 4
ORDER BY shot_index;

-- 全文检索（FTS5 可用时）
SELECT rowid, title
FROM prompt_fts
WHERE prompt_fts MATCH '时间冻结 OR 物理一致性';
```

## X 视频案例：局部时间冻结

作者公开说明的关键不是某个花哨特效词，而是先把四件事写清楚：

1. 触碰发生在哪一帧；
2. 具体冻结哪个目标；
3. 哪些环境元素必须继续运动；
4. 冻结持续多久、如何无缝恢复动量。

页面核对到的视频规格为 1920×1080 横屏、约 43.285 秒。封面是强日照城市广场，前景鸽群，背景游客、婴儿车、纪念性喷泉/建筑均提供“环境仍在流动”的参照。

以下是可直接复用的反推版提示词；它不是作者公开原始 prompt：

> {x_prompt.replace(chr(10), chr(10) + '> ')}

### X 条目最重要的负面约束

`禁止全世界一起冻结；禁止整帧定格；禁止用慢动作冒充冻结；冻结目标不得漂移、眨眼、呼吸式摆动或衣物继续飘动；背景行人、鸽子、阴影和相机必须持续运动；释放时必须从原姿态恢复原动量；不要魔法光圈、发光描边、粒子爆炸或绿幕边缘。`

## 数据质量说明

- `海盗舰队与巨兽激战提示词.md` 的时间轴覆盖 0–15 秒，但末尾另写“10s”；数据库以时间轴为准记录 15 秒，并保留冲突说明。
- `海盗舰队与巨兽激战提示词.txt` 是 0 字节空文件，未作为独立提示词导入。
- ID 4–6 的三个 X 视频作者未公开完整原始提示词，相关条目统一标记为反推版本，不会与作者原始 prompt 混淆。
- ID 7–10 来自同一动画风格合辑；作者在回复中逐字公开四份 16:9 生图提示词和四份 Seedance 2.0 视频提示词，数据库按原文收录并标记为 `author_published_full_prompt`。
- ID 11 的作者在正文中公开了完整 Seedance 2.0 视频提示词；原文要求 35 秒，公开视频实际为 31.201 秒、720×810，数据库保留原文并按实际媒体时长整理分镜。
- ID 12 的作者在正文中公开了完整 Seedance 2.0 河畔露营牛肉河粉视频提示词；公开视频为 12.5 秒、1280×720，数据库保留原文并按烹饪步骤整理为 7 段分镜。
- ID 13 的作者公开了 GPT Image 2 分镜板提示词与 Seedance 视频提示词；原文要求 15 秒、16:9，公开视频实际为 14.778 秒、1076×1330，数据库保留两份原文并按实际规格归档。
- ID 14 的作者未公开原始提示词或生成模型；数据库依据帖文、四个关键帧和 10.041 秒、832×1104 的媒体元数据反推，并明确标记为 `reverse_engineered_from_public_video_frames`。
"""
    INDEX_PATH.write_text(text, encoding="utf-8")


def validate() -> dict:
    conn = sqlite3.connect(DB_PATH)
    has_fts = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'prompt_fts'"
    ).fetchone()[0]
    result = {
        "sources": conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "prompts": conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0],
        "shots": conn.execute("SELECT COUNT(*) FROM shots").fetchone()[0],
        "tags": conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0],
        "fts_rows": conn.execute("SELECT COUNT(*) FROM prompt_fts").fetchone()[0]
        if has_fts
        else None,
        "fts_time_freeze_hits": conn.execute(
            "SELECT COUNT(*) FROM prompt_fts WHERE prompt_fts MATCH '时间冻结'"
        ).fetchone()[0]
        if has_fts
        else None,
        "foreign_key_errors": conn.execute("PRAGMA foreign_key_check").fetchall(),
        "quick_check": conn.execute("PRAGMA quick_check").fetchone()[0],
    }
    conn.close()
    return result


def main() -> None:
    sources, prompts = build_records()
    create_database(sources, prompts)
    export_csv(prompts)
    export_json(sources, prompts)
    export_index(prompts)
    print(json.dumps(validate(), ensure_ascii=False))


if __name__ == "__main__":
    main()
