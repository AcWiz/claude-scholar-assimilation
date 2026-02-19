---
description: "Generate promotion content for accepted paper across platforms"
arguments:
  - name: "platform"
    description: "Target platform: twitter, linkedin, blog, all"
    required: false
---

# /promote - Paper Promotion Content Generator

Generate promotion content for your accepted paper across multiple platforms. Target platform: "$platform" (default: all).

## What This Command Does

1. Generates platform-specific promotion content
2. Adapts tone and format for each platform
3. Includes key visual and link recommendations

## Workflow

1. Read the paper to extract key selling points
2. Identify the core contribution in one sentence
3. Generate content for each platform:

### Twitter/X Thread
- Hook tweet (attention-grabbing, < 280 chars)
- 3-5 follow-up tweets explaining method and results
- Include figure recommendations
- Relevant hashtags

### LinkedIn Post
- Professional tone, 3-4 paragraphs
- Problem statement, approach, key results
- Call to action (paper link, code link)

### Blog Post
- Accessible language for broader audience
- 500-800 words
- Sections: Motivation, What We Did, Key Results, What's Next
- Include figures and code snippets

### WeChat / Chinese Social Media
- Chinese language adaptation
- Adapted for Chinese academic community

## Output

Generate `promotion/` directory with:
- `twitter-thread.md`
- `linkedin-post.md`
- `blog-post.md`
- `wechat-post.md` (if Chinese audience targeted)

## Tips

- Prepare content 1 week before conference
- Coordinate timing with conference schedule
- Use high-quality visuals
- Include links to paper and code repository
