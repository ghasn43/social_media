import json
import time
import requests
import os
import textwrap
import platform
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import replicate

# ------------------------------------------------------------
# CONFIG IMPORT
# ------------------------------------------------------------
from config import (
    OPENAI_API_KEY,
    REPLICATE_API_TOKEN,
    ZAPIER_WEBHOOK_URL,
    IMGBB_API_KEY
)

# ------------------------------------------------------------
# INITIALIZE CLIENTS
# ------------------------------------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# ------------------------------------------------------------
# TEXT POSTS GENERATOR
# ------------------------------------------------------------
def generate_posts(topic):
    """Generate 3 social media posts about a given topic."""
    
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty")

    prompt = f"""
You are a Social Media Creative Agent.

Generate EXACTLY 3 posts about: {topic}

STYLE RULES:
- Write captions with 2-3 sentences.
- Professional and motivational.
- Relevant to the UAE.
- No repetition across posts.
- Include EXACTLY 5 high-performing hashtags.
- Return VALID JSON ONLY.

Return JSON ONLY:
{{
  "posts": [
    {{"title": "", "caption": "", "hashtags": ""}},
    {{"title": "", "caption": "", "hashtags": ""}},
    {{"title": "", "caption": "", "hashtags": ""}}
  ]
}}
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = resp.choices[0].message.content.strip()
        
        if not content:
            raise ValueError("Empty response from OpenAI")
        
        result = json.loads(content)
        
        # Validate structure
        if "posts" not in result or len(result["posts"]) != 3:
            raise ValueError("Invalid response structure from OpenAI")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON from OpenAI: {e}")
        print(f"Response was: {content[:200]}")
        raise
    except Exception as e:
        print(f"❌ Error generating posts: {e}")
        raise


# ------------------------------------------------------------
# IMAGE PROMPT GENERATOR - SMART VERSION WITH CUSTOM TEMPLATE
# ------------------------------------------------------------
def generate_image_prompts(posts, custom_prompt_template=None):
    """Generate contextually relevant image prompts for each post.
    
    Args:
        posts: Dictionary with posts list
        custom_prompt_template: Optional custom prompt template from user
    """
    
    if not posts or "posts" not in posts:
        return {"image_prompts": []}

    prompts = []

    for p in posts["posts"]:
        title = p.get("title", "")
        caption = p.get("caption", "")
        
        if not title:
            continue

        # If user provided custom prompt template, use it
        if custom_prompt_template:
            print(f"📝 Using custom prompt template for: {title[:50]}...")
            
            # Replace placeholders with actual content
            custom_prompt = custom_prompt_template
            custom_prompt = custom_prompt.replace("[TITLE]", title)
            custom_prompt = custom_prompt.replace("[CAPTION]", caption[:100])
            
            # Add strong technical specifications to prevent text generation
            final_prompt = f"""{custom_prompt}
CRITICAL: Absolutely NO text, NO words, NO letters, NO signs, NO labels, NO typography anywhere in the image.
Do not generate: store signs, product labels, brand names, written text, numbers, letters, Arabic text, English text, or any readable characters.
Clean product photography without any visible text or writing.
Aspect ratio: 16:9."""
            prompts.append(final_prompt)
            
        else:
            # Use AI to generate a contextually relevant prompt
            ai_prompt = f"""
Generate a detailed image prompt for AI image generation based on this social media post:

Title: {title}
Caption: {caption}

Create a professional product photography prompt that:
1. Shows the actual products/items mentioned or implied in the post
2. Uses appropriate styling for the industry (beauty/cosmetics/tech/fashion/etc)
3. Is visually appealing and commercial-quality
4. Relevant to UAE market
5. No text in the image

Return ONLY the image generation prompt, nothing else. Be specific about products, lighting, and composition.
"""

            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": ai_prompt}],
                    max_tokens=200
                )
                
                smart_prompt = resp.choices[0].message.content.strip()
                
                # Add strong technical specifications to prevent text generation
                final_prompt = f"""{smart_prompt}
