#!/usr/bin/env python3
"""
🎬 ULTIMATE YouTube Video Creator
Một lệnh duy nhất để tạo video từ tin tức đến video script

Usage:
    python create_video.py              # Full pipeline
    python create_video.py --quick      # Skip some steps
    python create_video.py --lang vi    # Vietnamese content
    python create_video.py --lang en    # English content
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional

try:
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError:
    pass  # Will handle gracefully if not installed

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}╔{'═'*66}╗{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}║  {text:<62}║{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}╚{'═'*66}╝{Colors.ENDC}\n")


def print_step(step_num: int, title: str, description: str = "") -> None:
    """Print step information"""
    print(f"{Colors.OKCYAN}{'─'*70}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}📍 STEP {step_num}: {title}{Colors.ENDC}")
    if description:
        print(f"   {description}")
    print(f"{Colors.OKCYAN}{'─'*70}{Colors.ENDC}")


def print_success(message: str) -> None:
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str) -> None:
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message: str) -> None:
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message: str) -> None:
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


def run_command(command: str, description: str = "", timeout: int = 300) -> Tuple[bool, str]:
    """
    Run a shell command and capture output
    
    Returns:
        (success: bool, output: str)
    """
    try:
        print_info(f"Executing: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


def check_prerequisites() -> bool:
    """Check if all required tools are installed"""
    print_step(0, "CHECKING PREREQUISITES", "Verifying required tools...")
    
    checks = []
    
    # Check Node.js
    success, _ = run_command("node --version")
    node_ok = success
    checks.append(("Node.js", node_ok))
    
    # Check Python
    success, _ = run_command("python --version")
    python_ok = success
    checks.append(("Python", python_ok))
    
    # Check npm
    success, _ = run_command("npm --version")
    npm_ok = success
    checks.append(("npm", npm_ok))
    
    # Check Jupyter (optional but recommended)
    success, _ = run_command("jupyter --version")
    jupyter_ok = success
    checks.append(("Jupyter", jupyter_ok))
    
    # Print results
    for tool, ok in checks:
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if ok else f"{Colors.FAIL}✗{Colors.ENDC}"
        required = "" if ok or tool == "Jupyter" else " (REQUIRED)"
        print(f"  {status} {tool}{required}")
    
    all_ok = node_ok and python_ok and npm_ok
    
    if all_ok:
        print_success("All prerequisites met!")
    else:
        print_error("Some required tools are missing!")
        if not node_ok:
            print_info("Install Node.js from: https://nodejs.org/")
        if not python_ok:
            print_info("Install Python from: https://www.python.org/")
        if not npm_ok:
            print_info("npm should be installed with Node.js")
    
    if not jupyter_ok:
        print_warning("Jupyter not found. Installing jupyter...")
        success, output = run_command("pip install jupyter ipykernel", timeout=120)
        if success:
            print_success("Jupyter installed successfully!")
        else:
            print_warning("Failed to install Jupyter, but pipeline may still work")
    
    return all_ok


def step1_generate_content(language: str = "vi", topic: str = "") -> bool:
    """Step 1: Generate YouTube content from news or topic"""
    if topic:
        print_step(1, "CONTENT GENERATION", 
                   f"Researching topic '{topic}' and creating content ({language})...")
    else:
        print_step(1, "CONTENT GENERATION", 
                   f"Fetching news and creating content ({language})...")
    
    if topic:
        cmd = f"npm run content-gen -- --topic \"{topic}\""
    else:
        cmd = "npm run content-gen"
    
    success, output = run_command(cmd, timeout=120)
    
    if success:
        print_success("Content generated successfully!")
        
        # Check for generated files
        today = datetime.now().strftime("%Y-%m-%d")
        content_file = Path(f"videos/{today}/youtube-content-{today}-{language}.md")
        
        if content_file.exists():
            file_size = content_file.stat().st_size
            print_info(f"Generated file: {content_file.name} ({file_size} bytes)")
            print_success("Content file created!")
            return True
        else:
            print_warning(f"Expected file not found: {content_file}")
            # Check what was actually created
            videos_dir = Path("videos")
            if videos_dir.exists():
                files = list(videos_dir.rglob("*.md"))
                if files:
                    print_info(f"Found {len(files)} markdown file(s)")
                    return True
            return False
    else:
        print_error("Content generation failed!")
        print_info(f"Error: {output[:200]}")
        return False


def step2_process_with_llm() -> bool:
    """Step 2: Process content with Claude API via Python script"""
    print_step(2, "LLM PROCESSING", 
               "Processing content with Claude API (Anthropic)...")
    
    # Use the Python script directly instead of notebook
    success, output = run_command(
        "python run_notebook_logic.py",
        timeout=300,  # Timeout for LLM processing
    )
    
    if success:
        # Check for generated scripts
        scripts_dir = Path("videos_scripts")
        if scripts_dir.exists():
            json_files = list(scripts_dir.glob("*.json"))
            text_files = list(scripts_dir.glob("*.txt"))
            
            print_info(f"Generated {len(json_files)} JSON script(s)")
            print_info(f"Generated {len(text_files)} text guide(s)")
            
            if json_files or text_files:
                print_success("Video scripts created!")
                if json_files:
                    latest_json = sorted(json_files)[-1]
                    print_info(f"Latest script: {latest_json.name}")
                return True
        
        print_warning("Script files not found in expected location")
        return False
    else:
        print_error("Script execution failed!")
        print_info(f"Error: {output[:200]}")
        
        if "ANTHROPIC_API_KEY" in output:
            print_error("API Key issue detected!")
            print_info("Make sure .env file has ANTHROPIC_API_KEY set correctly")
        
        return False


def step3_generate_video_guide() -> bool:
    """Step 3: Generate video production guide and resources"""
    print_step(3, "VIDEO GUIDE GENERATION", 
               "Creating video production guide and resources...")
    
    success, output = run_command("python generate_video.py", timeout=60)
    
    if success:
        print_success("Video guide generated successfully!")
        
        # Check for generated resources
        gen_dir = Path("generated_videos")
        if gen_dir.exists():
            resources = list(gen_dir.glob("*"))
            print_info(f"Generated {len(resources)} resource file(s)")
        
        print_success("All video resources created!")
        return True
    else:
        print_warning("Video guide generation had issues (may be expected)")
        # This step is less critical, so don't fail the whole pipeline
        return True


def show_results_summary() -> None:
    """Show summary of generated files"""
    print_step(4, "RESULTS SUMMARY", "Files generated...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\n{Colors.BOLD}📂 Generated Files:{Colors.ENDC}")
    
    # Content files
    content_dir = Path(f"videos/{today}")
    if content_dir.exists():
        md_files = list(content_dir.glob("*.md"))
        print(f"\n  📄 Content (Markdown):")
        for f in md_files:
            size = f.stat().st_size / 1024
            print(f"     • {f.name} ({size:.1f} KB)")
    
    # Script files
    script_dir = Path("videos_scripts")
    if script_dir.exists():
        json_files = list(script_dir.glob("*.json"))
        txt_files = list(script_dir.glob("*.txt"))
        
        if json_files:
            print(f"\n  📋 Scripts (JSON - for tools):")
            for f in sorted(json_files)[-3:]:  # Show last 3
                size = f.stat().st_size / 1024
                print(f"     • {f.name} ({size:.1f} KB)")
        
        if txt_files:
            print(f"\n  📝 Guides (Text - for reading):")
            for f in sorted(txt_files)[-3:]:  # Show last 3
                size = f.stat().st_size / 1024
                print(f"     • {f.name} ({size:.1f} KB)")
    
    # Video resources
    gen_dir = Path("generated_videos")
    if gen_dir.exists():
        resources = list(gen_dir.glob("*"))
        if resources:
            print(f"\n  🎬 Video Resources:")
            for item in resources[:5]:  # Show first 5
                if item.is_file():
                    print(f"     • {item.name}")
                elif item.is_dir():
                    sub_items = list(item.glob("*"))
                    print(f"     • {item.name}/ ({len(sub_items)} items)")


def show_next_steps() -> None:
    """Show next steps for user"""
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}✨ PIPELINE COMPLETE! ✨{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}📋 Next Steps:{Colors.ENDC}")
    print(f"""
  1. {Colors.OKBLUE}Review Generated Content{Colors.ENDC}
     Open: videos_scripts/script_*.txt
     (or *.json for programmatic use)
  
  2. {Colors.OKBLUE}Create Video{Colors.ENDC}
     Use one of these tools:
     • {Colors.OKCYAN}CapCut{Colors.ENDC} (Web): https://capcut.com
     • {Colors.OKCYAN}DaVinci Resolve{Colors.ENDC} (Free): https://blackmagicdesign.com
     • {Colors.OKCYAN}Premiere Pro{Colors.ENDC} (Pro): Adobe Creative Cloud
  
  3. {Colors.OKBLUE}Follow the Script{Colors.ENDC}
     Use timing cues from the generated script:
     - [00:00] Opening Hook (15 sec)
     - [00:15] Main Content (17.5 min)
     - [17:30] Call to Action (30 sec)
  
  4. {Colors.OKBLUE}Add Visuals{Colors.ENDC}
     • Insert news screenshots/charts
     • Add background music
     • Apply transitions & effects
     • Color grade if needed
  
  5. {Colors.OKBLUE}Export & Upload{Colors.ENDC}
     • Export as MP4 (H.264, 1080p)
     • Use the metadata from script:
       - Title, tags, description
       - Thumbnail concept
     • Upload to YouTube
