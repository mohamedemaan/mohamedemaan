import math
import os
import sys
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

def get_time_based_greeting(tz_name="Asia/Kolkata", force_mode=None):
    if force_mode:
        mode = force_mode.lower()
        if mode == "morning":
            return "Good Morning, Explorer!", "AI GUIDE // TIME: MORNING ACTIVE"
        elif mode == "afternoon":
            return "Good Afternoon, Explorer!", "AI GUIDE // TIME: AFTERNOON ACTIVE"
        elif mode == "evening":
            return "Good Evening, Explorer!", "AI GUIDE // TIME: EVENING ACTIVE"
        elif mode == "night":
            return "Good Night, Explorer!", "AI GUIDE // TIME: NIGHT PATROL"

    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
    except Exception:
        # Fallback to UTC + 5:30 (IST)
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)

    hour = now.hour
    
    # User's exact requested time slots:
    # 5:00 AM to 11:59 AM: Good Morning
    # 12:00 PM to 3:59 PM: Good Afternoon
    # 4:00 PM to 6:59 PM: Good Evening
    # 7:00 PM to 4:59 AM: Good Night
    if 5 <= hour < 12:
        return "Good Morning, Explorer!", "AI GUIDE // TIME: MORNING ACTIVE"
    elif 12 <= hour < 16:
        return "Good Afternoon, Explorer!", "AI GUIDE // TIME: AFTERNOON ACTIVE"
    elif 16 <= hour < 19:
        return "Good Evening, Explorer!", "AI GUIDE // TIME: EVENING ACTIVE"
    else:
        return "Good Night, Explorer!", "AI GUIDE // TIME: NIGHT PATROL"

