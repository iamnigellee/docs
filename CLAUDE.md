# CLAUDE.md - AI Assistant Documentation Guide

> **Last Updated**: 2026-01-14
> **Repository Type**: Mintlify Documentation Site
> **Framework**: Mintlify v3.x
> **Configuration**: docs.json

## Repository Overview

This repository contains a **Mintlify documentation site** - a modern documentation platform that uses MDX (Markdown + React components) to create beautiful, interactive documentation. This is based on the Mintlify Starter Kit and serves as a template for creating comprehensive documentation sites.

### Purpose
- Provide structured, searchable documentation
- Support both guide-style content and API reference documentation
- Enable local development with live preview
- Auto-deploy to production via GitHub integration

## Codebase Structure

```
/home/user/docs/
├── docs.json                      # Main configuration file (CRITICAL)
├── README.md                      # Development setup instructions
├── favicon.svg                    # Site favicon
│
├── introduction.mdx               # Homepage/landing page
├── quickstart.mdx                 # Getting started guide
├── development.mdx                # Development setup guide
│
├── essentials/                    # Essential documentation features
│   ├── markdown.mdx              # Markdown syntax guide
│   ├── code.mdx                  # Code blocks and syntax highlighting
│   ├── images.mdx                # Image handling
│   ├── settings.mdx              # Configuration settings
│   ├── navigation.mdx            # Navigation structure
│   └── reusable-snippets.mdx     # Content reuse patterns
│
├── api-reference/                 # API documentation section
│   ├── introduction.mdx          # API docs overview
│   ├── openapi.json              # OpenAPI/Swagger specification
│   └── endpoint/                 # Individual endpoint docs
│       ├── get.mdx
│       ├── create.mdx
│       ├── delete.mdx
│       └── webhook.mdx
│
├── snippets/                      # Reusable content snippets
│   └── snippet-intro.mdx
│
├── images/                        # Image assets
│   ├── hero-light.png
│   ├── hero-dark.png
│   └── checks-passed.png
│
└── logo/                          # Brand assets
    ├── light.svg                  # Light theme logo
    └── dark.svg                   # Dark theme logo
```

## File Types and Conventions

### Configuration Files

#### docs.json (CRITICAL - DO NOT BREAK)
The central configuration file that defines:
- **Theme and branding**: colors, logos, favicon
- **Navigation structure**: tabs, groups, pages
- **External links**: navbar, footer, global anchors
- **Page ordering**: determines sidebar and navigation

**Key Rules**:
- Must be valid JSON (no comments, trailing commas)
- Page paths are relative to root WITHOUT `.mdx` extension
- Navigation order in `docs.json` determines display order
- Breaking this file breaks the entire site

**Example structure**:
```json
{
  "$schema": "https://mintlify.com/docs.json",
  "name": "Site Name",
  "navigation": {
    "tabs": [
      {
        "tab": "Guides",
        "groups": [
          {
            "group": "Get Started",
            "pages": ["introduction", "quickstart"]
          }
        ]
      }
    ]
  }
}
```

### Content Files

#### MDX Files (.mdx)
MDX = Markdown + JSX/React components

**Frontmatter** (required at top of every .mdx file):
```yaml
---
title: 'Page Title'              # Required: shown in browser tab and page header
description: 'Page description'  # Required: used for SEO and page subtitle
icon: 'icon-name'               # Optional: FontAwesome icon name
---
```

**Supported Components**:
- `<Card>`, `<CardGroup>` - Interactive cards with links
- `<Accordion>`, `<AccordionGroup>` - Collapsible sections
- `<Tip>`, `<Info>`, `<Warning>`, `<Note>` - Callout boxes
- `<CodeGroup>` - Tabbed code blocks
- `<Frame>` - Image frames with styling
- `<Latex>` - Mathematical equations

**Markdown Conventions**:
- Use `##` for main sections (creates TOC entries)
- Use `###` for subsections
- Use relative links with full paths: `/essentials/markdown` not `../markdown`
- Code blocks with language: ` ```javascript `
- Images with alt text: `![Alt text](/images/filename.png)`

#### Markdown Files (.md)
- Currently only `README.md` exists
- Used for GitHub repository documentation
- Not rendered in Mintlify site

## Development Workflow

### Local Development

**Prerequisites**:
- Node.js v19 or higher
- npm or yarn package manager

**Commands**:
```bash
# Install Mintlify CLI globally
npm i -g mintlify

