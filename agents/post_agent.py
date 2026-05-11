from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

PLATFORM_CONFIG = {
    "LinkedIn": {
        "tone": "professional yet warm and personable",
        "length": "150-300 words",
        "hashtags": 5,
        "emojis": "1-3 tasteful emojis",
        "style": "Start with a scroll-stopping hook. Tell a brief story. End with a clear CTA asking connections to reach out or share.",
    },
    "Naukri": {
        "tone": "direct, professional, achievement-focused",
        "length": "100-180 words",
        "hashtags": 3,
        "emojis": "2-4 emojis",
        "style": "Lead with years of experience. Highlight top 3-4 skills prominently. Mention current location and open to relocation.",
    },
    "Indeed": {
        "tone": "factual, straightforward, professional",
        "length": "80-140 words",
        "hashtags": 2,
        "emojis": "0-2 emojis",
        "style": "List key qualifications clearly. State target role explicitly. Keep it concise and to the point.",
    },
    "Unstop": {
        "tone": "energetic, ambitious, student/early-career enthusiasm",
        "length": "100-200 words",
        "hashtags": 6,
        "emojis": "5-8 emojis throughout",
        "style": "Show excitement and ambition. Highlight projects, competitions, learning attitude. Very energetic tone.",
    },
    "Twitter/X": {
        "tone": "punchy, witty, concise",
        "length": "under 270 characters for main tweet, or a 3-4 tweet thread",
        "hashtags": 3,
        "emojis": "2-4 emojis",
        "style": "Hook in first 5 words. If thread, each tweet must stand alone. End with strong CTA.",
    },
}

POST_TYPE_CONTEXT = {
    "Open to Work / Job Seeking": "actively looking for new opportunities",
    "New Role Announcement": "excited to announce starting a new position",
    "Skills Showcase": "highlighting technical expertise and capabilities",
    "Project Highlight": "sharing an exciting project they built",
    "Achievement / Milestone": "celebrating a professional achievement",
    "Career Change": "transitioning to a new field or domain",
    "Learning Journey": "sharing what they are currently learning",
}


def generate_post(personal_info: dict, skills: list, experience: list,
                  platform: str, post_type: str, api_key: str) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        google_api_key=api_key,
        temperature=0.8,
    )

    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["LinkedIn"])
    context = POST_TYPE_CONTEXT.get(post_type, post_type)

    name = f"{personal_info.get('first_name', '')} {personal_info.get('last_name', '')}".strip()
    top_skills = [s.get("name", "") for s in skills[:8] if s.get("name")]
    roles = [e.get("role", "") for e in experience[:2] if e.get("role")]
    companies = [e.get("company", "") for e in experience[:2] if e.get("company")]

    years_exp = 0
    for e in experience:
        try:
            sd = e.get("start_date", "")
            ed = e.get("end_date", "")
            if sd and ed and ed.lower() not in ["present","current","now"]:
                years_exp += 1
            elif sd:
                years_exp += 1
        except Exception:
            pass

    prompt = f"""You are a professional social media content creator who specializes in authentic career posts.

Create a genuine, human-sounding {platform} post for this real professional.

PERSON DETAILS:
- Name: {name}
- Purpose: {context}
- Post Type: {post_type}
- Top Skills: {', '.join(top_skills)}
- Recent Roles: {', '.join(roles)}
- Companies: {', '.join(companies)}
- Experience: {years_exp}+ years

PLATFORM: {platform}
TONE: {config['tone']}
LENGTH: {config['length']}
STYLE GUIDE: {config['style']}
EMOJIS: Use {config['emojis']}
HASHTAGS: Include exactly {config['hashtags']} highly relevant hashtags at the end

CRITICAL REQUIREMENTS:
1. Sound like a REAL human wrote this — not AI
2. Use platform-native language and conventions
3. Include specific skills/technologies by name
4. Make it authentic and personal
5. For LinkedIn: use line breaks between paragraphs for readability
6. For Twitter: if thread, number tweets as 1/3, 2/3, 3/3
7. Hashtags should be on separate lines at the end
8. Include a compelling call-to-action

OUTPUT: Only the post text, ready to copy-paste. No labels, no meta-commentary.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
