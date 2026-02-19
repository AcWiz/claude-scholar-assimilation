#!/usr/bin/env node
/**
 * UserPromptSubmit Hook: Forced skill activation flow (cross-platform version)
 *
 * Event: UserPromptSubmit
 * Function: Force AI to evaluate available skills and begin implementation after activation
 */

const path = require('path');
const fs = require('fs');
const os = require('os');
const common = require('./hook-common');

// Read stdin input
let input = {};
try {
  const stdinData = require('fs').readFileSync(0, 'utf8');
  if (stdinData.trim()) {
    input = JSON.parse(stdinData);
  }
} catch {
  // Use default empty object
}

const userPrompt = input.user_prompt || '';

// Check if it is a slash command (escape)
if (userPrompt.startsWith('/')) {
  // Distinguish commands from paths:
  // - Commands: /commit, /update-github (no second slash after the first)
  // - Paths: /Users/xxx, /path/to/file (contains path separators)
  const rest = userPrompt.substring(1);
  if (rest.includes('/')) {
    // This is a path, continue with skill scanning
  } else {
    // This is a command, skip skill evaluation
    console.log(JSON.stringify({ continue: true }));
    process.exit(0);
  }
}

const homeDir = os.homedir();

// Dynamically collect skill list
function collectSkills() {
  const skills = [];
  const skillsDir = path.join(homeDir, '.claude', 'skills');

  // 1. Collect local skills
  if (fs.existsSync(skillsDir)) {
    const skillDirs = fs.readdirSync(skillsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);

    for (const skillName of skillDirs) {
      skills.push(skillName);
    }
  }

  // 2. Collect plugin skills
  const pluginsCache = path.join(homeDir, '.claude', 'plugins', 'cache');

  if (fs.existsSync(pluginsCache)) {
    const marketplaces = fs.readdirSync(pluginsCache, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);

    for (const marketplace of marketplaces) {
      const marketplacePath = path.join(pluginsCache, marketplace);
      const plugins = fs.readdirSync(marketplacePath, { withFileTypes: true })
        .filter(d => d.isDirectory() && !d.name.startsWith('.'))
        .map(d => d.name);

      for (const plugin of plugins) {
        const pluginPath = path.join(marketplacePath, plugin);
        const versions = fs.readdirSync(pluginPath, { withFileTypes: true })
          .filter(d => d.isDirectory())
          .map(d => d.name)
          .sort()
          .reverse();

        if (versions.length > 0) {
          const latestVersion = versions[0];
          const skillsDirPath = path.join(pluginPath, latestVersion, 'skills');

          if (fs.existsSync(skillsDirPath)) {
            const skillDirs = fs.readdirSync(skillsDirPath, { withFileTypes: true })
              .filter(d => d.isDirectory())
              .map(d => d.name);

            for (const skillName of skillDirs) {
              skills.push(`${plugin}:${skillName}`);
            }
          }
        }
      }
    }
  }

  // Deduplicate
  return [...new Set(skills)].sort();
}

// Categorize skills into groups
function categorizeSkills(skills) {
  const categories = {
    'Research & Writing': /research|paper|writing|citation|review-response|rebuttal|post-acceptance|doc-coauthoring|latex|daily-paper|ml-paper|results-analysis|brainstorm/,
    'Development': /coding|git|code-review|bug|architecture|verification|tdd|uv-package|webapp-testing|kaggle|driven-development|development-branch|planning|dispatching|executing|using-superpowers/,
    'Plugin Dev': /skill-|command-|hook-|mcp-|agent-identifier|command-name/,
    'Design & UI': /frontend|ui-ux|web-design|canvas|brand|theme|algorithmic-art|slack-gif|figma/,
    'Documents': /docx|xlsx|pptx|pdf|internal-comms|web-artifacts/,
  };

  const grouped = {};
  for (const cat of Object.keys(categories)) {
    grouped[cat] = [];
  }
  grouped['Other'] = [];

  for (const skill of skills) {
    let matched = false;
    for (const [cat, regex] of Object.entries(categories)) {
      if (regex.test(skill)) {
        grouped[cat].push(skill);
        matched = true;
        break;
      }
    }
    if (!matched) {
      grouped['Other'].push(skill);
    }
  }

  return grouped;
}

// Generate skill list
const SKILL_LIST = collectSkills();
const SKILL_GROUPS = categorizeSkills(SKILL_LIST);

// Format grouped skills (skip empty groups)
const groupedDisplay = Object.entries(SKILL_GROUPS)
  .filter(([, skills]) => skills.length > 0)
  .map(([cat, skills]) => `[${cat}] ${skills.join(', ')}`)
  .join('\n');

// Generate output
const output = `## Instruction: Forced Skill Activation (Mandatory)

Silently scan the user's request against available skills. Do NOT list every skill with Yes/No.

Available skills:
${groupedDisplay}

**Action**:
- If any skill matches → Activate via Skill tool, then output: "Activating: [skill-name] — [reason]"
- If no skill matches → Output: "No skills needed"
- Begin implementation only after activation is complete.
- When multiple skills match, activate all of them.
`;

console.log(output);

process.exit(0);