CRITICAL: Absolutely NO text, NO words, NO letters, NO signs, NO labels, NO typography anywhere in the image.
Do not generate: store signs, product labels, brand names, written text, numbers, letters, Arabic text, English text, or any readable characters.
Clean product photography without any visible text or writing.
Aspect ratio: 16:9. Professional commercial photography."""
                
                prompts.append(final_prompt)
                print(f"✓ Generated smart prompt for: {title[:50]}...")
                
            except Exception as e:
                print(f"⚠️ Error generating smart prompt, using fallback: {e}")
                # Fallback to basic prompt
                fallback_prompt = f"""
Professional commercial photograph.
Subject: {title}
Context: {caption[:100]}
Style: high-quality product photography, studio lighting
Mood: professional, commercial, aspirational
CRITICAL: Absolutely NO text, NO words, NO letters, NO signs, NO labels anywhere in the image.
Clean photography without any visible text or writing.
Aspect ratio: 16:9.
                """
                prompts.append(fallback_prompt.strip())

    return {"image_prompts": prompts}


# ------------------------------------------------------------
# VIDEO REELS SCRIPT GENERATOR
# ------------------------------------------------------------
def generate_reels_script(topic):
    """Generate a TikTok/Reel script about a given topic."""
    
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty")

    prompt = f"""
Create a TikTok/Reel Script about: {topic}

Return JSON ONLY:
{{
  "reel_script": {{
    "hook": "",
    "scenes": [
      {{"scene": 1, "description": "", "camera_direction": "", "narration": ""}},
      {{"scene": 2, "description": "", "camera_direction": "", "narration": ""}},
      {{"scene": 3, "description": "", "camera_direction": "", "narration": ""}}
    ],
    "cta": ""
  }}
}}
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = resp.choices[0].message.content.strip()
        
        if not content:
            raise ValueError("Empty response from OpenAI")
        
        result = json.loads(content)
        
        # Validate structure
        if "reel_script" not in result:
            raise ValueError("Invalid reel script response structure")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON from OpenAI: {e}")
        print(f"Response was: {content[:200]}")
        raise
    except Exception as e:
        print(f"❌ Error generating reel script: {e}")
        raise


# ------------------------------------------------------------
# HELPER: GET SYSTEM FONT
# ------------------------------------------------------------
def get_system_font():
    """Get appropriate font path based on operating system."""
    system = platform.system()
    
    if system == "Windows":
        return "arial.ttf"
    elif system == "Darwin":  # macOS
        return "/System/Library/Fonts/Helvetica.ttc"
    else:  # Linux
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ------------------------------------------------------------
# BRAND TEXT OVERLAY - RETURNS LOCAL FILE PATH
# ------------------------------------------------------------
def add_brand_text(image_url, brand_text="Experts Group FZE", website_text="", text_size=80):
    """Download image and add brand text overlay with optional second line. Returns local file path.
    
    Args:
        image_url: URL of the image to download
        brand_text: Text to overlay on the image (Line 1)
        website_text: Website or tagline text (Line 2, optional)
        text_size: Font size for the text (default: 80)
    """
    
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content)).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Load fonts with custom size
        try:
            main_font = ImageFont.truetype(get_system_font(), text_size)
            # Website text slightly smaller
            website_font = ImageFont.truetype(get_system_font(), int(text_size * 0.7))
        except Exception as e:
            print(f"⚠️ Could not load system font: {e}. Using default.")
            main_font = ImageFont.load_default()
            website_font = ImageFont.load_default()

        width, height = img.size

        # Prepare text lines
        texts_to_draw = []
        
        # Line 1: Brand text
        if brand_text:
            wrap_width = int(40 * (80 / text_size))
            wrapped_brand = textwrap.fill(brand_text, width=wrap_width)
            texts_to_draw.append((wrapped_brand, main_font))
        
        # Line 2: Website text (if provided)
        if website_text:
            wrap_width_web = int(50 * (80 / text_size))
            wrapped_website = textwrap.fill(website_text, width=wrap_width_web)
            texts_to_draw.append((wrapped_website, website_font))
        
        # Calculate total height needed
        total_height = 0
        line_spacing = int(text_size * 0.3)  # Space between lines
        
        for text, font in texts_to_draw:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_height = text_bbox[3] - text_bbox[1]
            total_height += text_height
            if len(texts_to_draw) > 1:
                total_height += line_spacing
        
        # Starting Y position (from bottom)
        current_y = height - total_height - 60
        
        # Draw each text line
        shadow_offset = max(3, int(text_size / 25))
        
        for text, font in texts_to_draw:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            
            # Draw shadow
            draw.text((x + shadow_offset, current_y + shadow_offset), text, font=font, fill=(0, 0, 0))
            # Draw text
            draw.text((x, current_y), text, font=font, fill=(255, 255, 255))
            
            # Move to next line
            current_y += text_height + line_spacing

        # Create images directory if it doesn't exist
        if not os.path.exists("images"):
            os.makedirs("images")

        output_path = f"images/branded_{int(datetime.now().timestamp())}.jpg"
        img.save(output_path, quality=95)

        print(f"✓ Branded image saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error adding brand text: {e}")
        raise


