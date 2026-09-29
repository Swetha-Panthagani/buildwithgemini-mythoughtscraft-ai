import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

async def run():
    print("Launching browser with Playwright video recording...")
    os.makedirs("/config/Desktop/BuildWithGemini/demo_recordings", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )
        context = await browser.new_context(
            record_video_dir="/config/Desktop/BuildWithGemini/demo_recordings",
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. First interaction: Show off what StoryCraft AI does best (narrative / poetry / pitch)
        print("Clicking poetry example chip...")
        chips = await page.query_selector_all(".chip")
        if len(chips) >= 2:
            print("Found chips, clicking chip[1]...")
            await chips[1].click()
            await asyncio.sleep(1)
        else:
            await page.fill("#input", "Write a reflective poem about late night coding in an empty room with rain outside")
            await asyncio.sleep(1)
        
        # Click send button
        print("Submitting Prompt 1...")
        await page.click("button:has-text('Send')")
        
        # Wait for the agent to respond with A2UI card / poetic verse
        print("Waiting for response to Prompt 1...")
        try:
            await page.wait_for_selector(".msg-row.agent", timeout=90000)
            # Give time for streaming to complete & visual presentation
            await asyncio.sleep(8)
            print("Response 1 received and displayed!")
        except Exception as e:
            print("Prompt 1 wait note:", e)

        # 2. Second prompt: Rich tool call, database lookup, or image generation
        print("Sending Prompt 2 (Tool invocation: generate cover art and save article)...")
        prompt2 = "Create an editorial cover art image for this piece and save this poem to Firestore with article_id 'rain-and-code-poem'."
        await page.fill("#input", prompt2)
        await asyncio.sleep(1)
        await page.click("button:has-text('Send')")

        print("Waiting for response to Prompt 2...")
        try:
            # We wait for the second assistant message
            await page.wait_for_function("document.querySelectorAll('.msg-row.agent').length >= 2", timeout=120000)
            print("Received response 2! Waiting for tool execution, image rendering and card display...")
            await asyncio.sleep(14)
            print("Response 2 rendered cleanly!")
        except Exception as e:
            print("Prompt 2 wait note:", e)

        video_path = await page.video.path()
        await context.close()
        await browser.close()
        print(f"Playwright raw video recorded at: {video_path}")
        
        # Convert webm to polished mp4 using ffmpeg
        target_mp4 = "/config/Desktop/BuildWithGemini/storycraft_agent_demo.mp4"
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p", target_mp4
        ]
        subprocess.run(cmd, check=True)
        print(f"Final polished MP4 saved to: {target_mp4}")

if __name__ == "__main__":
    asyncio.run(run())
