---
name: create-skill
description: Create hybrid skills that can be triggered by description (automatic) or command (manual). Use when you want to create a new automated capability, repetitive workflow, or custom command.
---

# Skill Factory (Hybrid Edition)

Design hybrid skills that can activate by description (automatic) or command (manual).

## Interview Process

Ask these questions one by one and wait for the answer before continuing:

1. **Name**: "What will be the skill ID? (use kebab-case, e.g.: `test-runner`, `module-generator`)"
2. **Manual Trigger**: "What command do you want to use to invoke it manually? (e.g: `/test-all`). If you don't want a manual command, write 'none'."
3. **Automatic Trigger**: "In what situations should the agent activate this skill automatically? (e.g: 'when modifying files in domain/', 'before answering about errors', 'never')."
4. **Action**: "What exact steps should the skill follow? Describe them in order."

## Build the Contract

With the user's answers, build the `SKILL.md` file:

- **Frontmatter**: If there's a manual command, include `name: <skill-id>` and `description: <keywords for auto-activation>`.
- **Instructions**: Define a clear flow with **Input → Process → Validation** sections.

## Execution

1. Create the file in `.opencode/skills/<name>/SKILL.md`
2. Follow opencode skill format with YAML frontmatter containing `name` and `description`

## Sync

Ask the user: "Do you want me to add this skill to the list in `.opencode/README.md`?"

If accepted, edit `.opencode/README.md` and add the new skill under the **Available Skills** section.
