# Adding a blog post

Add one file to `_posts/`. Nothing else — the Blog page and the homepage
"Recent" list pick it up on the next build.

## 1. Name the file

```
_posts/YYYY-MM-DD-your-post-slug.md
```

The date prefix is required. The slug becomes the URL:
`2026-09-28-agents-in-the-wild.md` → `/blogposts/agents-in-the-wild/`

## 2. Write it

```markdown
---
title: Agents in the Wild
authors: [marko-morrison, vyas-sekar]
description: One or two sentences. Shown on the Blog index and used as the page's search-result summary.
---

Opening paragraph. Plain Markdown from here down.

### A section heading

Some more text, with a [link](https://example.com) in it.

- a list item
- another one
```

That's the whole file. `title`, `authors` and `description` are the only
front-matter fields you need.

## Author ids

`authors` holds ids from `_data/people.yml`, not names. Current ids:

```
vyas-sekar      lujo-bauer      roman-belaire
marko-morrison  lakshmi-adiga   lesley-zhou
alicia-crotty   shaden-almodhy  luke-erbsen
merlin-enriquez ella-park
```

## Two things that fail quietly

- **A future date hides the post.** Jekyll skips posts dated later than the
  build, with no error. If your post isn't showing up, check this first.
- **A mistyped author id** prints the raw id instead of a linked name.

## Figures

Only if you need an interactive chart. Put a Vega-Lite spec in
`assets/data/`, then:

```markdown
<div class="figure" data-vega="/assets/data/your-spec.vl.json"></div>
<p class="figure-caption">What the reader should take from it.</p>
```