# ------------------------------------------------------------
# UPLOAD IMAGE TO IMGBB (Free Image Hosting)
# ------------------------------------------------------------
def upload_to_imgbb(image_path):
    """Upload local image to ImgBB and return public URL."""
    
    # Check if API key is configured
    if not IMGBB_API_KEY or IMGBB_API_KEY == "":
        print(f"⚠️  ImgBB API key not configured in .env file")
        print(f"   Cannot upload branded image to web")
        print(f"   Get free API key at: https://api.imgbb.com/")
        return None
    
    try:
        print(f"📤 Uploading to ImgBB: {image_path}")
        
        with open(image_path, "rb") as file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": IMGBB_API_KEY},
                files={"image": file},
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                url = data["data"]["url"]
                print(f"✓ Uploaded to ImgBB: {url}")
                return url
            else:
                print(f"⚠️  ImgBB upload failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"⚠️  ImgBB upload failed with status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"⚠️  ImgBB upload error: {e}")
        return None


# ------------------------------------------------------------
# AI IMAGE GENERATION WITH TEXT OVERLAY
# ------------------------------------------------------------
def generate_images(prompts, brand_text=None, website_text="", text_size=80):
    """Generate images with optional text overlay.
    
    Args:
        prompts: Dictionary with image_prompts list
        brand_text: Text to overlay on images - Line 1 (None = no overlay, clean images only)
        website_text: Website/tagline text - Line 2 (optional)
        text_size: Font size for text overlay (default: 80)
    
    Returns:
        Dictionary with image_urls list
        - If brand_text provided: URLs of uploaded branded images (or clean if upload fails)
        - If brand_text is None: Clean Replicate URLs
    """
    
    if not prompts or "image_prompts" not in prompts or not prompts["image_prompts"]:
        print("⚠️ No image prompts provided")
        return {"image_urls": []}

    image_urls = []

    for i, prompt in enumerate(prompts["image_prompts"], 1):
        print(f"\n🎨 Generating image {i}/{len(prompts['image_prompts'])}...")
        print(f"   Prompt: {prompt[:100]}...")

        try:
            # Generate AI image
            output = replicate_client.run(
                "black-forest-labs/flux-schnell",
                input={"prompt": prompt}
            )
            
            if not output or len(output) == 0:
                print(f"⚠️ No output from Replicate for prompt {i}")
                continue
            
            # Convert FileOutput to string URL
            clean_url = str(output[0]) if output[0] else None
            
            if not clean_url:
                print(f"⚠️ No URL in output for prompt {i}")
                continue
                
            print(f"✓ Generated clean image: {clean_url}")

            # DECISION: Add text overlay or use clean image?
            if brand_text:
                overlay_info = f"'{brand_text}'"
                if website_text:
                    overlay_info += f" + '{website_text}'"
                print(f"✍️  Adding text overlay: {overlay_info} (size: {text_size})")
                
                try:
                    # Download and add text overlay with custom size and optional second line
                    local_file = add_brand_text(clean_url, brand_text=brand_text, website_text=website_text, text_size=text_size)
                    
                    # Upload branded image to ImgBB
                    uploaded_url = upload_to_imgbb(local_file)
                    
                    if uploaded_url:
                        # Successfully uploaded branded image
                        print(f"✅ Using branded image URL: {uploaded_url}")
                        image_urls.append(uploaded_url)
                    else:
                        # Upload failed - fallback to clean image
                        print(f"⚠️  Upload failed, using clean image instead")
                        image_urls.append(clean_url)
                    
                except Exception as e:
                    print(f"⚠️ Text overlay failed: {e}")
                    # Fallback to clean image
                    image_urls.append(clean_url)
            else:
                # No text overlay requested - use clean Replicate URL
                print(f"   Using clean image (no text overlay)")
                image_urls.append(clean_url)
            
            # Small delay to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"❌ Image generation error for prompt {i}: {str(e)}")
            continue

    if brand_text:
        print(f"\n✅ Generated {len(image_urls)} images with text overlay: '{brand_text}'")
    else:
        print(f"\n✅ Generated {len(image_urls)} clean images (no text overlay)")
    
    return {"image_urls": image_urls}