""")
    
    print(f"{Colors.BOLD}💡 Tips:{Colors.ENDC}")
    print(f"""
  • Use the .txt script as reference while editing
  • Follow timing cues for accurate video length
  • Thumbnail concept guide is in the script
  • Tags and description are pre-generated
  • You can rerun this script daily for new content
""")


def main():
    """Main pipeline orchestrator"""
    
    print_header("🎬 ULTIMATE YOUTUBE VIDEO CREATOR")
    print(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Parse arguments
    args = sys.argv[1:]
    quick_mode = "--quick" in args
    language = "vi"  # Default to Vietnamese
    topic = ""  # Default to no topic (use predefined categories)
    
    # Parse language
    if "--lang" in args:
        idx = args.index("--lang")
        if idx + 1 < len(args):
            language = args[idx + 1]
    
    # Parse topic
    if "--topic" in args:
        idx = args.index("--topic")
        if idx + 1 < len(args):
            topic = args[idx + 1]
    else:
        # Check if topic is passed as positional argument (from npm)
        if args and not args[0].startswith("--"):
            topic = " ".join(args).split("--")[0].strip()
            if topic and topic != "quick":
                # It's a topic
                args = [a for a in args if a != topic]
    
    if quick_mode:
        print_warning("Quick mode enabled (skipping some validations)\n")
    
    if topic:
        print_warning(f"Topic mode: Researching '{topic}'\n")
    
    # Step 0: Check prerequisites
    if not check_prerequisites():
        print_error("\nPlease install missing tools and try again.")
        sys.exit(1)
    
    print()
    
    # Step 1: Generate Content
    start_time = time.time()
    if not step1_generate_content(language, topic):
        print_error("Failed at Step 1: Content Generation")
        sys.exit(1)
    step1_time = time.time() - start_time
    
    # Step 2: Process with LLM
    start_time = time.time()
    if not step2_process_with_llm():
        print_error("Failed at Step 2: LLM Processing")
        sys.exit(1)
    step2_time = time.time() - start_time
    
    # Step 3: Generate Video Guide
    start_time = time.time()
    if not step3_generate_video_guide():
        print_warning("Step 3: Video guide generation had issues (continuing...)")
    step3_time = time.time() - start_time
    
    # Show results
    show_results_summary()
    
    # Timing summary
    total_time = step1_time + step2_time + step3_time
    print(f"\n{Colors.BOLD}⏱️  Pipeline Timing:{Colors.ENDC}")
    print(f"  Step 1 (Content Gen):    {step1_time:6.1f}s")
    print(f"  Step 2 (LLM Process):    {step2_time:6.1f}s")
    print(f"  Step 3 (Video Guide):    {step3_time:6.1f}s")
    print(f"  {Colors.BOLD}Total Time:            {total_time:6.1f}s{Colors.ENDC}")
    
    # Next steps
    show_next_steps()
    
    print(f"{Colors.BOLD}{Colors.OKGREEN}Happy creating! 🚀{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Pipeline interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