# Start local development server (run from repo root)
cd /home/user/docs
mintlify dev

# Development server runs at http://localhost:3000

# Use custom port
mintlify dev --port 3333

# Validate links
mintlify broken-links

# Update CLI to latest
npm i -g mintlify@latest
```

**Common Issues**:
- "Could not load sharp module" → Update to Node v19+, reinstall mintlify
- Page loads as 404 → Ensure running in directory with `docs.json`
- Port already in use → CLI auto-increments to next available port

### Deployment

**Automatic Deployment**:
1. Push changes to main branch
2. GitHub App automatically deploys
3. Check commit hash for deployment status

**Manual Deployment**:
- Use Mintlify dashboard: https://dashboard.mintlify.com

## Key Patterns for AI Assistants

### When Creating New Content

1. **Always update docs.json navigation**
   - Add new page to appropriate group in `navigation.tabs`
   - Use correct path (no extension): `"path/to/file"` not `"path/to/file.mdx"`

2. **Follow frontmatter convention**
   ```yaml
   ---
   title: 'Clear, Descriptive Title'
   description: 'Concise description under 160 characters'
   icon: 'relevant-icon'  # Optional but recommended
   ---
   ```

3. **Use consistent heading structure**
   - Start content with `##` (not `#`, title comes from frontmatter)
   - Use `##` for major sections
   - Use `###` for subsections
   - Avoid going deeper than `###`

4. **Leverage Mintlify components**
   - Use `<CardGroup>` for feature showcases
   - Use `<Accordion>` for FAQs or optional content
   - Use `<Note>`, `<Tip>`, `<Info>`, `<Warning>` for callouts
   - Use `<CodeGroup>` for multi-language code examples

### When Editing Existing Content

1. **Preserve frontmatter** - Don't modify unless necessary
2. **Maintain existing structure** - Keep heading hierarchy consistent
3. **Update related navigation** - If renaming, update `docs.json` references
4. **Test locally** - Run `mintlify dev` to verify changes render correctly

### When Adding API Documentation

**Option 1: OpenAPI Specification** (Preferred)
- Update `/api-reference/openapi.json`
- Mintlify automatically generates endpoint pages
- Includes interactive API playground

**Option 2: MDX Components**
- Create individual `.mdx` files in `/api-reference/endpoint/`
- Use Mintlify's API components for request/response examples
- Add to navigation in `docs.json`

### When Adding Images or Assets

1. **Images** → `/images/` directory
   - Use descriptive filenames: `feature-screenshot.png`
   - Support light/dark variants: `hero-light.png`, `hero-dark.png`
   - Reference in MDX: `![Description](/images/filename.png)`

2. **Logos** → `/logo/` directory
   - Maintain `light.svg` and `dark.svg` for theme switching
   - Update `docs.json` if changing logo files

3. **Icons** → Use FontAwesome icon names
   - Set in frontmatter: `icon: 'book-open-cover'`
   - Available icons: https://fontawesome.com/icons

### When Creating Reusable Content

1. Create snippet in `/snippets/` directory
   ```mdx
   // snippets/my-snippet.mdx
   This content can be reused across pages.
   ```

2. Include snippet in other pages
   ```mdx
   <Snippet file="my-snippet.mdx" />
   ```

## Common Tasks

### Add a New Documentation Page

```bash
# 1. Create the file
touch /home/user/docs/path/to/new-page.mdx

# 2. Add frontmatter
cat > /home/user/docs/path/to/new-page.mdx << 'EOF'
---
title: 'New Page Title'
description: 'Clear description of the page content'
---

## Introduction

Your content here...
EOF

# 3. Update docs.json navigation
# Add "path/to/new-page" to appropriate group in navigation

# 4. Test locally
mintlify dev
```

### Reorganize Documentation Structure

1. Move files to new locations
2. Update ALL references in `docs.json` navigation
3. Update internal links in MDX files to match new paths
4. Run `mintlify broken-links` to verify

### Update Site Branding

Edit `docs.json`:
```json
{
  "name": "Your Site Name",
  "colors": {
    "primary": "#HEX",
    "light": "#HEX",
    "dark": "#HEX"
  },
  "logo": {
    "light": "/logo/light.svg",
    "dark": "/logo/dark.svg"
  },
  "favicon": "/favicon.svg"
}
```