# ------------------------------------------------------------
# SEND TO ZAPIER
# ------------------------------------------------------------
def send_to_zapier(payload):
    """Send content to Zapier webhook for Instagram posting."""
    
    print("\n" + "="*60)
    print("📤 SENDING TO ZAPIER")
    print("="*60)

    # Extract image URL (first image if available)
    image_url = None
    
    # Check if there are any images
    if payload.get("images") and payload["images"].get("image_urls"):
        images_list = payload["images"]["image_urls"]
        if images_list and len(images_list) > 0:
            image_url = images_list[0]
            
            # Should be a web URL now (either clean or uploaded branded)
            if image_url.startswith("http://") or image_url.startswith("https://"):
                print(f"✓ Using image URL: {image_url}")
            else:
                print(f"⚠️  Invalid image URL: {image_url}")
                image_url = None
    
    # Get first post
    if not payload.get("posts") or len(payload["posts"]) == 0:
        raise ValueError("No posts available to send to Zapier")
    
    first_post = payload["posts"][0]

    # Build Zapier payload with clear field names
    zapier_payload = {
        "topic": payload.get("topic", ""),
        "caption": first_post.get("caption", ""),
        "hashtags": first_post.get("hashtags", ""),
        "full_text": first_post.get("caption", "") + " " + first_post.get("hashtags", ""),
        "image_url": image_url,
        "post_title": first_post.get("title", ""),
        "timestamp": datetime.now().isoformat()
    }

    print("\n📦 Payload being sent:")
    print(json.dumps(zapier_payload, indent=2))
    print("\n🔍 Field verification:")
    print(f"   - caption: {'✓ Present' if zapier_payload['caption'] else '✗ Missing'}")
    print(f"   - hashtags: {'✓ Present' if zapier_payload['hashtags'] else '✗ Missing'}")
    if image_url:
        print(f"   - image_url: ✓ Present (WEB URL)")
    else:
        print(f"   - image_url: ✗ Missing (local file cannot be sent)")
    print(f"   - full_text: {'✓ Present' if zapier_payload['full_text'] else '✗ Missing'}")

    try:
        print(f"\n🌐 Sending POST request to:")
        print(f"   {ZAPIER_WEBHOOK_URL}")
        
        r = requests.post(
            ZAPIER_WEBHOOK_URL,
            json=zapier_payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n✓ Response Status: {r.status_code}")
        print(f"  Response Body: {r.text[:200]}")
        
        if r.status_code == 200:
            print("\n✅ Successfully sent to Zapier!")
        else:
            print(f"\n⚠️  Zapier returned status code: {r.status_code}")
        
        print("="*60 + "\n")
        
        return {
            "status": r.status_code,
            "response": r.text,
            "sent_payload": zapier_payload
        }
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Zapier error: {e}")
        print("="*60 + "\n")
        return {
            "status": "error",
            "response": str(e),
            "sent_payload": zapier_payload
        }


# ------------------------------------------------------------
# SAVE RESULT JSON
# ------------------------------------------------------------
def save_result_to_json(data):
    """Save pipeline result to JSON file with timestamp."""
    
    filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✓ Result saved to {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error saving result: {e}")
        raise