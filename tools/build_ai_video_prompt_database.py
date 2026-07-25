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

本库把当前文件夹中的 3 份有效提示词与 2 个 X 视频反推案例统一整理为可检索结构。主库是 SQLite，同时提供 UTF-8 BOM CSV、JSON 和本索引。

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
- 两个 X 视频作者均未公开完整原始提示词；第 4、5 条标记为 `reconstructed_from_page_and_visual_evidence`，不会与原文来源混淆。
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