### Add Code Examples

```mdx
<CodeGroup>

```bash npm
npm install package-name
```

```bash yarn
yarn add package-name
```

```bash pnpm
pnpm add package-name
```

</CodeGroup>
```

## Important Conventions

### DO ✅

- **Always validate docs.json syntax** before committing
- **Use root-relative paths** in links: `/path/to/page`
- **Include descriptive alt text** for images
- **Test locally** with `mintlify dev` before pushing
- **Follow existing naming conventions** for files (lowercase, hyphens)
- **Add icons** to frontmatter for visual consistency
- **Use semantic heading hierarchy** (##, then ###)
- **Leverage Mintlify components** for rich content
- **Keep descriptions concise** (under 160 chars for SEO)

### DON'T ❌

- **Don't use relative links** like `../page` (use `/path/to/page`)
- **Don't break docs.json** (validate JSON syntax)
- **Don't skip frontmatter** (required for every .mdx file)
- **Don't use `#` for page titles** (comes from frontmatter)
- **Don't commit without testing** (run `mintlify dev` first)
- **Don't hardcode URLs** that should be in `docs.json` config
- **Don't nest headings too deep** (stop at ###)
- **Don't forget to update navigation** when adding pages

## Git Workflow

### Branch Strategy
- Feature branches: `claude/feature-name-{sessionId}`
- Main branch: Auto-deploys to production
- Always create PRs for review

### Commit Conventions
```bash
# Good commit messages
git commit -m "Add API authentication documentation"
git commit -m "Update quickstart guide with Node.js v19 requirement"
git commit -m "Fix broken links in essentials section"

# Bad commit messages
git commit -m "Update files"
git commit -m "Changes"
git commit -m "Fix"
```

### Pre-commit Checklist
- [ ] Run `mintlify dev` and verify changes render correctly
- [ ] Check `docs.json` is valid JSON (no syntax errors)
- [ ] Run `mintlify broken-links` to catch broken links
- [ ] Verify all new pages are added to navigation
- [ ] Check images load correctly in both light/dark themes
- [ ] Ensure frontmatter is complete on all new .mdx files

## Troubleshooting

### Page Not Showing in Navigation
- Check if page is listed in `docs.json` navigation
- Verify path in `docs.json` matches file path (without .mdx)
- Ensure file has valid frontmatter with `title`

### Images Not Loading
- Verify image exists in `/images/` directory
- Check path starts with `/images/` not `./images/`
- Ensure image file extension matches reference

### Syntax Error in docs.json
- Validate JSON syntax (no trailing commas, no comments)
- Use JSON validator: `cat docs.json | jq .`
- Check all quotes are double quotes, not single

### Local Development Not Working
- Update Node.js to v19 or higher
- Reinstall Mintlify: `npm remove -g mintlify && npm i -g mintlify`
- Delete `~/.mintlify` folder and try again
- Ensure running from directory containing `docs.json`

## External Resources

- **Mintlify Documentation**: https://mintlify.com/docs
- **Mintlify Dashboard**: https://dashboard.mintlify.com
- **Mintlify CLI**: https://www.npmjs.com/package/mintlify
- **MDX Documentation**: https://mdxjs.com
- **FontAwesome Icons**: https://fontawesome.com/icons

## AI Assistant Best Practices

When working with this repository:

1. **Read before writing** - Always read existing files before making changes
2. **Validate configuration** - After editing `docs.json`, verify it's valid JSON
3. **Test changes** - Use `mintlify dev` to preview changes before committing
4. **Follow patterns** - Look at existing files for structure and style examples
5. **Update navigation** - Never forget to update `docs.json` when adding pages
6. **Maintain consistency** - Match the tone, style, and structure of existing content
7. **Use components** - Leverage Mintlify's rich component library
8. **Think holistically** - Consider how changes affect navigation, links, and user flow

## Questions to Ask Before Making Changes

- [ ] Does this change require updating `docs.json`?
- [ ] Are there internal links that need updating?
- [ ] Should this content be reusable (create a snippet)?
- [ ] Does this fit the existing information architecture?
- [ ] Will this render correctly in both light and dark themes?
- [ ] Is the content clear and concise?
- [ ] Are there related pages that should link to this?

---

**Remember**: This is a documentation site built for clarity and user experience. Every change should make it easier for users to find and understand information. When in doubt, test locally with `mintlify dev` before committing.