def generate_robot_gif(out_path, greeting_title, badge_text):
    # Canvas dimensions (supersampled 2x for retina sharpness)
    SCALE = 2
    CANVAS_W = 950 * SCALE
    CANVAS_H = 165 * SCALE
    FPS = 16
    DURATION_MS = 62
    NUM_FRAMES = 168

    # Fonts
    try:
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 10 * SCALE)
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 15 * SCALE)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 12 * SCALE)
    except Exception:
        try:
            font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10 * SCALE)
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15 * SCALE)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12 * SCALE)
        except Exception:
            font_badge = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()

    def draw_track(draw, frame_idx):
        track_y = int(148 * SCALE)
        start_x = int(60 * SCALE)
        end_x = int(890 * SCALE)
        total_len = end_x - start_x
        
        for x in range(start_x, end_x):
            norm_x = (x - start_x) / total_len
            alpha = math.sin(norm_x * math.pi)
            intensity = int(75 + alpha * 140)
            draw.line([(x, track_y), (x, track_y + 1 * SCALE)], fill=(intensity, intensity + 15, intensity + 30))
        
        # Center diamond marker
        cx = CANVAS_W // 2
        d_size = int(6 * SCALE)
        draw.polygon([
            (cx, track_y - d_size),
            (cx + d_size, track_y),
            (cx, track_y + d_size),
            (cx - d_size, track_y)
        ], fill=(248, 250, 252), outline=(148, 163, 184))
        
        # Laser pulse traveling along track
        pulse_pos = ((frame_idx * 15 * SCALE) % total_len) + start_x
        draw.line([(pulse_pos - int(25 * SCALE), track_y), (pulse_pos + int(25 * SCALE), track_y)], fill=(56, 189, 248), width=int(2 * SCALE))

    def draw_cute_robot(draw, cx, cy, frame_idx, state="idle", wave=True):
        bob = int(math.sin(frame_idx * 0.45) * (3.5 * SCALE))
        rcy = cy + bob
        
        # 1. Jet Thruster Flame
        jet_len = int((9 + math.sin(frame_idx * 0.9) * 4) * SCALE)
        jet_w = int(7 * SCALE)
        draw.polygon([
            (cx - jet_w, rcy + int(18 * SCALE)),
            (cx + jet_w, rcy + int(18 * SCALE)),
            (cx, rcy + int(18 * SCALE) + jet_len)
        ], fill=(56, 189, 248))
        draw.polygon([
            (cx - jet_w // 2, rcy + int(18 * SCALE)),
            (cx + jet_w // 2, rcy + int(18 * SCALE)),
            (cx, rcy + int(18 * SCALE) + int(jet_len * 0.6))
        ], fill=(255, 255, 255))
        
        # 2. Torso (Chubby Cute Chrome Capsule)
        tw = int(16 * SCALE)
        th_top = rcy - int(5 * SCALE)
        th_bot = rcy + int(18 * SCALE)
        draw.rounded_rectangle(
            [(cx - tw, th_top), (cx + tw, th_bot)],
            radius=int(9 * SCALE),
            fill=(148, 163, 184),
            outline=(241, 245, 249),
            width=int(2 * SCALE)
        )
        draw.ellipse(
            [(cx - int(6 * SCALE), rcy + int(2 * SCALE)), (cx + int(6 * SCALE), rcy + int(13 * SCALE))],
            fill=(56, 189, 248),
            outline=(255, 255, 255),
            width=int(1 * SCALE)
        )
        
        # 3. Head (Cute Chrome Sphere)
        hw = int(21 * SCALE)
        hh = int(18 * SCALE)
        head_cy = rcy - int(21 * SCALE)
        draw.rounded_rectangle(
            [(cx - hw, head_cy - hh), (cx + hw, head_cy + hh)],
            radius=int(15 * SCALE),
            fill=(203, 213, 225),
            outline=(248, 250, 252),
            width=int(2 * SCALE)
        )
        draw.ellipse(
            [(cx - int(14 * SCALE), head_cy - int(15 * SCALE)), (cx - int(5 * SCALE), head_cy - int(8 * SCALE))],
            fill=(255, 255, 255)
        )
        
        # 4. Black Glass Visor
        vw = int(16 * SCALE)
        vh = int(10 * SCALE)
        draw.rounded_rectangle(
            [(cx - vw, head_cy - vh), (cx + vw, head_cy + vh)],
            radius=int(7 * SCALE),
            fill=(13, 17, 23),
            outline=(100, 116, 139),
            width=int(1 * SCALE)
        )
        
        # 5. Cyber LED Eyes
        is_blink = (frame_idx % 38) in [0, 1]
        eye_offset = int(7.5 * SCALE)
        eye_rad = int(3.5 * SCALE)
        eye_y = head_cy
        
        if is_blink:
            draw.line([(cx - eye_offset - eye_rad, eye_y), (cx - eye_offset + eye_rad, eye_y)], fill=(56, 189, 248), width=int(2 * SCALE))
            draw.line([(cx + eye_offset - eye_rad, eye_y), (cx + eye_offset + eye_rad, eye_y)], fill=(56, 189, 248), width=int(2 * SCALE))
        elif wave:
            draw.arc([(cx - eye_offset - eye_rad, eye_y - eye_rad), (cx - eye_offset + eye_rad, eye_y + eye_rad)], start=180, end=0, fill=(56, 189, 248), width=int(2 * SCALE))
            draw.arc([(cx + eye_offset - eye_rad, eye_y - eye_rad), (cx + eye_offset + eye_rad, eye_y + eye_rad)], start=180, end=0, fill=(56, 189, 248), width=int(2 * SCALE))
        else:
            for ex in [cx - eye_offset, cx + eye_offset]:
                draw.ellipse([(ex - eye_rad, eye_y - eye_rad), (ex + eye_rad, eye_y + eye_rad)], fill=(56, 189, 248))
                draw.ellipse([(ex - int(1 * SCALE), eye_y - int(1.5 * SCALE)), (ex + int(1.5 * SCALE), eye_y + int(0.5 * SCALE))], fill=(255, 255, 255))
                
        # 6. Antenna with Pulsing Beacon
        ant_top_y = head_cy - hh - int(11 * SCALE)
        draw.line([(cx, head_cy - hh), (cx, ant_top_y)], fill=(148, 163, 184), width=int(2 * SCALE))
        beacon_pulse = int(4.5 * SCALE + math.sin(frame_idx * 0.6) * (1.5 * SCALE))
        draw.ellipse([(cx - beacon_pulse, ant_top_y - beacon_pulse), (cx + beacon_pulse, ant_top_y + beacon_pulse)], fill=(56, 189, 248), outline=(255, 255, 255), width=int(1 * SCALE))
        
        # 7. Floating Hands
        if wave:
            wave_dy = int(math.sin(frame_idx * 0.8) * (8 * SCALE))
            hand_r_x = cx + int(26 * SCALE)
            hand_r_y = head_cy - int(1 * SCALE) + wave_dy
            draw.ellipse([(hand_r_x - int(5 * SCALE), hand_r_y - int(5 * SCALE)), (hand_r_x + int(5 * SCALE), hand_r_y + int(5 * SCALE))], fill=(226, 232, 240), outline=(255, 255, 255), width=int(1 * SCALE))
            
            hand_l_x = cx - int(23 * SCALE)
            hand_l_y = rcy + int(7 * SCALE)
            draw.ellipse([(hand_l_x - int(4 * SCALE), hand_l_y - int(4 * SCALE)), (hand_l_x + int(4 * SCALE), hand_l_y + int(4 * SCALE))], fill=(148, 163, 184), outline=(241, 245, 249), width=int(1 * SCALE))
        else:
            hand_l_x = cx - int(23 * SCALE)
            hand_l_y = rcy + int(7 * SCALE)
            hand_r_x = cx + int(23 * SCALE)
            hand_r_y = rcy + int(7 * SCALE)
            draw.ellipse([(hand_l_x - int(4 * SCALE), hand_l_y - int(4 * SCALE)), (hand_l_x + int(4 * SCALE), hand_l_y + int(4 * SCALE))], fill=(148, 163, 184), outline=(241, 245, 249), width=int(1 * SCALE))
            draw.ellipse([(hand_r_x - int(4 * SCALE), hand_r_y - int(4 * SCALE)), (hand_r_x + int(4 * SCALE), hand_r_y + int(4 * SCALE))], fill=(148, 163, 184), outline=(241, 245, 249), width=int(1 * SCALE))

    frames = []
    cx_center = CANVAS_W // 2
    robot_cy = int(114 * SCALE)

    for f in range(NUM_FRAMES):
        im = Image.new("RGBA", (CANVAS_W, CANVAS_H), (13, 17, 23, 255))
        draw = ImageDraw.Draw(im)
        draw_track(draw, f)
        
        if f <= 23:
            prog = f / 23.0
            ease = 1 - (1 - prog)**2
            rx = int((-50 * SCALE) + ease * (cx_center - (-50 * SCALE)))
            draw_cute_robot(draw, rx, robot_cy, f, state="walk_right", wave=False)
            for i in range(3):
                px = rx - int((16 + i * 14) * SCALE)
                py = robot_cy + int(18 * SCALE) + (i % 2) * int(4 * SCALE)
                draw.ellipse([(px - int(2 * SCALE), py - int(2 * SCALE)), (px + int(2 * SCALE), py + int(2 * SCALE))], fill=(56, 189, 248, 170))
                
        elif f <= 143:
            rx = cx_center
            draw_cute_robot(draw, rx, robot_cy, f, state="idle", wave=True)
            
            df = f - 24
            slide_idx = df // 24
            
            if slide_idx == 0:
                current_badge = badge_text
                current_title = greeting_title
                current_sub = "I am your AI Companion - introducing Mohamed Emaan's Portfolio"
            elif slide_idx == 1:
                current_badge = "IDENTITY & CREDENTIALS"
                current_title = "Mohamed Emaan - Aspiring AI/ML Engineer"
                current_sub = "B.Tech in Artificial Intelligence & Data Science | CARE College (2023-2027)"
            elif slide_idx == 2:
                current_badge = "CORE RESEARCH & SPECIALIZATION"
                current_title = "Machine Learning, Generative AI & Predictive Telemetry"
                current_sub = "Building real-time ML pipelines, RAG systems & intelligent architectures"
            elif slide_idx == 3:
                current_badge = "FEATURED PRODUCTION PLATFORMS"
                current_title = "SalesMind AI & Ahnaf & Co E-Commerce"
                current_sub = "Explore full-stack platforms, telemetry dashboards & live deployments below"
            else:
                current_badge = "PORTFOLIO NAVIGATION"
                current_title = "Scroll Down to Explore Full Telemetry & Repositories!"
                current_sub = "Have a great journey through the code - departing for next patrol!"
                
            # Draw Glass Speech Bubble
            bw = int(600 * SCALE)
            bh = int(58 * SCALE)
            bx1 = cx_center - bw // 2
            by1 = int(10 * SCALE)
            bx2 = cx_center + bw // 2
            by2 = by1 + bh
            
            draw.rounded_rectangle(
                [(bx1, by1), (bx2, by2)],
                radius=int(10 * SCALE),
                fill=(10, 14, 23),
                outline=(56, 189, 248),
                width=int(1.5 * SCALE)
            )
            
            pw = int(7 * SCALE)
            ph = int(8 * SCALE)
            draw.polygon([
                (cx_center - pw, by2),
                (cx_center + pw, by2),
                (cx_center, by2 + ph)
            ], fill=(56, 189, 248))
            
            bbox_b = draw.textbbox((0, 0), current_badge, font=font_badge)
            bw_txt = bbox_b[2] - bbox_b[0]
            draw.text((cx_center - bw_txt // 2, by1 + int(6 * SCALE)), current_badge, font=font_badge, fill=(56, 189, 248))
            
            bbox_t = draw.textbbox((0, 0), current_title, font=font_title)
            tw = bbox_t[2] - bbox_t[0]
            draw.text((cx_center - tw // 2, by1 + int(21 * SCALE)), current_title, font=font_title, fill=(248, 250, 252))
            
            bbox_s = draw.textbbox((0, 0), current_sub, font=font_sub)
            sw = bbox_s[2] - bbox_s[0]
            draw.text((cx_center - sw // 2, by1 + int(40 * SCALE)), current_sub, font=font_sub, fill=(203, 213, 225))
            
        else:
            prog = (f - 143) / 24.0
            ease = prog ** 2
            rx = int(cx_center + ease * ((CANVAS_W + 60 * SCALE) - cx_center))
            draw_cute_robot(draw, rx, robot_cy, f, state="walk_right", wave=False)
            for i in range(4):
                dx1 = rx - int((22 + i * 16) * SCALE)
                dx2 = dx1 + int(12 * SCALE)
                dy = robot_cy + int((i * 4) * SCALE)
                draw.line([(dx1, dy), (dx2, dy)], fill=(203, 213, 225), width=int(2 * SCALE))
                
        im_final = im.resize((950, 165), resample=Image.Resampling.LANCZOS)
        im_quant = im_final.convert("RGB").quantize(colors=128, method=Image.Resampling.LANCZOS)
        frames.append(im_quant)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True
    )
    sz_kb = os.path.getsize(out_path) / 1024
    print(f"Generated {out_path} [{greeting_title}] ({sz_kb:.1f} KB)")

if __name__ == "__main__":
    force = sys.argv[1] if len(sys.argv) > 1 else None
    title, badge = get_time_based_greeting(force_mode=force)
    out = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\EMAAN\mohamedemaan\assets\robot-guide.gif"
    print(f"Generating for greeting: '{title}' ({badge}) -> {out}")
    generate_robot_gif(out, title, badge)
